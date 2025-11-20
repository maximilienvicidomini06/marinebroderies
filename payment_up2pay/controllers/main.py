# -*- coding: utf-8 -*-
import logging
import pprint
import json
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class Up2payController(http.Controller):

    @http.route(
        "/payment/up2pay/ipn",
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        save_session=False,
    )
    def ipn(self, **post):
        _logger.info("up2pay: entering ipn with post data %s", pprint.pformat(post))
        request.env["payment.transaction"].sudo()._process("up2pay", post)
        return ""

    @http.route(
        [
            "/payment/up2pay/accept",
            "/payment/up2pay/test/accept",
        ],
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        save_session=False,
    )
    def up2pay_form_feedback(self, **post):
        _logger.info(
            "up2pay: entering form_feedback with post data %s", pprint.pformat(post)
        )
        request.env["payment.transaction"].sudo()._process("up2pay", post)
        return request.redirect(post.pop("return_url", "/payment/status"))

    def _get_return_url(self, **post):
        """Extract the return URL from the data coming from up2pay."""
        return_url = post.pop("return_url", "")
        if not return_url:
            custom = json.loads(
                post.pop("custom", False) or post.pop("cm", False) or "{}"
            )
            return_url = custom.get("return_url", "/")
        return return_url

    @http.route(
        [
            "/payment/up2pay/cancel",
            "/payment/up2pay/test/cancel",
            "/payment/up2pay/decline",
            "/payment/up2pay/test/decline",
        ],
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        save_session=False,
    )
    def up2pay_cancel(self, **post):
        """When the user cancels its up2pay payment: GET on this route"""
        _logger.info("Beginning up2pay cancel with post data %s", pprint.pformat(post))
        return_url = self._get_return_url(**post)
        return request.redirect(return_url)
