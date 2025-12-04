# Guide d'Automatisation et Monitoring

Ce guide explique comment automatiser le scraping, le déploiement et le monitoring du projet Trustpilot Analytics.

## 📋 Vue d'ensemble

Le système d'automatisation comprend :
- **Airflow** : Orchestration des tâches quotidiennes
- **GitLab CI/CD** : Déploiement automatique
- **Prometheus + Grafana** : Monitoring en temps réel
- **Scripts PowerShell** : Gestion simplifiée

## 🚀 Démarrage Rapide

### Lancer l'infrastructure complète

```powershell
# Démarrer tous les services (Airflow, Prometheus, Grafana, etc.)
docker-compose up -d

# Attendre 30 secondes que tout démarre
Start-Sleep -Seconds 30

# Vérifier le statut
docker-compose ps
```

### Accéder aux interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | admin / admin |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **API Data** | http://localhost:8000/docs | - |
| **ML API** | http://localhost:8001/docs | - |
| **Dashboard** | http://localhost:8502 | - |
| **Elasticsearch** | http://localhost:9200 | - |
| **Kibana** | http://localhost:5601 | - |

## 📅 Airflow - Orchestration

### DAGs Disponibles

#### 1. `trustpilot_daily_scraping`
**Objectif :** Scraper les nouveaux avis quotidiennement

**Planification :** Tous les jours à 2h du matin

**Tâches :**
1. `check_prerequisites` - Vérifier Elasticsearch et PostgreSQL
2. `run_daily_scraping` - Scraper 16 entreprises prioritaires (200 avis/entreprise max)
3. `load_to_databases` - Charger dans Elasticsearch + PostgreSQL
4. `cleanup_old_files` - Supprimer les fichiers >30 jours

**Exécution manuelle :**
```bash
# Depuis l'interface Airflow
# Ou via CLI:
docker-compose exec airflow-scheduler airflow dags trigger trustpilot_daily_scraping
```

#### 2. `ml_monitoring_and_drift_detection`
**Objectif :** Surveiller les modèles ML et détecter les dérives

**Planification :** Tous les jours à 3h du matin (après le scraping)

**Tâches :**
1. `test_api_health` - Vérifier que l'API ML fonctionne
2. `detect_data_drift` - Détecter les dérives de données
3. `check_model_performance` - Vérifier le F1-score
4. `analyze_api_logs` - Analyser les logs pour anomalies
5. `generate_daily_report` - Rapport quotidien

**Résultats :**
- Rapports sauvegardés dans `docs/data_drift_reports/`
- Logs dans `data/logs/daily_report_YYYYMMDD.txt`
- Alertes si drift détecté

### Configuration Airflow

**Première initialisation :**
```bash
# Initialiser la base de données Airflow
docker-compose run --rm airflow-webserver airflow db init

# Créer un utilisateur admin
docker-compose run --rm airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

**Variables d'environnement :**
```bash
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres-airflow/airflow
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

## 🔄 GitLab CI/CD

### Pipeline Stages

Le fichier `.gitlab-ci.yml` définit 4 stages :

#### Stage 1: Test
- **test:python** - Linting (flake8) + tests unitaires (pytest)
- **test:api** - Tests de l'API ML avec services (Elasticsearch, PostgreSQL)

#### Stage 2: Build
- **build:api** - Build image Docker de l'API principale
- **build:ml-api** - Build image Docker de l'API ML
- **build:dashboard** - Build image Docker du dashboard

#### Stage 3: Deploy
- **deploy:staging** - Déploiement automatique sur serveur de staging (branche `develop`)
- **deploy:production** - Déploiement manuel sur production (branche `main`)

#### Stage 4: Monitor
- **monitor:health-check** - Vérifier la santé des services après déploiement
- **monitor:performance** - Tester la latence des APIs

### Configuration GitLab

**Variables à définir dans GitLab CI/CD Settings :**

```bash
# SSH Access
SSH_PRIVATE_KEY=<votre_clé_ssh_privée>

# Staging
STAGING_SERVER=staging.example.com
STAGING_USER=deploy
STAGING_PATH=/opt/trustpilot-analytics

# Production
PROD_SERVER=prod.example.com
PROD_USER=deploy
PROD_PATH=/opt/trustpilot-analytics
```

**Déclencher le pipeline :**
```bash
# Commit et push sur main
git add .
git commit -m "Deploy: new features"
git push origin main

# Le pipeline démarre automatiquement
# Suivre sur: https://gitlab.com/your-project/-/pipelines
```

## 📊 Prometheus - Monitoring

### Métriques Collectées

**API Metrics :**
- `http_requests_total` - Nombre total de requêtes
- `http_request_duration_seconds` - Latence des requêtes
- `ml_predictions_total` - Nombre de prédictions ML
- `ml_prediction_confidence` - Confiance des prédictions
- `ml_model_loaded` - Status du chargement du modèle

**Infrastructure Metrics :**
- `node_cpu_seconds_total` - Utilisation CPU
- `node_memory_MemAvailable_bytes` - Mémoire disponible
- `node_filesystem_avail_bytes` - Espace disque

**Database Metrics :**
- `pg_stat_activity_count` - Connexions PostgreSQL actives
- `elasticsearch_cluster_health_status` - Santé Elasticsearch

### Alertes Configurées

**Critiques (notif immédiate) :**
- API principale down > 1 min
- ML API down > 1 min
- Modèle ML non chargé > 2 min
- Elasticsearch ou PostgreSQL down > 1 min

**Warnings :**
- Taux d'erreur 5xx > 5%
- Latence P95 > 500ms
- Confiance moyenne < 70%
- Data drift détecté
- CPU > 80%
- Mémoire > 85%
- Disque < 15%

### Ajouter des métriques custom

```python
# Dans api/ml_api.py
from prometheus_client import Counter, Histogram, Gauge

# Compteur de prédictions
predictions_counter = Counter(
    'ml_predictions_total',
    'Total ML predictions',
    ['sentiment']
)

# Histogramme de latence
prediction_duration = Histogram(
    'ml_prediction_duration_seconds',
    'ML prediction duration'
)

# Gauge pour status du modèle
model_loaded = Gauge(
    'ml_model_loaded',
    'ML model loading status'
)

# Utilisation
@app.post("/api/ml/predict")
async def predict(review: ReviewInput):
    with prediction_duration.time():
        result = model.predict(...)
        predictions_counter.labels(sentiment=result['sentiment']).inc()
    return result
```

## 📈 Grafana - Dashboards

### Dashboard ML API

**Panels inclus :**
1. **Requests per Second** - Charge de l'API
2. **Latency (P50, P95, P99)** - Performance
3. **Predictions per Minute** - Activité ML
4. **Model Loaded Status** - Santé du modèle
5. **Average Confidence** - Qualité des prédictions
6. **Error Rate** - Taux d'erreur
7. **Sentiment Distribution** - Répartition des sentiments
8. **CPU Usage** - Utilisation CPU
9. **Memory Usage** - Utilisation mémoire
10. **Database Status** - Santé des BDD

### Créer un dashboard custom

1. Accéder à Grafana : http://localhost:3000
2. Login : admin / admin
3. Cliquer sur **"+ Create" → "Dashboard"**
4. Ajouter un panel avec une query Prometheus :
   ```promql
   rate(http_requests_total{job="ml-api"}[5m])
   ```
5. Personnaliser la visualisation
6. Sauvegarder

## 🤖 Scripts d'Automatisation

### Script PowerShell Interactif

```powershell
# Lancer le menu interactif
.\scripts\automation.ps1
```

**Fonctionnalités disponibles :**

**Services :**
- Démarrer/Arrêter/Redémarrer tous les services
- Afficher le statut de chaque service

**Scraping :**
- Lancer le scraping quotidien manuellement
- Voir les logs du dernier scraping

**Monitoring :**
- Détecter le data drift
- Voir les rapports de drift
- Ouvrir les dashboards (Prometheus, Grafana, Airflow)

**Déploiement :**
- Tester les APIs
- Déployer en production (push vers GitLab)

**Maintenance :**
- Nettoyer les vieilles données (>30 jours)
- Sauvegarder les bases de données

### Commandes rapides

```powershell
# Statut de tous les services
docker-compose ps

# Logs d'un service spécifique
docker-compose logs -f ml-api

# Redémarrer un service
docker-compose restart ml-api

# Exécuter un DAG Airflow
docker-compose exec airflow-scheduler airflow dags trigger trustpilot_daily_scraping

# Voir les métriques Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Data drift monitoring
python scripts/ml/data_drift_monitor.py
```

## 🔔 Alertes et Notifications

### Configuration Email (Airflow)

Dans `airflow/dags/`:

```python
default_args = {
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}
```

**Configurer SMTP dans Airflow :**
```ini
# airflow.cfg
[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = your-email@gmail.com
smtp_password = your-app-password
smtp_port = 587
smtp_mail_from = airflow@example.com
```

### Slack Notifications

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

task_notify = SlackWebhookOperator(
    task_id='notify_slack',
    http_conn_id='slack_webhook',
    message='🎉 Scraping quotidien terminé avec succès!',
    dag=dag
)
```

## 📅 Cron Jobs (Alternative à Airflow)

Si vous préférez utiliser des cron jobs système :

```bash
# Éditer crontab
crontab -e

# Ajouter:
# Scraping quotidien à 2h
0 2 * * * cd /path/to/project && python etl_elt/scripts/mass_scraping.py >> logs/scraping.log 2>&1

# Monitoring ML à 3h
0 3 * * * cd /path/to/project && python scripts/ml/data_drift_monitor.py >> logs/monitoring.log 2>&1

# Nettoyage hebdomadaire le dimanche à minuit
0 0 * * 0 find /path/to/project/data/raw -name "*.json" -mtime +30 -delete
```

## 🎯 Bonnes Pratiques

### 1. Monitoring
- Vérifier les dashboards Grafana quotidiennement
- Réagir aux alertes dans les 15 minutes
- Archiver les rapports de drift mensuellement

### 2. Scraping
- Limiter à 200 avis/entreprise/jour pour éviter le rate limiting
- Surveiller les erreurs de scraping
- Adapter les filtres selon les besoins

### 3. ML
- Réentraîner le modèle si data drift détecté
- Tester les nouveaux modèles en staging avant production
- Sauvegarder les modèles avec versioning

### 4. Déploiement
- Toujours tester en staging d'abord
- Déployer en production aux heures creuses
- Garder un rollback plan (images Docker précédentes)

### 5. Backup
- Backup quotidien des bases de données
- Retention: 7 jours daily, 4 weekly, 12 monthly
- Tester la restauration mensuellement

## 🆘 Troubleshooting

### Airflow ne démarre pas
```bash
# Vérifier les logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# Réinitialiser la DB
docker-compose run --rm airflow-webserver airflow db reset
docker-compose run --rm airflow-webserver airflow db init
```

### Prometheus ne collecte pas les métriques
```bash
# Vérifier les targets
curl http://localhost:9090/api/v1/targets

# Vérifier la config
docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

### DAG Airflow en erreur
```bash
# Voir les logs du DAG
docker-compose exec airflow-scheduler airflow tasks test <dag_id> <task_id> <execution_date>

# Relancer une tâche
docker-compose exec airflow-webserver airflow tasks clear <dag_id> --task-regex <task_id>
```

## 📚 Ressources

- **Airflow Docs:** https://airflow.apache.org/docs/
- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **GitLab CI/CD Docs:** https://docs.gitlab.com/ee/ci/

## ✅ Checklist de Déploiement

- [ ] Airflow opérationnel (http://localhost:8080)
- [ ] 2 DAGs activés (scraping + monitoring)
- [ ] Prometheus collecte les métriques (http://localhost:9090/targets)
- [ ] Dashboard Grafana configuré (http://localhost:3000)
- [ ] Pipeline GitLab CI/CD testé
- [ ] Variables GitLab configurées (SSH, servers)
- [ ] Alertes email/Slack configurées
- [ ] Scripts d'automatisation testés
- [ ] Backups automatiques configurés
- [ ] Documentation à jour

---

**Support:** Pour toute question, consultez la documentation ou ouvrez une issue sur GitLab.
