# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    delivery_time_days = fields.Integer(string='Temps de livraison (J)')
