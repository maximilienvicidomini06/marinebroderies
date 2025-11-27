
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_customer_id = fields.Many2one(
        'res.partner',
        string='Client',
        readonly=True,
        store=True,
    )

    available_move_ids = fields.Many2many(
        'stock.move',
        compute='_compute_available_move_ids',
        string='Available Moves'
    )

    @api.depends('move_ids.forecast_availability', 'move_ids.forecast_expected_date')
    def _compute_available_move_ids(self):
        for picking in self:
            picking.available_move_ids = picking.move_ids.filtered(
                lambda m: m.forecast_availability > 0 and not m.forecast_expected_date
            )
