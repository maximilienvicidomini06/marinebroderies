from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_reconciled_invoices_url(self):
        self.ensure_one()
        invoices = self.reconciled_bill_ids | self.reconciled_invoice_ids
        if len(invoices) > 1:
            return "/odoo/opsol-paid-invoices?active_ids=%s" % ",".join(
                str(invoice_id) for invoice_id in invoices.ids
            )
        if not invoices:
            return False

        return "/odoo/opsol-paid-invoices/%s" % invoices.id

    def _get_ordre_virement_lines(self):
        self.ensure_one()

        invoices = self.reconciled_bill_ids | self.reconciled_invoice_ids
        lines = []
        for move in invoices.sorted(key=lambda m: (m.invoice_date_due or m.invoice_date or m.date, m.id)):
            lines.append({
                "date": move.invoice_date or move.date,
                "move_id": move.id,
                "move_type": move.move_type,
                "numero_piece": move.name,
                "libelle": move.ref or move.invoice_origin or move.payment_reference or move.name,
                "partner": move.partner_id and move.partner_id.name, 
                "echeance": move.invoice_date_due,
                "avoir_ou_reglement": "Avoir" if move.move_type in ("in_refund", "out_refund") else "Reglement",
                "vos_factures": move.ref or move.name,
                "total_ttc": move.amount_total,
            })

        if not lines:
            lines.append({
                "date": self.date,
                "move_id": False,
                "numero_piece": self.name,
                "libelle": self.memo or "Paiement(s) non reconcilie(s)",
                "partner": "",
                "echeance": False,
                "avoir_ou_reglement": "Reglement",
                "vos_factures": "",
                "total_ttc": self.amount,
            })

        return lines
