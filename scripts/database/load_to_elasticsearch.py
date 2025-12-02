"""
Script pour charger les avis clients dans Elasticsearch
À partir des données JSON scrapées de Trustpilot
"""
import json
from elasticsearch import Elasticsearch, helpers
from pathlib import Path
from typing import List, Dict
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    def __init__(self, host='localhost', port=9200, scheme='http'):
        """Initialiser la connexion Elasticsearch"""
        # Essayer avec et sans authentification
        try:
            self.es = Elasticsearch(
                [{'host': host, 'port': port, 'scheme': scheme}],
                basic_auth=('elastic', 'elastic123')
            )
            if not self.es.ping():
                # Réessayer sans authentification
                self.es = Elasticsearch(
                    [{'host': host, 'port': port, 'scheme': scheme}]
                )
        except:
            # Fallback sans authentification
            self.es = Elasticsearch(
                [{'host': host, 'port': port, 'scheme': scheme}]
            )
        self.index_name = 'trustpilot_reviews'
    
    def check_connection(self) -> bool:
        """Vérifier la connexion à Elasticsearch"""
        try:
            # Utiliser info() plutôt que ping() car ping() peut retourner 400
            info = self.es.info()
            if info:
                logger.info("✓ Connexion à Elasticsearch établie")
                logger.info(f"  Version: {info['version']['number']}")
                return True
            else:
                logger.error("✗ Impossible de se connecter à Elasticsearch")
                return False
        except Exception as e:
            logger.error(f"✗ Erreur de connexion Elasticsearch: {e}")
            return False
    
    def create_index(self):
        """Créer l'index avec le mapping approprié"""
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "french_analyzer": {
                            "type": "standard",
                            "stopwords": "_french_"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "company_name": {
                        "type": "keyword"
                    },
                    "company_url": {
                        "type": "keyword"
                    },
                    "review_id": {
                        "type": "keyword"
                    },
                    "reviewer_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "reviewer_reviews_count": {
                        "type": "integer"
                    },
                    "rating": {
                        "type": "integer"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "french_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "french_analyzer"
                    },
                    "date": {
                        "type": "date",
                        "format": "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSS'Z'||epoch_millis"
                    },
                    "experience_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSS'Z'||epoch_millis"
                    },
                    "company_reply": {
                        "type": "object",
                        "enabled": False
                    },
                    "review_link": {
                        "type": "keyword"
                    },
                    "verified": {
                        "type": "boolean"
                    },
                    "scraped_at": {
                        "type": "date"
                    }
                }
            }
        }
        
        try:
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"ℹ Index '{self.index_name}' existe déjà")
                return True
            
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✓ Index '{self.index_name}' créé avec succès")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur création index: {e}")
            return False
    
    def load_json_files(self, data_dir: str) -> List[Dict]:
        """Charger tous les fichiers JSON du répertoire"""
        data_dir = Path(data_dir)
        all_reviews = []
        
        # Chercher les fichiers *_reviews.json et *_test.json
        json_files = list(data_dir.glob("*_reviews.json")) + list(data_dir.glob("*_test.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    company_info = data.get('company_info', {})
                    reviews = data.get('reviews', [])
                    
                    # Enrichir chaque avis avec les infos de l'entreprise
                    for review in reviews:
                        review['company_name'] = company_info.get('company_name', 'Unknown')
                        review['company_url'] = company_info.get('company_url', '')
                        review['scraped_at'] = datetime.now().isoformat()
                    
                    all_reviews.extend(reviews)
                    logger.info(f"✓ Chargé: {json_file.name} ({len(reviews)} avis)")
                    
            except Exception as e:
                logger.error(f"✗ Erreur lecture {json_file}: {e}")
        
        return all_reviews
    
    def prepare_bulk_actions(self, reviews: List[Dict]):
        """Préparer les actions pour bulk insert"""
        for review in reviews:
            # Générer un ID unique pour l'avis
            review_id = review.get('review_link', '').split('/')[-1]
            if not review_id:
                review_id = f"{review.get('company_name', 'unknown')}_{review.get('reviewer_name', 'anon')}_{review.get('date', 'unknown')}"
                review_id = review_id.replace(' ', '_').replace('/', '_')
            
            yield {
                "_index": self.index_name,
                "_id": review_id,
                "_source": review
            }
    
    def bulk_load_reviews(self, data_dir: str):
        """Charger tous les avis dans Elasticsearch"""
        if not self.check_connection():
            return False
        
        if not self.create_index():
            return False
        
        try:
            reviews = self.load_json_files(data_dir)
            logger.info(f"📊 {len(reviews)} avis à charger")
            
            if not reviews:
                logger.warning("⚠ Aucun avis trouvé")
                return False
            
            # Bulk insert
            success, failed = helpers.bulk(
                self.es,
                self.prepare_bulk_actions(reviews),
                stats_only=False,
                raise_on_error=False
            )
            
            logger.info(f"✓ {success} avis chargés avec succès")
            if failed:
                logger.warning(f"⚠ {len(failed)} avis ont échoué")
                # Afficher quelques exemples d'erreurs
                for i, error in enumerate(failed[:3]):
                    logger.error(f"  Exemple d'erreur {i+1}: {error}")
            
            # Rafraîchir l'index
            self.es.indices.refresh(index=self.index_name)
            
            # Afficher les statistiques
            count = self.es.count(index=self.index_name)
            logger.info(f"📊 Total avis dans l'index: {count['count']}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erreur lors du chargement: {e}")
            return False
    
    def get_index_stats(self):
        """Obtenir les statistiques de l'index"""
        try:
            stats = self.es.indices.stats(index=self.index_name)
            count = self.es.count(index=self.index_name)
            
            print("\n=== Statistiques Elasticsearch ===")
            print(f"Index: {self.index_name}")
            print(f"Documents: {count['count']}")
            print(f"Taille: {stats['_all']['primaries']['store']['size_in_bytes'] / 1024 / 1024:.2f} MB")
            print("==================================\n")
            
        except Exception as e:
            logger.error(f"Erreur statistiques: {e}")
    
    def sample_query(self):
        """Exemple de requête pour tester"""
        try:
            # Top 10 avis les mieux notés
            query = {
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {"rating": {"order": "desc"}},
                    {"date": {"order": "desc"}}
                ],
                "size": 10
            }
            
            results = self.es.search(index=self.index_name, body=query)
            
            print("\n=== Exemple: Top 10 avis récents bien notés ===")
            for hit in results['hits']['hits']:
                source = hit['_source']
                print(f"\n★ {source.get('rating', 0)}/5 - {source.get('company_name', 'N/A')}")
                print(f"  Par: {source.get('reviewer_name', 'Anonyme')} ({source.get('date', 'N/A')})")
                print(f"  Titre: {source.get('title', 'N/A')[:80]}...")
            print("=" * 50 + "\n")
            
        except Exception as e:
            logger.error(f"Erreur requête exemple: {e}")


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Charger les avis Trustpilot dans Elasticsearch')
    parser.add_argument('--data-dir', default='../data/raw',
                        help='Répertoire contenant les fichiers JSON')
    parser.add_argument('--host', default='localhost', help='Hôte Elasticsearch')
    parser.add_argument('--port', type=int, default=9200, help='Port Elasticsearch')
    parser.add_argument('--stats', action='store_true', help='Afficher les statistiques après chargement')
    parser.add_argument('--sample', action='store_true', help='Afficher un exemple de requête')
    
    args = parser.parse_args()
    
    loader = ElasticsearchLoader(host=args.host, port=args.port)
    
    success = loader.bulk_load_reviews(args.data_dir)
    
    if success:
        print("\n✓ Chargement terminé avec succès!")
        
        if args.stats:
            loader.get_index_stats()
        
        if args.sample:
            loader.sample_query()
    else:
        print("\n✗ Échec du chargement")
        exit(1)


if __name__ == "__main__":
    main()
