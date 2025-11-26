{
    'name': 'opsol_marinebroderies',
    'version': '1.1',
    'summary': 'Add custom modification for Marine Broderies',
    'description': 'Add custom modification for Marine Broderies',
    'category': 'Uncategorized',
    'author': 'OpenSolution',
    'website': 'https://www.opensolution.mc',
    'license': 'LGPL-3',
    'depends': ['base', 'purchase', 'sale_stock', "sale_purchase", "purchase_stock"],
    'data': [
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
}
