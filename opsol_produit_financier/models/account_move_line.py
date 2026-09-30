from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    financial_quantity = fields.Float(
        string="Quantite financiere",
        digits=(16, 6),
        copy=False,
        index=True,
        help="Quantite signee transferee depuis la ligne de releve bancaire.",
    )
    financial_isin_code = fields.Char(
        string="Code ISIN",
        copy=False,
        index=True,
        help="Copie historique du code ISIN du partenaire financier.",
    )
