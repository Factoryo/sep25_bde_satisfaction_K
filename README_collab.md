# Projet : Satisfaction Client dans la Supply Chain

## Présentation et Objectifs

Ce projet, réalisé dans le cadre de la formation [**Data Engineer - DataScientest**](https://datascientest.com/), a pour objectif d’analyser la **satisfaction client** à partir d’avis collectés en ligne, notamment sur **Trustpilot** et d’autres plateformes de notation.

La **supply chain** englobe l’ensemble du processus d’approvisionnement, de production et de distribution d’un produit.\
L’analyse de la satisfaction client permet d’évaluer la qualité de cette chaîne en identifiant des problématiques liées à :

- la conception des produits,
- la logistique et les délais de livraison,
- la tarification,
- la durabilité,
- ou encore la conformité du service aux attentes du marché.

L’objectif principal est donc de **mesurer, synthétiser et visualiser la satisfaction client**, tout en automatisant la collecte, le traitement et la mise à jour des données.

---

## Étapes du Projet

### 1. Extraction des Données

- **Objectif :** extraire des informations à partir de sites comme Trustpilot.
- **Méthodes :** web scraping et enregistrement des données dans des fichier CSV et JSON.
- **Livrables :**
  - Fichiers CSV et JSON,
  - Fichier explicatif du traitement (documentation technique).
- **Outils :** Python (requests, BeautifulSoup, Pandas) et no code (extension web scraper).

### 2. Organisation de la Donnée

- **Objectif :** concevoir une base de données relationnelle pour les informations sur les entreprises et une base orientée document pour les commentaires clients.
- **Livrables :**
  - Scripts SQL pour la création et les requêtes,
  - Implémentation ElasticSearch + dashboard Kibana.
- **Outils :** SQL, ElasticSearch, MongoDB (*à confirmer*), Kibana.

### 3. Analyse et Machine Learning

- **Objectif :** effectuer une **analyse de sentiment** sur les avis collectés.
- **Livrables :** notebook commenté avec les modèles d’analyse.
- **Outils :** Python (Pandas, Scikit-learn, NLTK, TextBlob).

### 4. Mise en Production

- **Objectif :** exposer les modèles via une API et rendre le projet déployable.
- **Livrables :**
  - API Flask ou FastAPI,
  - Conteneurisation Docker (Dockerfile + docker-compose).
- **Outils :** FastAPI, Docker, GitLab CI.

### 5. Automatisation et Monitoring

- **Objectif :** automatiser le scraping, le déploiement et la surveillance du système.
- **Livrables :**
  - Pipeline CI/CD,
  - DAG Airflow ou CronJob,
  - Monitoring avec Prometheus / Grafana.
- **Outils :** Airflow, GitLab, Prometheus, Grafana.

---

## Installation et Lancement via Docker

L’application est entièrement conteneurisée pour simplifier le déploiement et l’exécution sur tous les systèmes (Windows, Linux et macOS).

### Prérequis

Assurez-vous d’avoir installé :

- [**Docker Desktop**](https://www.docker.com/products/docker-desktop/) (Windows / macOS)
- [**Docker Engine**](https://docs.docker.com/engine/install/) (Linux)

Pour vérifier l’installation :

```bash
docker --version
docker compose version
```

### Lancer le projet

1. **Cloner le dépôt :**

   ```bash
   git clone <lien_du_dépôt_github>
   cd sep25_bde_satisfaction_b
   ```

2. **Démarrer le service ETL :**

   ```bash
   docker compose up -d
   ```

   Grâce au montage de volume de l’application, toute modification du code source est automatiquement prise en compte sans nécessiter de reconstruction complète de l’image.

   Une fois le conteneur lancé, les **bibliothèques Python nécessaires** sont automatiquement installées grâce au fichier `requirements.txt`, comme défini dans le `Dockerfile`. Cela garantit que l’environnement à l’intérieur du conteneur contient toutes les dépendances requises.

   **Extrait du `Dockerfile` :**
   ```dockerfile
   # Copier les dépendances
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   ```

   Cet extrait montre que les dépendances listées dans `requirements.txt` sont copiées dans l’image Docker, puis installées automatiquement lors du build initial. Ainsi, après le lancement de `docker compose up -d`, le conteneur prépare l’environnement Python avant d’exécuter le script principal.

   **Extrait du `docker-compose.yml` :**
   ```yaml
   build: .
   volumes:
     - .:/app
   ```

   L’instruction `build: .` indique à Docker d’utiliser le `Dockerfile` situé à la racine du projet pour construire l’image, tandis que le volume `.:/app` permet de synchroniser les fichiers locaux avec ceux du conteneur.

3. **Excécuter `etl.py` dans le CLI du conteneur :**
   
   Pour interagir directement avec le conteneur et exécuter des commandes à l’intérieur, il est possible d’ouvrir un shell (CLI) via la commande suivante :
   ```bash
   docker exec -it satisfaction_client_etl bash
   ```

   Une fois dans le CLI du conteneur, exécute le script principal `etl.py` avec :
   ```bash
   python etl.py
   ```
   
   Cette commande lance le script ETL et permet de vérifier son bon fonctionnement.
   Tu devrais voir apparaître dans la console le message défini dans ton code, par exemple :
      ```bash
   Démarrage du script ETL...
   ```

4. **Arrêter les conteneurs :**
   ```bash
   docker compose down
   ```

> ℹ️ Le `docker-compose.yml` est configuré pour un environnement de développement. Il sera enrichi progressivement pour inclure d’autres services (API, base de données, monitoring, etc.).

---

## Ajouter du code et gérer les imports dans `etl.py`

Le fichier principal `etl.py` est le point d’entrée du pipeline ETL. C’est ici que sont orchestrées les différentes étapes d’extraction, de transformation et de chargement des données.

### Structure typique du projet

```
project_root/
│
├── extract/
│   ├── __init__.py
│   ├── scrape_compagnies.py
│   ├── scrape_reviews.py
│
├── notebooks/
│
├── etl.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

### Ajouter du code dans `etl.py`

Pour intégrer une nouvelle fonctionnalité (par exemple une fonction de nettoyage ou une nouvelle source de données), créez un fichier Python dans le dossier `extract/` et importez-le ensuite dans `etl.py`.

**Exemple :**

Dans `extract/scrape_reviews.py` :

```python
def scrape_reviews():
    print("Scraping des avis clients...")
```

Dans `etl.py` :

```python
from extract.scrape_reviews import scrape_reviews

if __name__ == "__main__":
    scrape_reviews()
```

Grâce au montage de volume défini dans `docker-compose.yml`, toute modification locale dans ces fichiers est immédiatement prise en compte par le conteneur. Il n’est donc **pas nécessaire de reconstruire l’image** pour tester de nouvelles fonctions.

## Scraping des commentaires :

python src/scripts/mass_scraping.py

> 💡 **Astuce :** Assurez-vous que chaque module Python contient un fichier `__init__.py` (même vide) pour que Python reconnaisse le dossier comme un package importable.

---

## Gestion des variables d’environnement (.env)

Le projet inclut un fichier `.env` pour centraliser les variables sensibles (mots de passe, identifiants API, configurations de base de données, etc.).

### Pourquoi utiliser un fichier `.env` ?

Avoir un fichier `.env` permet d’adopter une approche **professionnelle et sécurisée** :
- Les mots de passe et clés API **ne doivent jamais être partagés** ni commités sur GitHub.
- Les informations sensibles peuvent être facilement modifiées sans impacter le code source.
- Cela facilite la gestion des environnements (développement, test, production).

### Exemple d’utilisation

**Fichier `.env` :**
```bash
DB_USER=my_user
DB_PASSWORD=my_password
API_KEY=abc123xyz
```

**Utilisation dans le code Python :**
```python
from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
api_key = os.getenv("API_KEY")
```

**Référence dans le `docker-compose.yml` :**
```yaml
env_file:
  - .env
```

> ⚠️ Le fichier `.env` doit être ajouté dans le `.gitignore` pour éviter toute fuite de données sensibles.

---

## Bonnes pratiques Docker

- Utiliser des **volumes montés** pour permettre le rechargement automatique du code sans rebuild.
- Éviter les reconstructions inutiles (`docker compose up` suffit pour appliquer les changements).
- Utiliser des **variables d’environnement** pour distinguer les contextes (développement, test, production).
- Exécuter les processus sous un **utilisateur non-root** pour des raisons de sécurité.
- Structurer le projet avec des dossiers dédiés (`/extract`, `/data`, `/api`, `/notebooks`, etc.) pour faciliter la maintenance.

---

## Équipe du Projet

- Ousmane Ibrahima SY [LinkedIn](https://www.linkedin.com/in/ousmane-sy-6926a6139) / [GitHub](https://github.com/Oussouke)
- Arnaud GUILLOUX [LinkedIn](https://www.linkedin.com/) / [GitHub](https://github.com/)
- Rodolphe Katz [LinkedIn](https://www.linkedin.com/) / [GitHub](https://github.com/)

