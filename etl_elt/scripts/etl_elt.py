"""Pipeline ETL"""

import time
from scrape_company_metadatas import *
#from insert_company_metadatas_in_sql import *
import os
import psycopg2

POSTGRES_SRV_ADDRESS = os.getenv('POSTGRES_SRV_ADDRESS', '127.0.0.1')
POSTGRES_SRV_PORT = os.getenv('POSTGRES_SRV_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'companies_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'troubadour')

def main_etl_elt():

    # int/out folders
    outputFolder = "/app/extracts/"
    scriptFolder = "/app/scripts/"

    """Main ETL"""
    # TODO
    company_list = ["www.showroomprive.com", "loaded.com", "westernunion.com", "justfly.com", "www.facebook.com"]

    # Collect
    companies_metadatas_df = create_company_data_dataframe(company_list)

    # CSV
    # optionnel
    companies_metadatas_df.to_csv(outputFolder + "companies_metadatas.csv")

    # SQL tables
    # 1er run
    conn = psycopg2.connect(
                            database=POSTGRES_DB,
                            host=POSTGRES_SRV_ADDRESS,
                            user=POSTGRES_USER,
                            password=POSTGRES_PASSWORD,
                            port=POSTGRES_SRV_PORT)

    
    conn.cursor().execute(open(scriptFolder + "postgres_schema.sql", "r").read())
    
    # Insert SQL

    insert_company_metadatas_from_csv_in_sql(outputFolder + "companies_metadatas.csv", conn)

    conn.close()

    # Pause Docker
    #time.sleep(5)


if __name__ == "__main__":
    print("Démarrage du script ETL...")
    main_etl_elt()
    print("Processus ETL/ELT terminés")
