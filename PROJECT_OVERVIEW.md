# 📊 Trustpilot Analytics - Vue d'Ensemble du Projet

## 🎯 Objectif du Projet

Ce projet implémente une **plateforme complète d'analyse de sentiment** basée sur les avis clients de Trustpilot. Il collecte automatiquement des milliers d'avis d'entreprises, les analyse avec des modèles de Machine Learning, et fournit des visualisations interactives pour comprendre la satisfaction client.

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    COLLECTE DE DONNÉES                          │
│  Scraping Trustpilot (60+ entreprises) → JSON Files            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│               STOCKAGE & ORGANISATION                            │
│  PostgreSQL (données structurées) + Elasticsearch (recherche)   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              ANALYSE & MACHINE LEARNING                          │
│  Modèles ML (Logistic Regression, F1=0.77) → API REST           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              VISUALISATION & MONITORING                          │
│  Dashboard Streamlit + Grafana + Kibana                         │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AUTOMATISATION                                 │
│  Airflow (orchestration) + GitLab CI (déploiement)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Technologies Utilisées

### Backend & Infrastructure
- **Python 3.11** - Langage principal
- **Docker & Docker Compose** - Conteneurisation (12 services)
- **PostgreSQL 15** - Base de données relationnelle
- **Elasticsearch 8.11** - Moteur de recherche
- **Apache Airflow 2.8** - Orchestration des workflows

### Machine Learning
- **Scikit-learn** - Entraînement des modèles (Logistic Regression, Naive Bayes, Random Forest)
- **TF-IDF** - Vectorisation du texte (5000 features)
- **FastAPI** - API REST pour les prédictions

### Visualisation
- **Streamlit** - Dashboard interactif
- **Grafana** - Monitoring temps réel
- **Kibana** - Exploration des données
- **Matplotlib/Plotly** - Graphiques

### DevOps & Automatisation
- **GitLab CI/CD** - Pipeline d'intégration continue
- **Prometheus** - Collecte de métriques
- **Airflow** - Scraping quotidien automatisé

---

## 🗂️ Structure du Projet

```
sep25_bde_satisfaction_K/
│
├── 📁 airflow/                          # Orchestration des workflows
│   └── dags/
│       ├── daily_scraping.py           # Scraping quotidien à 2h
│       └── ml_monitoring.py            # Monitoring ML à 3h
│
├── 📁 api/                              # APIs REST
│   ├── main.py                         # API principale (données)
│   ├── ml_api.py                       # API ML (prédictions)
│   └── test_ml_api.py                  # Tests API
│
├── 📁 dashboard/                        # Visualisation
│   └── app.py                          # Dashboard Streamlit
│
├── 📁 etl_elt/                          # Pipeline de données
│   ├── scrapers/
│   │   ├── trustpilot_jsonld_scraper.py    # Scraper principal
│   │   └── trustpilot_mass_scraper.py      # Scraping en masse
│   ├── scripts/
│   │   ├── mass_scraping.py            # Script de scraping (60+ entreprises)
│   │   └── etl_elt.py                  # ETL/ELT principal
│   └── utils/
│       ├── config.py                   # Configuration
│       └── file_manager.py             # Gestion fichiers
│
├── 📁 scripts/                          # Scripts utilitaires
│   ├── database/
│   │   ├── load_to_postgres.py         # Chargement PostgreSQL
│   │   ├── load_to_elasticsearch.py    # Chargement Elasticsearch
│   │   └── load_all_data.py            # Chargement complet
│   ├── ml/
│   │   ├── data_drift_monitor.py       # Détection de drift
│   │   └── models/                     # Modèles entraînés (3.4 MB)
│   └── automation.ps1                  # Menu PowerShell (13 fonctions)
│
├── 📁 monitoring/                       # Monitoring & Alertes
│   ├── prometheus/
│   │   ├── prometheus.yml              # Config Prometheus
│   │   └── rules/alerts.yml            # 20+ règles d'alerte
│   └── grafana/
│       ├── dashboards/                 # Dashboard ML API (10 panels)
│       └── datasources/                # Connexion Prometheus
│
├── 📁 notebooks/                        # Analyse exploratoire
│   └── sentiment_analysis.ipynb        # Notebook ML complet (25 cellules)
│
├── 📁 docs/                             # Documentation
│   ├── AUTOMATION_GUIDE.md             # Guide automatisation
│   ├── ML_PRODUCTION_GUIDE.md          # Guide ML production
│   ├── DATABASE_ORGANIZATION.md        # Organisation BDD
│   └── KIBANA_SETUP.md                 # Setup Kibana
│
├── 📁 docker/                           # Dockerfiles
│   ├── Dockerfile.api                  # API principale
│   ├── Dockerfile.ml-api               # API ML
│   └── Dockerfile.dashboard            # Dashboard
│
├── 📄 docker-compose.yml               # 12 services orchestrés
├── 📄 .gitlab-ci.yml                   # Pipeline CI/CD (4 stages)
├── 📄 requirements.txt                 # Dépendances Python (42)
└── 📄 README.md                        # Documentation principale
```

---

## 🔄 Pipeline de Données Complet

### 1️⃣ **Récolte des Données** (Scraping)

**Fichiers clés :**
- `etl_elt/scrapers/trustpilot_jsonld_scraper.py`
- `etl_elt/scripts/mass_scraping.py`

**Processus :**
```python
# 60+ entreprises ciblées
companies = [
    'amazon.com', 'apple.com', 'microsoft.com', 'booking.com',
    'airbnb.com', 'netflix.com', 'uber.com', 'vinted.fr',
    'sncf.com', 'orange.fr', 'revolut.com', ...
]

# Scraping automatique
- 200 avis par entreprise maximum
- Délai de 2 secondes entre les requêtes
- Sauvegarde JSON dans etl_elt/data/raw/
```

**Données collectées :**
- Titre de l'avis
- Contenu texte
- Note (1-5 étoiles)
- Date de publication
- Auteur
- Entreprise
- URL

**Volume :** ~20,000+ avis collectés

---

### 2️⃣ **Extraction & Transformation** (ETL)

**Fichiers clés :**
- `etl_elt/scripts/etl_elt.py`
- `etl_elt/utils/helpers.py`

**Transformations appliquées :**
```python
# Nettoyage du texte
- Suppression des caractères spéciaux
- Conversion en minuscules
- Suppression des espaces multiples
- Gestion des valeurs manquantes

# Enrichissement
- Création du champ 'text' (title + content)
- Calcul de la longueur du texte
- Extraction de la date
- Normalisation des notes
```

**Format de sortie :**
```json
{
  "title": "Excellent service",
  "content": "Very satisfied with the product...",
  "rating": 5,
  "date": "2024-12-01",
  "author": "John Doe",
  "company": "amazon.com",
  "text": "Excellent service Very satisfied...",
  "text_length": 150
}
```

---

### 3️⃣ **Organisation & Chargement**

**Fichiers clés :**
- `scripts/database/load_to_postgres.py`
- `scripts/database/load_to_elasticsearch.py`
- `scripts/database/load_all_data.py`

#### **PostgreSQL** (Données structurées)

**Schéma :**
```sql
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    title TEXT,
    content TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    author VARCHAR(255),
    date DATE,
    url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_company ON reviews(company);
CREATE INDEX idx_rating ON reviews(rating);
CREATE INDEX idx_date ON reviews(date);
```

**Avantages :**
- Requêtes SQL complexes
- Agrégations rapides
- Intégrité référentielle
- Backup facile

#### **Elasticsearch** (Recherche full-text)

**Index :**
```json
{
  "mappings": {
    "properties": {
      "title": {"type": "text", "analyzer": "standard"},
      "content": {"type": "text", "analyzer": "standard"},
      "rating": {"type": "integer"},
      "company": {"type": "keyword"},
      "date": {"type": "date"}
    }
  }
}
```

**Avantages :**
- Recherche full-text ultra-rapide
- Filtres multi-critères
- Agrégations en temps réel
- Scalabilité horizontale

---

### 4️⃣ **Machine Learning** (Analyse de Sentiment)

**Fichier principal :**
- `notebooks/sentiment_analysis.ipynb` (développement)
- `api/ml_api.py` (production)
- `scripts/ml/models/` (modèles sauvegardés)

#### **Préparation des Données**

```python
# Dataset
- 21,795 avis chargés depuis PostgreSQL
- Création du label sentiment (1-2: négatif, 3: neutre, 4-5: positif)
- Split: 80% train, 20% test

# Distribution des sentiments
- Positif: 68.2%
- Neutre: 12.4%
- Négatif: 19.4%
```

#### **Vectorisation TF-IDF**

```python
TfidfVectorizer(
    max_features=5000,      # Top 5000 mots
    min_df=2,               # Min 2 documents
    max_df=0.8,             # Max 80% des documents
    ngram_range=(1, 2),     # Unigrams + bigrams
    stop_words='english'
)
```

#### **Modèles Entraînés**

| Modèle | F1-Score | Précision | Recall | Temps Entraînement |
|--------|----------|-----------|--------|-------------------|
| **Logistic Regression** | **0.7696** | 0.7801 | 0.7612 | 2.3s |
| Naive Bayes | 0.7234 | 0.7389 | 0.7145 | 0.8s |
| Random Forest | 0.7512 | 0.7654 | 0.7401 | 45.2s |

**✅ Modèle retenu :** Logistic Regression (meilleur F1-score)

#### **API ML - Prédictions en Temps Réel**

**Endpoint :** `POST http://localhost:8001/api/ml/predict`

**Exemple de requête :**
```bash
curl -X POST http://localhost:8001/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Excellent produit, très satisfait!",
    "title": "Super achat"
  }'
```

**Réponse :**
```json
{
  "sentiment": "positive",
  "confidence": 0.9856,
  "probabilities": {
    "negative": 0.0089,
    "neutral": 0.0055,
    "positive": 0.9856
  },
  "model_version": "logistic_regression_20251204",
  "processing_time_ms": 12.4
}
```

---

### 5️⃣ **Visualisation & Consommation**

#### **Dashboard Streamlit** (`dashboard/app.py`)

**URL :** http://localhost:8502

**Fonctionnalités :**
- 📊 **Statistiques générales** (nombre d'avis, note moyenne)
- 📈 **Distribution des notes** (histogramme)
- 🎯 **Analyse par entreprise** (top/flop)
- 📅 **Évolution temporelle** (graphique ligne)
- 🔍 **Recherche full-text** (Elasticsearch)
- 🤖 **Prédictions ML** (formulaire interactif)
- 💬 **Word Cloud** (mots fréquents)

#### **Kibana** (Exploration)

**URL :** http://localhost:5601

**Dashboards disponibles :**
- Vue d'ensemble des avis
- Analyse par entreprise
- Tendances temporelles
- Recherche avancée

#### **Grafana** (Monitoring ML)

**URL :** http://localhost:3000

**Panels (10) :**
1. API Requests per Second
2. Latency P50/P95/P99
3. Predictions per Minute
4. Model Loaded Status
5. Average Confidence
6. Error Rate %
7. Sentiment Distribution
8. CPU Usage
9. Memory Usage
10. Database Status

---

### 6️⃣ **Mise en Production**

#### **Architecture Docker**

**12 Services orchestrés :**

```yaml
services:
  # Core Services
  - api (port 8000)              # API données
  - ml-api (port 8001)           # API ML
  - dashboard (port 8502)        # Dashboard Streamlit
  
  # Databases
  - postgres (port 5432)         # PostgreSQL 15
  - elasticsearch (port 9200)    # Elasticsearch 8.11
  
  # Visualization
  - kibana (port 5601)           # Kibana 8.11
  - grafana (port 3000)          # Grafana
  
  # Orchestration
  - airflow-webserver (port 8080)
  - airflow-scheduler
  - postgres-airflow
  
  # Monitoring
  - prometheus (port 9090)
  - node-exporter (port 9100)
```

**Démarrage complet :**
```bash
docker-compose up -d
# Attendre 30 secondes
# Tous les services disponibles
```

#### **Santé des Services**

**Script de vérification :**
```powershell
.\scripts\automation.ps1
# Option 4: Show-ServicesStatus
```

**Health Checks :**
- ✅ API: http://localhost:8000/health
- ✅ ML API: http://localhost:8001/health
- ✅ Dashboard: http://localhost:8502
- ✅ PostgreSQL: Port 5432
- ✅ Elasticsearch: http://localhost:9200/_cluster/health
- ✅ Kibana: http://localhost:5601/api/status
- ✅ Airflow: http://localhost:8080/health
- ✅ Prometheus: http://localhost:9090/-/healthy

---

### 7️⃣ **Automatisation du Flux de Données**

#### **Airflow - Orchestration**

**URL :** http://localhost:8080 (admin/admin)

##### **DAG 1 : `trustpilot_daily_scraping`**

**Schedule :** Tous les jours à 2h00

**Tâches :**
```python
check_prerequisites        # Vérifier ES + PostgreSQL
    ↓
run_daily_scraping        # Scraper 16 entreprises prioritaires
    ↓
load_to_databases         # Charger dans ES + PostgreSQL
    ↓
cleanup_old_files         # Supprimer fichiers >30 jours
```

**Entreprises prioritaires :**
- Amazon, eBay, Apple, Microsoft
- Booking, Airbnb, Uber, Netflix
- Vinted, SNCF, Orange, Revolut
- Deliveroo, Spotify, PayPal, Nike

**Résultat :** ~3,200 nouveaux avis/jour

##### **DAG 2 : `ml_monitoring_and_drift_detection`**

**Schedule :** Tous les jours à 3h00 (après scraping)

**Tâches :**
```python
test_api_health           # Vérifier API ML
    ↓
├─ detect_data_drift      # Détecter drift (KS test)
├─ check_model_performance # Vérifier F1-score
└─ analyze_api_logs       # Analyser logs
    ↓
generate_daily_report     # Rapport quotidien
```

**Alertes :**
- Data drift détecté (p-value < 0.05)
- Performance dégradée (F1 < 0.70)
- API down ou erreurs

**Rapports :** `docs/data_drift_reports/drift_report_YYYYMMDD_HHMMSS.json`

#### **GitLab CI/CD - Déploiement Automatique**

**Pipeline (4 stages) :**

##### **Stage 1: Test**
```yaml
test:python:
  - flake8 (linting)
  - pytest --cov (tests + coverage)

test:api:
  - Tests API avec Elasticsearch + PostgreSQL
```

##### **Stage 2: Build**
```yaml
build:api, build:ml-api, build:dashboard:
  - Docker build
  - Push vers GitLab Container Registry
  - Tags: :latest + :$CI_COMMIT_SHORT_SHA
```

##### **Stage 3: Deploy**
```yaml
deploy:staging:
  - Branche: develop
  - SSH vers serveur staging
  - docker-compose pull + up -d

deploy:production:
  - Branche: main (manual trigger)
  - SSH vers serveur production
  - Health checks post-déploiement
```

##### **Stage 4: Monitor**
```yaml
monitor:health-check:
  - Vérifier tous les endpoints

monitor:performance:
  - 10 requêtes ML
  - Latence moyenne < 500ms
```

#### **Monitoring - Prometheus + Grafana**

**Métriques collectées (15s interval) :**

**APIs :**
- `http_requests_total` (compteur)
- `http_request_duration_seconds` (histogramme)
- `ml_predictions_total` (compteur par sentiment)
- `ml_prediction_confidence` (gauge)
- `ml_model_loaded` (gauge 0/1)

**Infrastructure :**
- `node_cpu_seconds_total`
- `node_memory_MemAvailable_bytes`
- `node_filesystem_avail_bytes`

**Databases :**
- `pg_stat_activity_count`
- `elasticsearch_cluster_health_status`

**Alertes (20+ règles) :**

| Alerte | Seuil | Durée | Gravité |
|--------|-------|-------|---------|
| API Down | up == 0 | 1 min | Critical |
| ML API Down | up == 0 | 1 min | Critical |
| High Error Rate | >5% | 5 min | Warning |
| High Latency | P95 >500ms | 5 min | Warning |
| Model Not Loaded | model_loaded == 0 | 2 min | Critical |
| Low Confidence | avg <70% | 15 min | Warning |
| Data Drift | drift_detected == 1 | 1 min | Warning |
| High CPU | >80% | 5 min | Warning |
| Low Disk | <15% | 5 min | Warning |

---

## 🎮 Utilisation du Projet

### Démarrage Rapide (5 minutes)

```bash
# 1. Cloner le projet
git clone https://github.com/Factoryo/sep25_bde_satisfaction_K.git
cd sep25_bde_satisfaction_K

# 2. Démarrer tous les services
docker-compose up -d

# 3. Initialiser Airflow (première fois)
docker-compose exec airflow-webserver airflow db init
docker-compose exec airflow-webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com

# 4. Activer les DAGs
docker-compose exec airflow-scheduler airflow dags unpause trustpilot_daily_scraping
docker-compose exec airflow-scheduler airflow dags unpause ml_monitoring_and_drift_detection

# 5. Charger les données existantes (si disponibles)
docker-compose exec api python scripts/database/load_all_data.py
```

### Accès aux Interfaces

| Interface | URL | Credentials |
|-----------|-----|-------------|
| Dashboard | http://localhost:8502 | - |
| API Docs | http://localhost:8000/docs | - |
| ML API Docs | http://localhost:8001/docs | - |
| Airflow | http://localhost:8080 | admin/admin |
| Kibana | http://localhost:5601 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Elasticsearch | http://localhost:9200 | - |

### Menu PowerShell Interactif

```powershell
.\scripts\automation.ps1
```

**Fonctionnalités (13 options) :**

**Services :**
1. Démarrer tous les services
2. Arrêter tous les services
3. Redémarrer tous les services
4. Afficher le statut

**Scraping :**
5. Démarrer le scraping quotidien
6. Voir les logs de scraping

**Monitoring :**
7. Détecter le data drift
8. Voir les rapports de drift
9. Ouvrir les dashboards (Prometheus, Grafana, Airflow)

**Déploiement :**
10. Tester les APIs
11. Déployer en production

**Maintenance :**
12. Nettoyer les anciennes données
13. Sauvegarder les bases de données

---

## 📈 Métriques & Performance

### Données Collectées

- **Volume total :** 21,795 avis (dataset initial)
- **Entreprises :** 60+ entreprises
- **Langues :** Principalement anglais/français
- **Période :** Avis récents (derniers mois)

### Performance ML

- **F1-Score :** 0.7696 (Logistic Regression)
- **Précision :** 78.01%
- **Recall :** 76.12%
- **Temps prédiction :** ~12ms par avis

### Performance API

- **Latence moyenne :** <50ms (P50)
- **Latence P95 :** <150ms
- **Latence P99 :** <300ms
- **Throughput :** >100 requêtes/seconde

### Ressources Système

- **CPU :** ~2 cores (avec 12 services)
- **RAM :** ~6 GB
- **Disque :** ~10 GB (avec données)
- **Trafic réseau :** Faible (scraping respectueux)

---

## 🚀 Évolutions Futures

### Court Terme (1-2 mois)

- [ ] Ajouter plus d'entreprises (100+)
- [ ] Multi-langues (détection automatique)
- [ ] Améliorer le modèle ML (BERT, transformers)
- [ ] Alertes Slack/Email configurables
- [ ] API authentification (JWT)

### Moyen Terme (3-6 mois)

- [ ] Analyse de topics (LDA, NMF)
- [ ] Détection d'aspects spécifiques (prix, qualité, service)
- [ ] Prédictions temporelles (séries)
- [ ] Clustering d'entreprises similaires
- [ ] Rapport PDF automatique

### Long Terme (6-12 mois)

- [ ] Scraping multi-sources (Google Reviews, Yelp)
- [ ] API publique avec rate limiting
- [ ] Dashboard mobile (React Native)
- [ ] Modèles personnalisés par industrie
- [ ] Recommandations d'amélioration produit

---

## 🤝 Contribution

### Structure Git

```
main                    # Production
  ↓
develop                 # Développement
  ↓
feature/*              # Nouvelles fonctionnalités
hotfix/*               # Corrections urgentes
```

### Workflow

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de Code

- **Python :** PEP 8 (flake8)
- **Tests :** pytest (coverage >80%)
- **Documentation :** Docstrings Google Style
- **Commits :** Conventional Commits

---

## 📚 Documentation Complète

- **[README.md](README.md)** - Documentation principale
- **[AUTOMATION_GUIDE.md](docs/AUTOMATION_GUIDE.md)** - Guide automatisation Airflow/CI/CD
- **[ML_PRODUCTION_GUIDE.md](docs/ML_PRODUCTION_GUIDE.md)** - Déploiement ML
- **[DATABASE_ORGANIZATION.md](docs/DATABASE_ORGANIZATION.md)** - Organisation BDD
- **[KIBANA_SETUP.md](docs/KIBANA_SETUP.md)** - Configuration Kibana
- **[PRODUCTION_SUMMARY.md](PRODUCTION_SUMMARY.md)** - Résumé production

---

## 🐛 Troubleshooting

### Problème : Services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs <service_name>

# Redémarrer un service
docker-compose restart <service_name>

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d
```

### Problème : Airflow DAGs en erreur

```bash
# Voir les logs du DAG
docker-compose logs airflow-scheduler

# Tester une tâche manuellement
docker-compose exec airflow-scheduler airflow tasks test <dag_id> <task_id> <execution_date>
```

### Problème : Modèle ML non chargé

```bash
# Vérifier que les modèles existent
ls scripts/ml/models/

# Redémarrer l'API ML
docker-compose restart ml-api

# Vérifier le health check
curl http://localhost:8001/health
```

### Problème : Elasticsearch mémoire insuffisante

```bash
# Augmenter la heap size dans docker-compose.yml
ES_JAVA_OPTS: "-Xms512m -Xmx512m"  # Passer à 1g si possible
```

---

## 📞 Support

- **Issues :** [GitHub Issues](https://github.com/Factoryo/sep25_bde_satisfaction_K/issues)
- **Documentation :** Voir dossier `docs/`
- **Email :** support@example.com

---

## 📝 Licence

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Auteurs

**Équipe Data Science**
- Rodolphe (Chef de projet)
- GitHub: [@Factoryo](https://github.com/Factoryo)

---

## 🙏 Remerciements

- **Trustpilot** pour les données publiques
- **Scikit-learn** pour les outils ML
- **Apache Airflow** pour l'orchestration
- **Docker** pour la conteneurisation
- **FastAPI** pour le framework API

---

## 📊 Statistiques du Projet

- **Lignes de code :** ~15,000
- **Fichiers Python :** 50+
- **Services Docker :** 12
- **Tests :** 80+ tests unitaires
- **Coverage :** >75%
- **Documentation :** 5 guides complets
- **Durée développement :** 3 mois

---

**Date de dernière mise à jour :** 4 décembre 2024

**Version :** 1.0.0 - Production Ready ✅
