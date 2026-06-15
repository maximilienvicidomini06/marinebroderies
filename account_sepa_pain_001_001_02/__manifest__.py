# -*- coding: utf-8 -*-
{
    "name": "SEPA Virement pain.001.001.02",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Génère des fichiers de virement SEPA (SCT) au format legacy pain.001.001.02",
    "description": """
Ajoute un bouton "Générer SEPA pain.001.001.02" sur les lots de paiement
sortants (account.batch.payment). Produit un fichier XML conforme au schéma
ISO 20022 / SWIFT pain.001.001.02, pour les banques exigeant encore cette
version legacy non couverte par account_iso20022 (qui ne fournit que .03 / .09).
    """,
    "author": "Open Solution",
    "website": "https://opensolution.mc",
    "license": "LGPL-3",
    "depends": [
        "account_batch_payment",
        "account_iso20022",
    ],
    "data": [
        "views/account_batch_payment_views.xml",
    ],
    "installable": True,
    "application": False,
}
