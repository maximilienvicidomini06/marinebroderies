# account_invoice_ttc_no_tax

## Objectif

Ce module Odoo 19 convertit automatiquement les lignes de factures fournisseurs :
- **Avant** : Prix HT + TVA (ex: 100€ HT + 20% TVA = 120€ TTC)
- **Après** : Prix TTC sans TVA (ex: 120€ HT, 0% TVA = 120€ TTC)

Cela permet de comptabiliser des factures fournisseurs au prix TTC sans appliquer de TVA déductible.

## Installation

1. Copier le dossier `account_invoice_ttc_no_tax` dans le répertoire `addons` de votre Odoo
2. Mettre à jour la liste des modules : **Paramètres → Activer le mode développeur → Mettre à jour la liste des applications**
3. Rechercher `Facture Fournisseur : Prix TTC sans TVA` et cliquer sur **Installer**

## Fonctionnement

La conversion est déclenchée à **trois niveaux** :

| Déclencheur | Méthode | Cas d'usage |
|---|---|---|
| `create()` | `AccountMove.create` | Création via import/API |
| `write()` | `AccountMove.write` | Modification des lignes (OCR) |
| `_post()` | `AccountMove._post` | Confirmation de la facture |
| `onchange` | `AccountMoveLine` | Saisie manuelle en interface |

## Suppression de l'action automatisée

Une fois ce module installé, l'action automatisée précédemment créée peut être **désactivée ou supprimée** — elle est remplacée par ce module.

## Compatibilité

- Odoo 19
- Compatible Odoo 17 / 18 avec ajustements mineurs éventuels
