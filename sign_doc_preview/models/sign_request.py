# -*- coding: utf-8 -*-
from odoo import models


class SignRequest(models.Model):
    _inherit = 'sign.request'

    def action_open_pdf(self):
        """Ouvre le PDF du document signé dans un nouvel onglet."""
        self.ensure_one()

        # 1. Document signé → PDF final en pièce jointe
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'sign.request'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf'),
        ], order='id desc', limit=1)

        # 2. Fallback → PDF original du template
        if not attachment and self.template_id and self.template_id.attachment_id:
            attachment = self.template_id.attachment_id

        if not attachment:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Aucun PDF',
                    'message': 'Aucun document PDF disponible.',
                    'type': 'warning',
                }
            }

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=false',
            'target': 'new',
        }
