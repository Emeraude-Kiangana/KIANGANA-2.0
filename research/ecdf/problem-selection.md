# eCDF — Sélection du premier problème congolais

## Décision

eCDF doit commencer par la **preuve et la traçabilité des paiements agricoles effectués par un acheteur ou une coopérative à de petits producteurs en RDC**, dans un contexte où le règlement est aujourd’hui principalement effectué en espèces.

eCDF n’est pas une monnaie, une CBDC, un service bancaire, un opérateur de mobile money ni une infrastructure officielle de la Banque Centrale du Congo. La première version est un prototype technologique de paiement et de preuve.

## Problème formulé

> Comment permettre à une coopérative ou à un acheteur agricole de préparer, simuler et auditer un lot de paiements à des producteurs congolais, avec un reçu vérifiable pour chaque bénéficiaire, sans exposer leurs données personnelles et sans imposer immédiatement une blockchain ou un portefeuille à l’utilisateur final ?

## Pourquoi ce problème

La Banque mondiale rapporte que 81 % des bénéficiaires de revenus agricoles en RDC sont payés uniquement en espèces. Elle associe les paiements numériques à une meilleure traçabilité, à une réduction des risques de vol, à des coûts logistiques plus faibles et à la possibilité de documenter les flux de revenus.

Ce problème satisfait cinq critères :

1. douleur locale documentée ;
2. bénéficiaire et payeur identifiables ;
3. résultat mesurable ;
4. adéquation avec les capacités de paiement de Stellar ;
5. prototype réalisable sans licence financière ni fonds réels.

## Utilisateurs du pilote

- payeur primaire : une coopérative ou un acheteur agricole pilote ;
- bénéficiaires : 10 à 25 producteurs simulés ou volontaires ;
- vérificateur : responsable de la coopérative ou auditeur du pilote ;
- administrateur : équipe eCDF.

## Proposition de valeur V0

- importer un lot de paiements fictifs ;
- vérifier montants, doublons et identifiants pseudonymisés ;
- produire un plan de décaissement déterministe ;
- simuler le règlement via un `SettlementSimulator` ;
- générer un reçu et une preuve d’intégrité par paiement ;
- produire un rapport d’audit du lot ;
- comparer ensuite un adaptateur Stellar Testnet, sans fonds réels.

## Mesures du prototype

| Indicateur | Cible V0 |
|---|---:|
| Paiements simulés | 25 |
| Doublons non détectés | 0 |
| Sommes de contrôle incorrectes | 0 |
| Reçus produits | 100 % |
| Données personnelles écrites on-chain | 0 |
| Transactions mainnet | 0 |
| Temps de génération du rapport | moins de 60 secondes |

## Hors périmètre

- émission d’un « franc congolais numérique » ;
- conservation ou conversion de fonds ;
- KYC de production ;
- promesse de rendement, crédit ou token agricole ;
- intégration réelle à une banque, à la BCC ou à un opérateur mobile money ;
- déploiement Stellar Mainnet.

## Hypothèses à tester sur le terrain

1. Les coopératives ont un problème réel de rapprochement et de preuve des paiements.
2. Les producteurs valorisent davantage le reçu vérifiable que la technologie blockchain elle-même.
3. Une sortie mobile money est plus acceptable qu’un portefeuille crypto imposé.
4. Les données minimales pseudonymisées suffisent à résoudre les litiges courants.

## Architecture V0 recommandée

`Batch CSV → Validation → Plan de paiement → SettlementSimulator → Reçus → Rapport d’audit`

Stellar intervient comme adaptateur expérimental remplaçable après validation du problème, conformément à l’architecture eCDF hybride précédemment décidée.

## Sources

- Banque mondiale, *Digitalizing Agricultural Payments in Sub-Saharan Africa* : https://www.worldbank.org/en/publication/globalfindex/brief/data-from-the-global-findex-2021-digitalizing-agricultural-payments-in-sub-Saharan-africa
- Stellar Developer Documentation : https://developers.stellar.org/
- Stellar Community Fund : https://communityfund.stellar.org/awards
