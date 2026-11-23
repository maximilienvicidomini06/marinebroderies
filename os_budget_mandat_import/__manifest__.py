{
    "name": "Import des mandats budgétaires",
    "summary": "Importe les exports MANDAT en lignes analytiques pour le suivi budgétaire",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Open Solution",
    "website": "https://www.opensolution.mc",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/mandat_budget_mapping_views.xml",
        "views/account_analytic_line_views.xml",
        "wizard/mandat_import_wizard_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
