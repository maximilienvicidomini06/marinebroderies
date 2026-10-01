# Déclaration Monaco — module personnalisable Odoo 19

## Statut

Ce module contient la définition réellement extraite de « Tax Report (Monaco Declaration) » dans La Pampa, sur Odoo **19.0 Enterprise**. Il ne contient pas d'écritures comptables, de mots de passe, de comptes utilisateurs ou d'identifiants de base à réutiliser.

**61 lignes, 60 expressions, 1 colonne, 46 noms d'étiquettes fiscales.** Les calculs et libellés du rapport source sont conservés. Les libellés sont majoritairement anglais dans la source, y compris dans le contexte français.

Les contrôles hors Odoo vérifient la structure XML, les champs contre le schéma source, les références, la hiérarchie et la fidélité des expressions. **Une installation et une recette sur une base Odoo 19 Enterprise de test restent obligatoires. Ce module n'est pas une certification fiscale.**

## Prérequis

- Odoo 19 Enterprise sur Odoo.sh ou serveur privé.
- Addon Enterprise `account_reports` accessible et licence Odoo correspondante.
- Configuration comptable appropriée pour chaque société cible.
- Administrateur pour l'installation ; responsable comptable pour la configuration.

Odoo Community seul ne fournit pas le moteur Enterprise requis. Aucun accès à La Pampa n'est nécessaire après installation.

## Installation

### Odoo.sh

1. Décompresser ce ZIP et ajouter le dossier `opsol_monaco_tax_report` au dépôt d'addons du projet.
2. Tester d'abord dans une branche de développement/staging.
3. Actualiser la liste des applications en mode développeur.
4. Enlever le filtre « Applications », rechercher « OpenSolution — Déclaration Monaco personnalisable », puis installer.
5. Suivre la recette ci-dessous avant tout déploiement en production.

### Serveur privé

Placer le dossier dans un répertoire déclaré dans `addons_path`, puis exécuter avec la configuration de **test** adaptée :

```bash
odoo-bin -c /chemin/odoo-test.conf -d BASE_TEST -i opsol_monaco_tax_report --test-enable --test-tags /opsol_monaco_tax_report --stop-after-init
```

Cette commande installe le module et exécute ses tests d'intégration ; elle n'a pas été exécutée par le générateur du ZIP faute de serveur Enterprise de test disponible.

## Accès et personnalisation

- **Comptabilité → Reporting → Taxes et fiscalité → Déclaration Monaco — personnalisable** : affichage du rapport.
- **Comptabilité → Configuration → Comptabilité → Reporting → Déclaration Monaco — configuration** : définition du rapport, selon la traduction et l'organisation des menus Odoo.
- En mode développeur, le rapport est aussi présent dans la liste des rapports comptables.

Les responsables comptables peuvent modifier les noms, les lignes, la hiérarchie, les colonnes, les moteurs de calcul, les formules, les filtres et les options du moteur natif. Une présentation PDF totalement spécifique nécessitera un développement QWeb supplémentaire : le module utilise pour l'instant le rendu PDF/Excel natif d'Odoo.

Les définitions sont chargées avec `noupdate="1"` : une mise à jour normale du module ne remet pas à zéro les personnalisations faites dans chaque base. Les menus/actions restent maintenus lors des mises à jour. Une évolution future des données livrées devra passer par une migration explicite ; une simple modification du XML ne mettra pas à jour les enregistrements déjà installés.

## Ce qui est conservé et ce qui change

Conservé : toutes les lignes, colonnes, expressions, signes des formules, cibles de report, hiérarchies et options exportées. Le rapport reste une variante du rapport générique de taxes (`account.generic_tax_report`). Les références locales sont remplacées par des identifiants XML propres au module.

Différences délibérées :

1. Nom distinct : **Déclaration Monaco — personnalisable**. Le rapport source n'est pas modifié.
2. Période d'ouverture : **mois précédent**, au lieu de « période de déclaration précédente ». Cela permet l'ouverture sans créer de procédure de déclaration fiscale.
3. Le type de déclaration `VAT (MC)` et son automatisation présents sur La Pampa ne sont **pas** installés. Le module crée un modèle de rapport, pas une procédure de dépôt/paiement de TVA. Un rattachement à un type de déclaration et son calendrier devront être configurés séparément si nécessaire.
4. Les montants manuels, crédits historiques et valeurs externes ne sont pas exportés. Ils devront être repris séparément et validés pour chaque société.

## Attention : pays et étiquettes fiscales

Le rapport source porte le nom « Monaco », mais son pays est **France**. Le module conserve `base.fr` intentionnellement : en Odoo 19, une expression « Étiquettes fiscales » recherche les tags par **nom sans signe initial et pays**. Remplacer simplement France par Monaco changerait les tags utilisés et pourrait produire un rapport vide ou différent.

La création des expressions par Odoo réutilise les étiquettes existantes correspondantes et crée celles qui manquent. **Elle n'affecte pas automatiquement ces étiquettes aux taxes ou aux écritures de la base cible.** Le module n'écrit ni dans `account.tax`, ni dans `account.tax.repartition.line`, ni dans `account.move.line`.

Le fichier `docs/tax_mapping_reference.csv` décrit les correspondances constatées à la source, incluant des taxes archivées. C'est une référence pour contrôle, **pas un import automatique** et pas une prescription fiscale. Les noms de taxes ne sont pas des clés fiables : il faut vérifier société, usage achat/vente, taux, base/taxe, facture/avoir, facteur et contexte fiscal. Ne pas appliquer ce tableau aveuglément.

Sur une autre base, le rapport ne sera juste qu'après validation de ces correspondances. Les tags déjà présents dans d'autres rapports peuvent être partagés. Modifier une formule de tag, son pays, supprimer une expression ou désinstaller le module peut avoir des effets sur ces tags via le moteur natif Odoo : faire ces opérations uniquement après sauvegarde et essai sur une copie.

## Point fiscal non corrigé : crédit à reporter

La ligne `box_29` possède une expression :

- libellé `_carryover_balance` ;
- moteur `tax_tags` ;
- formule `box_29.balance` ;
- cible `box_20._applied_carryover_balance`.

Cette configuration a été conservée **exactement**. Avec ce moteur, la formule désigne un nom de tag, pas une référence d'agrégation. Le tag portant littéralement `box_29.balance` existe à la source. Si l'intention est de reporter le montant calculé de la ligne 29, ce moteur mérite une validation et probablement une correction par le responsable comptable. Aucune correction n'a été appliquée sans décision explicite.

Autre règle source à valider pour chaque client : la base à 20 % est calculée par différence (`C_A1.balance - box_32bs.balance - box_32bm.balance`), puis multipliée par `0.2`. Ce n'est pas une lecture directe de toutes les taxes à 20 % et cela dépend de la composition des opérations.

## Recette obligatoire sur une base de test

1. Installer le module et lancer les tests d'intégration fournis ; conserver le journal.
2. Vérifier les 61 lignes, 60 expressions, une colonne et les menus.
3. Vérifier le pays fiscal et l'accès au rapport pour chaque société autorisée.
4. Rapprocher les tags des répartitions de taxes, en distinguant facture/avoir et base/montant de TVA. Ne pas remplacer les autres tags sans analyse.
5. Tester les ventes 5,5 %, 10 % et 20 %, les achats, immobilisations, avoirs, opérations intracommunautaires et régularisations réellement utilisées par le client.
6. Comparer chaque ligne et les totaux avec un calcul de référence validé ; un rapport sans erreur technique peut néanmoins être fiscalement incorrect.
7. Vérifier les écritures brouillon/comptabilisées, la TVA exigible, les périodes, les sociétés, les montants manuels et crédits antérieurs.
8. Valider explicitement la logique de report de crédit décrite ci-dessus.
9. Tester PDF, Excel et accès au détail ; aucun formulaire officiel de télétransmission n'est fourni.
10. Modifier un libellé puis mettre à jour le module sur la base de test : la personnalisation doit rester en place.

## Désinstallation et confidentialité

Sauvegarder avant désinstallation : les personnalisations des enregistrements appartenant au module seront perdues. Vérifier les effets du moteur Odoo sur les tags partagés avant suppression. Les valeurs externes et déclarations éventuellement créées ensuite doivent être prises en compte.

Le ZIP ne contient que le module, son contrat de tests portable et la table de correspondance des taxes. L'export technique brut demeure séparé dans le dossier de travail et ne doit pas être ajouté à un dépôt public.
