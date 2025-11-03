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
import random

class TrustpilotMassScraper:
    def __init__(self, delay: float = 2.0, max_pages_per_company: int = 100, reviews_per_company: int = 5000):
        self.delay = delay
        self.max_pages_per_company = max_pages_per_company
        self.reviews_per_company = reviews_per_company
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

        self.data_dir = "data"
        self.companies_dir = os.path.join(self.data_dir, "companies")
        self.progress_dir = os.path.join(self.data_dir, "progress")
        
        for directory in [self.data_dir, self.companies_dir, self.progress_dir]:
            os.makedirs(directory, exist_ok=True)

    def save_progress(self, company: str, current_page: int, total_reviews: int):
        """Sauvegarde la progression du scraping"""
        progress = {
            'company': company,
            'last_page': current_page,
            'total_reviews': total_reviews,
            'last_update': datetime.now().isoformat(),
            'status': 'in_progress'
        }
        
        progress_file = os.path.join(self.progress_dir, f"{company}_progress.json")
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

    def load_progress(self, company: str) -> Optional[Dict]:
        """Charge la progression précédente"""
        progress_file = os.path.join(self.progress_dir, f"{company}_progress.json")
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def mark_company_completed(self, company: str, total_reviews: int):
        """Marque une entreprise comme terminée"""
        progress = {
            'company': company,
            'total_reviews': total_reviews,
            'completed_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        progress_file = os.path.join(self.progress_dir, f"{company}_progress.json")
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

    def save_company_batch(self, company: str, reviews: List[Dict], batch_number: int):
        """Sauvegarde un lot de reviews"""
        batch_data = {
            'company': company,
            'batch_number': batch_number,
            'reviews_count': len(reviews),
            'saved_at': datetime.now().isoformat(),
            'reviews': reviews
        }
        
        batch_file = os.path.join(self.companies_dir, f"{company}_batch_{batch_number:04d}.json")
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f" Lot {batch_number} sauvegardé: {len(reviews)} reviews")

    def extract_reviews_from_page(self, soup: BeautifulSoup, company_name: str) -> List[Dict]:
        """Extrait les reviews d'une page"""
        reviews = []
        review_elements = soup.select('article.styles_reviewCard__meSdm')
        
        for element in review_elements:
            try:
                review = self.parse_review_element(element, company_name)
                if review and review.get('author'):
                    reviews.append(review)
            except Exception as e:
                self.logger.debug(f"Erreur parsing review: {e}")
                continue
        
        return reviews

    def parse_review_element(self, element, company_name: str) -> Dict:
        """Parse un élément de review"""
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
            },
            'scraped_at': datetime.now().isoformat()
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
        if title_element:
            review['title'] = title_element.get_text(strip=True)

        content_elements = element.select('p.CDS_Typography_body-l__dd9b51, div.CDS_Typography_body-l__dd9b51')
        for content_elem in content_elements:
            text = content_elem.get_text(strip=True)
            if text and len(text) > 20:
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

    def scrape_company(self, company_name: str, resume: bool = True) -> Dict:
        """Scrape une entreprise complète avec reprise"""
        company_name_clean = f"www.{company_name}" if not company_name.startswith('www.') else company_name

        start_page = 1
        total_reviews = 0
        batch_number = 1
        
        if resume:
            progress = self.load_progress(company_name_clean)
            if progress and progress.get('status') == 'completed':
                self.logger.info(f"{company_name} déjà complétée avec {progress['total_reviews']} reviews")
                return {'status': 'already_completed', **progress}
            elif progress:
                start_page = progress.get('last_page', 1) + 1
                total_reviews = progress.get('total_reviews', 0)
                batch_number = progress.get('batch_number', 1) + 1
                self.logger.info(f"Reprise de {company_name} à la page {start_page}")

        all_reviews = []
        company_info = {}
        
        for page in range(start_page, start_page + self.max_pages_per_company):
            if total_reviews >= self.reviews_per_company:
                self.logger.info(f"Limite de {self.reviews_per_company} reviews atteinte pour {company_name}")
                break
            
            url = f"https://www.trustpilot.com/review/{company_name_clean}?page={page}"
            
            try:
                self.logger.info(f"{company_name} - Page {page} ({total_reviews} reviews accumulées)")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                if response.status_code == 404:
                    self.logger.info(f"🔚 Page 404 - Fin du scraping pour {company_name}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')

                if page == 1 and not company_info:
                    company_info = self.extract_company_info(soup, company_name)

                page_reviews = self.extract_reviews_from_page(soup, company_name)
                
                if not page_reviews:
                    self.logger.info(f"Aucune review trouvée - Fin du scraping pour {company_name}")
                    break
                
                all_reviews.extend(page_reviews)
                total_reviews += len(page_reviews)

                if len(all_reviews) >= 50:
                    self.save_company_batch(company_name_clean, all_reviews, batch_number)
                    batch_number += 1
                    all_reviews = []

                self.save_progress(company_name_clean, page, total_reviews)

                sleep_time = self.delay + random.uniform(0.5, 2.0)
                time.sleep(sleep_time)
                
            except requests.RequestException as e:
                self.logger.error(f"Erreur page {page}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Erreur inattendue page {page}: {e}")
                break

        if all_reviews:
            self.save_company_batch(company_name_clean, all_reviews, batch_number)

        self.mark_company_completed(company_name_clean, total_reviews)
        
        return {
            'company': company_name,
            'company_info': company_info,
            'total_reviews': total_reviews,
            'last_page_scraped': page,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }

    def extract_company_info(self, soup: BeautifulSoup, company_name: str) -> Dict:
        """Extrait les informations de l'entreprise"""
        company_info = {
            'company_name': company_name,
            'trustscore': '',
            'review_count': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            trustscore_element = soup.select_one('span.CDS_Typography_heading-l__dd9b51')
            if trustscore_element:
                company_info['trustscore'] = trustscore_element.get_text(strip=True)
            
            reviews_element = soup.find('span', string=re.compile(r'reviews', re.I))
            if reviews_element:
                text = reviews_element.get_text(strip=True)
                count_match = re.search(r'([\d,]+)', text)
                if count_match:
                    company_info['review_count'] = count_match.group(1).replace(',', '')
            
        except Exception as e:
            self.logger.warning(f"Erreur infos entreprise: {e}")
        
        return company_info

    def scrape_companies(self, companies: List[str], resume: bool = True) -> Dict:
        """Scrape plusieurs entreprises en séquence"""
        results = {}
        
        for i, company in enumerate(companies, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Scraping entreprise {i}/{len(companies)}: {company}")
            self.logger.info(f"{'='*60}")
            
            try:
                result = self.scrape_company(company, resume)
                results[company] = result

                self.logger.info(f"{company}: {result['total_reviews']} reviews scrapées")

                if i < len(companies):
                    pause = random.uniform(5.0, 10.0)
                    self.logger.info(f"Pause de {pause:.1f}s avant la prochaine entreprise...")
                    time.sleep(pause)
                    
            except Exception as e:
                self.logger.error(f"Erreur majeure sur {company}: {e}")
                results[company] = {'error': str(e), 'status': 'failed'}
                continue
        
        return results