"""Chargement de toutes les données"""
import sys
import time
import argparse
from pathlib import Path

# Chemin
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from load_to_postgres import PostgresLoader
from load_to_elasticsearch import ElasticsearchLoader


def print_header(text):
    """Affiche en-tête"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def wait_for_services():
    """Vérifie les services"""
    import psycopg2
    from elasticsearch import Elasticsearch
    
    print_header("Vérification des services")
    
    # PostgreSQL
    print("Chargement de PostgreSQL...")
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='trustpilot_db',
                user='trustpilot_user',
                password='trustpilot_pass'
            )
            conn.close()
            print("PostgreSQL est prêt")
            break
        except Exception as e:
            if i == max_retries - 1:
                print(f"PostgreSQL non disponible après {max_retries} tentatives")
                return False
            time.sleep(2)
    
    # Elasticsearch
    print("Chargement d'Elasticsearch...")
    for i in range(max_retries):
        try:
            es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
            # Info()
            info = es.info()
            if info:
                print("Elasticsearch est prêt")
                break
        except Exception as e:
            if i == max_retries - 1:
                print(f"Elasticsearch non disponible après {max_retries} tentatives")
                return False
            time.sleep(2)
    
    return True


def load_postgres_data(data_dir: str, host='localhost', port=5432):
    """Charge PostgreSQL"""
    print_header("Chargement PostgreSQL")
    
    loader = PostgresLoader(
        host=host,
        port=port,
        database='trustpilot_db',
        user='trustpilot_user',
        password='trustpilot_pass'
    )
    
    success = loader.load_companies_to_postgres(data_dir)
    return success


def load_elasticsearch_data(data_dir: str, host='localhost', port=9200):
    """Charge Elasticsearch"""
    print_header("Chargement Elasticsearch")
    
    loader = ElasticsearchLoader(host=host, port=port)
    success = loader.bulk_load_reviews(data_dir)
    
    if success:
        loader.get_index_stats()
    
    return success


def verify_data():
    """Vérifie les données"""
    print_header("Vérification des données")
    
    import psycopg2
    from elasticsearch import Elasticsearch
    
    # PostgreSQL
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='trustpilot_db',
            user='trustpilot_user',
            password='trustpilot_pass'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Entreprise")
        result = cursor.fetchone()
        entreprise_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM Rating")
        result = cursor.fetchone()
        rating_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM Category")
        result = cursor.fetchone()
        category_count = result[0] if result else 0
        
        print(f"PostgreSQL:")
        print(f"  - {entreprise_count} entreprises")
        print(f"  - {rating_count} ratings")
        print(f"  - {category_count} catégories")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur vérification PostgreSQL: {e}")
    
    # Elasticsearch
    try:
        es = Elasticsearch(
            [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
            basic_auth=('elastic', 'elastic123')
        )
        
        count = es.count(index='trustpilot_reviews')
        print(f"\nElasticsearch:")
        print(f"  - {count['count']} avis")
        
    except Exception as e:
        print(f"Erreur vérification Elasticsearch: {e}")


def show_next_steps():
    print_header("Prochaines étapes")
    print("Données chargées\n")
    print("Vous pouvez maintenant:")
    print("  1. Accéder à Kibana: http://localhost:5601")
    print("     - Créer l'index pattern 'trustpilot_reviews'")
    print("     - Créer les visualisations et le dashboard")
    print("     - Voir: docs/KIBANA_SETUP.md pour les instructions\n")
    print("  2. Exécuter les requêtes SQL:")
    print("     - Voir: scripts/database/sql_queries.sql")
    print("     - Utiliser pgAdmin ou psql pour se connecter\n")
    print("  3. Accéder à PostgreSQL:")
    print("     Host: localhost:5432")
    print("     Database: trustpilot_db")
    print("     User: trustpilot_user")
    print("     Password: trustpilot_pass\n")
    print("  4. Accéder à Elasticsearch:")
    print("     URL: http://localhost:9200")
    print("     User: elastic")
    print("     Password: elastic123\n")


def main():
    """Point d'entrée"""
    parser = argparse.ArgumentParser(
        description='Charger les données Trustpilot dans PostgreSQL et Elasticsearch'
    )
    parser.add_argument(
        '--data-dir',
        default='data/raw',
        help='Répertoire contenant les fichiers JSON (défaut: data/raw)'
    )
    parser.add_argument(
        '--skip-postgres',
        action='store_true',
        help='Ne pas charger PostgreSQL'
    )
    parser.add_argument(
        '--skip-elasticsearch',
        action='store_true',
        help='Ne pas charger Elasticsearch'
    )
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='Ne pas attendre que les services soient prêts'
    )
    parser.add_argument(
        '--pg-host',
        default='localhost',
        help='Hôte PostgreSQL (défaut: localhost)'
    )
    parser.add_argument(
        '--pg-port',
        type=int,
        default=5432,
        help='Port PostgreSQL (défaut: 5432)'
    )
    parser.add_argument(
        '--es-host',
        default='localhost',
        help='Hôte Elasticsearch (défaut: localhost)'
    )
    parser.add_argument(
        '--es-port',
        type=int,
        default=9200,
        help='Port Elasticsearch (défaut: 9200)'
    )
    
    args = parser.parse_args()
    
    # Répertoire
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Le répertoire {data_dir} n'existe pas")
        print(f"  Veuillez d'abord scraper des données avec:")
        print(f"  python etl_elt/scripts/test_mass_scraping.py")
        return 1
    
    # Fichiers JSON
    json_files = list(data_dir.glob("*_reviews.json")) + list(data_dir.glob("*_test.json"))
    if not json_files:
        print(f"Aucun fichier *_reviews.json ou *_test.json trouvé dans {data_dir}")
        print(f"  Veuillez d'abord scraper des données")
        return 1
    
    print(f"Répertoire de données: {data_dir.absolute()}")
    print(f"{len(json_files)} fichiers JSON trouvés")
    
    # Services
    if not args.no_wait:
        if not wait_for_services():
            print("\nLes services ne sont pas disponibles")
            print("  Assurez-vous que Docker Desktop est lancé")
            return 1
    
    success = True
    
    # PostgreSQL
    if not args.skip_postgres:
        if not load_postgres_data(str(data_dir), args.pg_host, args.pg_port):
            print("Échec du chargement PostgreSQL")
            success = False
    
    # Elasticsearch
    if not args.skip_elasticsearch:
        if not load_elasticsearch_data(str(data_dir), args.es_host, args.es_port):
            print("Échec du chargement Elasticsearch")
            success = False
    
    # Vérif
    if success:
        verify_data()
        show_next_steps()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
