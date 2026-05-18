# -*- coding: utf-8 -*-
{
    'name': 'Sign Document Preview Panel',
    'version': '19.0.1.0.0',
    'summary': 'Panneau aperçu PDF à droite dans la liste des documents signés',
    'author': 'Open Solution',
    'depends': ['sign'],
    'assets': {
        'web.assets_backend': [
            'sign_doc_preview/static/src/css/preview.css',
            'sign_doc_preview/static/src/xml/preview.xml',
            'sign_doc_preview/static/src/js/preview.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
