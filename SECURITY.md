# Politique de sécurité

## Secrets

- Ne jamais versionner clés API, jetons, mots de passe, clés privées ou données KYC.
- Utiliser les secrets du fournisseur d’exécution ou un gestionnaire dédié.
- Fournir seulement des fichiers `.env.example` sans valeur réelle.
- Révoquer immédiatement tout secret exposé et documenter l’incident.

## Actions interdites par défaut

- transaction financière ou blockchain réelle ;
- publication publique ou envoi à un tiers ;
- suppression irréversible ;
- changement d’identité, de permissions ou de facturation ;
- déploiement en production.

Ces actions exigent un contrat de mission explicite et une validation humaine P4 ou P5.

## Signalement

Créer une mission privée de type `security-incident`; ne jamais publier une vulnérabilité ou un secret dans une issue publique.

