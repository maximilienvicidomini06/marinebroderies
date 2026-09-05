from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    os_import_key = fields.Char(
        string="Clé d'import",
        index=True,
        copy=False,
        readonly=True,
        help="Identifiant de la pièce dans le fichier source. Garantit "
             "l'idempotence : une pièce déjà importée est ignorée lors "
             "d'un nouveau passage du même fichier.",
    )
