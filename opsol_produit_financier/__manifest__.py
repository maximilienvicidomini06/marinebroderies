{
    "name": "OPSol Produits financiers",
    "version": "19.0.1.0.13",
    "summary": "Suivi des achats et ventes de titres depuis les releves bancaires",
    "category": "Accounting",
    "author": "OpenSolution",
    "license": "LGPL-3",
    "depends": ["account_accountant", "account_reports"],
    "data": [
        "views/res_partner_views.xml",
        "views/account_bank_statement_line_views.xml",
        "views/res_config_settings_views.xml",
        "data/financial_partner_ledger.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "opsol_produit_financier/static/src/scss/bank_rec_quick_create.scss",
            "opsol_produit_financier/static/src/xml/bank_rec_statement_line.xml",
            "opsol_produit_financier/static/src/xml/financial_partner_ledger.xml",
        ],
    },
    "installable": True,
    "application": False,
}
