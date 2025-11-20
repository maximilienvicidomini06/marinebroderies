import pycountry
from odoo import api, fields, models


class ResCountryInherit(models.Model):
    _inherit = "res.country"

    up2pay_code_iso = fields.Char(
        string="Country Code",
        size=3,
        store=True,
        help="ISO 3166-1 numeric code for the country",
        compute="_compute_codes",
    )

    @api.depends("code")
    def _compute_codes(self):
        for country in self:
            c = False
            for country_type in ["countries", "historic_countries"]:
                try:
                    c = getattr(pycountry, country_type).get(alpha_2=country.code)
                except KeyError:
                    c = getattr(pycountry, country_type).get(alpha2=country.code)
                if c:
                    break
            if c:
                country.up2pay_code_iso = c.numeric
            else:
                country.up2pay_code_iso = False
