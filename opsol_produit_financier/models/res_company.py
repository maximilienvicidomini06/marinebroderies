from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    financial_mode = fields.Boolean(
        string="Mode produits financiers",
        help="Active le Grand livre produits financiers pour cette societe.",
    )
