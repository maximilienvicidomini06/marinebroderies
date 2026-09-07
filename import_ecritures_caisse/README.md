# Import écritures de caisse (Odoo 19)

Module d'import des écritures de caisse au format texte « ;-séparé »
(export type Ciel/Sage) dans la comptabilité Odoo.

## Installation
1. Copier le dossier `import_ecritures_caisse` dans votre répertoire d'addons.
2. Redémarrer Odoo et mettre à jour la liste des applications.
3. Installer « Import écritures de caisse ».

## Utilisation
Menu **Comptabilité → Écritures comptables → Import écritures de caisse** :
1. Sélectionner le fichier (`ecritures.txt`).
2. Cocher éventuellement « Comptabiliser automatiquement » (sinon brouillon).
3. Cliquer sur **Importer** → la liste des pièces créées s'ouvre.

## Format du fichier
Une ligne = une ligne d'écriture, colonnes séparées par `;` :

| Colonne | Contenu |
|---------|---------|
| 0 | Code du journal (doit exister dans Odoo, ex. `VTECPT`) |
| 1 | Date de la pièce `JJMMAA` (ex. `150426` = 15/04/2026) |
| 2 | Code du compte (doit exister dans le plan comptable) |
| 3 | Libellé du compte (repli si col. 11 vide) |
| 4 | Référence de la pièce → **critère de regroupement** |
| 8 | Code tiers (optionnel, recherché sur `ref` puis nom du partenaire) |
| 11 | Libellé de la ligne |
| 18 | Sens `D`/`C` |
| 21 / 22 | Montant débit / crédit (virgule décimale) |
| 26 | Date d'échéance `JJMMAA` (optionnelle) |

## Regroupement en pièces
Les lignes sont regroupées en une pièce comptable (`account.move`) par
triplet **(journal, date, référence)**. Chaque pièce est vérifiée
équilibrée (débit = crédit) **avant** toute création : si une pièce est
déséquilibrée, l'import est intégralement annulé.

## Notes
- Les journaux et comptes doivent exister au préalable (aucune création
  automatique).
- Le tiers est optionnel : s'il n'est pas trouvé, la ligne est créée sans
  partenaire (non bloquant).
- Encodages acceptés : UTF-8 (avec ou sans BOM), Windows-1252, Latin-1.
