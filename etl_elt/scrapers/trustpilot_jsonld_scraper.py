import json
import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin
import os
from datetime import datetime

class TrustpilotJSONLDScraper:
    """
    Scraper Trustpilot qui extrait les avis depuis le HTML.
    
    J'ai testé plusieurs approches :
    - API Trustpilot : pas publique, besoin d'un partenariat
    - JSON-LD embarqué : marche bien mais limité à ~20 avis/page
    - Parsing HTML direct : c'est ce que je fais ici
    
    Attention : Trustpilot bloque si on va trop vite (d'où le delay).
    """
    def __init__(self, delay: float = 3.0, max_pages: int = 3):
        self.delay = delay  # Pause entre requêtes pour éviter le ban
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.logger = logging.getLogger(__name__)

    def extract_company_info(self, soup: BeautifulSoup, company_name: str) -> Dict:
        """Récupère le TrustScore et le nombre total d'avis de l'entreprise."""
        company_info = {
            'company_name': company_name,
            'trustscore': '',
            'review_count': '',
            'rating': ''
        }
        
        try:
            # Score
            trustscore_element = soup.select_one('span.CDS_Typography_heading-l__dd9b51')
            if trustscore_element:
                company_info['trustscore'] = trustscore_element.get_text(strip=True)
            
            # Avis
            reviews_element = soup.find('span', string=re.compile(r'reviews', re.I))
            if reviews_element:
                text = reviews_element.get_text(strip=True)
                count_match = re.search(r'([\d,]+)', text)
                if count_match:
                    company_info['review_count'] = count_match.group(1).replace(',', '')
            
            self.logger.info(f"Infos entreprise: {company_info}")
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction infos entreprise: {e}")
        
        return company_info

    def extract_reviews_from_html(self, soup: BeautifulSoup, company_name: str) -> List[Dict]:
        """
        Parse les cartes d'avis de la page.
        
        Chaque avis est dans un <article class="styles_reviewCard__meSdm">.
        Le sélecteur CSS peut changer si Trustpilot met à jour son design.
        """
        reviews = []

        review_elements = soup.select('article.styles_reviewCard__meSdm')
        
        self.logger.info(f"Éléments review trouvés: {len(review_elements)}")
        
        for element in review_elements:
            try:
                review = self.parse_review_element_final(element, company_name)
                if review and review.get('author'):
                    reviews.append(review)
            except Exception as e:
                self.logger.debug(f"Erreur parsing review: {e}")
                continue
        
        return reviews

    def parse_review_element_final(self, element, company_name: str) -> Dict:
        """Extrait toutes les infos d'un avis : auteur, note, titre, contenu, date."""
        review = {
            'company_name': company_name,
            'author': '',
            'author_review_count': '',
            'date_absolute': '',
            'date_relative': '',
            'rating': 0,
            'title': '',
            'content': '',
            'review_link': '',
            'company_response': {
                'exists': False,
                'date': '',
                'content': ''
            }
        }

        author_element = element.select_one('a[data-consumer-profile-link] span.CDS_Typography_heading-xs__dd9b51')
        if author_element:
            review['author'] = author_element.get_text(strip=True)

        count_element = element.select_one('div.styles_consumerExtraDetails__9xAlV')
        if count_element:
            count_text = count_element.get_text(strip=True)
            count_match = re.search(r'(\d+)\s+reviews?', count_text)
            if count_match:
                review['author_review_count'] = int(count_match.group(1))

        date_element = element.select_one('time')
        if date_element:
            review['date_absolute'] = date_element.get('datetime', '')
            review['date_relative'] = date_element.get_text(strip=True)

        rating_element = element.select_one('img[alt*="out of"]')
        if rating_element:
            alt_text = rating_element.get('alt', '')
            rating_match = re.search(r'(\d+(?:\.\d+)?)\s*out of 5', alt_text)
            if rating_match:
                review['rating'] = float(rating_match.group(1))

        title_element = element.select_one('h2.CDS_Typography_heading-s__dd9b51')
        if not title_element:
            potential_titles = element.find_all(['span', 'div'], class_=re.compile(r'typography', re.I))
            for elem in potential_titles:
                text = elem.get_text(strip=True)
                if text and len(text) > 10 and len(text) < 100:
                    review['title'] = text
                    break
        
        content_elements = element.select('p.CDS_Typography_body-l__dd9b51, div.CDS_Typography_body-l__dd9b51')
        for content_elem in content_elements:
            text = content_elem.get_text(strip=True)
            if text and len(text) > 20:  
                review['content'] = text
                break

        if not review['content']:
            all_text_elements = element.find_all(['p', 'div', 'span'], string=True)
            for elem in all_text_elements:
                text = elem.get_text(strip=True)
                if text and 50 < len(text) < 1000 and not any(excluded in text for excluded in ['reviews', 'days ago', 'Rated']):
                    review['content'] = text
                    break
        
        link_element = element.select_one('a[href*="/review/"]')
        if link_element and 'href' in link_element.attrs:
            review['review_link'] = urljoin('https://www.trustpilot.com', link_element['href'])
        
        response_element = element.select_one('div.styles_businessResponse__1Sd7_')
        if response_element:
            review['company_response']['exists'] = True
            
            response_date = response_element.select_one('time')
            if response_date:
                review['company_response']['date'] = response_date.get('datetime', '')
            
            response_content = response_element.select_one('p, div')
            if response_content:
                review['company_response']['content'] = response_content.get_text(strip=True)
        
        return review

    def scrape_company(self, company_name: str, start_page: int = 1) -> Dict:
        """Scrape une entreprise"""
        all_reviews = []
        company_info = {}
        
        if not company_name.startswith('www.'):
            company_name_clean = f"www.{company_name}"
        else:
            company_name_clean = company_name
        
        page = start_page
        page_reviews = []
        
        for page in range(start_page, start_page + self.max_pages):
            if page == 1:
                url = f"https://www.trustpilot.com/review/{company_name_clean}"
            else:
                url = f"https://www.trustpilot.com/review/{company_name_clean}?page={page}"
            
            self.logger.info(f"Scraping de la page {page}: {url}")
            
            try:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                if page == 1:
                    company_info = self.extract_company_info(soup, company_name)

                page_reviews = self.extract_reviews_from_html(soup, company_name)
                
                if not page_reviews:
                    self.logger.info(f"Aucune review trouvée sur la page {page}")
                    break
                
                all_reviews.extend(page_reviews)
                self.logger.info(f"Page {page}: {len(page_reviews)} reviews (total: {len(all_reviews)})")

                if page_reviews:
                    sample = page_reviews[0]
                    self.logger.info(f"Exemple: {sample['author']} - Note: {sample['rating']} - '{sample.get('title', 'Sans titre')}'")
                
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Erreur page {page}: {e}")
                break
        
        return {
            'company_info': company_info,
            'reviews': all_reviews,
            'total_reviews': len(all_reviews),
            'last_page_scraped': page - 1 if not page_reviews else page,
            'scraping_date': datetime.now().isoformat()
        }