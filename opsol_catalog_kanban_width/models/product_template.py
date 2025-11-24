from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    catalog_color = fields.Char(
        string="Couleur (catalog)",
        compute="_compute_catalog_color",
        store=False,
    )

    def _compute_catalog_color(self):
        for template in self:
            # On prend le premier variant (ou celui que tu veux)
            product = template.product_variant_id
            template.catalog_color = product.catalog_color
