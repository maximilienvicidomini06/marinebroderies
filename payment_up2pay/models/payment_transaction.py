# coding: utf-8
import binascii
import hashlib
import logging
import base64
import unicodedata

from odoo import exceptions, models, _, api
from datetime import datetime
import urllib.request
import urllib.parse

from odoo.exceptions import ValidationError
from werkzeug import urls
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from odoo.modules.module import get_module_path
from .const import SUPPORTED_CURRENCIES, ERROR_SUCCESS, ERROR_CODE, AUTH_CODE
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class Signature:

    def verify(self, signature, msg, key):
        msg = self.remove_sign(msg)
        key = RSA.importKey(key)
        ha = SHA.new(msg.encode("utf-8"))
        verifier = PKCS1_v1_5.new(key)
        signature = urllib.request.unquote(signature)
        signature = base64.b64decode(signature)
        return verifier.verify(ha, signature)

    def remove_sign(self, msg):
        pos = msg.find("&Signature")
        if pos == -1:
            return msg
        return msg[:pos]


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    HASH = {"SHA512": hashlib.sha512}
    sign = Signature()

    def build_args(self, args):
        if "Auto" not in args:
            msg = "Mt=" + args["Mt"] + "&Ref=" + urllib.parse.quote(args["Ref"])
        else:
            msg = (
                "Mt="
                + args["Mt"]
                + "&Ref="
                + urllib.parse.quote(args["Ref"])
                + "&Auto="
                + args["Auto"]
            )
        msg += "&Erreur=" + args["Erreur"] + "&Signature=" + args["Signature"]
        return msg

    def check_error_code(self, erreur):

        if erreur in ERROR_CODE:
            error_msg = ERROR_CODE[erreur]
            return error_msg
        else:
            for err in ERROR_CODE:
                if erreur.startswith(err):
                    error_msg = AUTH_CODE[erreur[-2:]]
                    return error_msg
        return False

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def build_up2pay_args(self, provider, tx_values):
        reference = tx_values["reference"]
        amount = tx_values["amount"]
        key = provider["up2pay_key"]
        identifiant, devise = (
            provider["up2pay_identifier"],
            SUPPORTED_CURRENCIES[self.currency_id.name],
        )
        rang, site = provider["up2pay_rank"], provider["up2pay_site"]
        _hash = "SHA512"

        porteur = self.partner_email
        url = provider._up2pay_get_api_url()
        url_retour = self.get_base_url()

        if not url_retour:
            error_msg = _("up2pay: Paiement impossible, URL de retour non configurée")
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        amount = "%03u" % int(amount * 100)
        retour = "Mt:M;Ref:R;Auto:A;Erreur:E;Signature:K"
        url_effectue = urls.url_join(url_retour, "/payment/up2pay/accept")
        url_annule = urls.url_join(url_retour, "/payment/up2pay/cancel")
        url_refuse = urls.url_join(url_retour, "/payment/up2pay/decline")
        url_ipn = urls.url_join(url_retour, "/payment/up2pay/ipn")
        time = datetime.now().isoformat()

        shoppingcart = (
            '<?xml version="1.0" encoding="utf-8" ?>'
            "<shoppingcart>"
            "<total>"
            "<totalQuantity>{quantity}</totalQuantity>"
            "</total>"
            "</shoppingcart>"
        ).format(quantity=1)

        partner_first_name, partner_last_name = payment_utils.split_partner_name(
            self.partner_name
        )

        partner_first_name = (
            unicodedata.normalize("NFKD", partner_first_name)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        partner_last_name = (
            unicodedata.normalize("NFKD", partner_last_name)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        partner_address = (
            unicodedata.normalize("NFKD", self.partner_address)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        partner_zip = (
            unicodedata.normalize("NFKD", self.partner_zip)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        partner_city = (
            unicodedata.normalize("NFKD", self.partner_city)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )

        billing = (
            '<?xml version="1.0" encoding="utf-8" ?><Billing>'
            "<Address><FirstName>{firstname}</FirstName>"
            "<LastName>{lastname}</LastName>"
            "<Address1>{address1}</Address1>"
            "<ZipCode>{zipcode}</ZipCode>"
            "<City>{city}</City><CountryCode>{countrycode}</CountryCode>"
            "</Address></Billing>"
        ).format(
            firstname=str(partner_first_name)[:22],
            lastname=str(partner_last_name)[:22],
            address1=str(partner_address)[:50],
            zipcode=str(partner_zip)[:16],
            city=str(partner_city)[:50],
            countrycode=self.partner_country_id.up2pay_code_iso or 250,
        )

        challenge = provider.up2pay_challenge if provider.up2pay_challenge else "01"

        args = (
            "PBX_SITE="
            + site
            + "&PBX_RANG="
            + rang
            + "&PBX_HASH="
            + _hash
            + "&PBX_CMD="
            + reference
            + "&PBX_IDENTIFIANT="
            + identifiant
            + "&PBX_TOTAL="
            + amount
            + "&PBX_DEVISE="
            + devise
            + "&PBX_PORTEUR="
            + porteur
            + "&PBX_RETOUR="
            + retour
            + "&PBX_TIME="
            + time
            + "&PBX_EFFECTUE="
            + url_effectue
            + "&PBX_REFUSE="
            + url_refuse
            + "&PBX_ANNULE="
            + url_annule
            + "&PBX_REPONDRE_A="
            + url_ipn
            + "&PBX_SHOPPINGCART="
            + shoppingcart
            + "&PBX_BILLING="
            + billing
            + "&PBX_SOUHAITAUTHENT="
            + challenge
        )

        hmac = self.compute_hmac(key, _hash, args)
        return dict(
            hmac=hmac,
            hash=_hash,
            porteur=porteur,
            url=url,
            identifiant=identifiant,
            rank=rang,
            site=site,
            url_ipn=url_ipn,
            refuse=url_refuse,
            pbx_time=time,
            devise=devise,
            retour=retour,
            annule=url_annule,
            amount=amount,
            effectue=url_effectue,
            billing=billing,
            shoppingcart=shoppingcart,
            challenge=challenge,
        )

    def compute_hmac(self, key, hash_name, args):
        try:
            binary_key = binascii.unhexlify(key)
        except:
            _logger.exception("Cannot decode key")
            raise ValidationError(
                "Calcul HMAC impossible, Vérifiez la valeur de la clé"
            )

        try:
            import hmac

            hmac_value = (
                hmac.new(binary_key, args.encode("utf-8"), self.HASH[hash_name])
                .hexdigest()
                .upper()
            )

        except:
            _logger.exception("Calcul HMAC impossible")
            raise ValidationError("Calcul HMAC impossible, Une erreur s'est produite")
        return hmac_value

    def _get_specific_rendering_values(self, processing_values):
        """Override of payment to return up2pay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "up2pay":
            return res

        provider = self.provider_id
        vals = self.build_up2pay_args(provider, processing_values)
        processing_values.update(vals)
        processing_values.update(
            {
                "api_url": self.provider_id._up2pay_get_api_url(),
            }
        )

        return processing_values

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """Override of `payment` to extract the reference from the payment data."""
        if provider_code != "up2pay":
            return super()._extract_reference(provider_code, payment_data)
        return payment_data["Ref"]

    def _apply_updates(self, payment_data):
        """Override of `payment` to update the transaction based on the payment data."""
        if self.provider_code != "up2pay":
            return super()._apply_updates(payment_data)

        if self.state == "done":
            _logger.warning(
                "up2pay: trying to validate an already validated tx (ref %s)"
                % self.reference
            )
            return True

        ref = payment_data["Ref"]
        montant = payment_data["Mt"]

        error_code = payment_data["Erreur"]
        error_msg = self.check_error_code(error_code)

        if error_msg:
            self._set_canceled()
            return False

        if ref and montant and error_code in ERROR_SUCCESS:
            self._set_done()
            return True

    def _extract_amount_data(self, payment_data):
        """Override of `payment` to extract the amount and currency from the payment data."""
        if self.provider_code != "up2pay":
            return super()._extract_amount_data(payment_data)
        # Redirection payments don't have the amount or currency in their payment_data, but
        # processing them results in a pending transaction anyway.
        if payment_data.get("action", {}).get("type") == "redirect":
            return None  # Skip the validation

        amount = payment_utils.to_major_currency_units(
            float(payment_data.get("Mt", 0)), self.currency_id
        )
        return {
            "amount": amount,
            "currency_code": self.currency_id.name,
        }
