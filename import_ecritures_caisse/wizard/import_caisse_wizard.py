# -*- coding: utf-8 -*-
import base64
from collections import defaultdict
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ImportCaisseWizard(models.TransientModel):
    _name = "import.caisse.wizard"
    _description = "Assistant d'import des écritures de caisse"

    file_data = fields.Binary(string="Fichier d'écritures", required=True)
    file_name = fields.Char(string="Nom du fichier")
    post_moves = fields.Boolean(
        string="Comptabiliser automatiquement",
        default=False,
        help="Si coché, les pièces importées sont directement passées à l'état "
             "'Comptabilisé'. Sinon elles restent en brouillon.",
    )
    result_html = fields.Html(string="Résultat", readonly=True)
    state = fields.Selection(
        [("draft", "Import"), ("done", "Terminé")],
        default="draft",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_amount(value):
        """'1508,00' -> 1508.0 ; champ vide -> 0.0"""
        value = (value or "").strip()
        if not value:
            return 0.0
        return float(value.replace(" ", "").replace(",", "."))

    @staticmethod
    def _parse_date(value):
        """'150426' (JJMMAA) -> date(2026, 4, 15)"""
        value = (value or "").strip()
        if len(value) != 6 or not value.isdigit():
            raise UserError(_("Date invalide : « %s » (format attendu JJMMAA).") % value)
        return datetime.strptime(value, "%d%m%y").date()

    def _decode_file(self):
        raw = base64.b64decode(self.file_data)
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise UserError(_("Impossible de décoder le fichier (encodage inconnu)."))

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def _parse_lines(self, text):
        """Retourne une liste de dictionnaires, un par ligne du fichier.

        Format (séparateur ';') — index des colonnes utilisées :
          0  : code du journal (ex. VTECPT, DIFFER)
          1  : date de la pièce, JJMMAA (ex. 150426)
          2  : code du compte (ex. 707026, 580008, 411000)
          3  : libellé du compte
          4  : référence de la pièce (ex. 'VIS 150426', 'CAV1V0538724')
          8  : code du tiers (ex. MCGRANDTOURBUS) — optionnel
          11 : libellé de la ligne
          18 : sens D (débit) / C (crédit)
          19 : montant signé
          21 : montant au débit
          22 : montant au crédit
          26 : date d'échéance JJMMAA — optionnelle
        """
        lines = []
        for num, raw_line in enumerate(text.splitlines(), start=1):
            if not raw_line.strip():
                continue
            fields_ = raw_line.split(";")
            if len(fields_) < 23:
                raise UserError(
                    _("Ligne %(num)s : %(nb)s colonnes trouvées, au moins 23 attendues.",
                      num=num, nb=len(fields_))
                )
            debit = self._parse_amount(fields_[21])
            credit = self._parse_amount(fields_[22])
            sens = fields_[18].strip().upper()
            if sens == "D" and not debit and credit:
                debit, credit = credit, 0.0
            if sens == "C" and not credit and debit:
                credit, debit = debit, 0.0
            lines.append({
                "num": num,
                "journal_code": fields_[0].strip(),
                "date": self._parse_date(fields_[1]),
                "account_code": fields_[2].strip(),
                "ref": fields_[4].strip(),
                "partner_code": fields_[8].strip() if len(fields_) > 8 else "",
                "label": (fields_[11].strip() if len(fields_) > 11 else "")
                         or fields_[3].strip(),
                "debit": debit,
                "credit": credit,
                "date_maturity": (
                    self._parse_date(fields_[26])
                    if len(fields_) > 26 and fields_[26].strip() else False
                ),
            })
        if not lines:
            raise UserError(_("Le fichier ne contient aucune ligne exploitable."))
        return lines

    # ------------------------------------------------------------------
    # Résolution journaux / comptes / tiers
    # ------------------------------------------------------------------
    def _get_journals(self, codes):
        company = self.env.company
        journals = {}
        for code in codes:
            journal = self.env["account.journal"].search([
                ("code", "=", code),
                ("company_id", "=", company.id),
            ], limit=1)
            if not journal:
                raise UserError(
                    _("Journal introuvable pour le code « %s » "
                      "(société %s).") % (code, company.name))
            journals[code] = journal
        return journals

    def _get_accounts(self, codes):
        company = self.env.company
        accounts = {}
        for code in codes:
            account = self.env["account.account"].with_company(company).search([
                ("code", "=", code),
                ("company_ids", "in", [company.id]),
            ], limit=1)
            if not account:
                raise UserError(
                    _("Compte comptable introuvable : « %s » "
                      "(société %s).") % (code, company.name))
            accounts[code] = account
        return accounts

    def _get_partners(self, codes):
        """Recherche le tiers par référence interne (ref) puis par nom."""
        partners = {}
        for code in codes:
            partner = self.env["res.partner"].search(
                [("ref", "=", code)], limit=1)
            if not partner:
                partner = self.env["res.partner"].search(
                    [("name", "=ilike", code)], limit=1)
            partners[code] = partner  # peut rester vide : non bloquant
        return partners

    # ------------------------------------------------------------------
    # Action principale
    # ------------------------------------------------------------------
    def action_import(self):
        self.ensure_one()
        text = self._decode_file()
        lines = self._parse_lines(text)

        journals = self._get_journals({l["journal_code"] for l in lines})
        accounts = self._get_accounts({l["account_code"] for l in lines})
        partners = self._get_partners(
            {l["partner_code"] for l in lines if l["partner_code"]})

        # Regroupement en pièces : (journal, date, référence)
        grouped = defaultdict(list)
        for line in lines:
            grouped[(line["journal_code"], line["date"], line["ref"])].append(line)

        # Vérification de l'équilibre avant toute création
        currency = self.env.company.currency_id
        for (jcode, date, ref), move_lines in grouped.items():
            balance = sum(l["debit"] - l["credit"] for l in move_lines)
            if currency.compare_amounts(balance, 0.0) != 0:
                raise UserError(
                    _("Pièce déséquilibrée : journal %(journal)s, date %(date)s, "
                      "référence %(ref)s — écart de %(balance).2f. "
                      "Aucune écriture n'a été créée.",
                      journal=jcode, date=date, ref=ref, balance=balance))

        # Création des pièces
        moves_vals = []
        for (jcode, date, ref), move_lines in sorted(
                grouped.items(), key=lambda item: (item[0][1], item[0][2])):
            line_vals = []
            for l in move_lines:
                partner = partners.get(l["partner_code"])
                line_vals.append((0, 0, {
                    "account_id": accounts[l["account_code"]].id,
                    "name": l["label"],
                    "debit": l["debit"],
                    "credit": l["credit"],
                    "partner_id": partner.id if partner else False,
                    "date_maturity": l["date_maturity"] or date,
                }))
            moves_vals.append({
                "journal_id": journals[jcode].id,
                "date": date,
                "ref": ref,
                "move_type": "entry",
                "line_ids": line_vals,
            })

        moves = self.env["account.move"].create(moves_vals)
        if self.post_moves:
            moves.action_post()

        self.write({
            "state": "done",
            "result_html": _(
                "<p><b>%(moves)s pièce(s)</b> créée(s) (%(lines)s lignes) — "
                "état : %(state)s.</p>",
                moves=len(moves), lines=len(lines),
                state=_("Comptabilisé") if self.post_moves else _("Brouillon")),
        })

        return {
            "type": "ir.actions.act_window",
            "name": _("Écritures importées"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", moves.ids)],
        }
