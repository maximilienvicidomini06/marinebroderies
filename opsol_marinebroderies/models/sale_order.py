# -*- coding: utf-8 -*-

from venv import logger
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import timedelta
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    client_validation_date = fields.Datetime(
        string="Validation client",
        readonly=True,
        copy=False,
    )

    # def onchange(self, values, field_names, fields_spec):
    #     logger = logging.getLogger(__name__)
    #     logger.info("=====>         onchange")
    #     logger.info(values)
    #     logger.info(field_names)
    #     logger.info(fields_spec)
    #     return super(SaleOrder, self).onchange(values, field_names, fields_spec)

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
        for order in self:
            user = self.env.user
            is_admin = user.has_group("base.group_erp_manager") # groupe Droits d'accès
            is_salesperson = order.user_id and order.user_id == user
            is_team_manager = order.team_id and order.team_id.user_id == user
            if not (is_salesperson or is_team_manager or is_admin):
                raise UserError(
                    _(
                        "You are not allowed to confirm this quotation. "
                        "Only the salesperson, the sales team manager."
                    )
                )
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
