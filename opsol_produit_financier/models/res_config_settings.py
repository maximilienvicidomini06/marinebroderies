from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    financial_mode = fields.Boolean(
        related="company_id.financial_mode",
        readonly=False,
    )
