from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestResPartnerFinancialProduct(TransactionCase):

    def test_financial_isin_is_normalized_and_validated(self):
        partner = self.env["res.partner"].create({
            "name": "Action de test",
            "is_financial_product": True,
            "financial_isin_code": " fr0000120271 ",
        })

        self.assertEqual(partner.financial_isin_code, "FR0000120271")

    def test_invalid_financial_isin_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Action invalide",
                "is_financial_product": True,
                "financial_isin_code": "FR0000120272",
            })
