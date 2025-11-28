
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

    @api.depends('reference_ids.sale_ids', 'move_ids.sale_line_id.order_id')
    def _compute_sale_id(self):
        """Link the picking to a sale order only when it is unambiguous.

        When a purchase order is merged we can end up with moves pointing to
        different sale orders. Assigning that multi-recordset to the Many2one
        field raises an error, so we keep the link only when all moves relate
        to the same sale order.
        """
        for picking in self:
            sale_orders = picking.reference_ids.sale_ids or picking.move_ids.sale_line_id.order_id
            picking.sale_id = sale_orders if len(sale_orders) == 1 else False

    @api.depends('move_ids.forecast_availability', 'move_ids.forecast_expected_date')
    def _compute_available_move_ids(self):
        for picking in self:
            picking.available_move_ids = picking.move_ids.filtered(
                lambda m: m.forecast_availability > 0 and not m.forecast_expected_date
            )
