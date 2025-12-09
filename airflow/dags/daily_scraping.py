from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os


sys.path.insert(0, '/app')

default_args = {
    'owner': 'rodolphe',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 1),
    'email_on_failure': False,  # Désactivé en dev
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
}

dag = DAG(
    'trustpilot_daily_scraping',
    default_args=default_args,
    description='Scraping quotidien des avis Trustpilot',
    schedule_interval='0 2 * * *',  # 2h
    catchup=False,
    tags=['scraping', 'trustpilot', 'production']
)

def check_prerequisites():
    from elasticsearch import Elasticsearch
    import psycopg2
    
    print("Vérification des prérequis...")
    
    es = Elasticsearch(['http://elasticsearch:9200'])
    if not es.ping():
        raise Exception("Elasticsearch non accessible")
    print("Elasticsearch OK")

    try:
        conn = psycopg2.connect(
            host='postgres',
            database='trustpilot_db',
            user='trustpilot_user',
            password='trustpilot_pass'
        )
        conn.close()
        print("PostgreSQL OK")
    except Exception as e:
        raise Exception(f"PostgreSQL non accessible: {e}")
    
    return True

def run_daily_scraping():
    import sys
    sys.path.insert(0, '/app/etl_elt')
    
    from scrapers.trustpilot_jsonld_scraper import TrustpilotJSONLDScraper
    import json
    import os
    from pathlib import Path

    COMPANIES = [
        # E-commerce
        "amazon.com", "amazon.fr", "ebay.com", "aliexpress.com", "etsy.com",
        "cdiscount.com", "fnac.com", "darty.com", "boulanger.com",
        # Mode & Lifestyle
        "vinted.fr", "zalando.fr", "shein.com", "asos.com", "nike.com", "adidas.com",
        # Voyage & Transport
        "booking.com", "airbnb.fr", "tripadvisor.com", "expedia.com", "kayak.com",
        "sncf.com", "ouigo.com", "blablacar.fr", "flixbus.fr",
        "easyjet.com", "lufthansa.com", "airfrance.fr",
        # Livraison
        "ups.com", "fedex.com", "dhl.com", "chronopost.fr", "colissimo.fr", "mondial-relay.fr",
        # Tech & Services
        "apple.com", "samsung.com", "microsoft.com", "google.com",
        "netflix.com", "spotify.com", "disney.com", "amazon-prime-video.com",
        # Finance & Banque
        "revolut.com", "n26.com", "boursorama.com", "klarna.com", "paypal.com",
        # Télécom
        "orange.fr", "sfr.fr", "bouyguestelecom.fr", "free.fr",
        # Autres services
        "uber.com", "deliveroo.fr", "ubereats.com", "leboncoin.fr",
        "doctolib.fr", "linkedin.com", "indeed.com", "trustpilot.com", "zoom.us"
    ]
    
    # Dossier des données
    data_dir = Path('/app/data/raw')
    
    # Détecter les entreprises déjà scrapées
    existing_files = {f.stem.replace('_reviews', '').replace('_', '.') 
                      for f in data_dir.glob('*_reviews.json')}
    
    # Filtrer les entreprises non encore scrapées
    companies_to_scrape = [c for c in COMPANIES if c not in existing_files]
    
    print(f"Entreprises déjà scrapées: {len(existing_files)}")
    print(f"Entreprises à scraper: {len(companies_to_scrape)}")
    
    if not companies_to_scrape:
        print("Toutes les entreprises ont déjà été scrapées!")
        return {'companies_scraped': 0, 'total_reviews': 0, 'skipped': len(COMPANIES)}
    
    results = {
        'date': datetime.now().isoformat(),
        'companies_scraped': 0,
        'companies_skipped': len(existing_files),
        'total_reviews': 0,
        'errors': []
    }
    
    scraper = TrustpilotJSONLDScraper(delay=2.0)
    
    for company in companies_to_scrape:
        try:
            print(f"Scraping {company}...")
            reviews = scraper.scrape_company(
                company_domain=company,
                max_pages=10
            )
            
            results['companies_scraped'] += 1
            results['total_reviews'] += len(reviews)
            
            print(f"Succès {company}: {len(reviews)} nouveaux avis")
            
        except Exception as e:
            error_msg = f"Erreur {company}: {str(e)}"
            print(f"Échec {error_msg}")
            results['errors'].append(error_msg)
    
    with open('/app/data/logs/daily_scraping_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nRésumé:")
    print(f"   Entreprises: {results['companies_scraped']}/{len(COMPANIES)}")
    print(f"   Nouveaux avis: {results['total_reviews']}")
    print(f"   Erreurs: {len(results['errors'])}")
    
    return results

def load_to_databases():
    print("Chargement des données dans les bases...")
    
    import subprocess
    
    result = subprocess.run([
        'python', '/app/scripts/database/load_all_data.py',
        '--data-dir', '/app/data/raw',
        '--incremental' 
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Erreur lors du chargement: {result.stderr}")
    
    print("Données chargées avec succès")
    return True

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

task_check >> task_scraping >> task_load >> task_cleanup
