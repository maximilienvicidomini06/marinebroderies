# -*- coding: utf-8 -*-
from odoo import api, models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    catalog_color = fields.Char(
        string="Couleur (catalog)",
        compute="_compute_catalog_color",
        store=True,
    )
    catalog_label = fields.Char(
        string="Label Couleur (catalog)",
        compute="_compute_catalog_color",
        store=True,
    )

    @api.depends('product_template_attribute_value_ids')
    def _compute_catalog_color(self):
        for product in self:
            color = False
            color_label = False

            # On récupère les valeurs d'attribut liées à ce variant
            # product_template_attribute_value_ids -> product.template.attribute.value
            # et derrière product_attribute_value_id -> product.attribute.value (avec html_color)
            ptavs = product.product_template_attribute_value_ids.filtered(
                # attribut de type "color"
                lambda ptav: ptav.attribute_id.display_type == 'color'
                             and ptav.product_attribute_value_id.html_color
            )

            if ptavs:
                # On prend la première valeur de couleur trouvée
                color = ptavs[0].product_attribute_value_id.html_color
                color_label = ptavs[0].product_attribute_value_id.name

            product.catalog_color = color
            product.catalog_label = color_label
