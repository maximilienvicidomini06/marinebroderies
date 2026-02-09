# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name': 'All In One Quick Copy Order Lines',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    'support': 'support@softhealer.com',
    'license': 'OPL-1',
    'version': '0.0.1',
    'category': 'Extra Tools',
    'summary': 'Sale Order Copy Order Lines Sale Copy Order Lines Sales Copy Order Lines Sale Copy Product Lines Copy Sale Order Copy Purchase Order Copy Invoice Copy Invoice Lines Copy RFQ Lines Copy Request For Quotation Copy Bill Lines Duplicate Line Duplicate Order Line Duplicate Sale Order Line Duplicate Purchase Order Line Duplicate Invoice Order Line Copy Sale Order Line Copy Purchase Order Line Copy Invoice Order Line Sale Order Line Copy Purchase Order Line Copy Invoice Order Line Copy Quick Copy Sale Order Line Quick Copy Purchse Order Line Quick Copy Invoice Order Line Odoo Sale Order Quick Copy Order Lines Purchase Order Quick Copy Order Lines Invoice Quick Copy Order Lines',
    'description': """This module allows you to quickly copy order lines in sale order, purchase order and invoice so you can easily manage order lines. That's it. Cheers!""",
    'depends': [
        'sale_management',
        'purchase',
    ],
    'data': [
        'sh_sale/views/sale_order_line_views.xml',
        'sh_account/views/account_move_line_views.xml',
        'sh_purchase/views/purchase_order_line_views.xml',
    ],
    "images": ["static/description/background.png", ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': '17',
    'currency': 'EUR',
}
