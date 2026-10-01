# Vérifications de cette livraison

## Exécuté

- Connexion authentifiée au site source via le coffre-fort ; aucune écriture de configuration demandée à Odoo.
- Version source lue : `19.0+e`.
- Extraction du rapport, des 61 lignes, 60 expressions, une colonne, des schémas et des correspondances fiscales.
- Vérification des 46 noms de tags par nom/pays/applicabilité.
- Génération du module depuis les fichiers extraits, sans reconstruction manuelle des formules.
- Exécution de `validate_module.py` : **11 tests réussis**, dont un contrôle de non-régression excluant le champ optionnel `filter_cash_basis` absent de la cible (structure, compilation Python, schéma, références XML, hiérarchie, expressions, graphe des agrégations, noupdate, tags, différences déclarées).

## Non exécuté / à faire

- Installation sur une base Odoo 19 Enterprise de test.
- Tests ORM `tests/test_monaco_report.py` fournis dans le module.
- Test d'affichage du nouveau rapport, export PDF/Excel et validation chiffrée.
- Correspondances de taxes et reprise des valeurs externes sur l'instance cible.
- Validation fiscale du pays France, du calcul de base à 20 % et du moteur de report de crédit source.

Aucun serveur Odoo Enterprise de test n'était disponible dans l'environnement local. Les tests hors Odoo ne permettent pas d'annoncer le module comme validé en production.

La session navigateur source a expiré pendant la génération locale. Aucun appel de création, modification, suppression ou installation n'a été effectué dans La Pampa ; la relecture finale supplémentaire n'a pas pu être faite sans réauthentification.
