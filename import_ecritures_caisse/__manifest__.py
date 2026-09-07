# -*- coding: utf-8 -*-
{
    "name": "Import écritures de caisse",
    "summary": "Import d'écritures comptables de caisse depuis un fichier texte (séparateur ;)",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_caisse_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}
