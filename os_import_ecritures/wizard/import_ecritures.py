import base64
import csv
import io
import logging
from collections import OrderedDict

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Description du format source.
#
# Le fichier compte 29 colonnes séparées par ';', sans ligne d'en-tête.
# Seules les colonnes ci-dessous portent de l'information exploitable ; les
# autres sont vides ou constantes dans l'export d'origine.
# ---------------------------------------------------------------------------
COL_JOURNAL = 0       # code journal source (ex. VTECPT, DIFFER)
COL_DATE = 1          # date JJMMAA
COL_ACCOUNT = 2       # code du compte général
COL_ACCOUNT_LABEL = 3  # libellé du compte (informatif)
COL_PIECE = 4         # référence de pièce -> clé de regroupement
COL_PARTNER = 8       # code tiers (renseigné sur les lignes de compte collectif)
COL_LABEL = 11        # libellé de la ligne
COL_DEBIT = 21        # montant au débit
COL_CREDIT = 22       # montant au crédit
COL_MATURITY = 26     # date d'échéance JJMMAA
MIN_COLS = 27


def _to_float(value):
    """Convertit '1 234,56' ou '1234.56' en float. Chaîne vide -> 0.0."""
    if not value:
        return 0.0
    cleaned = value.strip().replace(" ", "").replace("\xa0", "").replace(",", ".")
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(value)


def _to_date(value, century):
    """Convertit 'JJMMAA' en date. Chaîne vide -> False."""
    if not value or not value.strip():
        return False
    raw = value.strip().zfill(6)
    if not raw.isdigit():
        raise ValueError(value)
    day, month, year = int(raw[0:2]), int(raw[2:4]), century + int(raw[4:6])
    return fields.Date.to_date("%04d-%02d-%02d" % (year, month, day))


class ImportEcrituresJournal(models.TransientModel):
    _name = "os.import.ecritures.journal"
    _description = "Correspondance journal source / journal Odoo"

    wizard_id = fields.Many2one("os.import.ecritures", required=True, ondelete="cascade")
    code_source = fields.Char(string="Code source", readonly=True)
    move_count = fields.Integer(string="Pièces", readonly=True)
    journal_id = fields.Many2one(
        "account.journal", string="Journal Odoo", required=True,
        domain="[('company_id', '=', parent.company_id)]",
    )


class ImportEcrituresPartner(models.TransientModel):
    _name = "os.import.ecritures.partner"
    _description = "Correspondance tiers source / partenaire Odoo"

    wizard_id = fields.Many2one("os.import.ecritures", required=True, ondelete="cascade")
    code_source = fields.Char(string="Code source", readonly=True)
    name_source = fields.Char(string="Raison sociale (source)", readonly=True)
    move_count = fields.Integer(string="Pièces", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partenaire Odoo")


class ImportEcrituresAccount(models.TransientModel):
    _name = "os.import.ecritures.account"
    _description = "Compte source non résolu dans Odoo"

    wizard_id = fields.Many2one("os.import.ecritures", required=True, ondelete="cascade")
    code_source = fields.Char(string="Code compte", readonly=True)
    name_source = fields.Char(string="Libellé (source)", readonly=True)
    line_count = fields.Integer(string="Lignes", readonly=True)


class ImportEcritures(models.TransientModel):
    _name = "os.import.ecritures"
    _description = "Import d'écritures comptables depuis un fichier tabulé"

    state = fields.Selection(
        [("choose", "Fichier"), ("map", "Correspondances"), ("done", "Terminé")],
        default="choose", required=True,
    )
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company,
    )
    file_data = fields.Binary(string="Fichier", attachment=False)
    file_name = fields.Char(string="Nom du fichier")

    encoding = fields.Selection(
        [("latin-1", "Latin-1 (ISO-8859-1)"), ("cp1252", "Windows-1252"), ("utf-8", "UTF-8")],
        default="latin-1", required=True,
        help="Les exports comptables français sont généralement en Latin-1. "
             "Un mauvais encodage se voit sur les accents des libellés.",
    )
    separator = fields.Char(string="Séparateur", default=";", required=True, size=1)
    century = fields.Integer(
        string="Siècle des dates", default=2000, required=True,
        help="Les dates du fichier sont au format JJMMAA sur deux chiffres. "
             "260426 sera lu comme le 26/04/2026 avec la valeur 2000.",
    )
    default_journal_id = fields.Many2one(
        "account.journal", string="Journal par défaut",
        domain="[('company_id', '=', company_id), ('type', 'in', ('sale', 'general'))]",
        help="Proposé pour tout code journal du fichier sans correspondance évidente.",
    )

    post_entries = fields.Boolean(
        string="Comptabiliser après import",
        help="Décoché, les pièces sont créées en brouillon et restent modifiables.",
    )
    create_partners = fields.Boolean(
        string="Créer les tiers manquants",
        help="Crée un partenaire pour chaque code tiers laissé sans correspondance, "
             "en reprenant la raison sociale du fichier et le code dans le champ Référence.",
    )

    journal_line_ids = fields.One2many(
        "os.import.ecritures.journal", "wizard_id", string="Journaux")
    partner_line_ids = fields.One2many(
        "os.import.ecritures.partner", "wizard_id", string="Tiers")
    account_line_ids = fields.One2many(
        "os.import.ecritures.account", "wizard_id", string="Comptes introuvables")

    preview_html = fields.Html(string="Analyse", readonly=True, sanitize=False)
    result_html = fields.Html(string="Résultat", readonly=True, sanitize=False)
    move_ids = fields.Many2many("account.move", string="Pièces créées")

    # ------------------------------------------------------------------
    # Lecture et découpage du fichier
    # ------------------------------------------------------------------
    def _read_rows(self):
        """Retourne la liste des lignes non vides du fichier, en listes de chaînes."""
        self.ensure_one()
        if not self.file_data:
            raise UserError(self.env._("Aucun fichier n'a été chargé."))
        try:
            content = base64.b64decode(self.file_data).decode(self.encoding)
        except UnicodeDecodeError:
            raise UserError(self.env._(
                "Le fichier n'est pas lisible en %s. Essayez un autre encodage.",
                self.encoding,
            ))
        rows = []
        reader = csv.reader(io.StringIO(content), delimiter=self.separator)
        for number, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) < MIN_COLS:
                raise UserError(self.env._(
                    "Ligne %(line)s : %(found)s colonnes lues alors que le format en "
                    "attend au moins %(expected)s. Vérifiez le séparateur.",
                    line=number, found=len(row), expected=MIN_COLS,
                ))
            rows.append((number, row))
        if not rows:
            raise UserError(self.env._("Le fichier ne contient aucune ligne exploitable."))
        return rows

    def _parse(self):
        """Découpe le fichier en pièces. Retourne un OrderedDict {clé: [lignes]}."""
        self.ensure_one()
        pieces = OrderedDict()
        for number, row in self._read_rows():
            try:
                debit = _to_float(row[COL_DEBIT])
                credit = _to_float(row[COL_CREDIT])
                date = _to_date(row[COL_DATE], self.century)
                maturity = _to_date(row[COL_MATURITY], self.century)
            except ValueError as err:
                raise UserError(self.env._(
                    "Ligne %(line)s : valeur illisible (%(value)s).",
                    line=number, value=err.args[0],
                ))
            if not date:
                raise UserError(self.env._("Ligne %s : date absente.", number))

            journal_code = row[COL_JOURNAL].strip()
            piece_ref = row[COL_PIECE].strip()
            if not journal_code or not piece_ref:
                raise UserError(self.env._(
                    "Ligne %s : code journal ou référence de pièce absent.", number))

            pieces.setdefault((journal_code, piece_ref), []).append({
                "line": number,
                "journal_code": journal_code,
                "piece_ref": piece_ref,
                "date": date,
                "maturity": maturity,
                "account_code": row[COL_ACCOUNT].strip(),
                "account_label": row[COL_ACCOUNT_LABEL].strip(),
                "partner_code": row[COL_PARTNER].strip(),
                "label": row[COL_LABEL].strip() or "/",
                "debit": debit,
                "credit": credit,
            })
        return pieces

    def _check_balance(self, pieces):
        """Retourne la liste des pièces déséquilibrées, sous forme de messages."""
        rounding = self.company_id.currency_id.rounding
        errors = []
        for (journal_code, piece_ref), lines in pieces.items():
            debit = sum(line["debit"] for line in lines)
            credit = sum(line["credit"] for line in lines)
            if float_compare(debit, credit, precision_rounding=rounding) != 0:
                errors.append(self.env._(
                    "%(journal)s / %(piece)s : débit %(debit).2f ≠ crédit %(credit).2f",
                    journal=journal_code, piece=piece_ref, debit=debit, credit=credit,
                ))
        return errors

    # ------------------------------------------------------------------
    # Résolution des référentiels
    # ------------------------------------------------------------------
    def _resolve_accounts(self, codes):
        """Retourne {code: account.account}. Odoo 19 : code est company-dependent,
        la recherche doit donc se faire dans le contexte de la société cible."""
        self.ensure_one()
        Account = self.env["account.account"].with_company(self.company_id)
        found = Account.search([
            ("code", "in", list(codes)),
            ("company_ids", "in", self.company_id.id),
        ])
        mapping = {}
        for account in found:
            mapping[account.with_company(self.company_id).code] = account
        return mapping

    def _resolve_partner(self, code, name):
        """Cherche un partenaire par référence puis par raison sociale."""
        Partner = self.env["res.partner"]
        partner = Partner.search([("ref", "=", code)], limit=1)
        if not partner and name:
            partner = Partner.search([("name", "=ilike", name)], limit=1)
        return partner

    def _resolve_journal(self, code):
        Journal = self.env["account.journal"]
        domain = [("company_id", "=", self.company_id.id)]
        journal = Journal.search(domain + [("code", "=", code)], limit=1)
        if not journal:
            journal = Journal.search(domain + [("name", "=ilike", code)], limit=1)
        return journal

    # ------------------------------------------------------------------
    # Étape 1 -> 2 : analyse
    # ------------------------------------------------------------------
    def action_analyse(self):
        self.ensure_one()
        pieces = self._parse()

        errors = self._check_balance(pieces)
        if errors:
            raise UserError(self.env._(
                "Import interrompu : %(count)s pièce(s) déséquilibrée(s).\n\n%(detail)s",
                count=len(errors), detail="\n".join(errors[:20]),
            ))

        all_lines = [line for lines in pieces.values() for line in lines]

        # --- journaux ---
        journal_counts = {}
        for journal_code, _piece in pieces:
            journal_counts[journal_code] = journal_counts.get(journal_code, 0) + 1
        journal_vals = []
        for code, count in sorted(journal_counts.items()):
            journal = self._resolve_journal(code) or self.default_journal_id
            journal_vals.append((0, 0, {
                "code_source": code,
                "move_count": count,
                "journal_id": journal.id or False,
            }))

        # --- comptes ---
        account_codes = {line["account_code"] for line in all_lines}
        accounts = self._resolve_accounts(account_codes)
        missing = sorted(account_codes - set(accounts))
        account_vals = []
        for code in missing:
            sample = next(line for line in all_lines if line["account_code"] == code)
            account_vals.append((0, 0, {
                "code_source": code,
                "name_source": sample["account_label"],
                "line_count": sum(1 for line in all_lines if line["account_code"] == code),
            }))

        # --- tiers ---
        partner_seen = {}
        for (journal_code, piece_ref), lines in pieces.items():
            for line in lines:
                if not line["partner_code"]:
                    continue
                entry = partner_seen.setdefault(
                    line["partner_code"], {"name": line["label"], "pieces": set()})
                entry["pieces"].add((journal_code, piece_ref))
        partner_vals = []
        for code in sorted(partner_seen):
            info = partner_seen[code]
            partner = self._resolve_partner(code, info["name"])
            partner_vals.append((0, 0, {
                "code_source": code,
                "name_source": info["name"],
                "move_count": len(info["pieces"]),
                "partner_id": partner.id or False,
            }))

        # --- pièces déjà importées ---
        keys = ["%s/%s" % (journal_code, piece_ref) for journal_code, piece_ref in pieces]
        already = self.env["account.move"].search([
            ("os_import_key", "in", keys),
            ("company_id", "=", self.company_id.id),
        ])

        total_debit = sum(line["debit"] for line in all_lines)
        total_credit = sum(line["credit"] for line in all_lines)
        dates = sorted({line["date"] for line in all_lines})

        rows = [
            (self.env._("Pièces"), str(len(pieces))),
            (self.env._("Lignes"), str(len(all_lines))),
            (self.env._("Période"), "%s → %s" % (
                fields.Date.to_string(dates[0]), fields.Date.to_string(dates[-1]))),
            (self.env._("Total débit"), "%.2f" % total_debit),
            (self.env._("Total crédit"), "%.2f" % total_credit),
            (self.env._("Comptes distincts"), str(len(account_codes))),
            (self.env._("Tiers distincts"), str(len(partner_seen))),
        ]
        if already:
            rows.append((self.env._("Déjà importées (seront ignorées)"), str(len(already))))
        if missing:
            rows.append((self.env._("Comptes introuvables"), str(len(missing))))

        html = "<table class='table table-sm o_main_table'><tbody>"
        for label, value in rows:
            html += "<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (label, value)
        html += "</tbody></table>"

        self.write({
            "state": "map",
            "preview_html": html,
            "journal_line_ids": [fields.Command.clear()] + journal_vals,
            "partner_line_ids": [fields.Command.clear()] + partner_vals,
            "account_line_ids": [fields.Command.clear()] + account_vals,
        })
        return self._reopen()

    # ------------------------------------------------------------------
    # Étape 2 -> 3 : import
    # ------------------------------------------------------------------
    def action_import(self):
        self.ensure_one()
        if self.account_line_ids:
            raise UserError(self.env._(
                "%s compte(s) du fichier n'existent pas dans le plan comptable de "
                "la société. Créez-les puis relancez l'analyse.",
                len(self.account_line_ids),
            ))

        pieces = self._parse()
        errors = self._check_balance(pieces)
        if errors:
            raise UserError(self.env._(
                "Le fichier n'est plus équilibré :\n%s", "\n".join(errors[:20])))

        journal_map = {line.code_source: line.journal_id for line in self.journal_line_ids}
        missing_journal = [code for code, journal in journal_map.items() if not journal]
        if missing_journal:
            raise UserError(self.env._(
                "Aucun journal Odoo n'est associé aux codes : %s",
                ", ".join(sorted(missing_journal)),
            ))

        partner_map = {}
        for line in self.partner_line_ids:
            partner = line.partner_id
            if not partner and self.create_partners:
                partner = self.env["res.partner"].create({
                    "name": line.name_source or line.code_source,
                    "ref": line.code_source,
                    "company_type": "company",
                })
            partner_map[line.code_source] = partner

        all_lines = [line for lines in pieces.values() for line in lines]
        accounts = self._resolve_accounts({line["account_code"] for line in all_lines})

        existing = set(self.env["account.move"].search([
            ("os_import_key", "in", ["%s/%s" % key for key in pieces]),
            ("company_id", "=", self.company_id.id),
        ]).mapped("os_import_key"))

        move_vals = []
        skipped = 0
        for (journal_code, piece_ref), lines in pieces.items():
            key = "%s/%s" % (journal_code, piece_ref)
            if key in existing:
                skipped += 1
                continue
            header_partner = False
            for line in lines:
                if line["partner_code"]:
                    header_partner = partner_map.get(line["partner_code"])
                    break
            move_vals.append({
                "move_type": "entry",
                "company_id": self.company_id.id,
                "journal_id": journal_map[journal_code].id,
                "date": lines[0]["date"],
                "ref": piece_ref,
                "os_import_key": key,
                "partner_id": header_partner.id if header_partner else False,
                "line_ids": [fields.Command.create({
                    "account_id": accounts[line["account_code"]].id,
                    "partner_id": (
                        partner_map.get(line["partner_code"]).id
                        if line["partner_code"] and partner_map.get(line["partner_code"])
                        else False
                    ),
                    "name": line["label"],
                    "debit": line["debit"],
                    "credit": line["credit"],
                    "date_maturity": line["maturity"] or False,
                }) for line in lines],
            })

        moves = self.env["account.move"]
        if move_vals:
            moves = self.env["account.move"].with_company(self.company_id).create(move_vals)
            _logger.info("Import écritures : %s pièces créées depuis %s",
                         len(moves), self.file_name or "fichier")

        posted = 0
        if self.post_entries and moves:
            moves._post(soft=False)
            posted = len(moves)

        html = "<table class='table table-sm o_main_table'><tbody>"
        html += "<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (
            self.env._("Pièces créées"), len(moves))
        if skipped:
            html += "<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (
                self.env._("Ignorées (déjà importées)"), skipped)
        html += "<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (
            self.env._("Comptabilisées"), posted or self.env._("aucune (brouillon)"))
        html += "</tbody></table>"

        self.write({"state": "done", "result_html": html, "move_ids": [(6, 0, moves.ids)]})
        return self._reopen()

    def action_open_moves(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Pièces importées"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", self.move_ids.ids)],
            "context": {"create": False},
        }

    def action_back(self):
        self.ensure_one()
        self.state = "choose"
        return self._reopen()

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if self.default_journal_id.company_id != self.company_id:
            self.default_journal_id = False
