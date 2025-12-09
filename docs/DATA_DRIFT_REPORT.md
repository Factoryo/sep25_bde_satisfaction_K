# Rapport de Dérive des Données (Data Drift)

**Date générée** : 7 décembre 2025  
**Période analysée** : Données de scraping Trustpilot (60 entreprises, 	82 410 avis)

---

## 1. Contexte

Le data drift (dérive des données) se produit lorsque la distribution des données d'entrée change au fil du temps. Cela peut dégrader les performances du modèle de ML si les nouvelles données diffèrent trop de celles utilisées pour l'entraînement.

### Méthode de détection
- **Test statistique** : Kolmogorov-Smirnov (KS)
- **Seuil d'alerte** : p-value < 0.05
- **Fréquence de vérification** : Quotidienne (via DAG Airflow)

---

## 2. Analyse de la distribution des ratings

### Distribution actuelle

| Rating | Nombre d'avis | Pourcentage |
|--------|---------------|-------------|
| 1 ⭐   | 43 969        | 55.5%       |
| 2 ⭐   | 7 237         | 9.1%        |
| 3 ⭐   | 5 893         | 7.4%        |
| 4 ⭐   | 5 766         | 7.3%        |
| 5 ⭐   | 16 338        | 20.6%       |

### Observation
La distribution est **fortement déséquilibrée** vers les avis négatifs (1★ = 55.5%). C'est normal sur Trustpilot car les clients mécontents sont plus enclins à laisser un avis.

### Risque de drift
⚠️ **Risque modéré** : Si la proportion d'avis positifs augmente significativement (ex: campagne marketing), le modèle pourrait être moins performant sur ces nouvelles données.

---

## 3. Analyse des sentiments

### Distribution des classes après labellisation

| Sentiment | Nombre | Pourcentage |
|-----------|--------|-------------|
| Négatif   | 51 206 | 64.6%       |
| Positif   | 22 104 | 27.9%       |
| Neutre    | 5 893  | 7.4%        |

### Mapping utilisé
- **Négatif** : 1-2 étoiles
- **Neutre** : 3 étoiles
- **Positif** : 4-5 étoiles

---

## 4. Métriques du modèle

### Performance sur le jeu de test

| Métrique  | Score |
|-----------|-------|
| Accuracy  | 0.938 |
| Precision | 0.936 |
| Recall    | 0.938 |
| F1-Score  | 0.935 |

### Performance par classe

| Classe  | Precision | Recall | F1-Score | Support |
|---------|-----------|--------|----------|---------|
| Négatif | 0.83      | 0.60   | 0.69     | 1 179   |
| Neutre  | 0.95      | 0.98   | 0.96     | 10 241  |
| Positif | 0.93      | 0.93   | 0.93     | 4 421   |

### Observation
Le modèle a le plus de difficulté avec la classe "Négatif" (recall = 0.60). Cela peut être dû au déséquilibre des classes.

---

## 5. Indicateurs de drift à surveiller

### Variables critiques

1. **Distribution des ratings**
   - Baseline : 55.5% avis 1★
   - Seuil d'alerte : variation > 10%

2. **Longueur moyenne des textes**
   - Baseline : ~150 caractères
   - Seuil d'alerte : variation > 20%

3. **Top mots-clés**
   - Surveiller l'apparition de nouveaux termes (nouveaux produits, problèmes)

### Fréquence de monitoring
- **Quotidien** : Distribution des ratings (automatisé via Airflow)
- **Hebdomadaire** : Analyse des mots-clés
- **Mensuel** : Ré-évaluation des performances du modèle

---

## 6. Actions recommandées

### En cas de drift détecté

1. **Drift léger (p-value entre 0.01 et 0.05)**
   - Continuer à monitorer
   - Documenter le changement

2. **Drift modéré (p-value < 0.01)**
   - Analyser les nouvelles données
   - Évaluer les performances sur un échantillon récent
   - Considérer un ré-entraînement partiel

3. **Drift sévère (performances dégradées > 10%)**
   - Ré-entraînement complet du modèle
   - Mise à jour du vectorizer TF-IDF
   - Revue du pipeline de features

---

## 7. Script de monitoring

Le script `scripts/ml/data_drift_monitor.py` permet de :
- Charger les données depuis Elasticsearch
- Comparer les distributions (test KS)
- Générer des visualisations
- Alerter si drift détecté

### Exécution manuelle
```bash
python scripts/ml/data_drift_monitor.py
```

### Exécution automatisée
DAG Airflow : `ml_monitoring.py` (tous les jours à 3h)

---

## 8. Conclusion

Le modèle actuel (Logistic Regression, F1=0.935) est performant et stable. Le monitoring quotidien permettra de détecter rapidement tout changement dans la distribution des données.
