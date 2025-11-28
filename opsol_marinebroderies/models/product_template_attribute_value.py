from odoo import api, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def name_get(self):
        res = []
        for ptav in self:
            # seulement le nom de la valeur (ex: "Rouge")
            name = ptav.product_attribute_value_id.name or ptav.name
            res.append((ptav.id, name))
        return res

    @api.depends('attribute_id')
    def _compute_display_name(self):
        """Override because in general the name of the value is confusing if it
        is displayed without the name of the corresponding attribute.
        Eg. on exclusion rules form
        """
        for value in self:
            value.display_name = f"{value.name}"




# TAche cron

# ptav_records = self.sudo().search([])
# if ptav_records:
#     # Option 1 : appeler explicitement le compute
#     ptav_records._compute_display_name()