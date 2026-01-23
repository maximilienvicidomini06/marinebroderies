
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

    @api.depends(
        'name',
        'partner_id',
        'partner_id.display_name',
        'location_dest_id',
        'location_dest_id.display_name',
    )
    def _compute_display_name(self):
        for picking in self:
            parts = [picking.name]
            if picking.partner_id:
                parts.append(picking.partner_id.display_name)
            if picking.location_dest_id:
                parts.append(picking.location_dest_id.display_name)
            new_name = " - ".join([part for part in parts if part])
            picking.display_name = new_name

    def _get_default_supplier_partner(self, product, company=None, quantity=1.0, uom=None):
        company = company or self.company_id
        uom = uom or product.uom_id
        seller = False
        if hasattr(product, '_select_seller'):
            try:
                seller = product._select_seller(
                    partner_id=False,
                    quantity=quantity,
                    date=fields.Date.context_today(self),
                    uom_id=uom,
                    company_id=company,
                )
            except TypeError:
                seller = product._select_seller(
                    partner_id=False,
                    quantity=quantity,
                    date=fields.Date.context_today(self),
                    uom_id=uom,
                )

        if not seller:
            today = fields.Date.context_today(self)
            sellers = product.seller_ids.filtered(
                lambda s: (
                    (not s.company_id or s.company_id == company)
                    and (not s.date_start or s.date_start <= today)
                    and (not s.date_end or s.date_end >= today)
                    and (not s.min_qty or s.min_qty <= quantity)
                )
            ).sorted('sequence')
            seller = sellers[:1]

        if not seller:
            return False

        return getattr(seller, 'partner_id', False) or getattr(seller, 'name', False)

    def _get_supplier_groups(self):
        self.ensure_one()
        return self._get_supplier_groups_multi()

    def _get_supplier_groups_multi(self):
        moves = self.mapped('move_ids').filtered(lambda m: m.state != 'cancel')
        groups = {}
        for move in moves:
            partner = self._get_default_supplier_partner(
                move.product_id,
                company=move.company_id,
                quantity=move.product_uom_qty or 0.0,
                uom=move.product_uom,
            )
            key = partner.id if partner else 0
            if key not in groups:
                groups[key] = {
                    'partner': partner,
                    'moves': self.env['stock.move'],
                    'lines': [],
                }
            groups[key]['moves'] |= move
        for group in groups.values():
            aggregated = {}
            for move in group['moves']:
                description = move.description_picking or ''
                line_key = (move.product_id.id, move.product_uom.id, description)
                if line_key not in aggregated:
                    aggregated[line_key] = {
                        'product': move.product_id,
                        'description': description,
                        'qty': 0.0,
                        'uom': move.product_uom,
                        '_customer_ids': set(),
                    }
                aggregated[line_key]['qty'] += move.product_uom_qty
                customer = move.sale_line_id.order_id.partner_id if move.sale_line_id else False
                if customer:
                    aggregated[line_key]['_customer_ids'].add(customer)
            group['lines'] = sorted(
                aggregated.values(),
                key=lambda l: (l['product'].display_name, l['description'])
            )
        return sorted(
            groups.values(),
            key=lambda g: (not g['partner'], (g['partner'].display_name if g['partner'] else ''))
        )
