from odoo import fields, models, _


class PpmcPaymentReportWizard(models.TransientModel):
    _name = "opsol.ppmc.report.wizard"
    _description = "PPMC Vendor Payments Report"

    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    journal_ids = fields.Many2many(
        comodel_name="account.journal",
        string="Journals",
        domain=[("type", "in", ["bank", "cash"])],
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    def _get_payments(self):
        self.ensure_one()
        domain = [
            ("payment_type", "=", "outbound"),
            ("partner_type", "=", "supplier"),
            ("state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
        ]
        if self.date_from:
            domain.append(("date", ">=", self.date_from))
        if self.date_to:
            domain.append(("date", "<=", self.date_to))
        if self.journal_ids:
            domain.append(("journal_id", "in", self.journal_ids.ids))
        return self.env["account.payment"].search(domain, order="date, id")

    def _get_header_data(self):
        self.ensure_one()
        payments = self._get_payments()
        journal = self.journal_ids[:1] or payments[:1].journal_id
        bank_account = journal.bank_account_id if journal else False
        return {
            "company": self.company_id,
            "company_partner": self.company_id.partner_id,
            "journal": journal,
            "bank_account": bank_account,
            "currency": (journal.currency_id or self.company_id.currency_id) if journal else self.company_id.currency_id,
            "emission_date": fields.Date.context_today(self),
            "draw_date": self.date_to or fields.Date.context_today(self),
        }

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref("opsol_ppmc.action_report_ppmc_payments").report_action(self)
