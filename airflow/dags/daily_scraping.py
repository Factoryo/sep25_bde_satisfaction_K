"""
DAG Airflow - Scraping Quotidien Trustpilot
Collecte automatique des nouveaux avis chaque jour à 2h du matin
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, '/app')

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 1),
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
}

dag = DAG(
    'trustpilot_daily_scraping',
    default_args=default_args,
    description='Scraping quotidien des avis Trustpilot',
    schedule_interval='0 2 * * *',  # Tous les jours à 2h du matin
    catchup=False,
    tags=['scraping', 'trustpilot', 'production']
)

def check_prerequisites():
    """Vérifier que Elasticsearch et PostgreSQL sont accessibles"""
    from elasticsearch import Elasticsearch
    import psycopg2
    
    print("Vérification des prérequis...")
    
    # Test Elasticsearch
    es = Elasticsearch(['http://elasticsearch:9200'])
    if not es.ping():
        raise Exception("Elasticsearch non accessible")
    print("✓ Elasticsearch OK")
    
    # Test PostgreSQL
    try:
        conn = psycopg2.connect(
            host='postgres',
            database='trustpilot_db',
            user='trustpilot_user',
            password='trustpilot_pass'
        )
        conn.close()
        print("✓ PostgreSQL OK")
    except Exception as e:
        raise Exception(f"PostgreSQL non accessible: {e}")
    
    return True

def run_daily_scraping():
    """Exécuter le scraping quotidien pour toutes les entreprises"""
    import sys
    sys.path.insert(0, '/app/etl_elt')
    
    from scrapers.trustpilot_reviews_scraper import TrustpilotReviewsScraper
    import json
    
    # Liste des entreprises à scraper (top priorités)
    COMPANIES = [
        "amazon.com", "amazon.co.uk", "ebay.com", "aliexpress.com",
        "apple.com", "microsoft.com", "google.com", "samsung.com",
        "booking.com", "airbnb.com", "uber.com", "netflix.com",
        "vinted.fr", "leboncoin.fr", "sncf.com", "cdiscount.com"
    ]
    
    results = {
        'date': datetime.now().isoformat(),
        'companies_scraped': 0,
        'total_reviews': 0,
        'errors': []
    }
    
    scraper = TrustpilotReviewsScraper()
    
    for company in COMPANIES:
        try:
            print(f"Scraping {company}...")
            # Scraper uniquement les nouveaux avis (last 7 days)
            reviews = scraper.scrape_reviews(
                company_name=company,
                max_pages=10,  # Limiter à 200 reviews par jour
                filters={'date_range': 'last_7_days'}
            )
            
            results['companies_scraped'] += 1
            results['total_reviews'] += len(reviews)
            
            print(f"✓ {company}: {len(reviews)} nouveaux avis")
            
        except Exception as e:
            error_msg = f"Erreur {company}: {str(e)}"
            print(f"✗ {error_msg}")
            results['errors'].append(error_msg)
    
    # Sauvegarder les résultats
    with open('/app/data/logs/daily_scraping_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Résumé:")
    print(f"   Entreprises: {results['companies_scraped']}/{len(COMPANIES)}")
    print(f"   Nouveaux avis: {results['total_reviews']}")
    print(f"   Erreurs: {len(results['errors'])}")
    
    return results

def load_to_databases():
    """Charger les données scrapées dans Elasticsearch et PostgreSQL"""
    print("Chargement des données dans les bases...")
    
    # Cette fonction appelle les scripts de chargement existants
    import subprocess
    
    result = subprocess.run([
        'python', '/app/scripts/database/load_all_data.py',
        '--data-dir', '/app/data/raw',
        '--incremental'  # Mode incrémental pour ne charger que les nouveaux
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Erreur lors du chargement: {result.stderr}")
    
    print("✓ Données chargées avec succès")
    return True

# Définir les tâches
task_check = PythonOperator(
    task_id='check_prerequisites',
    python_callable=check_prerequisites,
    dag=dag
)

task_scraping = PythonOperator(
    task_id='run_daily_scraping',
    python_callable=run_daily_scraping,
    dag=dag
)

task_load = PythonOperator(
    task_id='load_to_databases',
    python_callable=load_to_databases,
    dag=dag
)

task_cleanup = BashOperator(
    task_id='cleanup_old_files',
    bash_command='find /app/data/raw -name "*.json" -mtime +30 -delete',
    dag=dag
)

# Définir le flux
task_check >> task_scraping >> task_load >> task_cleanup
