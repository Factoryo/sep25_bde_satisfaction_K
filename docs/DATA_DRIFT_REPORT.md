# Rapport Data Drift

Dernière mise à jour : 7 décembre 2025

## C'est quoi le data drift ?

Quand les nouvelles données sont trop différentes de celles utilisées pour entraîner le modèle, les prédictions peuvent devenir moins fiables. C'est ce qu'on appelle le "drift".

Pour le détecter, j'utilise le test de Kolmogorov-Smirnov qui compare les distributions.

## Distribution actuelle des avis (82 410 avis)

| Rating | Nombre | % |
|--------|--------|---|
| 1★ | 43 969 | 55.5% |
| 2★ | 7 237 | 9.1% |
| 3★ | 5 893 | 7.4% |
| 4★ | 5 766 | 7.3% |
| 5★ | 16 338 | 20.6% |

C'est déséquilibré vers les avis négatifs, ce qui est normal sur Trustpilot (les gens mécontents écrivent plus).

## Performance du modèle

| Métrique | Score |
|----------|-------|
| F1-Score | 0.935 |
| Accuracy | 0.938 |

Le modèle galère un peu sur les avis négatifs (recall = 0.60), probablement à cause du déséquilibre.

## Ce que je surveille

- **Distribution des notes** : si y'a soudainement plus d'avis positifs (genre campagne marketing), faut ré-entraîner
- **Longueur des textes** : si les gens écrivent beaucoup plus long/court qu'avant
- **Nouveaux mots-clés** : apparition de termes liés à des nouveaux problèmes

## Comment lancer le monitoring

```bash
python scripts/ml/data_drift_monitor.py
```

Ou automatiquement via le DAG Airflow `ml_monitoring.py` (tous les jours à 3h).

## Que faire si drift détecté ?

1. **P-value entre 0.01 et 0.05** → Surveiller, rien de grave
2. **P-value < 0.01** → Analyser les nouvelles données, peut-être ré-entraîner
3. **Performances en baisse de +10%** → Ré-entraînement complet
