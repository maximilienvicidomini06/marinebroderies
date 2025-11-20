from odoo import api, fields, models

ThreeDSecureChallengeValue = [
    ("01", "Pas de préférence"),
    ("02", "Pas de chalenge demandé"),
    ("03", "Chalenge souhaité"),
    ("04", "Chalenge requis"),
]


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("up2pay", "Up2pay")], ondelete={"up2pay": "set default"}
    )
    up2pay_site = fields.Char(
        "Numéro du site", size=7, default="1999888", required_if_provider="up2pay"
    )
    up2pay_rank = fields.Char(
        "Numéro de rang", size=3, default="32", required_if_provider="up2pay"
    )
    up2pay_identifier = fields.Char(
        "Identifiant", size=9, default="2", required_if_provider="up2pay"
    )
    up2pay_key = fields.Char(
        "Clé",
        default="0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF",
        required_if_provider="up2pay",
    )
    up2pay_server = fields.Selection(
        [("pro_01", "Production 1"), ("pro_02", "Production 2")],
        "Serveur",
        default="pro_01",
        required_if_provider="up2pay",
    )
    up2pay_challenge = fields.Selection(
        ThreeDSecureChallengeValue, "3DSv2 Chalenge", default="01"
    )

    def _up2pay_get_api_url(self):
        """Return the appropriate URL of the requested API for the acquirer state.
        Note: self.ensure_one()
        :param str api_key: The API whose URL to get: 'hosted_payment_page' or 'directlink'
        :return: The API URL
        :rtype: str
        """
        self.ensure_one()

        if self.state == "enabled":
            if self.up2pay_server == "pro_01":
                url = "https://tpeweb.e-transactions.fr/php/"
            else:
                url = "https://tpeweb1.e-transactions.fr/php/"
        else:  # 'test'
            url = "https://recette-tpeweb.e-transactions.fr/php/"

        return url
