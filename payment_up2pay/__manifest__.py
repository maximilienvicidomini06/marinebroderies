# -*- coding: utf-8 -*-

{
    "name": "Up2pay e-transactions Payment Provider",
    "category": "Accounting/Payment Providers",
    "version": "19.0.0.0",
    "author": "DevTalents",
    "website": "www.dev-talents.com",
    "summary": "Up2pay e-transactions Payment Provider - Seamlessly integrate Up2Pay for secure and efficient payment processing in Odoo, enhancing the checkout experience with various payment options and real-time transaction management",
    "description": """
        Up2Pay payment gateway / Passerelle de paiement Up2Pay
        Up2Pay integration / Intégration Up2Pay
        Up2Pay API / API Up2Pay
        Up2Pay payment solutions / Solutions de paiement Up2Pay
        Up2Pay checkout process / Processus de paiement Up2Pay
        Up2Pay fees / Frais Up2Pay
        Up2Pay secure payments / Paiements sécurisés Up2Pay
        Up2Pay online payments / Paiements en ligne Up2Pay
        Up2Pay transaction management / Gestion des transactions Up2Pay
        Up2Pay customer support / Support client Up2Pay
        Crédit Agricole payment solutions / Solutions de paiement Crédit Agricole
        Crédit Agricole banking services / Services bancaires Crédit Agricole
        Crédit Agricole online banking / Banque en ligne Crédit Agricole
        Crédit Agricole mobile app / Application mobile Crédit Agricole
        Crédit Agricole credit card / Carte de crédit Crédit Agricole
        Crédit Agricole loan options / Options de prêt Crédit Agricole
        Crédit Agricole investment services / Services d'investissement Crédit Agricole
        Crédit Agricole insurance products / Produits d'assurance Crédit Agricole
        Crédit Agricole customer service / Service client Crédit Agricole
        Crédit Agricole digital banking / Banque digitale Crédit Agricole

    """,
    "depends": ["payment"],
    "external_dependencies": {
        "python": ["pycryptodome", "pycountry"],
        # pip install pycountry
         pip install pycryptodome
    },
    "data": [
        "views/res_country_views.xml",
        "views/payment_up2pay_templates.xml",
        "views/payment_provider_views.xml",
        "data/payment_method_data.xml",
        "data/payment_provider_data.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "installable": True,
    "application": False,
    "price": "180",
    "license": "OPL-1",
    "currency": "EUR",
    "support": "support@dev-talents.com",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
