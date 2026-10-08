{
    "name": "opsol Répartition analytique en montant",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Saisir la répartition analytique d'une ligne d'écriture en montants",
    "author": "Open Solution",
    "website": "https://opensolution.mc",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/analytic_amount_wizard_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
}
