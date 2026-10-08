from odoo import _, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def action_open_analytic_amount_wizard(self):
        self.ensure_one()
        if self.company_currency_id.is_zero(self.balance):
            raise UserError(_("Saisissez d'abord le débit ou le crédit de la ligne."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Répartition analytique en montant"),
            "res_model": "analytic.amount.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_move_line_id": self.id},
        }
