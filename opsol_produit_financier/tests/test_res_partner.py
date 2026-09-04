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

    def test_financial_partner_display_name_is_isin(self):
        financial_partner = self.env["res.partner"].create({
            "name": "Action de test",
            "is_financial_product": True,
            "financial_isin_code": "FR0000120271",
        })
        standard_partner = self.env["res.partner"].create({"name": "Tiers standard"})

        self.assertEqual(financial_partner.display_name, "FR0000120271")
        self.assertEqual(standard_partner.display_name, "Tiers standard")

    def test_financial_isin_is_required_for_financial_products(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Action sans ISIN",
                "is_financial_product": True,
            })

    def test_invalid_financial_isin_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Action invalide",
                "is_financial_product": True,
                "financial_isin_code": "FR0000120272",
            })

    def test_financial_products_are_searched_by_isin_only(self):
        financial_partner = self.env["res.partner"].create({
            "name": "Action de test",
            "is_financial_product": True,
            "financial_isin_code": "FR0000120271",
        })
        standard_partner = self.env["res.partner"].create({
            "name": "Action de test",
        })

        isin_results = self.env["res.partner"].name_search("FR0000120271")
        name_results = self.env["res.partner"].name_search("Action de test")

        self.assertIn((financial_partner.id, financial_partner.display_name), isin_results)
        self.assertNotIn((financial_partner.id, financial_partner.display_name), name_results)
        self.assertIn((standard_partner.id, standard_partner.display_name), name_results)

    def test_financial_ledger_menu_visibility_depends_on_company_mode(self):
        financial_menu = self.env.ref(
            "opsol_produit_financier.menu_financial_partner_ledger"
        )
        self.env.company.financial_mode = False
        self.assertIn(financial_menu.id, self.env["ir.ui.menu"]._load_menus_blacklist())

        self.env.company.financial_mode = True
        self.assertNotIn(financial_menu.id, self.env["ir.ui.menu"]._load_menus_blacklist())
