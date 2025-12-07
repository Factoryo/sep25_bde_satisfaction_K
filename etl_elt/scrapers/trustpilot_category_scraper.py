"""Scraper catégories"""
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
import json
import re
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrustpilotCategoryScraper:
    """Scraper catégories"""
    
    BASE_URL = "https://www.trustpilot.com"
    
    def __init__(self, delay: float = 2.0):
        """Init scraper"""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def get_companies_from_category(self, category_url: str, max_pages: int = 5) -> List[Dict]:
        """Récup entreprises"""
        companies = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping de la page {page} de la catégorie: {category_url}")
            
            # URL
            if page == 1:
                page_url = category_url
            else:
                page_url = f"{category_url}?page={page}"
            
            try:
                response = self.session.get(page_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Entreprises
                page_companies = self._extract_companies_from_page(soup)
                
                if not page_companies:
                    logger.info(f"Plus d'entreprises trouvées sur la page {page}")
                    break
                
                companies.extend(page_companies)
                logger.info(f"Trouvé {len(page_companies)} entreprises sur la page {page}")
                
                # Délai
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Erreur lors du scraping de la page {page}: {e}")
                break
        
        logger.info(f"Total companies scraped: {len(companies)}")
        return companies
    
    def _extract_companies_from_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Extraction entreprises"""
        companies = []
        
        # Cartes
        company_cards = soup.find_all('div', class_=re.compile(r'styles_businessUnitCard'))
        
        if not company_cards:
            # Alt sélecteur
            company_cards = soup.find_all('article', attrs={'data-business-unit-card': True})
        
        for card in company_cards:
            try:
                company_info = self._extract_company_info(card)
                if company_info:
                    companies.append(company_info)
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction des infos de l'entreprise: {e}")
                continue
        
        return companies
    
    def _extract_company_info(self, card) -> Optional[Dict]:
        """Infos carte"""
        try:
            company_info = {}
            
            # Nom + URL
            name_elem = card.find('a', class_=re.compile(r'styles_businessUnitCardLink'))
            if not name_elem:
                name_elem = card.find('a', href=re.compile(r'/review/'))
            
            if name_elem:
                company_info['company_name'] = name_elem.get_text(strip=True)
                company_info['company_url'] = urljoin(self.BASE_URL, name_elem['href'])
            else:
                return None
            
            # Score
            score_elem = card.find('p', class_=re.compile(r'styles_trustScore'))
            if not score_elem:
                score_elem = card.find('p', attrs={'data-rating-typography': 'true'})
            if score_elem:
                company_info['trustscore'] = float(score_elem.get_text(strip=True))
            
            # Avis
            review_count_elem = card.find('p', class_=re.compile(r'styles_ratingText'))
            if review_count_elem:
                text = review_count_elem.get_text(strip=True)
                # Nombre
                match = re.search(r'([\d,]+)', text)
                if match:
                    company_info['total_reviews'] = int(match.group(1).replace(',', ''))
            
            # Distribution
            rating_distribution = self._extract_rating_distribution(card)
            if rating_distribution:
                company_info.update(rating_distribution)
            
            # Domaine
            if 'company_url' in company_info:
                domain = company_info['company_url'].split('/review/')[-1].split('/')[0]
                company_info['domain'] = domain
            
            return company_info
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des infos de l'entreprise: {e}")
            return None
    
    def _extract_rating_distribution(self, card) -> Dict:
        """Distribution notes"""
        distribution = {
            'percent_excellent': 0.0,
            'percent_great': 0.0,
            'percent_average': 0.0,
            'percent_poor': 0.0,
            'percent_bad': 0.0
        }
        
        # HTML
        
        return distribution
    
    def get_detailed_company_info(self, company_url: str) -> Dict:
        """Infos détaillées"""
        try:
            logger.info(f"Récupération des infos détaillées pour: {company_url}")
            response = self.session.get(company_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            company_info = {
                'company_url': company_url,
                'company_name': '',
                'trustscore': 0.0,
                'total_reviews': 0,
                'domain': '',
            }
            
            # Nom
            name_elem = soup.find('span', class_=re.compile(r'title_displayName'))
            if name_elem:
                company_info['company_name'] = name_elem.get_text(strip=True)
            
            # Score
            score_elem = soup.find('p', class_=re.compile(r'typography_heading'))
            if score_elem:
                try:
                    company_info['trustscore'] = float(score_elem.get_text(strip=True))
                except:
                    pass
            
            # Avis
            review_elem = soup.find('p', string=re.compile(r'reviews|avis', re.I))
            if review_elem:
                text = review_elem.get_text(strip=True)
                match = re.search(r'([\d,]+)', text)
                if match:
                    company_info['total_reviews'] = int(match.group(1).replace(',', ''))
            
            # Notes
            distribution = self._extract_detailed_rating_distribution(soup)
            company_info.update(distribution)
            
            # Domaine
            domain_elem = soup.find('a', href=re.compile(r'^http'))
            if domain_elem:
                company_info['domain'] = domain_elem.get_text(strip=True)
            
            time.sleep(self.delay)
            return company_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos détaillées: {e}")
            return {}
    
    def _extract_detailed_rating_distribution(self, soup: BeautifulSoup) -> Dict:
        """Distribution notes"""
        distribution = {
            'percent_excellent': 0.0,
            'percent_great': 0.0,
            'percent_average': 0.0,
            'percent_poor': 0.0,
            'percent_bad': 0.0
        }
        
        # Distribution
        # Format
        rating_elements = soup.find_all('p', class_=re.compile(r'styles_percentageLabel'))
        
        for elem in rating_elements:
            text = elem.get_text(strip=True).lower()
            
            # %
            match = re.search(r'(\d+)%', text)
            if match:
                percentage = float(match.group(1))
                
                if 'excellent' in text:
                    distribution['percent_excellent'] = percentage
                elif 'great' in text or 'good' in text:
                    distribution['percent_great'] = percentage
                elif 'average' in text:
                    distribution['percent_average'] = percentage
                elif 'poor' in text:
                    distribution['percent_poor'] = percentage
                elif 'bad' in text:
                    distribution['percent_bad'] = percentage
        
        return distribution
    
    def save_to_json(self, companies: List[Dict], filename: str):
        """Sauvegarde JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2, ensure_ascii=False)
            logger.info(f"Données sauvegardées dans {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde en JSON: {e}")


def main():
    """Exemple"""
    scraper = TrustpilotCategoryScraper(delay=2.0)
    
    # ATM
    category_url = "https://www.trustpilot.com/categories/atm"
    companies = scraper.get_companies_from_category(category_url, max_pages=3)
    
    # Enrichir
    detailed_companies = []
    for company in companies[:5]:  # Top 5
        if 'company_url' in company:
            detailed_info = scraper.get_detailed_company_info(company['company_url'])
            if detailed_info:
                detailed_companies.append(detailed_info)
    
    # Sauvegarder
    scraper.save_to_json(companies, 'data/raw/companies_atm_basic.json')
    scraper.save_to_json(detailed_companies, 'data/raw/companies_atm_detailed.json')
    
    print(f"Scraped {len(companies)} companies")
    print(f"Detailed info for {len(detailed_companies)} companies")


if __name__ == "__main__":
    main()
