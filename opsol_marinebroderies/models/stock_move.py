# -*- coding: utf-8 -*-

from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='sale_line_id.order_id.partner_id',
        string='Client',
        store=True,
        readonly=True
    )
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        related='sale_line_id.order_id',
        string='Commande client',
        store=True,
        readonly=True
    )

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        res = super(StockMove, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, supplier, po)
        if self.sale_line_id:
            delivery_date = self.sale_line_id.commitment_date or self.sale_line_id.order_id.commitment_date
            if delivery_date:
                res['x_customer_delivery_date'] = delivery_date.date()
        return res
