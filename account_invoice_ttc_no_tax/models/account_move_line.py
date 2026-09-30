# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.fields import Command


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _convert_tax_to_ttc(self):
        """
        Pour chaque ligne ayant des taxes, remplace le prix HT
        par le prix TTC et supprime les taxes.
        S'applique uniquement aux factures fournisseurs (in_invoice, in_refund).
        """
        for line in self:
            move = line.move_id
            if move.move_type not in ('in_invoice', 'in_refund'):
                continue
            if not move.company_id.enable_ttc_no_tax_conversion:
                continue
            if not line.tax_ids:
                continue

            qty = line.quantity or 1.0
            taxes_res = line.tax_ids.compute_all(
                line.price_unit,
                currency=move.currency_id,
                quantity=qty,
                product=line.product_id,
                partner=move.partner_id,
            )
            price_ttc = taxes_res['total_included'] / qty

            # Write en bypassant les validations et recomputations
            line.with_context(
                check_move_validity=False,
                skip_account_move_synchronization=True,
                no_recompute=True,
            ).write({
                'price_unit': price_ttc,
                'tax_ids': [Command.clear()],
            })

    @api.onchange('tax_ids', 'price_unit', 'quantity', 'product_id')
    def _onchange_convert_ttc_on_vendor_bill(self):
        """
        Déclenché dans l'interface lors de la modification d'une ligne.
        Convertit HT+TVA → TTC sans TVA en temps réel.
        """
        for line in self:
            if line.move_id.move_type not in ('in_invoice', 'in_refund'):
                continue
            if not line.move_id.company_id.enable_ttc_no_tax_conversion:
                continue
            if not line.tax_ids:
                continue

            qty = line.quantity or 1.0
            taxes_res = line.tax_ids.compute_all(
                line.price_unit,
                currency=line.move_id.currency_id,
                quantity=qty,
                product=line.product_id,
                partner=line.move_id.partner_id,
            )
            price_ttc = taxes_res['total_included'] / qty

            # Assignation directe — dans un onchange, pas de write()
            line.price_unit = price_ttc
            line.tax_ids = [Command.clear()]
