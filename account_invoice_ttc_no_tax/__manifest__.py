# -*- coding: utf-8 -*-
{
    'name': 'Facture Fournisseur : Prix TTC sans TVA',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Convertit automatiquement les prix HT+TVA en TTC sans TVA sur les factures fournisseurs',
    'description': """
        Ce module détecte automatiquement les taxes sur les lignes de factures fournisseurs
        et remplace le prix HT par le prix TTC correspondant, en supprimant la TVA.
        
        Cela s'applique lors de la reconnaissance OCR et à chaque modification de la facture.
    """,
    'author': 'Custom',
    'depends': ['account'],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
