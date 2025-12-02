"""
Scraper pour récupérer tous les avis d'une entreprise Trustpilot avec plus de 10000 avis
"""
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
import json
import re
from urllib.parse import urljoin, urlencode
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrustpilotReviewsScraper:
    """Scraper pour récupérer tous les avis d'une entreprise Trustpilot"""
    
    BASE_URL = "https://www.trustpilot.com"
    
    def __init__(self, delay: float = 2.0):
        """
        Args:
            delay: Délai entre les requêtes pour être respectueux du site
        """
        self.delay = delay
        self.company_info = {}  # Informations sur l'entreprise
        self.reviews = []  # Reviews collectées
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def scrape_all_reviews(
        self, 
        company_url: str, 
        max_reviews: Optional[int] = None,
        max_pages: Optional[int] = None,
        use_filters: bool = True
    ) -> List[Dict]:
        """
        Récupère tous les avis d'une entreprise
        
        Args:
            company_url: URL de l'entreprise (ex: https://www.trustpilot.com/review/showroom.com)
            max_reviews: Nombre maximum d'avis à récupérer (None = tous)
            max_pages: Nombre maximum de pages à scraper (None = toutes)
            use_filters: Utiliser plusieurs filtres pour contourner la limite de pagination
            
        Returns:
            Liste de dictionnaires contenant les avis
        """
        # Récupérer les infos de l'entreprise
        self.company_info = self.get_company_stats(company_url)
        
        if use_filters:
            reviews = self._scrape_with_filters(company_url, max_reviews)
            self.reviews = reviews
            return reviews
        
        reviews = []
        page = 1
        consecutive_empty_pages = 0
        
        logger.info(f"Starting to scrape reviews from: {company_url}")
        
        while True:
            # Vérifier les limites
            if max_pages and page > max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break
            
            if max_reviews and len(reviews) >= max_reviews:
                logger.info(f"Reached max reviews limit: {max_reviews}")
                break
            
            # Si on a 3 pages vides consécutives, arrêter
            if consecutive_empty_pages >= 3:
                logger.info(f"Found {consecutive_empty_pages} empty pages, stopping")
                break
            
            # Construction de l'URL de la page
            page_url = f"{company_url}?page={page}"
            
            try:
                logger.info(f"Scraping page {page}")
                response = self.session.get(page_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraire les avis de cette page
                page_reviews = self._extract_reviews_from_page(soup)
                
                if not page_reviews:
                    logger.warning(f"No reviews found on page {page}")
                    consecutive_empty_pages += 1
                    # Continuer quand même pour vérifier les pages suivantes
                    page += 1
                    time.sleep(self.delay)
                    continue
                
                consecutive_empty_pages = 0
                reviews.extend(page_reviews)
                logger.info(f"Found {len(page_reviews)} reviews on page {page}. Total: {len(reviews)}")
                
                # Vérifier s'il y a une page suivante
                if not self._has_next_page(soup):
                    logger.info("No more pages available")
                    break
                
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= 3:
                    break
                page += 1
                time.sleep(self.delay)
        
        logger.info(f"Total reviews scraped: {len(reviews)}")
        self.reviews = reviews
        return reviews
    
    def _scrape_with_filters(self, company_url: str, max_reviews: Optional[int] = None) -> List[Dict]:
        """
        Scrape avec différents filtres pour contourner la limite de pagination
        Trustpilot limite à ~200 pages, donc on utilise des filtres par note
        """
        logger.info("Using multi-filter strategy to bypass pagination limits")
        
        all_reviews = []
        review_ids = set()  # Pour éviter les doublons
        
        # Scraper par note (5 étoiles, 4 étoiles, etc.)
        for stars in [5, 4, 3, 2, 1]:
            if max_reviews and len(all_reviews) >= max_reviews:
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping {stars}-star reviews")
            logger.info(f"{'='*60}")
            
            filter_url = f"{company_url}?stars={stars}"
            
            page = 1
            consecutive_empty = 0
            
            while True:
                if max_reviews and len(all_reviews) >= max_reviews:
                    break
                
                if consecutive_empty >= 3:
                    break
                
                page_url = f"{filter_url}&page={page}"
                
                try:
                    logger.info(f"Scraping page {page} (filter: {stars} stars)")
                    response = self.session.get(page_url, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_reviews = self._extract_reviews_from_page(soup)
                    
                    if not page_reviews:
                        consecutive_empty += 1
                        page += 1
                        time.sleep(self.delay)
                        continue
                    
                    consecutive_empty = 0
                    
                    # Filtrer les doublons
                    new_reviews = 0
                    for review in page_reviews:
                        review_id = review.get('review_id', '') or str(review)
                        if review_id not in review_ids:
                            review_ids.add(review_id)
                            all_reviews.append(review)
                            new_reviews += 1
                    
                    logger.info(f"Found {len(page_reviews)} reviews ({new_reviews} new). Total: {len(all_reviews)}")
                    
                    if not self._has_next_page(soup):
                        logger.info(f"No more pages for {stars}-star reviews")
                        break
                    
                    page += 1
                    time.sleep(self.delay)
                    
                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                    consecutive_empty += 1
                    page += 1
                    time.sleep(self.delay)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total unique reviews scraped: {len(all_reviews)}")
        logger.info(f"{'='*60}\n")
        
        return all_reviews
    
    def _extract_reviews_from_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrait tous les avis d'une page"""
        reviews = []
        
        # Trouver tous les éléments d'avis
        review_cards = soup.find_all('article', class_=re.compile(r'styles_reviewCard'))
        
        if not review_cards:
            # Essayer avec un autre sélecteur
            review_cards = soup.find_all('div', attrs={'data-service-review-card-paper': True})
        
        for card in review_cards:
            try:
                review_data = self._extract_review_data(card)
                if review_data:
                    reviews.append(review_data)
            except Exception as e:
                logger.error(f"Error extracting review: {e}")
                continue
        
        return reviews
    
    def _extract_review_data(self, card) -> Optional[Dict]:
        """Extrait les données d'un avis avec tous les détails demandés"""
        try:
            review = {}
            
            # ========== INFORMATIONS DE BASE ==========
            
            # ID de l'avis
            review_id = card.get('data-review-id') or card.get('id', '')
            review['review_id'] = review_id
            
            # Lien vers le commentaire détaillé
            review_link = card.find('a', class_=re.compile(r'styles_reviewTitle'))
            if review_link and review_link.has_attr('href'):
                review['review_url'] = urljoin(self.BASE_URL, review_link['href'])
            else:
                review['review_url'] = ''
            
            # ========== NOTE (ÉTOILES) ==========
            
            # Note (nombre d'étoiles) - chercher de plusieurs façons
            # Méthode 1 : via l'attribut alt de l'image (plus fiable)
            rating_img = card.find('img', alt=re.compile(r'Noté|Rated'))
            if rating_img:
                alt_text = rating_img.get('alt', '')
                match = re.search(r'(\d+)', alt_text)
                if match:
                    review['stars'] = int(match.group(1))
                    review['rating'] = int(match.group(1))  # Alias pour compatibilité
            
            # Méthode 2 : Si pas trouvé, chercher dans l'en-tête
            if 'stars' not in review:
                rating_elem = card.find('div', class_=re.compile(r'styles_reviewHeader'))
                if rating_elem:
                    rating_img = rating_elem.find('img', alt=re.compile(r'Rated'))
                    if rating_img:
                        alt_text = rating_img.get('alt', '')
                        match = re.search(r'(\d+)', alt_text)
                        if match:
                            review['stars'] = int(match.group(1))
                            review['rating'] = int(match.group(1))
            
            # Si pas trouvé, chercher autrement
            if 'stars' not in review:
                star_elem = card.find('div', attrs={'data-service-review-rating': True})
                if star_elem:
                    rating = int(star_elem.get('data-service-review-rating', 0))
                    review['stars'] = rating
                    review['rating'] = rating
            
            # Score (normaliser sur 10 ou 100 si nécessaire)
            if 'stars' in review:
                review['score'] = review['stars'] / 5.0 * 10  # Score sur 10
            
            # ========== TITRE ET CONTENU ==========
            
            # Titre du commentaire
            title_elem = card.find('h2', class_=re.compile(r'styles_reviewTitle'))
            if not title_elem:
                title_elem = card.find('a', attrs={'data-review-title-typography': 'true'})
            if not title_elem:
                title_elem = card.find('h2', attrs={'data-service-review-title-typography': 'true'})
            if title_elem:
                review['title'] = title_elem.get_text(strip=True)
            else:
                review['title'] = ''
            
            # Texte brut du commentaire
            content_elem = card.find('p', attrs={'data-relevant-review-text-typography': 'true'})
            if not content_elem:
                content_elem = card.find('p', class_=re.compile(r'styles_reviewContent'))
            if not content_elem:
                content_elem = card.find('p', attrs={'data-service-review-text-typography': 'true'})
            if content_elem:
                review['content'] = content_elem.get_text(strip=True)
                review['comment_text'] = content_elem.get_text(strip=True)  # Alias
            else:
                review['content'] = ''
                review['comment_text'] = ''
            
            # ========== DATE DU COMMENTAIRE ==========
            
            # Date du commentaire (absolue et relative)
            date_elem = card.find('time')
            if date_elem:
                review['date_absolute'] = date_elem.get('datetime', '')  # Format ISO
                review['date'] = date_elem.get('datetime', '')  # Alias
                review['date_relative'] = date_elem.get_text(strip=True)  # "2 days ago"
                review['date_text'] = date_elem.get_text(strip=True)  # Alias
            else:
                review['date_absolute'] = ''
                review['date'] = ''
                review['date_relative'] = ''
                review['date_text'] = ''
            
            # ========== AUTEUR DU COMMENTAIRE ==========
            
            # Nom de la personne à l'origine du commentaire
            author_elem = card.find('span', class_=re.compile(r'styles_consumerName'))
            if not author_elem:
                author_elem = card.find('span', attrs={'data-consumer-name-typography': 'true'})
            if author_elem:
                review['author_name'] = author_elem.get_text(strip=True)
                review['reviewer_name'] = author_elem.get_text(strip=True)  # Alias
            else:
                review['author_name'] = ''
                review['reviewer_name'] = ''
            
            # Localisation de l'auteur (bonus)
            location_elem = card.find('div', class_=re.compile(r'styles_consumerLocation'))
            if location_elem:
                review['author_location'] = location_elem.get_text(strip=True)
            else:
                review['author_location'] = ''
            
            # Nombre de commentaires de cette personne sur TrustPilot
            # Méthode 1 : Via l'attribut data-consumer-reviews-count (le plus fiable)
            author_info = card.find('div', attrs={'data-consumer-reviews-count': True})
            if author_info:
                count = author_info.get('data-consumer-reviews-count', '0')
                try:
                    review['author_review_count'] = int(count)
                    review['reviewer_total_reviews'] = int(count)
                except:
                    review['author_review_count'] = 0
                    review['reviewer_total_reviews'] = 0
            else:
                # Méthode 2 : Chercher dans le texte
                author_reviews_elem = card.find('span', string=re.compile(r'reviews?', re.I))
                if not author_reviews_elem:
                    # Chercher dans un élément parent
                    author_info = card.find('div', class_=re.compile(r'styles_consumerExtraDetails'))
                    if author_info:
                        author_reviews_elem = author_info.find('span', string=re.compile(r'\d+\s*reviews?', re.I))
                
                if author_reviews_elem:
                    text = author_reviews_elem.get_text(strip=True)
                    match = re.search(r'(\d+)', text)
                    if match:
                        review['author_review_count'] = int(match.group(1))
                        review['reviewer_total_reviews'] = int(match.group(1))
                    else:
                        review['author_review_count'] = 0
                        review['reviewer_total_reviews'] = 0
                else:
                    review['author_review_count'] = 0
                    review['reviewer_total_reviews'] = 0
            
            # ========== RÉPONSE DE L'ENTREPRISE ==========
            
            # Vérifier si l'entreprise a répondu
            reply_elem = card.find('div', class_=re.compile(r'styles_reply'))
            if not reply_elem:
                reply_elem = card.find('div', attrs={'data-service-review-business-reply-wrapper': True})
            
            review['has_company_reply'] = reply_elem is not None
            review['company_replied'] = reply_elem is not None  # Alias
            
            # Si oui, extraire la réponse et sa date
            if reply_elem:
                # Contenu de la réponse
                reply_content = reply_elem.find('p', class_=re.compile(r'styles_message'))
                if reply_content:
                    review['company_reply'] = reply_content.get_text(strip=True)
                    review['company_reply_text'] = reply_content.get_text(strip=True)  # Alias
                else:
                    review['company_reply'] = ''
                    review['company_reply_text'] = ''
                
                # Date de la réponse (absolue et relative)
                reply_date = reply_elem.find('time')
                if reply_date:
                    review['company_reply_date_absolute'] = reply_date.get('datetime', '')
                    review['company_reply_date'] = reply_date.get('datetime', '')
                    review['company_reply_date_relative'] = reply_date.get_text(strip=True)
                else:
                    review['company_reply_date_absolute'] = ''
                    review['company_reply_date'] = ''
                    review['company_reply_date_relative'] = ''
            else:
                review['company_reply'] = ''
                review['company_reply_text'] = ''
                review['company_reply_date_absolute'] = ''
                review['company_reply_date'] = ''
                review['company_reply_date_relative'] = ''
            
            # ========== INFORMATIONS SUPPLÉMENTAIRES ==========
            
            # Vérifier si l'avis est vérifié
            verified_elem = card.find('div', string=re.compile(r'Verified', re.I))
            review['is_verified'] = verified_elem is not None
            
            # Informations sur l'expérience (date d'achat/expérience)
            experience_elem = card.find('p', string=re.compile(r'Date of experience', re.I))
            if experience_elem:
                review['experience_date_text'] = experience_elem.get_text(strip=True)
            else:
                review['experience_date_text'] = ''
            
            # Nombre de "helpful" votes
            helpful_elem = card.find('button', string=re.compile(r'helpful', re.I))
            if helpful_elem:
                text = helpful_elem.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    review['helpful_count'] = int(match.group(1))
                else:
                    review['helpful_count'] = 0
            else:
                review['helpful_count'] = 0
            
            # Timestamp de scraping
            review['scraped_at'] = datetime.now().isoformat()
            
            return review
            
        except Exception as e:
            logger.error(f"Error extracting review data: {e}")
            return None
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Vérifie s'il y a une page suivante"""
        # Chercher le bouton "Next" ou "Suivant"
        next_button = soup.find('a', attrs={'name': 'pagination-button-next'})
        if not next_button:
            next_button = soup.find('a', class_=re.compile(r'next'))
        
        return next_button is not None and not next_button.has_attr('disabled')
    
    def get_company_stats(self, company_url: str) -> Dict:
        """Récupère les statistiques globales de l'entreprise"""
        try:
            logger.info(f"Fetching company stats: {company_url}")
            response = self.session.get(company_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stats = {
                'company_url': company_url,
                'company_name': '',
                'trustscore': 0.0,
                'total_reviews': 0,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Nom de l'entreprise
            name_elem = soup.find('span', class_=re.compile(r'title_displayName'))
            if name_elem:
                stats['company_name'] = name_elem.get_text(strip=True)
            
            # TrustScore
            score_elem = soup.find('p', class_=re.compile(r'typography_heading-1'))
            if score_elem:
                try:
                    stats['trustscore'] = float(score_elem.get_text(strip=True))
                except:
                    pass
            
            # Nombre total d'avis
            review_elem = soup.find('p', string=re.compile(r'reviews', re.I))
            if review_elem:
                text = review_elem.get_text(strip=True)
                match = re.search(r'([\d,]+)', text)
                if match:
                    stats['total_reviews'] = int(match.group(1).replace(',', ''))
            
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching company stats: {e}")
            return {}
    
    def save_to_json(self, reviews: List[Dict], filename: str):
        """Sauvegarde les avis dans un fichier JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, indent=2, ensure_ascii=False)
            logger.info(f"Reviews saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_to_jsonl(self, reviews: List[Dict], filename: str):
        """Sauvegarde les avis dans un fichier JSONL (une ligne par avis)"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for review in reviews:
                    f.write(json.dumps(review, ensure_ascii=False) + '\n')
            logger.info(f"Reviews saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSONL: {e}")


def main():
    """Exemple d'utilisation"""
    scraper = TrustpilotReviewsScraper(delay=2.0)
    
    # URL de l'entreprise à scraper (exemple: ShowRoom)
    company_url = "https://www.trustpilot.com/review/www.showroom.com"
    
    # Récupérer les statistiques de l'entreprise
    stats = scraper.get_company_stats(company_url)
    print(f"Company: {stats.get('company_name')}")
    print(f"TrustScore: {stats.get('trustscore')}")
    print(f"Total Reviews: {stats.get('total_reviews')}")
    
    # Scraper les avis (limiter à 100 pour le test, mettre None pour tous)
    reviews = scraper.scrape_all_reviews(
        company_url=company_url,
        max_reviews=100,  # Limiter à 100 pour le test
        max_pages=5       # Limiter à 5 pages pour le test
    )
    
    # Sauvegarder
    scraper.save_to_json(reviews, 'data/raw/showroom_reviews.json')
    scraper.save_to_jsonl(reviews, 'data/raw/showroom_reviews.jsonl')
    
    print(f"\nScraped {len(reviews)} reviews")
    
    # Statistiques sur les avis
    if reviews:
        ratings = [r.get('rating', 0) for r in reviews]
        print(f"Average rating: {sum(ratings) / len(ratings):.2f}")
        
        with_reply = sum(1 for r in reviews if r.get('has_company_reply'))
        print(f"Reviews with company reply: {with_reply} ({with_reply/len(reviews)*100:.1f}%)")


if __name__ == "__main__":
    main()
