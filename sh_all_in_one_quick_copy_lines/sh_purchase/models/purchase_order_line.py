# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, api


class PurchaseOrderLine(models.Model):
    '''this is a custom purchase order line model'''
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals):
        '''this is a custom create method for purchase order line'''
        res = super(PurchaseOrderLine, self).create(vals)
        count = len(res.order_id.order_line.ids)
        res.sequence = count
        return res

    def line_copy(self):
        '''this is a custom copy method for purchase order line'''
        seq = self.sequence
        new_seq_will_be = seq + 1

        lines = self.search([
            ('order_id', '=', self.order_id.id),
            ('sequence', '>=', new_seq_will_be)
        ])

        for line in lines:
            line.sequence = line.sequence + 1

        new_line = self.copy({'order_id': self.order_id.id})

        new_line.order_id = self.order_id.id

        new_line.write({
            'sequence': new_seq_will_be
        })
