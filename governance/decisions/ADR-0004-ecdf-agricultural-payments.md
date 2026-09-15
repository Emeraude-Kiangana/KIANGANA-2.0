# ADR-0004 — Premier problème eCDF

- Statut : accepté
- Date : 2026-09-15
- Décideur : Emeraude Kiangana via mission KIA-2026-003

## Décision

Le premier problème eCDF est la traçabilité et la preuve des paiements agricoles d’une coopérative ou d’un acheteur vers de petits producteurs en RDC.

## Conséquences

- eCDF reste un prototype de recherche orienté paiement, pas une CBDC.
- Le premier runtime utilise `SettlementSimulator` et des données fictives ou consenties.
- Stellar est évalué sur Testnet comme adaptateur interchangeable.
- Aucune donnée personnelle n’est inscrite on-chain.
- AGRICHAIN DAO peut devenir ultérieurement un domaine consommateur, sans dépendance structurelle immédiate.

## Alternatives rejetées pour V0

- paiement généraliste national : trop large et institutionnellement risqué ;
- transferts internationaux grand public : concurrence et conformité trop lourdes pour un premier prototype ;
- tokenisation agricole : prématurée avant validation du paiement et de la preuve ;
- paiement universitaire : moins directement relié aux données publiques actuellement disponibles.

