# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    state = fields.Selection(related="move_id.state", string="state")

    @api.model_create_multi
    def create(self, vals_list):

        res = super(AccountMoveLine, self).create(vals_list)

        count = 0
        for line in res.move_id.invoice_line_ids:
            count += 1
            line.sudo().with_context(check_move_validity=False).sequence = count

        return res

    def line_copy(self):
        seq = self.sequence
        new_seq_will_be = seq + 1

        lines = self.search([
            ('move_id', '=', self.move_id.id),
            ('sequence', '>=', new_seq_will_be)
        ])

        for line in lines:
            line.sudo().with_context(check_move_validity=False).sequence = line.sequence + 1

        new_line = self.sudo().with_context(
            check_move_validity=False).copy({'move_id': self.move_id.id})

        new_line.sudo().with_context(check_move_validity=False).move_id = self.move_id.id

        new_line.sudo().with_context(check_move_validity=False).write({
            'sequence': new_seq_will_be
        })
