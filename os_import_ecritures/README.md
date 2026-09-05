# Import d'écritures comptables (format tabulé)

Module Odoo 19 ajoutant un assistant d'import d'écritures comptables depuis
un export texte à 29 colonnes séparées par `;`, sans ligne d'en-tête.

## Installation

Copier le dossier `os_import_ecritures` dans un répertoire d'addons, puis :

    ./odoo-bin -u all -d <base> --addons-path=...,<votre_repertoire>

Ou : Applications → Mettre à jour la liste → rechercher « Import d'écritures ».

## Utilisation

Deux points d'entrée :

- Comptabilité → Comptabilité → **Importer des écritures**
- Bouton **Importer des écritures** sur la fiche d'un journal (le journal est
  alors présélectionné comme journal par défaut)

L'assistant se déroule en trois étapes :

1. **Fichier** — chargement, encodage, séparateur, siècle des dates,
   journal par défaut, création automatique des tiers, comptabilisation.
2. **Correspondances** — récapitulatif de l'analyse (pièces, lignes, période,
   totaux) et trois onglets de mapping : journaux, tiers, comptes introuvables.
   L'import est bloqué tant qu'un compte du fichier n'existe pas dans le plan
   comptable.
3. **Terminé** — nombre de pièces créées, ignorées, comptabilisées, avec accès
   direct à la liste des pièces.

## Format attendu

| Col | Contenu                | Cible Odoo                |
|-----|------------------------|---------------------------|
| 0   | Code journal           | `journal_id` (mappé)      |
| 1   | Date JJMMAA           | `date`                    |
| 2   | Code compte général    | `line_ids/account_id`     |
| 3   | Libellé du compte      | informatif                |
| 4   | Référence de pièce     | `ref` + clé de regroupement |
| 8   | Code tiers             | `partner_id` (mappé)      |
| 11  | Libellé de ligne       | `line_ids/name`           |
| 21  | Débit                  | `line_ids/debit`          |
| 22  | Crédit                 | `line_ids/credit`         |
| 26  | Date d'échéance JJMMAA| `line_ids/date_maturity`  |

Les colonnes restantes sont vides ou constantes dans l'export d'origine et
sont ignorées. Les indices sont définis en tête de
`wizard/import_ecritures.py` : un export d'une autre origine se supporte en
ajustant ces constantes.

## Garanties

- **Équilibre** : chaque pièce est contrôlée avant toute écriture en base.
  Une seule pièce déséquilibrée interrompt l'import complet.
- **Idempotence** : chaque pièce porte une clé `os_import_key` de la forme
  `CODEJOURNAL/REFPIECE`. Rejouer le même fichier ne crée pas de doublons.
  Le filtre « Issues d'un import » de la vue recherche des pièces les isole.
- **Brouillon par défaut** : la comptabilisation est une option explicite.

## Limites connues

- Aucune gestion de la TVA : les écritures sont créées sans ligne de taxe.
  Un fichier source portant de la TVA nécessite une extension.
- Les pièces sont créées en type `entry` (opération diverse), pas en facture
  client. Le lettrage automatique n'est donc pas déclenché.
- Import monodevise : les montants sont repris dans la devise de la société.
