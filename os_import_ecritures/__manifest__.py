{
    "name": "Import d'écritures comptables (format tabulé)",
    "summary": "Importe un fichier d'écritures comptables séparé par ';' "
               "et génère les pièces comptables équilibrées.",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Open Solution",
    "website": "https://opensolution.mc",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/import_ecritures_views.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
