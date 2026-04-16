# Hypothèses & limites du projet

## Objectif du projet

Ce dépôt a été conçu comme une démonstration portfolio d’un pipeline d’analytics opérationnel inspiré d’un réseau McDonald’s.

Son objectif est de montrer :
- la structuration de données
- la logique de simulation de la demande
- le raisonnement stock / réapprovisionnement
- la création d’indicateurs décisionnels
- la traduction business via dashboard

Ce projet n’est pas un outil de décision prêt pour la production.

---

## 1. Hypothèses sur les données

### Données simulées / reconstruites
Les données utilisées dans ce projet ne proviennent pas d’un export certifié d’un système réel de caisse, d’ERP ou de supply chain.

Certaines données ont été :
- structurées manuellement
- reconstruites à partir de la logique du fichier source
- simplifiées pour la démonstration
- enrichies pour permettre un pipeline complet de bout en bout

### Périmètre de la simulation
Le projet se concentre sur un réseau de 2 restaurants à Dreux :
- S001 — Centre-ville
- S002 — Haut de la ville

Ce périmètre réduit a été choisi pour garder un projet lisible tout en montrant une logique multi-sites.

### Structure produits / composants
Les relations entre produits finis, recettes et composants sont une version simplifiée de la manière dont un restaurant de restauration rapide consomme ses ingrédients, emballages et consommables.

Elles sont suffisantes pour démontrer :
- la propagation de la demande des ventes vers les composants
- la pression stock par composant
- la priorisation des besoins de réapprovisionnement

En revanche, elles ne reflètent pas toute la complexité réelle d’un environnement QSR.

---

## 2. Hypothèses sur le forecasting

### Logique de demande simplifiée
La couche de forecasting repose sur une logique de ventes simulées et sur des règles métier, et non sur un modèle statistique ou machine learning avancé entraîné sur de vraies séries temporelles.

La demande simulée reflète des schémas simplifiés comme :
- les effets heure de la journée
- les variations journalières
- les différences entre restaurants
- les pics de service

### Absence de variables externes
La logique actuelle n’intègre pas explicitement :
- la météo
- les promotions
- les actions concurrentes
- le calendrier scolaire
- les jours fériés
- les événements locaux
- l’impact des plateformes de livraison

Dans un vrai déploiement, ces variables influenceraient fortement la demande.

### Interprétation des prévisions
Les outputs de forecast doivent être interprétés comme des estimations opérationnelles servant la démonstration du moteur de réapprovisionnement, et non comme des prévisions commerciales auditées.

---

## 3. Hypothèses sur le stock

### Logique de réapprovisionnement par règles
La simulation de stock et les recommandations d’achat sont fondées sur une logique simple basée sur des règles, par exemple :
- seuil de réapprovisionnement
- logique de couverture
- niveau d’urgence
- quantité recommandée à commander

Cela permet d’obtenir une logique claire, lisible et explicable.

### Délais d’approvisionnement supposés stables
Les délais fournisseurs, contraintes de livraison et aléas d’approvisionnement sont supposés stables.

En pratique, les décisions de réapprovisionnement dépendraient aussi de :
- l’heure limite de commande
- la quantité minimale d’achat
- la fréquence de livraison
- la disponibilité fournisseur
- la chaîne du froid
- la capacité de stockage

### Logique de stockage simplifiée
Les zones de stockage comme sec, froid ou négatif sont représentées de manière simplifiée afin d’introduire une logique opérationnelle, sans modéliser toute la réalité terrain.

---

## 4. Hypothèses sur les recommandations

### Logique orientée achat
Le moteur de recommandation suggère aujourd’hui principalement des achats lorsque le stock projeté devient risqué.

Ce choix a été fait volontairement pour la démonstration, car les achats sont plus faciles à tracer, agréger et visualiser.

### Pas encore de logique de transfert inter-sites
Le projet ne modélise pas encore une logique avancée de transfert de stock entre S001 et S002.

Pourtant, dans un cas réel où les deux restaurants appartiennent au même franchisé, une partie des tensions pourrait être résolue via :
- des transferts inter-restaurants
- une mutualisation de certains composants
- une réduction des achats inutiles
- une meilleure allocation du stock existant

C’est donc une piste d’amélioration stratégique importante du projet.

### Pas d’optimisation économique complète
Les recommandations ne prennent pas encore en compte une optimisation complète entre :
- coût d’achat
- coût de rupture
- coût de surstock
- coût de perte / DLC
- arbitrage entre achat et transfert

Le moteur actuel doit donc être lu comme un démonstrateur d’aide à la décision, pas comme un optimiseur final.

---

## 5. Hypothèses sur les dashboards

### Dashboard de démonstration
Les dashboards produits dans le projet ont un objectif de visualisation, de synthèse et de mise en valeur des compétences.

Ils servent à répondre à des questions comme :
- quels restaurants génèrent le plus de chiffre d’affaires ?
- à quelles heures se concentre la demande ?
- quels produits tirent le volume et le revenu ?
- quels composants créent le plus de tension stock ?
- quelles recommandations nécessitent une action prioritaire ?

### Pas de pilotage temps réel
Les dashboards ne sont pas connectés à un flux live ou à un environnement BI de production.

Ils reflètent une photographie analytique basée sur les fichiers générés par le pipeline.

---

## 6. Limites générales du projet

### Fiabilité partielle des données
Les données de ce projet ne doivent pas être interprétées comme 100 % exactes, exhaustives ou directement exploitables pour prendre une décision d’achat réelle.

Le projet a surtout été conçu pour démontrer :
- une méthode
- une logique analytique
- une capacité à structurer un pipeline
- une capacité à transformer de la donnée en raisonnement opérationnel

### Démonstration de compétences avant tout
Ce projet montre surtout des compétences en :
- Python
- pandas
- structuration de pipeline
- logique business
- simulation opérationnelle
- visualisation
- restitution analytique

Il s’agit donc d’un cas de démonstration crédible, mais pas d’un jumeau exact d’un système McDonald’s réel.

### Ce qu’il faudrait pour passer en environnement réel
Pour un vrai déploiement, il faudrait notamment :
- des données transactionnelles réelles
- des historiques plus longs
- des règles fournisseurs réelles
- des lead times validés
- des stocks initiaux fiables
- des coûts à jour
- une logique de transfert inter-sites
- un vrai moteur de forecast
- une validation métier avec les équipes opérationnelles

---

## 7. Améliorations possibles

Prochaines évolutions pertinentes :
- intégrer une logique de transfert de stock entre restaurants
- ajouter de vraies variables externes à la demande
- remplacer la logique actuelle par un modèle de forecast plus robuste
- mieux distinguer achat recommandé vs transfert recommandé
- intégrer une logique de coût complet
- connecter le projet à Power BI, Streamlit ou un environnement cloud pour une restitution plus professionnelle

---

## Conclusion

Ce projet doit être compris comme une démonstration structurée de compétences data / ops / supply, construite sur des hypothèses simplifiées mais cohérentes.

L’objectif n’était pas de produire un outil de production prêt à l’emploi, mais de montrer la capacité à :
- structurer des données
- modéliser une logique métier
- simuler des scénarios opérationnels
- produire des indicateurs utiles
- transformer un cas métier en projet analytique lisible et crédible