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
    def __init__(self, delay: float = 2.0, max_pages_per_company: int = 1000, reviews_per_company: int = 10000):
        self.delay = delay
        self.max_pages_per_company = max_pages_per_company
        self.reviews_per_company = reviews_per_company
        self.session = requests.Session()
        
        # Headers mis à jour avec Referer
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://fr.trustpilot.com/',
        })
        
        # AJOUT DES COOKIES DE SESSION POUR DÉPASSER LA LIMITE DES 10 PAGES
        trustpilot_cookies = {
            'TP.uuid': '098be84b-c197-4e9e-8713-1a4b906899ad',
            'jwt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb25zdW1lcklkIjoiNjhlZmFjNjFmNTI5Zjk4MmUzZjg5YWU1IiwiaGFzQWNjZXB0ZWRUZXJtcyI6ZmFsc2UsImlzQmxvY2tlZEZvclJlcG9ydGluZyI6ZmFsc2UsImFjY2Vzc1Rva2VuIjoid3ZUR3A2emY0aDluTERMb2RzdnFiQzV4WWpVMSIsImF1dGhlbnRpY2F0aW9uU291cmNlIjoiZ29vZ2xlIiwiaWF0IjoxNzYwNTM3Njk4LCJleHAiOjE3NjgzMTM2OTh9.UvwVAP2HWCAuR4d9EE8Q0YHaNnYFXb8zK_AnS56yV3M'
        }
        
        # Application des cookies à la session
        for cookie_name, cookie_value in trustpilot_cookies.items():
            self.session.cookies.set(cookie_name, cookie_value, domain='.trustpilot.com')
        
        self.logger = logging.getLogger(__name__)

        self.data_dir = "data"
        self.companies_dir = os.path.join(self.data_dir, "companies")
        self.progress_dir = os.path.join(self.data_dir, "progress")
        
        for directory in [self.data_dir, self.companies_dir, self.progress_dir]:
            os.makedirs(directory, exist_ok=True)

    def extract_from_next_data(self, soup: BeautifulSoup, company_name: str) -> Dict:
        """Extrait les données depuis la balise __NEXT_DATA__"""
        try:
            next_data_script = soup.find('script', id='__NEXT_DATA__')
            if not next_data_script:
                self.logger.warning("Balise __NEXT_DATA__ non trouvée")
                return {'reviews': [], 'company_info': {}}
            
            data = json.loads(next_data_script.string)
            return self.parse_next_data(data, company_name)
            
        except Exception as e:
            self.logger.error(f"Erreur extraction NEXT_DATA: {e}")
            return {'reviews': [], 'company_info': {}}

    def parse_next_data(self, data: Dict, company_name: str) -> Dict:
        """Parse la structure NEXT_DATA"""
        reviews = []
        company_info = {}
        
        try:
            # Extraction des reviews
            reviews_data = data.get('props', {}).get('pageProps', {}).get('reviews', [])
            for review_data in reviews_data:
                review = self.parse_review_json(review_data, company_name)
                if review:
                    reviews.append(review)
            
            # Extraction infos entreprise
            business_unit = data.get('props', {}).get('pageProps', {}).get('businessUnit', {})
            company_info = self.parse_company_info_json(business_unit, company_name)
            
        except Exception as e:
            self.logger.error(f"Erreur parsing NEXT_DATA: {e}")
            
        return {'reviews': reviews, 'company_info': company_info}

    def parse_review_json(self, review_data: Dict, company_name: str) -> Optional[Dict]:
        """Parse une review depuis le JSON"""
        try:
            consumer = review_data.get('consumer', {})
            dates = review_data.get('dates', {})
            company_reply = review_data.get('companyReply')
            
            review = {
                'company_name': company_name,
                'author': consumer.get('displayName', ''),
                'author_review_count': consumer.get('numberOfReviews', 0),
                'date_absolute': dates.get('publishedDate', ''),
                'rating': review_data.get('rating', 0),
                'title': review_data.get('title', ''),
                'content': review_data.get('text', ''),
                'review_id': review_data.get('id', ''),
                'review_link': f"https://fr.trustpilot.com/reviews/{review_data.get('id', '')}",
                'verified': review_data.get('verified', False),
                'company_response': {
                    'exists': company_reply is not None,
                    'date': company_reply.get('createdAt', '') if company_reply else '',
                    'content': company_reply.get('text', '') if company_reply else ''
                },
                'scraped_at': datetime.now().isoformat()
            }
            
            return review
            
        except Exception as e:
            self.logger.debug(f"Erreur parsing review JSON: {e}")
            return None

    def parse_company_info_json(self, business_unit: Dict, company_name: str) -> Dict:
        """Parse les infos entreprise depuis le JSON"""
        company_info = {
            'company_name': company_name,
            'trustscore': str(business_unit.get('trustScore', '')),
            'review_count': str(business_unit.get('numberOfReviews', {}).get('total', '')),
            'website': business_unit.get('websiteUrl', ''),
            'business_unit_id': business_unit.get('id', ''),
            'scraped_at': datetime.now().isoformat()
        }
        return company_info

    def build_url(self, company_name: str, page: int) -> str:
        """Construit l'URL avec fr.trustpilot.com"""
        company_clean = f"www.{company_name}" if not company_name.startswith('www.') else company_name
        base_url = f"https://fr.trustpilot.com/review/{company_clean}"
        return f"{base_url}?page={page}" if page > 1 else base_url

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

    def scrape_company(self, company_name: str, resume: bool = True) -> Dict:
        """Scrape une entreprise complète avec la méthode JSON"""
        start_page = 1
        total_reviews = 0
        batch_number = 1
        
        if resume:
            progress = self.load_progress(company_name)
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
            
            url = self.build_url(company_name, page)
            
            try:
                self.logger.info(f"{company_name} - Page {page} ({total_reviews} reviews accumulées)")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                if response.status_code == 404:
                    self.logger.info(f"🔚 Page 404 - Fin du scraping pour {company_name}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extraction via __NEXT_DATA__
                page_data = self.extract_from_next_data(soup, company_name)
                
                if page == 1 and not company_info:
                    company_info = page_data['company_info']

                page_reviews = page_data['reviews']
                
                if not page_reviews:
                    self.logger.info(f"Aucune review trouvée - Fin du scraping pour {company_name}")
                    break
                
                all_reviews.extend(page_reviews)
                total_reviews += len(page_reviews)

                if len(all_reviews) >= 50:
                    self.save_company_batch(company_name, all_reviews, batch_number)
                    batch_number += 1
                    all_reviews = []

                self.save_progress(company_name, page, total_reviews)

                sleep_time = self.delay + random.uniform(0.5, 2.0)
                time.sleep(sleep_time)
                
            except requests.RequestException as e:
                self.logger.error(f"Erreur page {page}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Erreur inattendue page {page}: {e}")
                break

        if all_reviews:
            self.save_company_batch(company_name, all_reviews, batch_number)

        self.mark_company_completed(company_name, total_reviews)
        
        return {
            'company': company_name,
            'company_info': company_info,
            'total_reviews': total_reviews,
            'last_page_scraped': page,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }

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
