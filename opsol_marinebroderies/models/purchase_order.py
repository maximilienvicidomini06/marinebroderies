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
            description = line.name or ''
            color, size = self._get_purchase_report_variant_groups(line.product_id)
            if by_customer:
                line_key = (
                    customer.id, line.order_id.partner_id.id,
                    line.product_id.id, line.product_uom_id.id,
                    description,
                )
            else:
                # Keep the supplier report hierarchy explicit: color, size,
                # customer, then product details. This makes the sorted lines
                # directly usable for the color and size rowspans.
                line_key = (
                    color, size, customer.id, line.order_id.partner_id.id,
                    line.product_id.id, line.product_uom_id.id,
                    description,
                )
            if line_key not in group['lines']:
                group['lines'][line_key] = {
                    'supplier': line.order_id.partner_id,
                    'product': line.product_id,
                    'description': description,
                    'color': color,
                    'size': size,
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
            for values in group['lines'].values():
                values['x_note'] = '\n'.join(dict.fromkeys(
                    note for note in values['purchase_lines'].mapped('x_note') if note
                ))
            if by_customer:
                sort_key = lambda line: (
                    not line['_customer_ids'],
                    line['_customer_ids'].display_name or '',
                    line['_customer_ids'].id or 0,
                    line['product'].display_name,
                    line['description'],
                )
            else:
                sort_key = lambda line: (
                    line['color'] == 'Autres',
                    line['color'],
                    line['size'] == 'Autres',
                    line['size'],
                    not line['_customer_ids'],
                    line['_customer_ids'].display_name or '',
                    line['_customer_ids'].id or 0,
                    line['product'].display_name,
                    line['description'],
                )
            group['lines'] = sorted(
                group['lines'].values(),
                key=sort_key,
            )
            if not by_customer:
                for report_index, line in enumerate(group['lines'], 1):
                    line['report_index'] = report_index
                group['variant_groups'] = self._build_supplier_report_variant_groups(
                    group['lines']
                )
        return sorted(
            groups.values(),
            key=lambda group: (not group['partner'], group['partner'].display_name or ''),
        )

    @staticmethod
    def _get_purchase_report_variant_groups(product):
        """Return the Couleur and Taille HF values used by the supplier report."""
        values_by_attribute = {}
        for ptav in product.product_template_attribute_value_ids:
            attribute_name = (ptav.attribute_id.name or '').strip().casefold()
            if attribute_name != 'couleur' and 'taille' not in attribute_name:
                continue
            value_name = (
                ptav.product_attribute_value_id.name
                or ptav.name
                or ''
            ).strip()
            if value_name:
                attribute_group = 'couleur' if attribute_name == 'couleur' else 'taille'
                values_by_attribute.setdefault(attribute_group, []).append(value_name)

        return (
            ', '.join(dict.fromkeys(values_by_attribute.get('couleur', []))) or 'Autres',
            ', '.join(dict.fromkeys(values_by_attribute.get('taille', []))) or 'Autres',
        )

    @staticmethod
    def _build_supplier_report_variant_groups(lines):
        """Build the color/size/client hierarchy consumed by the supplier QWeb."""
        color_groups = []
        for report_index, line in enumerate(lines, 1):
            line['report_index'] = report_index
            if not color_groups or color_groups[-1]['color'] != line['color']:
                color_groups.append({
                    'color': line['color'],
                    'tailles': [],
                    'color_span': 0,
                })
            color_group = color_groups[-1]
            if not color_group['tailles'] or color_group['tailles'][-1]['taille'] != line['size']:
                color_group['tailles'].append({
                    'taille': line['size'],
                    'lines': [],
                    'size_span': 0,
                    'is_first_in_color': not color_group['tailles'],
                })
            size_group = color_group['tailles'][-1]
            customer_key = tuple(line['_customer_ids'].ids)
            if (
                not size_group['lines']
                or size_group['lines'][-1]['_customer_key'] != customer_key
            ):
                size_group['lines'].append({
                    'client': line['_customer_ids'],
                    'articles': [],
                    '_customer_key': customer_key,
                })
            size_group['lines'][-1]['articles'].append(line)

        for color_group in color_groups:
            color_articles = 0
            color_clients = 0
            for size_group in color_group['tailles']:
                size_articles = sum(
                    len(client_group['articles'])
                    for client_group in size_group['lines']
                )
                size_clients = len(size_group['lines'])
                size_group['size_span'] = size_articles + size_clients - 1
                color_articles += size_articles
                color_clients += size_clients
                for client_group in size_group['lines']:
                    client_group.pop('_customer_key', None)
            color_group['color_span'] = color_articles + color_clients - 1
        return color_groups

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        sale_order_partners = self.order_line.mapped('sale_line_id.order_id.partner_id')
        if len(sale_order_partners) == 1:
            res['x_customer_id'] = sale_order_partners.id
        elif len(sale_order_partners) > 1:
            res['x_customer_id'] = sale_order_partners[0].id
        return res
