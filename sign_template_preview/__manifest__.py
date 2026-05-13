# -*- coding: utf-8 -*-
{
    'name': 'Sign Document Preview',
    'version': '19.0.2.0.0',
    'summary': 'Aperçu PDF inline dans la vue liste All Documents (sign.request)',
    'author': 'Open Solution',
    'category': 'Sign',
    'depends': ['sign'],
    'data': [
        'views/sign_request_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sign_template_preview/static/src/css/sign_template_preview.css',
            'sign_template_preview/static/src/xml/sign_request_list_preview.xml',
            'sign_template_preview/static/src/js/sign_request_list_preview.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
