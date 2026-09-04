from odoo import models


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    def _apply_lines_for_bank_widget(
        self, residual_amount_currency, residual_balance, partner, st_line
    ):
        vals_list = super()._apply_lines_for_bank_widget(
            residual_amount_currency=residual_amount_currency,
            residual_balance=residual_balance,
            partner=partner,
            st_line=st_line,
        )
        financial_vals = st_line._get_financial_counterpart_vals()
        if not financial_vals:
            return vals_list

        counterpart_vals_list = [
            vals
            for vals in vals_list
            if vals.get("account_id") and not vals.get("tax_repartition_line_id")
        ]
        if len(counterpart_vals_list) == 1:
            counterpart_vals_list[0].update(financial_vals)

        return vals_list
