# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        for rec in self:
            if not rec.commitment_date:
                if rec.team_id and rec.team_id.delivery_time_days:
                    rec.commitment_date = fields.Date.today() + timedelta(days=rec.team_id.delivery_time_days)
                else:
                    rec.commitment_date = fields.Date.today()

            rec.broderie_lines()
        return super().action_confirm()

    @api.constrains('commitment_date')
    def broderie_lines(self):
        for rec in self.filtered(lambda l: l.state not in ['sale', 'cancel']):
            for line in rec.order_line.filtered(lambda l: not l.display_type and l.product_id.type  == "consu" and l.type_broderie_id):
                line.update_related_broderie_line()
