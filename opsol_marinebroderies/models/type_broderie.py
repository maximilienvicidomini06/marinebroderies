from odoo import fields, models


class TypeBroderie(models.Model):
    _name = "opsol_marinebroderies.type_broderie"
    _description = "Type de broderie"

    name = fields.Char(required=True)
    description = fields.Text()
    related_product_id = fields.Many2one(
        "product.product",
        string="Produit lié",
        help="Produit lié à ce type de broderie, si applicable.",
        domain=[('type', '=', 'service')]
    )
