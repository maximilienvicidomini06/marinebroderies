{
    "name": "OPSol Produits financiers",
    "version": "19.0.1.0.2",
    "summary": "Suivi des achats et ventes de titres depuis les releves bancaires",
    "category": "Accounting",
    "author": "OpenSolution",
    "license": "LGPL-3",
    "depends": ["account_accountant"],
    "data": [
        "views/res_partner_views.xml",
        "views/account_bank_statement_line_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "opsol_produit_financier/static/src/scss/bank_rec_quick_create.scss",
        ],
    },
    "installable": True,
    "application": False,
}
