# Configuration Kibana - Visualisation des avis Trustpilot

## Accès
- URL: http://localhost:5601
- Pas d'authentification requise (mode dev)

## Créer l'index pattern

1. Aller dans **Stack Management** > **Index Patterns**
2. Cliquer **Create index pattern**
3. Entrer: `trustpilot_reviews*`
4. Sélectionner `date` comme champ temporel
5. Cliquer **Create**

## Dashboards recommandés

### 1. Distribution des ratings
- Type: **Pie chart**
- Metric: Count
- Bucket: Terms sur `rating`

### 2. Avis par entreprise
- Type: **Bar chart horizontal**
- Metric: Count
- Bucket: Terms sur `company.keyword`, Top 20

### 3. Timeline des avis
- Type: **Line chart**
- Metric: Count
- X-axis: Date histogram sur `date`

### 4. Recherche full-text
- Utiliser la barre de recherche Kibana
- Exemple: `content:livraison AND rating:1`

## Requêtes utiles

### Avis négatifs récents
```
rating:[1 TO 2] AND date:[now-7d TO now]
```

### Mentions de "livraison"
```
content:livraison OR title:livraison
```

### Avis d'une entreprise spécifique
```
company:"Amazon" AND rating:5
```

## Export des données

1. Discover > Sélectionner les champs
2. Share > CSV Reports
3. Télécharger le fichier
