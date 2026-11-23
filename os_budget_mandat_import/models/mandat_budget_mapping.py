from odoo import api, fields, models


class MandatBudgetMapping(models.Model):
    _name = "mandat.budget.mapping"
    _description = "Correspondance ligne budgétaire / compte analytique"
    _order = "code"
    _rec_name = "code"

    code = fields.Char("Code budgétaire", required=True, index=True,
                       help="Code tel qu'il figure dans l'export (ex. 691332)")
    name = fields.Char("Libellé")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Compte analytique", required=True, ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", "Société", required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Ce code budgétaire a déjà une correspondance pour cette société.",
    )

    @api.model
    def _get_mapping(self, company):
        recs = self.search([("company_id", "=", company.id)])
        return {r.code: r.analytic_account_id for r in recs}
