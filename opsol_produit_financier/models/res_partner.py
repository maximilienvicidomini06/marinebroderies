from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_financial_product = fields.Boolean(
        string="Produit financier",
        help="Indique que ce partenaire represente un titre financier.",
    )
    financial_isin_code = fields.Char(
        string="Code ISIN",
        copy=False,
        index=True,
        help="Identifiant ISIN du titre financier.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        self._normalize_financial_isin_codes(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        self._normalize_financial_isin_codes([vals])
        return super().write(vals)

    @api.model
    def _normalize_financial_isin_codes(self, vals_list):
        for vals in vals_list:
            isin_code = vals.get("financial_isin_code")
            if isinstance(isin_code, str):
                vals["financial_isin_code"] = isin_code.strip().upper() or False

    @api.constrains("is_financial_product", "financial_isin_code")
    def _check_financial_isin_code(self):
        for partner in self:
            if not partner.financial_isin_code:
                continue
            if not self._is_valid_isin(partner.financial_isin_code):
                raise ValidationError(_("Le code ISIN doit etre valide."))
            if partner.is_financial_product and self.search_count([
                ("id", "!=", partner.id),
                ("is_financial_product", "=", True),
                ("financial_isin_code", "=", partner.financial_isin_code),
            ]):
                raise ValidationError(_("Le code ISIN doit etre unique pour les produits financiers."))

    @staticmethod
    def _is_valid_isin(isin_code):
        if len(isin_code) != 12 or not isin_code[:2].isalpha() or not isin_code[-1].isdigit():
            return False
        if not isin_code.isalnum() or isin_code != isin_code.upper():
            return False

        digits = "".join(str(ord(character) - 55) if character.isalpha() else character for character in isin_code)
        checksum = 0
        for index, character in enumerate(reversed(digits)):
            value = int(character)
            if index % 2:
                value *= 2
            checksum += value // 10 + value % 10
        return checksum % 10 == 0
