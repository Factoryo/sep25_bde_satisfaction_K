import requests
import json
import pandas as pd
from bs4 import BeautifulSoup as bs


def get_company_data_from_trustpilot(company_name):
    """
    Get HTML code from Trustpilot website review page

    Args:
        company_name (str): Name of the company.

    Returns:
        str: Text content of the HTML code
    """

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/137.0.0.0 Safari/537.36"}

    page_url = "https://www.trustpilot.com/review/{}".format(company_name)
    page_html = requests.get(page_url, headers=headers)

    return page_html.content


def parse_company_data(company_data_html):
    """
    Parses HTML content to extract company information

    Args:
        company_data_html (bytes): bytes object containing the HTML content

    Returns:
        dict: company information
    """

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
    """
    Collect information of companies and store it in a dataframe.

    Args:
        company_list (list(str)): list of company names

    Returns:
        dataFrame: company information
    """
    # create an empty dataframe to store gathered company information
    temp_df = pd.DataFrame()

    # loop to get company information and store it in companies_df dataframe
    for company in company_list:
        # collect and parse information of the company
        company_html = get_company_data_from_trustpilot(company)
        company_row = parse_company_data(company_html)
        # store collected information as a new raw in companies_df dataframe
        temp_df = pd.concat([temp_df, pd.DataFrame([company_row])], ignore_index=False)

    # set the companies_df index to 'id' column
    temp_df = temp_df.set_index('id')

    return temp_df


def insert_company_metadatas_from_csv_in_sql(csv_file, conn):
    """
    Launch information about companies from csv file in a dataframe.
    Stores this df in Postgresql server

    Args:
        csv_file (str): path to CSV file
        conn: db connection object
    Returns:
        nothing
    """
    companies_df = pd.read_csv(csv_file, dtype='str')
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
                             INSERT INTO Entreprise (entreprise_id, entreprise_name, profileImageUrl, mail, phone, web_site, category_id)
                             VALUES ('{}','{}','{}','{}','{}','{}',(select category_id from Category where category_name = '{}'))
                             ON CONFLICT (entreprise_id) DO NOTHING;
                             """.format(company.id, company.displayName, company.profileImageUrl, company.email, company.phone, company.websiteUrl, company.category)
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
                             INSERT INTO Rating (entreprise_id, one_star, two_star, three_star, four_star, five_star, trustScore)
                             VALUES ('{}','{}','{}','{}','{}','{}','{}')
                             ON CONFLICT (entreprise_id) DO NOTHING;
                             """.format(company.id, company.one_star_rating_count, company.two_star_rating_count, company.three_star_rating_count, company.four_star_rating_count, company.five_star_rating_count, company.trustScore)
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

