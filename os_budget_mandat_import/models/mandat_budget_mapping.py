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
    general_account_id = fields.Many2one(
        "account.account", "Compte comptable", compute="_compute_general_account_id",
        store=True, readonly=False, check_company=True,
        help="Compte du plan comptable portant le même code que l'imputation budgétaire.")
    company_id = fields.Many2one(
        "res.company", "Société", required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Ce code budgétaire a déjà une correspondance pour cette société.",
    )

    @api.depends("code", "company_id")
    def _compute_general_account_id(self):
        for rec in self:
            rec.general_account_id = rec._find_account(rec.code, rec.company_id)

    @api.model
    def _find_account(self, code, company):
        if not code or not company:
            return self.env["account.account"]
        return self.env["account.account"].with_company(company).search(
            [("code", "=", code.strip()), *self.env["account.account"]._check_company_domain(company)],
            limit=1)

    @api.model
    def _get_mapping(self, company):
        recs = self.search([("company_id", "=", company.id)])
        return {r.code: r.analytic_account_id for r in recs}
