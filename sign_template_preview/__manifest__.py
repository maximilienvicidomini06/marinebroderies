# -*- coding: utf-8 -*-
{
    'name': 'Sign Template Preview',
    'version': '19.0.1.0.0',
    'summary': 'Aperçu PDF inline dans la vue liste des modèles de signature',
    'description': """
        Affiche un aperçu du document PDF directement dans la vue liste
        du modèle sign.template, sur la même page, sans quitter la liste.
    """,
    'author': 'Open Solution',
    'category': 'Sign',
    'depends': ['sign'],
    'data': [
        'views/sign_template_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sign_template_preview/static/src/css/sign_template_preview.css',
            'sign_template_preview/static/src/xml/sign_template_list_preview.xml',
            'sign_template_preview/static/src/js/sign_template_list_preview.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
