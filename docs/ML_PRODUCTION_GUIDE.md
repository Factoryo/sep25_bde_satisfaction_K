# Guide de Mise en Production - ML API

Ce guide décrit le processus complet pour déployer les modèles de Machine Learning en production.

## 📋 Vue d'ensemble

Le système de production ML comprend :
- **Notebook ML** : Entraînement et sauvegarde des modèles (`notebooks/sentiment_analysis.ipynb`)
- **ML API** : Service FastAPI pour les prédictions (`api/ml_api.py`)
- **Data Drift Monitor** : Surveillance de la qualité des données (`scripts/ml/data_drift_monitor.py`)
- **Docker** : Conteneurisation et déploiement

## 🚀 Étapes de Déploiement

### Étape 1: Entraîner et Sauvegarder les Modèles

1. **Ouvrir le notebook Jupyter**
   ```bash
   jupyter notebook notebooks/sentiment_analysis.ipynb
   ```

2. **Exécuter toutes les cellules** jusqu'à la cellule 22 (conclusion)
   - Chargement des 21,795 reviews depuis Elasticsearch
   - Nettoyage et prétraitement du texte
   - Vectorisation TF-IDF
   - Entraînement de 3 modèles (Logistic Regression, Naive Bayes, Random Forest)
   - Évaluation des performances

3. **Exécuter la cellule 24 - Sauvegarde des modèles**
   
   Cette cellule crée automatiquement :
   ```
   scripts/ml/models/
   ├── sentiment_model_best.pkl          # Meilleur modèle (pour production)
   ├── tfidf_vectorizer.pkl              # Vectoriseur TF-IDF
   ├── logistic_regression_YYYYMMDD_HHMMSS.pkl
   ├── naive_bayes_YYYYMMDD_HHMMSS.pkl
   ├── random_forest_YYYYMMDD_HHMMSS.pkl
   └── models_metadata.json              # Métriques et métadonnées
   ```

4. **Vérifier les fichiers générés**
   ```powershell
   ls scripts/ml/models/
   ```

   Vous devriez voir :
   - ✅ `sentiment_model_best.pkl` (~2-5 MB)
   - ✅ `tfidf_vectorizer.pkl` (~1-3 MB)
   - ✅ `models_metadata.json` (quelques KB)

5. **Examiner les métadonnées**
   ```powershell
   cat scripts/ml/models/models_metadata.json
   ```

   Contenu typique :
   ```json
   {
     "best_model": "LogisticRegression",
     "f1_score": 0.87,
     "training_date": "2024-12-04T15:30:00",
     "dataset_size": 21795,
     "n_features": 5000,
     "models_performance": {
       "LogisticRegression": {"f1": 0.87, "precision": 0.88, "recall": 0.86},
       "MultinomialNB": {"f1": 0.82, "precision": 0.81, "recall": 0.83},
       "RandomForest": {"f1": 0.84, "precision": 0.85, "recall": 0.83}
     },
     "sentiment_distribution": {
       "positif": 0.65,
       "negatif": 0.20,
       "neutre": 0.15
     }
   }
   ```

### Étape 2: Tester l'API ML en Local

1. **Installer les dépendances ML**
   ```bash
   pip install -r api/requirements_ml.txt
   ```

2. **Lancer l'API en mode développement**
   ```bash
   cd api
   uvicorn ml_api:app --reload --port 8001
   ```

   Logs attendus :
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Chargement du meilleur modèle...
   INFO:     ✓ Modèle chargé: LogisticRegression
   INFO:     ✓ Vectoriseur chargé
   INFO:     ✓ Métadonnées chargées
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8001
   ```

3. **Tester le health check**
   ```bash
   curl http://localhost:8001/health
   ```

   Réponse attendue :
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "model_name": "LogisticRegression",
     "timestamp": "2024-12-04T15:35:00"
   }
   ```

4. **Tester une prédiction simple**
   ```bash
   curl -X POST http://localhost:8001/api/ml/predict \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Excellent service, livraison rapide et produit conforme!",
       "title": "Très satisfait"
     }'
   ```

   Réponse attendue :
   ```json
   {
     "sentiment": "positif",
     "confidence": 0.92,
     "probabilities": {
       "positif": 0.92,
       "negatif": 0.05,
       "neutre": 0.03
     },
     "cleaned_text": "excellent service livraison rapide produit conforme"
   }
   ```

5. **Tester les métadonnées du modèle**
   ```bash
   curl http://localhost:8001/api/ml/model-info
   ```

6. **Tester une prédiction batch**
   ```bash
   curl -X POST http://localhost:8001/api/ml/predict-batch \
     -H "Content-Type: application/json" \
     -d '{
       "reviews": [
         {"text": "Service excellent!", "title": "Top"},
         {"text": "Très déçu, produit défectueux", "title": "Mauvais"},
         {"text": "Correct sans plus", "title": "OK"}
       ]
     }'
   ```

### Étape 3: Déployer avec Docker

1. **Vérifier que les modèles existent**
   ```bash
   ls scripts/ml/models/sentiment_model_best.pkl
   ls scripts/ml/models/tfidf_vectorizer.pkl
   ```

2. **Build l'image Docker de l'API ML**
   ```bash
   docker-compose build ml-api
   ```

   Sortie attendue :
   ```
   Building ml-api
   Step 1/10 : FROM python:3.11-slim
   ...
   Successfully built abcd1234efgh
   Successfully tagged sep25_bde_satisfaction_k_ml-api:latest
   ```

3. **Lancer tous les services (incluant ML API)**
   ```bash
   docker-compose up -d
   ```

   Services démarrés :
   - ✅ postgres (port 5432)
   - ✅ elasticsearch (port 9200)
   - ✅ kibana (port 5601)
   - ✅ api (port 8000)
   - ✅ ml-api (port 8001)
   - ✅ dashboard (port 8502)

4. **Vérifier les logs de l'API ML**
   ```bash
   docker-compose logs ml-api
   ```

   Rechercher :
   ```
   ✓ Modèle chargé: LogisticRegression
   ✓ Vectoriseur chargé
   ✓ Métadonnées chargées
   ```

5. **Tester l'API dans Docker**
   ```bash
   curl http://localhost:8001/health
   curl -X POST http://localhost:8001/api/ml/predict \
     -H "Content-Type: application/json" \
     -d '{"text": "Service excellent!", "title": "Top"}'
   ```

### Étape 4: Configurer le Monitoring Data Drift

1. **Tester le script de monitoring**
   ```bash
   python scripts/ml/data_drift_monitor.py
   ```

   Le script va :
   - Charger toutes les reviews depuis Elasticsearch
   - Séparer en données de référence (70%) et courantes (30%)
   - Analyser les dérives de distribution (ratings, longueur texte, entreprises)
   - Générer des visualisations
   - Créer un rapport JSON

2. **Examiner les résultats**
   ```bash
   ls docs/data_drift_reports/
   ```

   Fichiers générés :
   - `data_drift_report_YYYYMMDD_HHMMSS.json`
   - `drift_visualization_YYYYMMDD_HHMMSS.png`

3. **Lire le rapport**
   ```bash
   cat docs/data_drift_reports/data_drift_report_*.json
   ```

4. **Automatiser le monitoring (optionnel)**
   
   Ajouter un DAG Airflow pour exécution quotidienne :
   ```python
   # airflow/dags/data_drift_monitoring.py
   from airflow import DAG
   from airflow.operators.bash import BashOperator
   from datetime import datetime, timedelta

   default_args = {
       'owner': 'data_team',
       'depends_on_past': False,
       'start_date': datetime(2024, 12, 1),
       'retries': 1,
       'retry_delay': timedelta(minutes=5),
   }

   dag = DAG(
       'data_drift_monitoring',
       default_args=default_args,
       description='Daily data drift detection',
       schedule_interval='@daily',
       catchup=False
   )

   monitor_task = BashOperator(
       task_id='run_drift_monitor',
       bash_command='python /app/scripts/ml/data_drift_monitor.py',
       dag=dag
   )
   ```

## 📊 Architecture de Production

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐        ┌──────────────┐                 │
│  │   API Data   │        │   ML API     │                 │
│  │  Port 8000   │        │  Port 8001   │                 │
│  │              │        │              │                 │
│  │ - /api/stats │        │ - /predict   │                 │
│  │ - /api/reviews│       │ - /model-info│                 │
│  │ - /api/companies│     │ - /health    │                 │
│  └──────┬───────┘        └──────┬───────┘                 │
│         │                       │                          │
│         │                       │ loads                    │
│         │                       ▼                          │
│         │              ┌──────────────┐                   │
│         │              │   ML Models  │                   │
│         │              │  (.pkl files)│                   │
│         │              └──────────────┘                   │
│         │                                                  │
│         ▼                       ▲                          │
│  ┌──────────────┐              │                          │
│  │ Elasticsearch│              │ monitors                 │
│  │  Port 9200   │              │                          │
│  │              │       ┌──────┴───────┐                 │
│  │ 21,795 reviews│      │ Data Drift   │                 │
│  └──────────────┘       │  Monitor     │                 │
│                          │  (daily)     │                 │
│  ┌──────────────┐       └──────────────┘                 │
│  │  PostgreSQL  │                                         │
│  │  Port 5432   │                                         │
│  │              │                                         │
│  │ 52 companies │                                         │
│  └──────────────┘                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 Endpoints Disponibles

### API Principale (Port 8000)
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Documentation API |
| `/health` | GET | Health check |
| `/api/stats` | GET | Statistiques globales |
| `/api/reviews` | GET | Liste des avis (pagination) |
| `/api/companies` | GET | Liste des entreprises |

### ML API (Port 8001)
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Documentation ML API |
| `/health` | GET | État du modèle |
| `/api/ml/predict` | POST | Prédiction unique |
| `/api/ml/predict-batch` | POST | Prédictions batch |
| `/api/ml/model-info` | GET | Infos modèle en production |
| `/api/ml/model-performance` | GET | Comparaison des modèles |

## 🧪 Tests de Charge

### Test de prédiction simple (Apache Bench)
```bash
ab -n 1000 -c 10 -p test_review.json -T application/json \
  http://localhost:8001/api/ml/predict
```

Contenu de `test_review.json` :
```json
{"text": "Service excellent et livraison rapide!", "title": "Très satisfait"}
```

### Test de batch (Python)
```python
import requests
import time

reviews = [
    {"text": f"Test review {i}", "title": f"Test {i}"}
    for i in range(100)
]

start = time.time()
response = requests.post(
    "http://localhost:8001/api/ml/predict-batch",
    json={"reviews": reviews}
)
elapsed = time.time() - start

print(f"Temps pour 100 prédictions: {elapsed:.2f}s")
print(f"Throughput: {100/elapsed:.1f} prédictions/seconde")
```

## ⚠️ Troubleshooting

### Problème: Modèles non chargés
**Symptôme:**
```
ERROR: Modèles non chargés. Exécutez le notebook pour sauvegarder les modèles.
```

**Solution:**
1. Vérifier que les fichiers existent :
   ```bash
   ls scripts/ml/models/sentiment_model_best.pkl
   ls scripts/ml/models/tfidf_vectorizer.pkl
   ```
2. Si absents, exécuter la cellule 24 du notebook
3. Redémarrer l'API : `docker-compose restart ml-api`

### Problème: Erreur de prédiction
**Symptôme:**
```
422 Unprocessable Entity
```

**Solution:**
Vérifier le format de la requête JSON :
```json
{
  "text": "Votre texte ici (OBLIGATOIRE)",
  "title": "Optionnel"
}
```

### Problème: Data drift non détecté
**Symptôme:**
Le script s'exécute mais aucune dérive n'est détectée malgré des changements évidents.

**Solution:**
1. Vérifier la taille des échantillons (minimum 1000 reviews recommandé)
2. Ajuster le seuil de p-value dans le code (actuellement 0.05)
3. Examiner les distributions manuellement dans les visualisations

### Problème: Elasticsearch connection refused
**Symptôme:**
```
ConnectionError: [Errno 111] Connection refused
```

**Solution:**
1. Vérifier que le service est démarré : `docker-compose ps elasticsearch`
2. Attendre 30 secondes que le service soit prêt
3. Vérifier la connexion : `curl http://localhost:9200`

## 📈 Métriques de Performance

### Modèles entraînés (sur 21,795 reviews)
| Modèle | F1-Score | Precision | Recall | Temps entraînement |
|--------|----------|-----------|--------|-------------------|
| Logistic Regression | 0.87 | 0.88 | 0.86 | ~2s |
| Naive Bayes | 0.82 | 0.81 | 0.83 | ~1s |
| Random Forest | 0.84 | 0.85 | 0.83 | ~30s |

### API Performance (machine locale)
- Prédiction unique : ~10-50ms
- Batch de 100 reviews : ~500-800ms
- Throughput : ~100-200 prédictions/seconde
- Taille modèle en mémoire : ~5-10 MB

## 🔄 Workflow de Re-entraînement

Quand réentraîner les modèles :
1. **Data drift détecté** : p-value < 0.05 sur les distributions
2. **Performance dégradée** : Baisse de F1-score en production
3. **Nouvelles données** : +10,000 reviews collectées
4. **Périodiquement** : Tous les 30 jours minimum

Processus :
1. Exécuter le monitoring : `python scripts/ml/data_drift_monitor.py`
2. Analyser les rapports dans `docs/data_drift_reports/`
3. Si dérive significative :
   - Ouvrir le notebook `sentiment_analysis.ipynb`
   - Exécuter toutes les cellules (entraînement)
   - Exécuter cellule 24 (sauvegarde)
   - Redémarrer l'API : `docker-compose restart ml-api`
4. Valider les nouvelles prédictions avec des tests

## 📚 Ressources Additionnelles

- **Notebook ML complet** : `notebooks/sentiment_analysis.ipynb`
- **Code ML API** : `api/ml_api.py`
- **Script de monitoring** : `scripts/ml/data_drift_monitor.py`
- **Configuration Docker** : `docker-compose.yml`, `docker/Dockerfile.ml-api`
- **Documentation FastAPI interactive** : http://localhost:8001/docs

## ✅ Checklist de Déploiement

- [ ] Notebook exécuté complètement
- [ ] Modèles sauvegardés (`.pkl` files présents)
- [ ] Métadonnées générées (`models_metadata.json`)
- [ ] API testée en local (port 8001)
- [ ] Prédictions validées (POST `/api/ml/predict`)
- [ ] Docker build réussi (`ml-api` service)
- [ ] Services Docker démarrés (6 services actifs)
- [ ] Health check OK dans Docker
- [ ] Data drift monitor testé
- [ ] Documentation à jour
- [ ] Tests de charge effectués
- [ ] Monitoring configuré (optionnel avec Airflow)
