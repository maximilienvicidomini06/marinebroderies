# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    client_validation_date = fields.Datetime(
        string="Validation client",
        readonly=True,
        copy=False,
    )

    def action_request_client_confirmation(self):
        self.ensure_one()
        template = self.env.ref(
            "opsol_marinebroderies.mail_template_sale_order_client_validation",
            raise_if_not_found=False,
        )
        if not template:
            return False
        return {
            "type": "ir.actions.act_window",
            "res_model": "mail.compose.message",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model": "sale.order",
                "default_res_ids": [self.id],
                "default_use_template": True,
                "default_template_id": template.id,
                "default_composition_mode": "comment",
                "force_email": True,
            },
        }

    def action_confirm(self):
        for rec in self:
            if not rec.commitment_date:
                if rec.team_id and rec.team_id.delivery_time_days:
                    rec.commitment_date = fields.Date.today() + timedelta(days=rec.team_id.delivery_time_days)
                else:
                    rec.commitment_date = fields.Date.today()

            rec.broderie_lines()
        return super().action_confirm()

    def action_draft(self):
        res = super().action_draft()
        self.filtered(lambda order: order.state == "draft").write(
            {"client_validation_date": False}
        )
        return res

    @api.constrains('commitment_date')
    def broderie_lines(self):
        for rec in self.filtered(lambda l: l.state not in ['sale', 'cancel']):
            for line in rec.order_line.filtered(lambda l: not l.display_type and l.product_id.type  == "consu" and l.type_broderie_id):
                line.update_related_broderie_line()
