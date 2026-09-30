# 19.0.1.0.1 — Correction de l'installation Odoo.sh

Le registre de l'instance cible rejette `account.report.filter_cash_basis`, bien que ce champ soit présent dans le schéma source La Pampa. La définition XML ne transmet plus ce champ optionnel, dont la valeur source était False. Aucune formule, ligne, colonne, référence XML ou hiérarchie n'est modifiée.

Le générateur a également été corrigé ; il refusera désormais un export où cette option serait activée plutôt que de l'ignorer silencieusement.

Le test de non-régression échoue sur le module initial et passe sur cette version. Les 11 tests hors Odoo passent. Le schéma complet de la destination n'a pas été interrogé : cette correction répond au champ identifié dans la trace et ne constitue pas une validation d'installation complète.

## Déploiement après échec de première installation

Remplacer le dossier `opsol_monaco_tax_report` dans le dépôt de la branche de test Odoo.sh par celui du nouveau ZIP. Conserver son nom technique. Commit/push, attendre la reconstruction réussie, puis relancer Installer dans Applications. Ne pas désinstaller ni supprimer manuellement de données pour ce correctif.

Le test d'installation Enterprise, le rendu et la recette fiscale restent à exécuter sur la destination. Le rapport de vérification conserve les limites de la livraison initiale.
