import requests
import json
import pandas as pd
from bs4 import BeautifulSoup as bs


def get_company_data_from_trustpilot(company_name):
    """Récupère HTML"""

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/137.0.0.0 Safari/537.36"}

    page_url = "https://www.trustpilot.com/review/{}".format(company_name)
    page_html = requests.get(page_url, headers=headers)

    return page_html.content


def parse_company_data(company_data_html):
    """Parse HTML"""

    soup = bs(company_data_html, "lxml")

    company_raw_data = soup.find("script", attrs={"id": "__NEXT_DATA__"})

    company_json_data = json.loads(company_raw_data.text)

    company_details_data = company_json_data["props"]["pageProps"]["businessUnit"]

    if len(company_details_data['categories']) == 1:
        category = company_details_data['categories'][0]["name"]
    else:
        for item in company_details_data['categories']:
            if item['isPrimary'] is True:
                category = item["name"]

    company_dict_data = {
                        'id': company_details_data['id'],
                        'displayName': company_details_data['displayName'],
                        'profileImageUrl': company_details_data['profileImageUrl'],
                        'numberOfReviews': company_details_data['numberOfReviews'],
                        'trustScore': company_details_data['trustScore'],
                        'websiteUrl': company_details_data['websiteUrl'],
                        'stars': company_details_data['stars'],
                        'category': category,
                        'email': company_details_data['contactInfo']['email'],
                        'address': company_details_data['contactInfo']['address'],
                        'city': company_details_data['contactInfo']['city'],
                        'country': company_details_data['contactInfo']['country'],
                        'phone': company_details_data['contactInfo']['phone'],
                        'zipCode': company_details_data['contactInfo']['zipCode'],
                        'five_star_rating_count': soup.find("label", attrs={"data-star-rating": "five"}).attrs["title"].split(" of ")[0].replace(",",""),
                        'four_star_rating_count': soup.find("label", attrs={"data-star-rating": "four"}).attrs["title"].split(" of ")[0].replace(",",""),
                        'three_star_rating_count': soup.find("label", attrs={"data-star-rating": "three"}).attrs["title"].split(" of ")[0].replace(",",""),
                        'two_star_rating_count': soup.find("label", attrs={"data-star-rating": "two"}).attrs["title"].split(" of ")[0].replace(",",""),
                        'one_star_rating_count': soup.find("label", attrs={"data-star-rating": "one"}).attrs["title"].split(" of ")[0].replace(",",""),
                        }

    return company_dict_data


def create_company_data_dataframe(company_list):
    """Crée dataframe"""
    # DataFrame
    temp_df = pd.DataFrame()

    # Boucle
    for company in company_list:
        # Parse
        company_html = get_company_data_from_trustpilot(company)
        company_row = parse_company_data(company_html)
        # Concat
        temp_df = pd.concat([temp_df, pd.DataFrame([company_row])], ignore_index=False)

    # Index
    temp_df = temp_df.set_index('id')

    return temp_df


def insert_company_metadatas_from_csv_in_sql(csv_file, conn):
    """Insere SQL"""
    companies_df = pd.read_csv(csv_file, dtype='str')
    cur= conn.cursor()

    for company in companies_df.itertuples(index=False):
        # 1. Catégorie
        sql_insert_request = """
                             INSERT INTO Category (category_name)
                             VALUES ('{category}')
                             ON CONFLICT (category_name) DO NOTHING;
                             """.format(
                                        category=company.category
                                        )

        cur.execute(sql_insert_request)

        # 2. Entreprise
        sql_insert_request = """
                             INSERT INTO Entreprise (entreprise_id, entreprise_name, profileImageUrl, mail, phone, web_site, category_id)
                             VALUES ('{entreprise_id}','{entreprise_name}','{profileImageUrl}','{mail}','{phone}','{web_site}',(select category_id from Category where category_name = '{category}'))
                             ON CONFLICT (entreprise_id) DO
                             UPDATE
                             SET profileImageUrl = EXCLUDED.profileImageUrl, 
                                 mail = EXCLUDED.mail, 
                                 phone = EXCLUDED.phone, 
                                 web_site = EXCLUDED.web_site,
                                 category_id = EXCLUDED.category_id;
                             """.format(
                                        entreprise_id = company.id, 
                                        entreprise_name = company.displayName, 
                                        profileImageUrl = company.profileImageUrl, 
                                        mail = company.email, 
                                        phone = company.phone, 
                                        web_site = company.websiteUrl, 
                                        category = company.category
                                        )
        
        cur.execute(sql_insert_request)

        # 3. Adresse
        sql_insert_request = """
                             INSERT INTO Address (entreprise_id, street, zip_code, city, country)
                             VALUES ('{entreprise_id}','{street}','{zip_code}','{city}','{country}')
                             ON CONFLICT (entreprise_id) DO 
                             UPDATE
                             SET street = EXCLUDED.street, 
                                 zip_code = EXCLUDED.zip_code, 
                                 city = EXCLUDED.city, 
                                 country = EXCLUDED.country;
                             """.format(
                                        entreprise_id = company.id, 
                                        street = company.address, 
                                        zip_code = company.zipCode, 
                                        city = company.phone, 
                                        country = company.country
                                        )
        cur.execute(sql_insert_request)

        # 4. Note
        sql_insert_request = """
                             INSERT INTO Rating (entreprise_id, one_star, two_star, three_star, four_star, five_star, trustScore)
                             VALUES ('{entreprise_id}','{one_star}','{two_star}','{three_star}','{four_star}','{five_star}','{trustScore}')
                             ON CONFLICT (entreprise_id) DO
                             UPDATE
                             SET one_star = EXCLUDED.one_star, 
                                 two_star = EXCLUDED.two_star, 
                                 three_star = EXCLUDED.three_star, 
                                 four_star = EXCLUDED.four_star,
                                 five_star = EXCLUDED.five_star,
                                 trustScore = EXCLUDED.trustScore;
                             """.format(
                                        entreprise_id = company.id, 
                                        one_star = company.one_star_rating_count, 
                                        two_star = company.two_star_rating_count, 
                                        three_star = company.three_star_rating_count, 
                                        four_star = company.four_star_rating_count, 
                                        five_star = company.five_star_rating_count, 
                                        trustScore = company.trustScore
                                        )
        cur.execute(sql_insert_request)
    
    conn.commit()
    cur.close()


def test_get_company_data_from_trustpilot():
    company = "www.showroomprive.com"
    html = get_company_data_from_trustpilot(company)
    output = str(html).find(company)

    assert output != -1


def test_parse_company_data():
    company = "www.showroomprive.com"
    html = get_company_data_from_trustpilot(company)
    data = parse_company_data(html)
    output = data["displayName"]

    assert output == "Showroomprive"

