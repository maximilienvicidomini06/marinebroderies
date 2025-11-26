
from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_customer_id = fields.Many2one(
        'res.partner',
        string='Client',
        readonly=True,
        store=True,
    )
