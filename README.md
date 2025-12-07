# Trustpilot Sentiment Analysis

Plateforme d'analyse de satisfaction client basée sur les avis Trustpilot avec Machine Learning et orchestration automatisée.

## Fonctionnalités

- **Scraping automatisé** : Collecte quotidienne d'avis Trustpilot via Airflow
- **Machine Learning** : Analyse de sentiment (F1-Score: 0.77, Logistic Regression)
- **APIs REST** : Accès aux données et prédictions ML
- **Dashboard Streamlit** : Visualisation interactive
- **Monitoring** : Data drift detection et métriques Prometheus/Grafana
- **Orchestration** : Airflow DAGs pour automatisation complète

## Quick Start

```bash
# Démarrer les services
docker-compose up -d

# Initialiser Airflow (première fois uniquement)
docker exec -it airflow-webserver airflow db init
docker exec -it airflow-webserver airflow users create \
  --username admin --password admin --firstname Admin --lastname User \
  --role Admin --email admin@example.com

# Charger des données initiales
python scripts/database/load_all_data.py --data-dir data/raw
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| API principale | http://localhost:8000 | Données et statistiques |
| ML API | http://localhost:8001 | Prédictions de sentiment |
| Dashboard | http://localhost:8502 | Interface Streamlit |
| Airflow | http://localhost:8080 | Orchestration (admin/admin) |
| Elasticsearch | http://localhost:9200 | Recherche full-text |
| PostgreSQL | localhost:5432 | Base de données |
| Grafana | http://localhost:3000 | Monitoring (admin/admin) |

## Architecture

### Stack Technique
- **Backend**: Python 3.11, FastAPI
- **ML**: Scikit-learn, TF-IDF vectorization
- **Bases de données**: PostgreSQL 15, Elasticsearch 8.11
- **Orchestration**: Apache Airflow 2.8
- **Monitoring**: Prometheus, Grafana
- **Frontend**: Streamlit
- **Infrastructure**: Docker Compose (12 services)

### Pipeline de Données

```
Trustpilot → Airflow DAG (daily @ 2AM) → PostgreSQL + Elasticsearch
                    ↓
              ML Training → Drift Detection (daily @ 3AM)
                    ↓
              ML API (predictions) → Dashboard Streamlit
```

## Utilisation

### Prédiction de Sentiment

```bash
curl -X POST http://localhost:8001/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Service excellent et livraison rapide!",
    "title": "Très satisfait"
  }'
```

**Réponse:**
```json
{
  "sentiment": "positif",
  "confidence": 0.92,
  "probabilities": {
    "positif": 0.92,
    "negatif": 0.05,
    "neutre": 0.03
  }
}
```

### Monitoring Data Drift

```bash
python scripts/ml/data_drift_monitor.py
```

Génère des rapports JSON et visualisations dans `docs/data_drift_reports/`

### Automatisation PowerShell

```powershell
# Menu interactif de gestion
.\scripts\automation.ps1
```

Options: Start/Stop services, trigger scraping, check status

## Structure du Projet

```
sep25_bde_satisfaction_K/
├── airflow/              # DAGs Airflow (scraping, monitoring)
├── api/                  # FastAPI applications
│   ├── main.py          # API données
│   └── ml_api.py        # API ML prédictions
├── dashboard/            # Streamlit dashboard
├── data/                 # Données scrapées (raw/processed)
├── scripts/
│   ├── database/        # Load PostgreSQL/Elasticsearch
│   ├── ml/              # Training, drift detection
│   └── automation.ps1   # Menu gestion services
├── notebooks/            # Jupyter analysis
├── monitoring/           # Prometheus + Grafana config
├── docker/               # Dockerfiles
├── docker-compose.yml    # 12 services orchestrés
└── requirements.txt
```

## Installation

### Prérequis
- Python 3.11+
- Docker Desktop
- Git

### Setup

```bash
# Clone
git clone https://github.com/Factoryo/sep25_bde_satisfaction_K.git
cd sep25_bde_satisfaction_K

# Environnement Python
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Démarrer Docker
docker-compose up -d

# Initialiser Airflow
docker exec -it airflow-webserver airflow db init
```

## CI/CD

Pipeline GitLab CI avec 4 stages:
1. **Test**: Linting, tests unitaires
2. **Build**: Docker images
3. **Deploy**: Push images, deploy services
4. **Monitor**: Health checks, alertes

## Modèle ML

- **Algorithme**: Logistic Regression (meilleur F1-Score)
- **Features**: TF-IDF (5000 features, 1-2 grams)
- **Performance**: F1=0.7696, Précision=0.77, Rappel=0.77
- **Dataset**: 21,795 reviews entraînement
- **Classes**: Positif, Négatif, Neutre

## Licence

MIT License - Voir [LICENSE](LICENSE)
