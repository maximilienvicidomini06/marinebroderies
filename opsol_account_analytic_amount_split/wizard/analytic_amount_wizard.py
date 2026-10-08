from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class AnalyticAmountWizard(models.TransientModel):
    _name = "analytic.amount.wizard"
    _description = "Répartition analytique en montant"

    move_line_id = fields.Many2one(
        "account.move.line", string="Ligne d'écriture", required=True, readonly=True
    )
    currency_id = fields.Many2one(related="move_line_id.company_currency_id")
    total_amount = fields.Monetary(
        string="Montant à répartir",
        compute="_compute_total_amount",
        currency_field="currency_id",
    )
    line_ids = fields.One2many(
        "analytic.amount.wizard.line", "wizard_id", string="Répartition"
    )

    @api.depends("move_line_id.balance")
    def _compute_total_amount(self):
        for wiz in self:
            wiz.total_amount = abs(wiz.move_line_id.balance)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        aml = self.env["account.move.line"].browse(
            res.get("move_line_id") or self.env.context.get("default_move_line_id")
        )
        # Pré-remplit avec la répartition existante, convertie en montants
        if aml and aml.analytic_distribution and "line_ids" in fields_list:
            total = abs(aml.balance)
            lines = []
            for key, pct in aml.analytic_distribution.items():
                for acc_id in str(key).split(","):
                    lines.append(Command.create({
                        "analytic_account_id": int(acc_id),
                        "amount": aml.company_currency_id.round(total * pct / 100.0),
                    }))
            res["line_ids"] = lines
        return res

    def action_apply(self):
        self.ensure_one()
        aml = self.move_line_id
        cur = aml.company_currency_id
        total = abs(aml.balance)
        if cur.is_zero(total):
            raise UserError(_("La ligne d'écriture n'a pas de montant."))

        amounts = defaultdict(float)
        by_plan = defaultdict(float)
        for line in self.line_ids:
            if cur.compare_amounts(line.amount, 0.0) <= 0:
                raise UserError(_("Les montants répartis doivent être positifs."))
            amounts[line.analytic_account_id] += line.amount
            by_plan[line.analytic_account_id.root_plan_id] += line.amount

        # Chaque axe analytique doit être réparti à 100 % du montant de la ligne
        for plan, amount in by_plan.items():
            if cur.compare_amounts(amount, total) != 0:
                raise UserError(_(
                    "Axe « %(plan)s » : %(amount)s réparti pour un montant de ligne de %(total)s.",
                    plan=plan.display_name,
                    amount=f"{amount:.2f}",
                    total=f"{total:.2f}",
                ))

        # Pourcentages stockés en pleine précision : Odoo recalcule exactement les montants
        aml.analytic_distribution = {
            str(account.id): amount * 100.0 / total
            for account, amount in amounts.items()
        }
        return {"type": "ir.actions.act_window_close"}


class AnalyticAmountWizardLine(models.TransientModel):
    _name = "analytic.amount.wizard.line"
    _description = "Ligne de répartition analytique en montant"

    wizard_id = fields.Many2one(
        "analytic.amount.wizard", required=True, ondelete="cascade"
    )
    currency_id = fields.Many2one(related="wizard_id.currency_id")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Compte analytique", required=True
    )
    plan_id = fields.Many2one(
        related="analytic_account_id.root_plan_id", string="Axe"
    )
    amount = fields.Monetary(
        string="Montant", currency_field="currency_id", required=True
    )
    percentage = fields.Float(
        string="%", compute="_compute_percentage", digits=(16, 4)
    )

    @api.depends("amount", "wizard_id.total_amount")
    def _compute_percentage(self):
        for line in self:
            total = line.wizard_id.total_amount
            line.percentage = line.amount * 100.0 / total if total else 0.0
