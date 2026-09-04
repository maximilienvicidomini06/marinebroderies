from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        blacklist = super()._load_menus_blacklist()
        if not self.env.company.financial_mode:
            blacklist.append(
                self.env.ref(
                    "opsol_produit_financier.menu_financial_partner_ledger"
                ).id
            )
        return blacklist
