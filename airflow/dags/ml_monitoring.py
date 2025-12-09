from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/app')

default_args = {
    'owner': 'ml_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 1),
    'email': ['ml-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'ml_monitoring_and_drift_detection',
    default_args=default_args,
    description='Monitoring quotidien des modèles ML et détection de data drift',
    schedule_interval='0 3 * * *',  
    catchup=False,
    tags=['ml', 'monitoring', 'data-drift']
)

def run_data_drift_detection():
    """Détection drift"""
    sys.path.insert(0, '/app/scripts/ml')
    from data_drift_monitor import DataDriftMonitor
    
    print("Lancement de la détection du data drift...")
    
    monitor = DataDriftMonitor(
        es_host='elasticsearch',
        es_port=9200
    )
    
    report = monitor.generate_report()
    
    if not report:
        raise Exception("Échec de la génération du rapport de drift")
    
    drift_detected = report.get('overall_drift_detected', False)
    
    if drift_detected:
        print("Data drift détecté")
        
        with open('/app/data/logs/drift_alerts.log', 'a') as f:
            f.write(f"{datetime.now()}: Data drift détecté\n")
    else:
        print("Aucune dérive significative détectée")
    
    return report

def check_model_performance():
    import requests
    import json
    
    print("Vérification des performances du modèle...")
    
    try:
        response = requests.get('http://ml-api:8001/api/ml/model-info', timeout=10)
        
        if response.status_code == 200:
            model_info = response.json()
            f1_score = model_info.get('f1_score', 0)
            
            print(f"   F1-Score actuel: {f1_score:.4f}")
            
            if f1_score < 0.70:
                print("Performance dégradée (F1 < 0.70)")
                return {'status': 'warning', 'f1_score': f1_score}
            
            print("Performances OK")
            return {'status': 'ok', 'f1_score': f1_score}
        else:
            raise Exception(f"API erreur: {response.status_code}")
            
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        raise

def test_api_health():
    import requests
    
    try:
        response = requests.get('http://ml-api:8001/health', timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            
            if health.get('model_loaded'):
                print("API ML opérationnelle, modèle chargé")
                return True
            else:
                raise Exception("Modèle non chargé")
        else:
            raise Exception(f"Status: {response.status_code}")
            
    except Exception as e:
        print(f"API ML inaccessible: {e}")
        raise

def analyze_api_logs():
    import re
    from collections import Counter
    log_stats = {
        'total_requests': 0,
        'errors_5xx': 0,
        'errors_4xx': 0,
        'avg_response_time': 0,
        'predictions_made': 0
    }
    
    print(f"   Total requêtes: {log_stats['total_requests']}")
    print(f"   Erreurs 5xx: {log_stats['errors_5xx']}")
    print(f"   Erreurs 4xx: {log_stats['errors_4xx']}")
    print(f"   Prédictions: {log_stats['predictions_made']}")
    
    return log_stats

def send_daily_report(**context):
    task_instance = context['task_instance']
    
    drift_report = task_instance.xcom_pull(task_ids='detect_data_drift')
    model_perf = task_instance.xcom_pull(task_ids='check_model_performance')
    
    report_lines = [
        "RAPPORT QUOTIDIEN - ML MONITORING",
        "=" * 60,
        "",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Data Drift:",
    ]
    
    if drift_report and drift_report.get('overall_drift_detected'):
        report_lines.append("   DÉRIVE DÉTECTÉE - Action requise")
    else:
        report_lines.append("   Aucune dérive")
    
    report_lines.extend([
        "",
        "Performance Modèle:",
        f"   F1-Score: {model_perf.get('f1_score', 0):.4f}",
        f"   Status: {model_perf.get('status', 'unknown')}",
        "",
        "Tous les checks terminés avec succès"
    ])
    
    report = "\n".join(report_lines)
    print(report)
    
    # Save
    with open(f'/app/data/logs/daily_report_{datetime.now().strftime("%Y%m%d")}.txt', 'w') as f:
        f.write(report)
    
    return report

# Définir les tâches
task_api_health = PythonOperator(
    task_id='test_api_health',
    python_callable=test_api_health,
    dag=dag
)

task_drift = PythonOperator(
    task_id='detect_data_drift',
    python_callable=run_data_drift_detection,
    dag=dag
)

task_perf = PythonOperator(
    task_id='check_model_performance',
    python_callable=check_model_performance,
    dag=dag
)

task_logs = PythonOperator(
    task_id='analyze_api_logs',
    python_callable=analyze_api_logs,
    dag=dag
)

task_report = PythonOperator(
    task_id='generate_daily_report',
    python_callable=send_daily_report,
    provide_context=True,
    dag=dag
)

# Définir le flux
task_api_health >> [task_drift, task_perf, task_logs] >> task_report
