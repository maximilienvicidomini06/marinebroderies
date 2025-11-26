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

    @api.depends('product_template_attribute_value_ids')
    def _compute_taille_product_template_attribute_value_ids(self):
        for product in self:
            product.taille_product_template_attribute_value_ids = product.product_template_attribute_value_ids.filtered(
                lambda line: 'taille' in line.attribute_id.name.lower()
            )
