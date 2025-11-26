# -*- coding: utf-8 -*-
{
    "name": "Product Catalog Kanban Width",
    "version": "19.0.1.0.1",
    "category": "Sales",
    "summary": "Fixe la largeur des cartes de la vue catalogue à 200px",
    "author": "FMV / OpenSolution",
    "license": "LGPL-3",
    "depends": ["web", "product", "sale"],
    "data": [
      "views/product_catalog_kanban_view.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "opsol_catalog_kanban_width/static/src/scss/product_catalog.scss",
        ],
    },
    "installable": True,
    "application": False,
}
