# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_sale_partner_ids = fields.Many2many(
        'res.partner',
        string='Clients',
        compute='_compute_sale_partner_ids',
        store=True,
        groups='sales_team.group_sale_salesman',
    )

    @api.depends(
        'order_line.sale_order_id.partner_id',
        'reference_ids.sale_ids.partner_id',
    )
    def _compute_sale_partner_ids(self):
        for order in self:
            order.x_sale_partner_ids = order._get_sale_orders().mapped('partner_id')

    def action_print_receipts_by_supplier(self):
        return self.env.ref(
            'opsol_marinebroderies.action_report_purchase_by_supplier'
        ).report_action(self)

    def action_print_receipts_by_customer_available(self):
        return self.env.ref(
            'opsol_marinebroderies.action_report_purchase_by_customer_available'
        ).report_action(self)

    def _get_purchase_report_groups(self, by_customer=False):
        groups = {}
        lines = self.mapped('order_line').filtered(
            lambda line: not line.display_type and line.product_id
            and line.order_id.state != 'cancel'
        )
        for line in lines:
            customer = line.x_sale_partner_id or line.sale_line_id.order_id.partner_id
            partner = customer if by_customer else line.order_id.partner_id
            key = (line.company_id.id, partner.id)
            if key not in groups:
                groups[key] = {
                    'partner': partner,
                    'orders': self.env['purchase.order'],
                    'lines': {},
                }
            group = groups[key]
            group['orders'] |= line.order_id
            line_key = (line.product_id.id, line.product_uom_id.id, line.name)
            if line_key not in group['lines']:
                group['lines'][line_key] = {
                    'product': line.product_id,
                    'description': line.name,
                    'uom': line.product_uom_id,
                    'qty': 0.0,
                    '_customer_ids': self.env['res.partner'],
                    'purchase_lines': self.env['purchase.order.line'],
                }
            values = group['lines'][line_key]
            values['qty'] += line.product_qty
            values['_customer_ids'] |= customer
            values['purchase_lines'] |= line
        for group in groups.values():
            group['lines'] = sorted(
                group['lines'].values(),
                key=lambda line: (line['product'].display_name, line['description']),
            )
        return sorted(
            groups.values(),
            key=lambda group: (not group['partner'], group['partner'].display_name or ''),
        )

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        sale_order_partners = self.order_line.mapped('sale_line_id.order_id.partner_id')
        if len(sale_order_partners) == 1:
            res['x_customer_id'] = sale_order_partners.id
        elif len(sale_order_partners) > 1:
            res['x_customer_id'] = sale_order_partners[0].id
        return res
