from odoo import fields, _
from odoo.addons.sale.controllers import portal as sale_portal
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class CustomerPortal(sale_portal.CustomerPortal):
    @sale_portal.http.route(
        ["/my/orders/<int:order_id>/client_validate"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def portal_order_client_validate(self, order_id, access_token=None, **kwargs):
        access_token = access_token or request.httprequest.args.get("access_token")
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        order = order_sudo.with_user(request.env.user)
        try:
            if not order.client_validation_date:
                order_sudo.write({"client_validation_date": fields.Datetime.now()})
            order.message_post(
                body=_("Client validated the order."),
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
        except AccessError:
            return request.redirect("/my")

        return request.redirect(order_sudo.get_portal_url())
