# -*- coding: utf-8 -*-

from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        res = super(StockMove, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, supplier, po)
        if self.sale_line_id:
            delivery_date = self.sale_line_id.commitment_date or self.sale_line_id.order_id.commitment_date
            if delivery_date:
                res['x_customer_delivery_date'] = delivery_date.date()
        return res
