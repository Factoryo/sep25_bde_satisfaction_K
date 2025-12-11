"""Chargement PostgreSQL"""
import json
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class PostgresLoader:
    def __init__(self, host='localhost', port=5432, database='trustpilot_db', 
                 user='trustpilot_user', password='trustpilot_pass'):
        """Init"""
        self.conn_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connexion"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
            logger.info("Connexion à PostgreSQL établie")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion PostgreSQL: {e}")
            return False
    
    def close(self):
        """Fermeture"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Connexion PostgreSQL fermée")
    
    def load_json_files(self, data_dir: str) -> List[Dict]:
        """Charge JSON"""
        data_dir = Path(data_dir)
        companies_data = []
        
        # Fichiers
        json_files = list(data_dir.glob("*_reviews.json")) + list(data_dir.glob("*_test.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'company_info' in data:
                        companies_data.append(data['company_info'])
                        logger.info(f"Chargé: {json_file.name}")
            except Exception as e:
                logger.error(f"Erreur lecture {json_file}: {e}")
        
        return companies_data
    
    def insert_category(self, category_name: str) -> int:
        """Insérer catégorie"""
        if not category_name:
            category_name = "Unknown"
        
        try:
            self.cursor.execute(
                (category_name,)
            )
            category_id = self.cursor.fetchone()[0]
            return category_id
        except Exception as e:
            logger.error(f"Erreur insertion catégorie: {e}")
            return None
    
    def insert_entreprise(self, company_data: Dict, category_id: int):
        """Insert entreprise"""
        try:
            # ID
            entreprise_id = company_data.get('company_url', '').replace('https://fr.trustpilot.com/review/', '')
            if not entreprise_id:
                entreprise_id = company_data.get('company_name', 'unknown').lower().replace(' ', '-')
            
            # Insert
            self.cursor.execute(
                (
                    entreprise_id,
                    company_data.get('company_name', 'Unknown'),
                    company_data.get('contact_info', {}).get('email'),
                    company_data.get('contact_info', {}).get('phone'),
                    company_data.get('website', company_data.get('company_url')),
                    category_id
                )
            )
            
            # Notes
            total_reviews = company_data.get('total_reviews', 0)
            trustscore = company_data.get('trustscore', 0.0) or company_data.get('trust_score', 0.0)
            
            # Distribution estimée
            if trustscore >= 4.5:
                five_star = int(total_reviews * 0.7)
                four_star = int(total_reviews * 0.2)
                three_star = int(total_reviews * 0.05)
                two_star = int(total_reviews * 0.03)
                one_star = total_reviews - five_star - four_star - three_star - two_star
            elif trustscore >= 3.5:
                five_star = int(total_reviews * 0.4)
                four_star = int(total_reviews * 0.3)
                three_star = int(total_reviews * 0.15)
                two_star = int(total_reviews * 0.1)
                one_star = total_reviews - five_star - four_star - three_star - two_star
            else:
                five_star = int(total_reviews * 0.2)
                four_star = int(total_reviews * 0.2)
                three_star = int(total_reviews * 0.2)
                two_star = int(total_reviews * 0.2)
                one_star = total_reviews - five_star - four_star - three_star - two_star
            
            self.cursor.execute(
                (entreprise_id, float(trustscore), one_star, two_star, three_star, four_star, five_star)
            )
            
            # Adresse
            if 'address' in company_data or 'location' in company_data:
                address = company_data.get('address', company_data.get('location', {}))
                self.cursor.execute(
                    (
                        entreprise_id,
                        address.get('street'),
                        address.get('zip_code'),
                        address.get('city'),
                        address.get('country')
                    )
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur d'insertion des entreprise {company_data.get('company_name')}: {e}")
            return False
    
    def load_companies_to_postgres(self, data_dir: str):
        """Charge PostgreSQL"""
        if not self.connect():
            return False
        
        try:
            companies_data = self.load_json_files(data_dir)
            logger.info(f"{len(companies_data)} entreprises à charger")
            
            success_count = 0
            
            for company in companies_data:
                # Catégorie
                categories = company.get('categories', [])
                category_name = categories[0] if categories else "General"
                
                # Insérer la catégorie
                category_id = self.insert_category(category_name)
                
                if category_id:
                    # Insérer l'entreprise
                    if self.insert_entreprise(company, category_id):
                        success_count += 1
            
            # Commit
            self.conn.commit()
            logger.info(f"{success_count}/{len(companies_data)} entreprises chargées avec succès")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            self.close()


def main():
    """Point d'entrée"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Charger les données Trustpilot dans PostgreSQL')
    parser.add_argument('--data-dir', default='../data/raw', 
                        help='Répertoire contenant les fichiers JSON')
    parser.add_argument('--host', default='localhost', help='Hôte PostgreSQL')
    parser.add_argument('--port', type=int, default=5432, help='Port PostgreSQL')
    parser.add_argument('--database', default='trustpilot_db', help='Nom de la base de données')
    parser.add_argument('--user', default='trustpilot_user', help='Utilisateur PostgreSQL')
    parser.add_argument('--password', default='trustpilot_pass', help='Mot de passe PostgreSQL')
    
    args = parser.parse_args()
    
    loader = PostgresLoader(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )
    
    success = loader.load_companies_to_postgres(args.data_dir)
    
    if success:
        print("\nChargement terminé")
    else:
        print("\nÉchec du chargement")
        exit(1)


if __name__ == "__main__":
    main()
