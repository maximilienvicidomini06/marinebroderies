# -*- coding: utf-8 -*-
from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        """
        Override de la confirmation de facture.
        On s'assure que la conversion TTC est appliquée avant la validation finale.
        """
        for move in self:
            if move.move_type in ('in_invoice', 'in_refund') and move.company_id.enable_ttc_no_tax_conversion:
                move.invoice_line_ids._convert_tax_to_ttc()
        return super()._post(soft=soft)

    def write(self, vals):
        """
        Override de write pour intercepter les modifications liées à l'OCR.
        Quand les lignes de facture sont modifiées (ex: après reconnaissance),
        on déclenche la conversion.
        """
        result = super().write(vals)

        # On ne réagit que si les lignes ont été modifiées
        if 'invoice_line_ids' in vals:
            for move in self:
                if (
                    move.move_type in ('in_invoice', 'in_refund')
                    and move.state == 'draft'
                    and move.company_id.enable_ttc_no_tax_conversion
                ):
                    move.invoice_line_ids.with_context(
                        check_move_validity=False,
                        skip_account_move_synchronization=True,
                        no_recompute=True,
                    )._convert_tax_to_ttc()

        return result

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override de create : applique la conversion dès la création.
        """
        moves = super().create(vals_list)
        for move in moves:
            if move.move_type in ('in_invoice', 'in_refund') and move.company_id.enable_ttc_no_tax_conversion:
                move.invoice_line_ids._convert_tax_to_ttc()
        return moves

    def _get_mail_template(self):
        """
        Hook OCR Odoo 17+ : appelé après la reconnaissance automatique.
        On profite de ce cycle pour appliquer la conversion.
        """
        for move in self:
            if move.move_type in ('in_invoice', 'in_refund') and move.company_id.enable_ttc_no_tax_conversion:
                move.invoice_line_ids._convert_tax_to_ttc()
        return super()._get_mail_template()
