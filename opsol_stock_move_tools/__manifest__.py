{
    'name': 'opsol_stock_move_tools',
    'version': '1.0.2',
    'summary': 'Stock move list tools (selectors + reset)',
    'description': 'Adds selection checkboxes and reset button for stock move one2many list.',
    'category': 'Stock',
    'author': 'OpenSolution',
    'website': 'https://www.opensolution.mc',
    'license': 'LGPL-3',
    'depends': ['web', 'stock'],
    'assets': {
        'web.assets_backend': [
            'opsol_stock_move_tools/static/src/js/stock_move_selectors.js',
            'opsol_stock_move_tools/static/src/xml/stock_move_selectors.xml',
        ],
    },
    'installable': True,
    'application': False,
}
