import pandas as pd
import psycopg2

def db_connect():
    conn = psycopg2.connect(database="companies_db",
                            host="127.0.0.1",
                            user="user",
                            password="password",
                            port="5432")
    return conn

def insert_company_metadatas_from_csv_in_sql(csv_file, conn):
    companies_df = pd.read_csv(csv_file)
    cur= conn.cursor()

    for company in companies_df.itertuples(index=False):
        # step 1: insert category in Category table if not already exists
        sql_insert_request = """
                             INSERT INTO Category (category_name)
                             VALUES ('{}')
                             ON CONFLICT (category_name) DO NOTHING;
                             """.format(company.category)
        cur.execute(sql_insert_request)

        # step 2: insert entreprise in Entreprise table if not already exists
        sql_insert_request = """
                             INSERT INTO Entreprise (entreprise_id, entreprise_name, mail, phone, web_site, category_id)
                             VALUES ('{}','{}','{}','{}','{}',(select category_id from Category where category_name = '{}'))
                             ON CONFLICT (entreprise_id) DO NOTHING;
                             """.format(company.id, company.displayName, company.email, company.phone, company.websiteUrl, company.category)
        cur.execute(sql_insert_request)

        # step 3: insert entreprise address details in Address table
        sql_insert_request = """
                             INSERT INTO Address (entreprise_id, street, zip_code, city, country)
                             VALUES ('{}','{}','{}','{}','{}')
                             ON CONFLICT (entreprise_id) DO NOTHING;
                             """.format(company.id, company.address, company.zipCode, company.phone, company.country)
        cur.execute(sql_insert_request)

        # step 4: insert entreprise rating details in rating table
        sql_insert_request = """
                             INSERT INTO Rating (entreprise_id, one_star, two_star, three_star, four_star, five_star)
                             VALUES ('{}','{}','{}','{}','{}','{}')
                             ON CONFLICT (entreprise_id) DO NOTHING;
                             """.format(company.id, company.one_star_rating_count, company.two_star_rating_count, company.three_star_rating_count, company.four_star_rating_count, company.five_star_rating_count)
        cur.execute(sql_insert_request)
    
    conn.commit()
    cur.close()
    conn.close()

def create_company_metadata_tables(conn):
    cur = conn.cursor()

    request = """
    CREATE TABLE IF NOT EXISTS Category (
        category_id serial PRIMARY KEY, 
        category_name varchar(120) UNIQUE NOT NULL);

    CREATE TABLE IF NOT EXISTS Entreprise (
        entreprise_id varchar(256) PRIMARY KEY,
        entreprise_name varchar(256) NOT NULL,
        mail varchar(150) DEFAULT NULL,
        phone varchar(50) DEFAULT NULL,
        web_site varchar(150),
        category_id integer REFERENCES Category (category_id));

    CREATE TABLE IF NOT EXISTS Address (
        entreprise_id varchar(256) PRIMARY KEY REFERENCES Entreprise (entreprise_id),
        street varchar(256) DEFAULT NULL,
        zip_code varchar(50) DEFAULT NULL,
        city varchar(85) DEFAULT NULL,
        country varchar(56) DEFAULT NULL);

    CREATE TABLE IF NOT EXISTS Rating (
        entreprise_id varchar(256) PRIMARY KEY REFERENCES Entreprise (entreprise_id),
        one_star integer NOT NULL,
        two_star integer NOT NULL,
        three_star integer NOT NULL,
        four_star integer NOT NULL,
        five_star integer NOT NULL);
    """

    cur.execute(request)
    conn.commit()
    cur.close()
    conn.close()

def execute_db_request(conn,sql_request):
    cur = conn.cursor()
    try:
        cur.execute(sql_request)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erreur: {e}")
    cur.close()
    conn.close()


create_company_metadata_tables(db_connect())

insert_company_metadatas_from_csv_in_sql("/root/datascientest/projet_formation/sep25_bde_satisfaction_b/volumes/etl_elt/companies_metadatas.csv", db_connect())

