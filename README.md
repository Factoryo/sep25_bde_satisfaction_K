# Analyse de Sentiment Trustpilot

Projet de data engineering : scraping d'avis Trustpilot, stockage, et prédiction de sentiment avec du ML.

## Pourquoi ce projet ?

Je voulais construire un pipeline complet de données, du scraping jusqu'à l'API de prédiction. Trustpilot était un bon choix car les avis sont structurés et y'a beaucoup de données disponibles.

**Le plus compliqué** : Trustpilot bloque facilement les scrapers. J'ai dû ruser en filtrant par étoiles (1★, 2★, etc.) pour récupérer plus d'avis par entreprise. Sans ça, on est limité à ~100 avis max.

## Ce que j'ai appris

- Scraping "intelligent" avec BeautifulSoup (parsing du JSON-LD embarqué dans les pages)
- Pipeline ETL avec stockage PostgreSQL + Elasticsearch
- Entraînement d'un modèle de sentiment (Logistic Regression, F1=0.94)
- Conteneurisation avec Docker Compose
- Orchestration avec Airflow (DAGs quotidiens)

## Démarrage rapide

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier que tout tourne
docker ps
```

## Accès aux services

| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard | http://localhost:8502 | - |
| API | http://localhost:8000/docs | - |
| ML API | http://localhost:8001/docs | - |
| Airflow | http://localhost:8080 | admin / admin |
| Grafana | http://localhost:3000 | admin / admin |
| Kibana | http://localhost:5601 | - |

## Données collectées

J'ai scrapé **52 entreprises** et récupéré environ **79 000 avis**. Les entreprises sont variées : e-commerce (Amazon, Cdiscount, Vinted), voyage (Booking, Airbnb), services (Uber, Netflix), etc.

Les données brutes sont en JSON dans `data/raw/`.

## Architecture simplifiée

```
Scraper (Python) → JSON files → API FastAPI → Dashboard Streamlit
                       ↓
              PostgreSQL + Elasticsearch
                       ↓
                  ML Training → ML API (prédictions)
```

## Structure du projet

```
├── api/                  # API FastAPI (données + stats)
├── dashboard/            # Interface Streamlit
├── etl_elt/
│   ├── scrapers/        # Le scraper Trustpilot
│   └── scripts/         # Scripts de scraping massif
├── scripts/
│   ├── database/        # Chargement des données
│   └── ml/              # Entraînement du modèle
├── airflow/dags/        # DAGs pour l'automatisation
├── docker/              # Dockerfiles
└── docker-compose.yml   # Orchestration des 12 services
```

## Le modèle ML

J'ai testé plusieurs algos sur les avis :
- Naive Bayes → F1 = 0.91
- Random Forest → F1 = 0.93
- **Logistic Regression → F1 = 0.94** ← Celui que j'utilise

Features : TF-IDF sur le texte des avis (5000 features, uni+bigrams)

### Exemple de prédiction

```bash
curl -X POST http://localhost:8001/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Livraison rapide, produit conforme", "title": "Super"}'
```

Réponse :
```json
{"sentiment": "positif", "confidence": 0.89}
```

## Difficultés rencontrées

1. **Trustpilot anti-scraping**
2. **Données déséquilibrées**

## TODO / Améliorations possibles

- [ ] Ajouter un cache Redis pour l'API
- [ ] Dashboard plus interactif (filtres par date)
- [ ] Tester des modèles type BERT (mais lourd à déployer)
- [ ] Monitoring des erreurs avec Sentry

## Installation dev

```bash
# Environnement Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt

# Lancer en dev
docker-compose up -d
```

## Licence

MIT
