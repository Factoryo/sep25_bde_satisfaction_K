"""
Module ETL (Extract, Transform, Load)

Ce fichier servira de point d'entrée pour orchestrer le pipeline ETL.
Les fonctions d'extraction, de transformation et de chargement seront
appelées ici lorsque le code sera prêt.
"""

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

    """Fonction principale du pipeline ETL."""
    # TODO: Appelez les fonctions ici (extraction, transformation, chargement)
    company_list = ["www.showroomprive.com", "loaded.com", "westernunion.com", "justfly.com", "www.facebook.com"]

    # collect company metadatas in a dataframe
    companies_metadatas_df = create_company_data_dataframe(company_list)

    # write the content of companies_df to a csv file
    # useless step in "real world", we could directly jump to inserting data in sql
    companies_metadatas_df.to_csv(outputFolder + "companies_metadatas.csv")

    # create tables and views in sql
    # will only have impact on first run
    conn = psycopg2.connect(
                            database=POSTGRES_DB,
                            host=POSTGRES_SRV_ADDRESS,
                            user=POSTGRES_USER,
                            password=POSTGRES_PASSWORD,
                            port=POSTGRES_SRV_PORT)

    
    conn.cursor().execute(open(scriptFolder + "postgres_schema.sql", "r").read())
    
    # read the content of csv file to a dataframe
    # in "real world", we would have directly used previous dataframe
    # postgres_database, postgres_host, postgres_user, postgres_password, postgres_port

    insert_company_metadatas_from_csv_in_sql(outputFolder + "companies_metadatas.csv", conn)

    conn.close()

    # Petit délai pour éviter la fermeture immédiate du conteneur Docker
    time.sleep(5)


if __name__ == "__main__":
    print("Démarrage du script ETL...")
    main_etl_elt()
