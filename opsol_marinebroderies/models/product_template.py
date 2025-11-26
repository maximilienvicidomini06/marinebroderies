# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    taille_attribute_line_ids = fields.Many2many(
        'product.template.attribute.line',
        string='Taille Attributes',
        compute='_compute_taille_attribute_line_ids',
        store=True,
    )

    @api.depends('attribute_line_ids')
    def _compute_taille_attribute_line_ids(self):
        for product in self:
            product.taille_attribute_line_ids = product.attribute_line_ids.filtered(
                lambda line: 'taille' in line.attribute_id.name.lower()
            )
