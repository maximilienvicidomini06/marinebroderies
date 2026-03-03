from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_order_virement(self):
        self.ensure_one()
        payments = self.payment_ids
        if not payments:
            raise UserError(_("No payment found to print the ordre de virement."))
        return self.env.ref("opsol_ppmc.action_report_order_virement").report_action(payments)
