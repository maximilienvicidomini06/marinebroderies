# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    broderie_service = fields.Boolean(string="Service de Broderie", default=False)
    broderie_source_id = fields.Integer(string="Ligne source", default=False)
    type_broderie_id = fields.Many2one(
        'opsol_marinebroderies.type_broderie',
        string='Type de broderie',
        help='Type de broderie associé à la ligne de vente.'
    )

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        """ Returns the values to create the purchase order line from the current SO line.
            :param purchase_order: record of purchase.order
            :rtype: dict
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        self.ensure_one()
        result = super()._purchase_service_prepare_line_values(purchase_order, quantity)
        result['x_customer_delivery_date'] = self.order_id.date_order
        return result
