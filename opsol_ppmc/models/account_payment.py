from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_ordre_virement_lines(self):
        self.ensure_one()

        invoices = self.reconciled_bill_ids | self.reconciled_invoice_ids
        lines = []
        for move in invoices.sorted(key=lambda m: (m.invoice_date_due or m.invoice_date or m.date, m.id)):
            lines.append({
                "date": move.invoice_date or move.date,
                "numero_piece": move.name,
                "libelle": move.ref or move.invoice_origin or move.payment_reference or move.name,
                "echeance": move.invoice_date_due,
                "avoir_ou_reglement": "Avoir" if move.move_type in ("in_refund", "out_refund") else "Reglement",
                "vos_factures": move.ref or move.name,
            })

        if not lines:
            lines.append({
                "date": self.date,
                "numero_piece": self.name,
                "libelle": "Paiement(s) non reconcilie(s)",
                "echeance": False,
                "avoir_ou_reglement": "Reglement",
                "vos_factures": "",
            })

        return lines
