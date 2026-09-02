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

    def test_financial_ledger_menu_visibility_depends_on_company_mode(self):
        financial_menu = self.env.ref(
            "opsol_produit_financier.menu_financial_partner_ledger"
        )
        self.env.company.financial_mode = False
        self.assertIn(financial_menu.id, self.env["ir.ui.menu"]._load_menus_blacklist())

        self.env.company.financial_mode = True
        self.assertNotIn(financial_menu.id, self.env["ir.ui.menu"]._load_menus_blacklist())
