from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    financial_partner_is_product = fields.Boolean(
        related="partner_id.is_financial_product",
        readonly=True,
    )
    financial_quantity = fields.Float(
        string="Quantite",
        digits=(16, 6),
        copy=False,
        help="Nombre de titres. La quantite doit etre saisie positive.",
    )
    financial_unit_price = fields.Monetary(
        string="Prix unitaire",
        compute="_compute_financial_unit_price",
        currency_field="currency_id",
        help="Valeur absolue du montant bancaire divisee par la quantite.",
    )

    @api.depends("amount", "financial_quantity")
    def _compute_financial_unit_price(self):
        for line in self:
            line.financial_unit_price = (
                abs(line.amount) / line.financial_quantity
                if line.financial_quantity
                else 0.0
            )

    def _get_financial_counterpart_vals(self):
        self.ensure_one()
        if not self.financial_partner_is_product or not self.financial_quantity:
            return {}
        return {
            "financial_quantity": (
                self.financial_quantity if self.amount < 0 else -self.financial_quantity
            ),
            "financial_isin_code": self.partner_id.financial_isin_code or False,
        }

    def set_account_bank_statement_line(self, aml_id, account_id):
        result = super().set_account_bank_statement_line(aml_id, account_id)
        financial_vals = self._get_financial_counterpart_vals()
        if financial_vals:
            counterpart_line = self.line_ids.filtered(lambda line: line.id == aml_id)

            counterpart_line.write(financial_vals)
        return result
    @api.constrains("amount", "financial_quantity", "partner_id")
    def _check_financial_quantity(self):
        for line in self:
            if float_compare(line.financial_quantity, 0.0, precision_digits=6) < 0:
                raise ValidationError(_("La quantite financiere doit etre positive."))
            if not line.financial_quantity:
                continue
            if not line.financial_partner_is_product:
                raise ValidationError(_(
                    "Le partenaire doit etre marque comme produit financier pour saisir une quantite."
                ))
            if float_is_zero(line.amount, precision_rounding=line.currency_id.rounding):
                raise ValidationError(_(
                    "Le montant bancaire doit etre different de zero pour un achat ou une vente de titres."
                ))
