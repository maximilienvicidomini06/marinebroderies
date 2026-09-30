# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_ttc_no_tax_conversion = fields.Boolean(
        string='Activer la conversion TTC sans TVA sur les factures fournisseurs',
        default=True,
        help='Si activé, les lignes de facture fournisseur sont converties de HT+TVA vers TTC sans taxes.',
    )
