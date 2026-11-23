import base64
import csv
import io
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation

from markupsafe import Markup, escape

from odoo import api, fields, models
from odoo.exceptions import UserError

# Positions des colonnes dans l'export MANDAT (séparateur ';')
COL_TYPE, COL_DATE, COL_CODE, COL_LABEL, COL_PIECE = 0, 1, 2, 3, 4
COL_SUPPLIER, COL_SENS, COL_AMOUNT = 11, 18, 20


class MandatImportWizard(models.TransientModel):
    _name = "mandat.import.wizard"
    _description = "Assistant d'import des mandats"

    state = fields.Selection([("upload", "Fichier"), ("preview", "Aperçu")], default="upload")
    file = fields.Binary("Fichier export", required=True)
    filename = fields.Char()
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    create_partners = fields.Boolean(
        "Créer les fournisseurs manquants",
        help="Sinon, les lignes sont importées sans fournisseur quand il n'existe pas dans Odoo.")
    remember_mapping = fields.Boolean(
        "Mémoriser les correspondances saisies", default=True,
        help="Les comptes analytiques choisis dans l'aperçu pour des codes inconnus "
             "sont enregistrés pour les prochains imports.")
    line_ids = fields.One2many("mandat.import.wizard.line", "wizard_id", "Lignes")
    count_ok = fields.Integer(compute="_compute_stats")
    count_duplicate = fields.Integer(compute="_compute_stats")
    count_unmapped = fields.Integer(compute="_compute_stats")
    summary_html = fields.Html(compute="_compute_stats", sanitize=False)

    @api.depends("line_ids.status", "line_ids.amount", "line_ids.analytic_account_id")
    def _compute_stats(self):
        for wiz in self:
            status = Counter(wiz.line_ids.mapped("status"))
            wiz.count_ok = status["ok"]
            wiz.count_duplicate = status["duplicate"]
            wiz.count_unmapped = status["unmapped"]
            totals = defaultdict(Decimal)
            for line in wiz.line_ids.filtered(lambda l: l.status == "ok"):
                key = (line.budget_code, line.analytic_account_id.display_name)
                totals[key] += Decimal(str(line.amount))
            rows = Markup("").join(
                Markup("<tr><td>%s</td><td>%s</td><td class='text-end'>%s</td></tr>") % (
                    code, acc, f"{amt:,.2f}".replace(",", " ").replace(".", ","))
                for (code, acc), amt in sorted(totals.items())
            )
            grand = sum(totals.values(), Decimal(0))
            wiz.summary_html = Markup(
                "<table class='table table-sm'><thead><tr><th>Code</th><th>Compte analytique</th>"
                "<th class='text-end'>Montant à importer</th></tr></thead><tbody>%s</tbody>"
                "<tfoot><tr><th colspan='2'>Total</th><th class='text-end'>%s</th></tr></tfoot></table>"
            ) % (rows, f"{grand:,.2f}".replace(",", " ").replace(".", ","))

    # ------------------------------------------------------------------ parsing
    @staticmethod
    def _decode(raw):
        for enc in ("utf-8-sig", "cp1252"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("latin-1")

    @staticmethod
    def _to_decimal(value):
        return Decimal(value.strip().replace(" ", "").replace(" ", "").replace(",", "."))

    def _parse_file(self):
        self.ensure_one()
        text = self._decode(base64.b64decode(self.file))
        parsed, errors = [], []
        for lineno, cols in enumerate(csv.reader(io.StringIO(text), delimiter=";"), start=1):
            if not cols or not cols[0].strip():
                continue
            if cols[COL_TYPE].strip() != "MANDAT":
                continue
            try:
                date = datetime.strptime(cols[COL_DATE].strip(), "%d%m%y").date()
                amount = self._to_decimal(cols[COL_AMOUNT])
            except (ValueError, IndexError, InvalidOperation):
                errors.append(lineno)
                continue
            parsed.append({
                "lineno": lineno,
                "date": date,
                "budget_code": cols[COL_CODE].strip(),
                "budget_label": cols[COL_LABEL].strip(),
                "piece": cols[COL_PIECE].strip(),
                "supplier": cols[COL_SUPPLIER].strip(),
                "sens": cols[COL_SENS].strip() if len(cols) > COL_SENS else "",
                "amount": amount,  # signé : débit positif, crédit (réduction) négatif
            })
        if errors:
            raise UserError(self.env._(
                "Lignes illisibles dans le fichier (numéros) : %s", ", ".join(map(str, errors))))
        if not parsed:
            raise UserError(self.env._("Aucune ligne MANDAT trouvée dans ce fichier."))
        return parsed

    @staticmethod
    def _make_keys(parsed):
        """Clé stable par ligne : pièce|code|montant|rang d'occurrence dans la pièce."""
        seen = Counter()
        for row in parsed:
            base = f"{row['piece']}|{row['budget_code']}|{row['amount']:.2f}"
            seen[base] += 1
            row["key"] = f"{base}|{seen[base]}"
        return parsed

    def action_parse(self):
        self.ensure_one()
        parsed = self._make_keys(self._parse_file())
        mapping = self.env["mandat.budget.mapping"]._get_mapping(self.company_id)
        existing = set(self.env["account.analytic.line"].search([
            ("company_id", "=", self.company_id.id),
            ("mandat_key", "in", [r["key"] for r in parsed]),
        ]).mapped("mandat_key"))
        self.line_ids = [fields.Command.clear()] + [
            fields.Command.create({
                "date": r["date"],
                "piece": r["piece"],
                "budget_code": r["budget_code"],
                "budget_label": r["budget_label"],
                "supplier": r["supplier"],
                "amount": float(r["amount"]),
                "key": r["key"],
                "analytic_account_id": mapping.get(r["budget_code"], self.env["account.analytic.account"]).id,
                "is_duplicate": r["key"] in existing,
            })
            for r in parsed
        ]
        self.state = "preview"
        return self._reopen()

    def action_back(self):
        self.line_ids = [fields.Command.clear()]
        self.state = "upload"
        return self._reopen()

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "name": self.env._("Importer des mandats"),
        }

    # ------------------------------------------------------------------ import
    def _find_partners(self, names):
        Partner = self.env["res.partner"].with_context(active_test=False)
        result = {}
        for name in names:
            if not name:
                continue
            partner = Partner.search([("name", "=ilike", name), ("is_company", "=", True)], limit=1) \
                or Partner.search([("name", "=ilike", name)], limit=1)
            if not partner and self.create_partners:
                partner = Partner.create({"name": name, "is_company": True, "company_id": False})
            result[name] = partner
        return result

    def action_import(self):
        self.ensure_one()
        lines = self.line_ids.filtered(lambda l: l.status == "ok")
        if self.count_unmapped:
            raise UserError(self.env._(
                "%s ligne(s) n'ont pas de compte analytique. Renseignez-le dans l'aperçu "
                "ou créez la correspondance avant d'importer.", self.count_unmapped))
        if not lines:
            raise UserError(self.env._("Rien à importer : toutes les lignes ont déjà été importées."))

        if self.remember_mapping:
            Mapping = self.env["mandat.budget.mapping"]
            known = Mapping._get_mapping(self.company_id)
            for code, line in {l.budget_code: l for l in lines}.items():
                if code not in known:
                    Mapping.create({"code": code, "name": line.budget_label,
                                    "analytic_account_id": line.analytic_account_id.id,
                                    "company_id": self.company_id.id})

        partners = self._find_partners(set(lines.mapped("supplier")))
        vals_list = []
        for line in lines:
            account = line.analytic_account_id
            column = account.root_plan_id._column_name()
            vals_list.append({
                "name": f"{line.piece} - {line.supplier or line.budget_label}",
                "date": line.date,
                "amount": -line.amount,  # dépense = montant négatif en analytique
                column: account.id,
                "partner_id": partners.get(line.supplier, self.env["res.partner"]).id or False,
                "ref": line.piece,
                "company_id": self.company_id.id,
                "mandat_ref": line.piece,
                "mandat_budget_code": line.budget_code,
                "mandat_key": line.key,
            })
        created = self.env["account.analytic.line"].create(vals_list)
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Mandats importés"),
            "res_model": "account.analytic.line",
            "view_mode": "list,form",
            "views": [(self.env.ref("os_budget_mandat_import.view_analytic_line_mandat_list").id, "list"),
                      (False, "form")],
            "domain": [("id", "in", created.ids)],
            "target": "current",
        }


class MandatImportWizardLine(models.TransientModel):
    _name = "mandat.import.wizard.line"
    _description = "Ligne d'aperçu d'import de mandat"
    _order = "piece, id"

    wizard_id = fields.Many2one("mandat.import.wizard", required=True, ondelete="cascade")
    date = fields.Date(readonly=True)
    piece = fields.Char("Pièce", readonly=True)
    budget_code = fields.Char("Code", readonly=True)
    budget_label = fields.Char("Ligne budgétaire", readonly=True)
    supplier = fields.Char("Fournisseur", readonly=True)
    amount = fields.Float("Montant", readonly=True, digits=(16, 2))
    key = fields.Char(readonly=True)
    is_duplicate = fields.Boolean(readonly=True)
    analytic_account_id = fields.Many2one("account.analytic.account", "Compte analytique")
    status = fields.Selection([
        ("ok", "À importer"),
        ("unmapped", "Compte analytique manquant"),
        ("duplicate", "Déjà importée"),
    ], compute="_compute_status")

    @api.depends("is_duplicate", "analytic_account_id")
    def _compute_status(self):
        for line in self:
            if line.is_duplicate:
                line.status = "duplicate"
            elif not line.analytic_account_id:
                line.status = "unmapped"
            else:
                line.status = "ok"
