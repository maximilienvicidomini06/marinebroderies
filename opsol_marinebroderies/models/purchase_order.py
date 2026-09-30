# -*- coding: utf-8 -*-

from odoo import _, models, fields
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _print_receipt_report(self, report_xmlid):
        pickings = self.mapped('picking_ids').filtered(
            lambda picking: picking.picking_type_id.code == 'incoming'
            and picking.state != 'cancel'
        )
        if not pickings:
            raise UserError(_("Aucun bon de réception non annulé n'est associé aux commandes sélectionnées."))
        return self.env.ref(report_xmlid).report_action(pickings)

    def action_print_receipts_by_supplier(self):
        return self._print_receipt_report(
            'opsol_marinebroderies.action_report_stock_picking_by_supplier'
        )

    def action_print_receipts_by_customer_available(self):
        return self._print_receipt_report(
            'opsol_marinebroderies.action_report_stock_picking_by_supplier_available'
        )

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        sale_order_partners = self.order_line.mapped('sale_line_id.order_id.partner_id')
        if len(sale_order_partners) == 1:
            res['x_customer_id'] = sale_order_partners.id
        elif len(sale_order_partners) > 1:
            res['x_customer_id'] = sale_order_partners[0].id
        return res
