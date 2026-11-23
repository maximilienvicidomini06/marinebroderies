from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    mandat_ref = fields.Char("Pièce mandat", index=True, readonly=True, copy=False)
    mandat_budget_code = fields.Char("Code budgétaire", readonly=True, copy=False)
    mandat_key = fields.Char("Clé d'import mandat", readonly=True, copy=False,
                             help="Identifiant unique de la ligne importée (anti-doublon)")

    _mandat_key_uniq = models.Constraint(
        "UNIQUE(mandat_key, company_id)",
        "Cette ligne de mandat a déjà été importée.",
    )
