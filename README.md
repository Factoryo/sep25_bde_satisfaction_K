# Supply Chain Satisfaction Client

## 🎯 Description du Projet

Ce projet de Data Engineering vise à analyser la satisfaction client dans le contexte de la supply chain en collectant et analysant **600,000+ reviews Trustpilot** de 60+ entreprises majeures. Il combine plusieurs technologies modernes pour collecter, traiter, analyser et visualiser des données de satisfaction client.

### ✨ Fonctionnalités principales

- **Web Scraping Massif** : Collecte automatisée de 10,000+ reviews par entreprise avec stratégie multi-filtres
- **Machine Learning** : Analyse prédictive et classification des retours clients
- **API REST** : Interface pour accéder aux données et aux modèles de prédiction
- **Dashboard** : Visualisation interactive des métriques de satisfaction
- **Orchestration** : Automatisation des workflows de données avec Airflow

## 🚀 Quick Start - Mass Scraping

### Option 1: Script PowerShell (Recommandé)
```powershell
cd etl_elt

# Test sur 3 entreprises (~30 min)
.\scraping.ps1 test

# Vérifier les résultats
.\scraping.ps1 check

# Lancer le scraping complet (~30-40h)
.\scraping.ps1 run
```

### Option 2: Python Direct
```powershell
cd etl_elt

# Test
python scripts/test_mass_scraping.py

# Production
python scripts/mass_scraping.py

# Vérifier la progression
python scripts/check_progress.py
```

📚 **Documentation détaillée** : 
- Scraping: `etl_elt/scripts/SETUP_COMPLETE.md`
- Organisation des données: `docs/DATABASE_ORGANIZATION.md`

---

## 💾 Organisation des Données

### Architecture en 2 bases

1. **PostgreSQL** (Données relationnelles)
   - Informations d'entreprises (nom, catégorie, contacts)
   - TrustScores et distribution des étoiles
   - Adresses et métadonnées
   
2. **Elasticsearch** (Données orientées documents)
   - Avis clients complets (600,000+ reviews)
   - Recherche full-text en français
   - Agrégations et analytics temps réel

### Chargement des données

```powershell
# 1. Démarrer les services Docker
docker-compose up -d

# 2. Charger toutes les données (PostgreSQL + Elasticsearch)
python scripts/database/load_all_data.py --data-dir data/raw

# 3. Accéder aux services
# PostgreSQL: localhost:5432 (trustpilot_db/trustpilot_user/trustpilot_pass)
# Elasticsearch: http://localhost:9200
# Kibana: http://localhost:5601
```

### Analyse SQL et visualisation

```sql
-- Top 10 entreprises par TrustScore
SELECT e.entreprise_name, r.trustscore
FROM Entreprise e
JOIN Rating r ON e.entreprise_id = r.entreprise_id
ORDER BY r.trustscore DESC LIMIT 10;
```

📊 **Kibana Dashboard**: `docs/KIBANA_SETUP.md`  
📈 **Requêtes SQL**: `scripts/database/sql_queries.sql`

---

## 📊 Données Collectées

### 60+ Entreprises Scrapées
- **E-commerce**: Amazon, eBay, AliExpress, Walmart, Target, Etsy, Wish
- **Tech**: Apple, Microsoft, Google, Samsung, Dell, HP
- **Services**: Facebook, Netflix, Spotify, PayPal, Zoom
- **Travel**: Booking.com, Airbnb, Uber, Expedia, Ryanair
- **Fashion**: ASOS, Nike, Adidas, Zara, H&M
- **Finance**: Revolut, N26, Coinbase
- **France**: Vinted, SNCF, Orange, Fnac, Cdiscount

### 30+ Champs par Review
- Identifiants, scores, dates (absolues/relatives)
- Contenu (titre, texte), réponses entreprise
- Métadonnées reviewer (nom, nombre d'avis)

**Target**: ~600,000 reviews totales (10,000 × 60 entreprises)

## Technologies Utilisées

| Technologie | Utilisation |
|-------------|-------------|
| **Python** | Langage principal pour le développement |
| **FastAPI** | Framework pour l'API REST haute performance |
| **Docker** | Conteneurisation et déploiement |
| **PostgreSQL** | Base de données relationnelle (entreprises) |
| **Elasticsearch** | Stockage et recherche de données (reviews) |
| **Kibana** | Visualisation et dashboard analytics |
| **Streamlit** | Dashboard interactif |
| **Apache Airflow** | Orchestration des workflows |
| **Scikit-learn** | Modèles de machine learning |
| **BeautifulSoup** | Web scraping Trustpilot |

## Structure du Projet

```
supply-chain-satisfaction-client/
├── data/
│   ├── raw/                 # Données JSON scrapées (~600,000 reviews)
│   └── processed/           # Données traitées et nettoyées
├── scripts/
│   ├── scraping/            # Scripts de web scraping
│   ├── database/            # Scripts de chargement PostgreSQL/Elasticsearch
│   └── ml/                  # Scripts de machine learning
├── api/                     # Application FastAPI
├── dashboard/               # Application Streamlit
├── docker/                  # Fichiers Docker (API, Dashboard)
├── airflow/                 # DAGs et configuration Airflow
├── docs/                    # Documentation complète
│   ├── DATABASE_ORGANIZATION.md  # Guide base de données
│   └── KIBANA_SETUP.md          # Configuration Kibana
├── etl_elt/                 # Système de scraping Trustpilot
│   ├── scrapers/            # Scripts de scraping
│   ├── scripts/             # Mass scraping et utilitaires
│   └── QUICKSTART.md        # Guide rapide scraping
├── tests/                   # Tests unitaires et d'intégration
├── .gitignore               # Fichiers ignorés par Git
├── requirements.txt         # Dépendances Python
├── docker-compose.yml       # 6 services (API, Dashboard, PostgreSQL, Elasticsearch, Kibana, Airflow)
├── README.md                # Documentation principale
└── LICENSE                  # Licence du projet
```

## Instructions d'Installation

### Prérequis

- Python 3.9 ou supérieur
- Docker et Docker Compose
- Git

### Installation locale

1. **Cloner le repository**
   ```bash
   git clone https://github.com/Factoryo/sep25_bde_satisfaction_K.git
   cd sep25_bde_satisfaction_K
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   .\venv\Scripts\activate   # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

### Déploiement avec Docker

1. **Lancer tous les services**
   ```bash
   docker-compose up -d
   ```

2. **Accéder aux services**
   - API FastAPI : http://localhost:8000
   - Documentation API : http://localhost:8000/docs
   - Dashboard Streamlit : http://localhost:8502
   - PostgreSQL : localhost:5432 (trustpilot_db)
   - Elasticsearch : http://localhost:9200
   - Kibana : http://localhost:5601

3. **Charger les données scrapées**
   ```bash
   # Attendre 30 secondes que les services soient prêts
   python scripts/database/load_all_data.py --data-dir data/raw
   ```

### Arrêter les services

```bash
docker-compose down
```

## Utilisation

### API

L'API FastAPI expose des endpoints pour :
- Récupérer les données de satisfaction
- Soumettre de nouvelles données
- Obtenir des prédictions du modèle ML

### Dashboard

Le dashboard Streamlit permet de :
- Visualiser les métriques de satisfaction en temps réel
- Explorer les tendances historiques
- Analyser les résultats des prédictions

## Tests

Exécuter les tests :
```bash
pytest tests/ -v
```

## Contribution

Les contributions sont les bienvenues ! Veuillez consulter les guidelines de contribution dans le dossier `docs/`.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
