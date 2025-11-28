# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_customer_delivery_date = fields.Date(
        string='Date de livraison Client',
        readonly=False,
        compute='_compute_customer_delivery_date',
        store=True
    )
    x_sale_partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        readonly=False,
        compute='_compute_customer_delivery_date',
        store=True
    )

    @api.depends('sale_line_id', 'order_id')
    def _compute_customer_delivery_date(self):
        for line in self:
            customer_date = False
            partner = False
            # Try to get date from sale_line_id first
            if line.sale_line_id and line.sale_line_id.order_id:
                customer_date = line.sale_line_id.order_id.commitment_date
                partner = line.sale_line_id.order_id.partner_id
            # If not found, try from related sale_order_id
            elif line.order_id and line.sale_order_id:
                customer_date = line.sale_order_id.commitment_date
                partner = line.sale_order_id.partner_id

            # Convert datetime to date if needed
            if customer_date and hasattr(customer_date, 'date'):
                customer_date = customer_date.date()

            line.x_customer_delivery_date = customer_date
            line.x_sale_partner_id = partner

    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, location_dest_id, name,
        origin, company_id, values, po):
        res = super(PurchaseOrderLine, self)._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, po)
        res['sale_line_id'] = values.get('sale_line_id')
        return res

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for move_vals in res:
            move_vals['sale_line_id'] = self.sale_line_id.id
        return res
