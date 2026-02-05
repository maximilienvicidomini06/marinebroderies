from odoo import fields, models


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    def _get_payments(self):
        self.ensure_one()
        payments = self.payment_ids
        return payments.sorted(key=lambda p: (p.date or fields.Date.context_today(self), p.id))

    def _get_header_data(self):
        self.ensure_one()
        journal = self.journal_id
        bank_account = journal.bank_account_id if journal else False
        return {
            "company": self.company_id,
            "company_partner": self.company_id.partner_id,
            "journal": journal,
            "bank_account": bank_account,
            "currency": (journal.currency_id or self.company_id.currency_id) if journal else self.company_id.currency_id,
            "emission_date": fields.Date.context_today(self),
            "draw_date": self.date or fields.Date.context_today(self),
        }
