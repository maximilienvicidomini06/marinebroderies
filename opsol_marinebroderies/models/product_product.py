# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    taille_product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value',
        string='Taille Attributes',
        compute='_compute_taille_product_template_attribute_value_ids',
        store=True,
    )

    @api.depends(
        'product_template_attribute_value_ids',
        'product_template_attribute_value_ids.attribute_line_id.attribute_id.name',
        'product_template_attribute_value_ids.product_attribute_value_id.name',
        'product_template_attribute_value_ids.product_attribute_value_id.sequence',
        'product_tmpl_id.attribute_line_ids',
        'product_tmpl_id.attribute_line_ids.attribute_id.name',
        'product_tmpl_id.attribute_line_ids.value_ids.name',
        'product_tmpl_id.attribute_line_ids.value_ids.sequence',
    )
    def _compute_taille_product_template_attribute_value_ids(self):
        for product in self:
            taille_line_attribute = product.product_tmpl_id.attribute_line_ids.filtered(
                lambda line: (
                    'taille' in (line.attribute_id.name or '').lower()
                    or any('taille' in (value.name or '').lower() for value in line.value_ids)
                )
            )
            product.taille_product_template_attribute_value_ids = (
                product.product_template_attribute_value_ids.filtered(
                    lambda value: value.attribute_line_id in taille_line_attribute
                )
            )
