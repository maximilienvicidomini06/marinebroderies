from collections import defaultdict

from odoo import Command, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        self.ensure_one()

        if self.is_register_payment_on_draft:
            self.payment_difference_handling = "open"

        payments = self._create_payments()
        if not payments:
            return True

        grouped_payment_ids = defaultdict(list)
        for payment in payments:
            key = (
                payment.journal_id.id,
                payment.payment_type,
                payment.payment_method_id.id,
            )
            grouped_payment_ids[key].append(payment.id)

        batches = self.env["account.batch.payment"]
        for (journal_id, payment_type, payment_method_id), payment_ids in grouped_payment_ids.items():
            batch_date = self.payment_date or fields.Date.context_today(self)
            existing_batch = self.env["account.batch.payment"].search([
                ("state", "=", "draft"),
                ("date", "=", batch_date),
                ("journal_id", "=", journal_id),
                ("batch_type", "=", payment_type),
                ("payment_method_id", "=", payment_method_id),
            ], limit=1)

            if existing_batch:
                existing_batch.write({
                    "payment_ids": [Command.link(payment_id) for payment_id in payment_ids],
                })
                batches |= existing_batch
                continue

            batch_vals = {
                "journal_id": journal_id,
                "batch_type": payment_type,
                "payment_method_id": payment_method_id,
                "date": batch_date,
                "payment_ids": [Command.set(payment_ids)],
            }
            batches |= self.env["account.batch.payment"].create(batch_vals)

        report_action = self.env.ref("opsol_ppmc.action_report_ppmc_payments")
        return report_action.report_action(batches)
