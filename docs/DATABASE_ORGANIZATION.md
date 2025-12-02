# Guide complet: Organisation des données Trustpilot

## Vue d'ensemble

Ce guide explique comment organiser les données scrapées de Trustpilot dans deux systèmes de bases de données:
- **PostgreSQL**: Pour les informations d'entreprises (données relationnelles)
- **Elasticsearch**: Pour les avis clients (données orientées documents)

## Architecture des données

```
Données scrapées (JSON)
         │
         ├──────────────────────┬─────────────────────┐
         │                      │                     │
         ▼                      ▼                     ▼
   company_info            reviews               metadata
         │                      │                     │
         ▼                      ▼                     ▼
   PostgreSQL            Elasticsearch          Kibana
   (relationnel)        (documents)         (visualisation)
```

## 1. Prérequis

### 1.1 Services Docker nécessaires
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tous les services sont UP
docker-compose ps
```

Services requis:
- ✅ PostgreSQL (port 5432)
- ✅ Elasticsearch (port 9200)
- ✅ Kibana (port 5601)

### 1.2 Données scrapées
Assurez-vous d'avoir des fichiers JSON dans `data/raw/`:
```
data/raw/
  ├── amazon_com_reviews.json
  ├── apple_com_reviews.json
  ├── booking_com_reviews.json
  └── ...
```

Format JSON attendu:
```json
{
  "company_info": {
    "company_name": "Amazon",
    "company_url": "https://fr.trustpilot.com/review/amazon.com",
    "trustscore": 4.2,
    "total_reviews": 15000,
    "categories": ["E-commerce"],
    ...
  },
  "reviews": [
    {
      "reviewer_name": "John Doe",
      "rating": 5,
      "title": "Excellent service",
      "content": "Livraison rapide...",
      "date": "2024-01-15",
      ...
    }
  ]
}
```

## 2. PostgreSQL - Données d'entreprises

### 2.1 Schéma de la base de données

Le schéma PostgreSQL est défini dans `etl_elt/scripts/postgres_schema.sql` et comprend:

**Tables principales:**
- `Category`: Catégories d'entreprises (E-commerce, Tech, Services, etc.)
- `Entreprise`: Informations d'entreprises (nom, site web, contacts)
- `Address`: Adresses des entreprises
- `Rating`: Scores et distribution des étoiles

**Vues:**
- `all_company_raw_data`: Vue complète de toutes les données
- `company_ratings`: Vue simplifiée des ratings

### 2.2 Chargement des données

#### Option A: Script Python complet (RECOMMANDÉ)
```bash
# Depuis la racine du projet
python scripts/database/load_all_data.py --data-dir data/raw
```

#### Option B: PostgreSQL uniquement
```bash
python scripts/database/load_to_postgres.py --data-dir data/raw
```

#### Option C: Avec paramètres personnalisés
```bash
python scripts/database/load_to_postgres.py \
  --data-dir data/raw \
  --host localhost \
  --port 5432 \
  --database trustpilot_db \
  --user trustpilot_user \
  --password trustpilot_pass
```

### 2.3 Connexion à PostgreSQL

**Via Docker:**
```bash
docker exec -it postgres psql -U trustpilot_user -d trustpilot_db
```

**Via client externe (pgAdmin, DBeaver, etc.):**
- Host: `localhost`
- Port: `5432`
- Database: `trustpilot_db`
- User: `trustpilot_user`
- Password: `trustpilot_pass`

### 2.4 Requêtes SQL de démonstration

Toutes les requêtes sont dans `scripts/database/sql_queries.sql`:

```sql
-- Top 10 entreprises par TrustScore
SELECT 
    e.entreprise_name,
    r.trustscore,
    (r.five_star + r.four_star + r.three_star + r.two_star + r.one_star) as total_avis
FROM Entreprise e
JOIN Rating r ON e.entreprise_id = r.entreprise_id
ORDER BY r.trustscore DESC
LIMIT 10;

-- Distribution des notes
SELECT 
    CASE 
        WHEN trustscore >= 4.5 THEN 'Excellent (4.5-5.0)'
        WHEN trustscore >= 4.0 THEN 'Très bon (4.0-4.5)'
        WHEN trustscore >= 3.5 THEN 'Bon (3.5-4.0)'
        ELSE 'Moyen (< 3.5)'
    END as categorie,
    COUNT(*) as nombre_entreprises
FROM Rating
GROUP BY categorie;

-- Utiliser la vue
SELECT * FROM company_ratings ORDER BY trustscore DESC;
```

## 3. Elasticsearch - Avis clients

### 3.1 Structure de l'index

Index: `trustpilot_reviews`

**Champs principaux:**
- `company_name` (keyword): Nom de l'entreprise
- `reviewer_name` (text): Nom du reviewer
- `rating` (integer): Note (1-5 étoiles)
- `title` (text): Titre de l'avis
- `content` (text): Contenu de l'avis (analysé en français)
- `date` (date): Date de publication
- `company_reply` (object): Réponse de l'entreprise (si présente)

### 3.2 Chargement des données

#### Option A: Script Python complet (RECOMMANDÉ)
```bash
python scripts/database/load_all_data.py --data-dir data/raw
```

#### Option B: Elasticsearch uniquement
```bash
python scripts/database/load_to_elasticsearch.py --data-dir data/raw
```

#### Option C: Avec statistiques et exemple
```bash
python scripts/database/load_to_elasticsearch.py \
  --data-dir data/raw \
  --stats \
  --sample
```

### 3.3 Vérification des données

**Via curl:**
```bash
# Compter les documents
curl -u elastic:elastic123 "http://localhost:9200/trustpilot_reviews/_count"

# Rechercher les premiers documents
curl -u elastic:elastic123 "http://localhost:9200/trustpilot_reviews/_search?size=5"
```

**Via Kibana Dev Tools:**
```json
GET trustpilot_reviews/_count

GET trustpilot_reviews/_search
{
  "query": {"match_all": {}},
  "size": 10
}
```

## 4. Kibana - Visualisation et Dashboard

### 4.1 Configuration initiale

1. Ouvrir Kibana: http://localhost:5601
2. Aller dans **Stack Management** > **Index Patterns**
3. Créer l'index pattern `trustpilot_reviews`
4. Sélectionner `date` comme Time field

### 4.2 Dashboard recommandé

Créer les visualisations suivantes (voir `docs/KIBANA_SETUP.md`):

1. **Metrics**:
   - Total des avis
   - Note moyenne
   - % d'avis positifs

2. **Charts**:
   - Distribution des notes (Pie Chart)
   - Top 10 entreprises (Bar Chart)
   - Évolution temporelle (Line Chart)
   - Notes moyennes par entreprise (Horizontal Bar)

3. **Tables**:
   - Derniers avis (Data Table)
   - Reviewers actifs (Tag Cloud)

### 4.3 Requêtes Kibana utiles

Voir le fichier complet: `docs/KIBANA_SETUP.md`

**Exemple - Avis négatifs:**
```json
GET trustpilot_reviews/_search
{
  "query": {
    "range": {
      "rating": {"lte": 2}
    }
  },
  "sort": [{"date": "desc"}]
}
```

**Exemple - Note moyenne par entreprise:**
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "companies": {
      "terms": {"field": "company_name.keyword"},
      "aggs": {
        "avg_rating": {"avg": {"field": "rating"}}
      }
    }
  }
}
```

## 5. Processus complet de chargement

### 5.1 Étape par étape

```bash
# 1. S'assurer que Docker est lancé
docker-compose up -d

# 2. Vérifier que les services sont UP
docker-compose ps

# 3. Attendre que les services soient prêts (environ 30 secondes)
# PostgreSQL: Attendre "database system is ready to accept connections"
docker-compose logs postgres | grep "ready"

# Elasticsearch: Attendre "started"
docker-compose logs elasticsearch | grep "started"

# 4. Charger toutes les données
python scripts/database/load_all_data.py --data-dir data/raw

# 5. Vérifier le chargement
python scripts/database/load_all_data.py --data-dir data/raw --no-wait
```

### 5.2 Script PowerShell automatisé

```powershell
# Fichier: scripts/database/load_data.ps1

# Démarrer Docker
Write-Host "Démarrage des services Docker..." -ForegroundColor Cyan
docker-compose up -d

# Attendre 30 secondes
Write-Host "Attente de 30 secondes..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Charger les données
Write-Host "Chargement des données..." -ForegroundColor Cyan
python scripts/database/load_all_data.py --data-dir data/raw

Write-Host "Terminé!" -ForegroundColor Green
```

## 6. Vérification et validation

### 6.1 PostgreSQL

```sql
-- Compter les entreprises
SELECT COUNT(*) FROM Entreprise;

-- Vérifier les catégories
SELECT category_name, COUNT(*) as nb_entreprises
FROM Category c
JOIN Entreprise e ON c.category_id = e.category_id
GROUP BY category_name;

-- Statistiques des TrustScores
SELECT 
    COUNT(*) as total,
    ROUND(AVG(trustscore)::numeric, 2) as moyenne,
    ROUND(MIN(trustscore)::numeric, 2) as min,
    ROUND(MAX(trustscore)::numeric, 2) as max
FROM Rating;
```

### 6.2 Elasticsearch

```bash
# Via curl
curl -u elastic:elastic123 "http://localhost:9200/trustpilot_reviews/_count"

# Via Python
python -c "
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}], basic_auth=('elastic', 'elastic123'))
print(f'Total avis: {es.count(index=\"trustpilot_reviews\")[\"count\"]}')
"
```

### 6.3 Kibana

1. Ouvrir http://localhost:5601
2. Aller dans **Discover**
3. Sélectionner l'index pattern `trustpilot_reviews`
4. Vérifier que les avis s'affichent

## 7. Dépannage

### 7.1 PostgreSQL: Connexion refusée

**Problème:** `could not connect to server: Connection refused`

**Solutions:**
```bash
# Vérifier que le service est UP
docker-compose ps postgres

# Voir les logs
docker-compose logs postgres

# Redémarrer le service
docker-compose restart postgres
```

### 7.2 Elasticsearch: Connection timeout

**Problème:** `Connection timeout to Elasticsearch`

**Solutions:**
```bash
# Vérifier le service
docker-compose ps elasticsearch

# Voir les logs
docker-compose logs elasticsearch

# Redémarrer
docker-compose restart elasticsearch

# Attendre que le service soit prêt (peut prendre 1-2 minutes)
docker-compose logs -f elasticsearch | grep "started"
```

### 7.3 Données non chargées

**Problème:** Aucune donnée dans les bases

**Vérifications:**
```bash
# 1. Vérifier que les fichiers JSON existent
ls data/raw/*_reviews.json

# 2. Vérifier le format JSON
python -c "
import json
with open('data/raw/amazon_com_reviews.json') as f:
    data = json.load(f)
    print(f'Company: {data.get(\"company_info\", {}).get(\"company_name\")}')
    print(f'Reviews: {len(data.get(\"reviews\", []))}')
"

# 3. Relancer le chargement avec plus de logs
python scripts/database/load_all_data.py --data-dir data/raw
```

### 7.4 Kibana: Index pattern non trouvé

**Problème:** `No matching indices found: trustpilot_reviews`

**Solution:**
```bash
# Vérifier que l'index existe
curl -u elastic:elastic123 "http://localhost:9200/_cat/indices?v"

# Recharger les données dans Elasticsearch
python scripts/database/load_to_elasticsearch.py --data-dir data/raw

# Rafraîchir la page Kibana et recréer l'index pattern
```

## 8. Maintenance

### 8.1 Réinitialiser les données

**PostgreSQL:**
```sql
-- Supprimer toutes les données
TRUNCATE TABLE Rating CASCADE;
TRUNCATE TABLE Address CASCADE;
TRUNCATE TABLE Entreprise CASCADE;
TRUNCATE TABLE Category CASCADE;

-- Ou supprimer et recréer la base
DROP DATABASE trustpilot_db;
CREATE DATABASE trustpilot_db OWNER trustpilot_user;
```

**Elasticsearch:**
```bash
# Supprimer l'index
curl -X DELETE -u elastic:elastic123 "http://localhost:9200/trustpilot_reviews"

# Ou via Python
python -c "
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}], basic_auth=('elastic', 'elastic123'))
es.indices.delete(index='trustpilot_reviews', ignore=[400, 404])
"
```

### 8.2 Backup des données

**PostgreSQL:**
```bash
# Backup
docker exec postgres pg_dump -U trustpilot_user trustpilot_db > backup_postgres.sql

# Restore
docker exec -i postgres psql -U trustpilot_user trustpilot_db < backup_postgres.sql
```

**Elasticsearch:**
```bash
# Snapshot (nécessite configuration préalable)
curl -X PUT -u elastic:elastic123 "http://localhost:9200/_snapshot/my_backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/backup"
  }
}'
```

## 9. Prochaines étapes

Après avoir chargé les données:

1. ✅ Explorer les données dans Kibana
2. ✅ Exécuter les requêtes SQL d'analyse
3. ✅ Créer des visualisations personnalisées
4. 🔄 Développer des modèles de ML sur les avis
5. 🔄 Automatiser le scraping et le chargement avec Airflow
6. 🔄 Créer des API REST pour exposer les données

## 10. Ressources

- **PostgreSQL**: `scripts/database/load_to_postgres.py`
- **Elasticsearch**: `scripts/database/load_to_elasticsearch.py`
- **Script complet**: `scripts/database/load_all_data.py`
- **Requêtes SQL**: `scripts/database/sql_queries.sql`
- **Kibana**: `docs/KIBANA_SETUP.md`
- **Docker**: `docker-compose.yml`
- **Schéma DB**: `etl_elt/scripts/postgres_schema.sql`
