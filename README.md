# Supply Chain Satisfaction Client

## Description du Projet

Ce projet de Data Engineering vise à analyser la satisfaction client dans le contexte de la supply chain. Il combine plusieurs technologies modernes pour collecter, traiter, analyser et visualiser des données de satisfaction client.

### Fonctionnalités principales

- **Web Scraping** : Collecte automatisée de données de satisfaction client depuis diverses sources
- **Machine Learning** : Analyse prédictive et classification des retours clients
- **API REST** : Interface pour accéder aux données et aux modèles de prédiction
- **Dashboard** : Visualisation interactive des métriques de satisfaction
- **Orchestration** : Automatisation des workflows de données avec Airflow

## Technologies Utilisées

| Technologie | Utilisation |
|-------------|-------------|
| **Python** | Langage principal pour le développement |
| **FastAPI** | Framework pour l'API REST haute performance |
| **Docker** | Conteneurisation et déploiement |
| **Elasticsearch** | Stockage et recherche de données |
| **Streamlit** | Dashboard interactif |
| **Apache Airflow** | Orchestration des workflows |
| **Scikit-learn** | Modèles de machine learning |
| **BeautifulSoup/Selenium** | Web scraping |

## Structure du Projet

```
supply-chain-satisfaction-client/
├── data/
│   ├── raw/                 # Données brutes collectées
│   └── processed/           # Données traitées et nettoyées
├── scripts/
│   ├── scraping/            # Scripts de web scraping
│   ├── database/            # Scripts de gestion de base de données
│   └── ml/                  # Scripts de machine learning
├── api/                     # Application FastAPI
├── dashboard/               # Application Streamlit
├── docker/                  # Fichiers Docker
├── airflow/                 # DAGs et configuration Airflow
├── docs/                    # Documentation du projet
├── tests/                   # Tests unitaires et d'intégration
├── .gitignore               # Fichiers ignorés par Git
├── requirements.txt         # Dépendances Python
├── docker-compose.yml       # Configuration Docker Compose
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
   - Dashboard Streamlit : http://localhost:8501
   - Elasticsearch : http://localhost:9200
   - Kibana : http://localhost:5601

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
