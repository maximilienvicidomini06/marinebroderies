# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
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

    def unlink(self):
        for line in self:
            if line.type_broderie_id:
                line.remove_related_broderie_service()
        return super().unlink()

    def remove_related_broderie_service(self):
        existing = self.order_id.order_line.filtered(lambda l: l.broderie_service and l.broderie_source_id == self.id)
        if existing:
            existing.unlink()

    @api.constrains('display_type', 'type_broderie_id', 'name', 'product_id', 'product_uom_qty')
    def update_related_broderie_line(self):
        for line in self:
    
            order = line.order_id
            existing = order.order_line.filtered(lambda l: l.broderie_service and l.broderie_source_id == line.id)
            if existing:
                existing.unlink()

            type_broderie = line.type_broderie_id
            if not type_broderie:
                continue
            
            service_product = type_broderie.related_product_id
            if not service_product:
                raise UserError(_("le type de boderie (%s) n'a pas de service rattache"), type_broderie.name)

            self.env['sale.order.line'].sudo().create({
                'name': f"{type_broderie.name}: {line.product_uom_qty} x {line.name.replace('\n', '').replace('\r', '')} - date limite: {order.commitment_date and order.commitment_date.strftime('%d/%m/%Y') or 'N/A'}",
                'sequence': line.sequence + 1, 'order_id': order.id,
                'product_id': service_product.id,
                'product_uom_qty': line.product_uom_qty, 
                'price_unit': service_product.lst_price,
                'broderie_source_id': line.id, 'broderie_service': True,
            })
