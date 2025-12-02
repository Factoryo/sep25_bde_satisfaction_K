"""
Script principal pour scraper Trustpilot
Partie 1: Scraper les entreprises d'une catégorie
Partie 2: Scraper tous les avis d'entreprises avec >10000 avis
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.trustpilot_category_scraper import TrustpilotCategoryScraper
from scrapers.trustpilot_reviews_scraper import TrustpilotReviewsScraper
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_category_companies(category_url: str, category_name: str, max_pages: int = 10):
    """
    Scrape toutes les entreprises d'une catégorie
    
    Args:
        category_url: URL de la catégorie (ex: https://www.trustpilot.com/categories/atm)
        category_name: Nom de la catégorie pour le fichier de sortie
        max_pages: Nombre maximum de pages à scraper
    """
    logger.info(f"Starting to scrape category: {category_name}")
    
    scraper = TrustpilotCategoryScraper(delay=2.0)
    
    # Étape 1: Récupérer la liste des entreprises
    companies = scraper.get_companies_from_category(category_url, max_pages=max_pages)
    
    if not companies:
        logger.error("No companies found")
        return []
    
    logger.info(f"Found {len(companies)} companies")
    
    # Étape 2: Enrichir avec les informations détaillées
    logger.info("Enriching with detailed information...")
    detailed_companies = []
    
    for i, company in enumerate(companies, 1):
        logger.info(f"Processing company {i}/{len(companies)}: {company.get('company_name')}")
        
        if 'company_url' in company:
            detailed_info = scraper.get_detailed_company_info(company['company_url'])
            if detailed_info:
                # Fusionner les infos
                company.update(detailed_info)
                detailed_companies.append(company)
    
    # Sauvegarder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/raw/companies_{category_name}_{timestamp}.json'
    
    os.makedirs('data/raw', exist_ok=True)
    scraper.save_to_json(detailed_companies, filename)
    
    logger.info(f"Saved {len(detailed_companies)} companies to {filename}")
    return detailed_companies


def scrape_company_reviews(company_url: str, company_name: str, max_reviews: int = None, use_filters: bool = True):
    """
    Scrape tous les avis d'une entreprise
    
    Args:
        company_url: URL de l'entreprise
        company_name: Nom de l'entreprise pour le fichier de sortie
        max_reviews: Nombre maximum d'avis à récupérer (None = tous)
        use_filters: Utiliser la stratégie multi-filtres pour plus d'avis
    """
    logger.info(f"Starting to scrape reviews for: {company_name}")
    
    scraper = TrustpilotReviewsScraper(delay=2.0)
    
    # Récupérer les statistiques
    stats = scraper.get_company_stats(company_url)
    total_reviews = stats.get('total_reviews', 0)
    
    logger.info(f"Company: {stats.get('company_name')}")
    logger.info(f"Total reviews available: {total_reviews}")
    
    if use_filters:
        logger.info("Using multi-filter strategy to bypass Trustpilot's pagination limits")
    
    if total_reviews < 10000:
        logger.warning(f"Company has only {total_reviews} reviews (< 10000)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return []
    
    # Scraper les avis
    reviews = scraper.scrape_all_reviews(
        company_url=company_url,
        max_reviews=max_reviews,
        use_filters=use_filters
    )
    
    if not reviews:
        logger.error("No reviews found")
        return []
    
    # Ajouter les métadonnées de l'entreprise
    for review in reviews:
        review['company_name'] = stats.get('company_name', company_name)
        review['company_trustscore'] = stats.get('trustscore')
        review['company_total_reviews'] = stats.get('total_reviews')
    
    # Sauvegarder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('data/raw', exist_ok=True)
    
    # Sauvegarder en JSON et JSONL
    json_filename = f'data/raw/reviews_{company_name}_{timestamp}.json'
    jsonl_filename = f'data/raw/reviews_{company_name}_{timestamp}.jsonl'
    
    scraper.save_to_json(reviews, json_filename)
    scraper.save_to_jsonl(reviews, jsonl_filename)
    
    logger.info(f"Saved {len(reviews)} reviews")
    
    # Statistiques
    print_review_statistics(reviews)
    
    return reviews


def print_review_statistics(reviews: list):
    """Affiche des statistiques sur les avis récupérés"""
    if not reviews:
        return
    
    print("\n" + "="*50)
    print("REVIEW STATISTICS")
    print("="*50)
    
    print(f"Total reviews: {len(reviews)}")
    
    # Distribution des notes
    ratings = [r.get('rating', 0) for r in reviews if r.get('rating')]
    if ratings:
        print(f"\nAverage rating: {sum(ratings) / len(ratings):.2f}")
        print("\nRating distribution:")
        for star in range(5, 0, -1):
            count = ratings.count(star)
            percentage = (count / len(ratings)) * 100
            print(f"  {star} stars: {count} ({percentage:.1f}%)")
    
    # Réponses de l'entreprise
    with_reply = sum(1 for r in reviews if r.get('has_company_reply'))
    if with_reply > 0:
        percentage = (with_reply / len(reviews)) * 100
        print(f"\nReviews with company reply: {with_reply} ({percentage:.1f}%)")
    
    # Avis vérifiés
    verified = sum(1 for r in reviews if r.get('is_verified'))
    if verified > 0:
        percentage = (verified / len(reviews)) * 100
        print(f"Verified reviews: {verified} ({percentage:.1f}%)")
    
    print("="*50 + "\n")


def main():
    """Menu principal"""
    print("\n" + "="*60)
    print("TRUSTPILOT SCRAPER")
    print("="*60)
    print("\n1. Scraper les entreprises d'une catégorie")
    print("2. Scraper les avis d'une entreprise")
    print("3. Scraper ATM (banques) + Avis d'une entreprise du secteur")
    print("4. Quitter")
    
    choice = input("\nVotre choix (1-4): ")
    
    if choice == '1':
        print("\nExemples de catégories:")
        print("  - ATM (banques): https://www.trustpilot.com/categories/atm")
        print("  - Electronics: https://www.trustpilot.com/categories/electronics_technology")
        print("  - Shopping: https://www.trustpilot.com/categories/shopping_fashion")
        
        category_url = input("\nURL de la catégorie: ").strip()
        category_name = input("Nom de la catégorie (pour le fichier): ").strip()
        max_pages = input("Nombre de pages max (défaut=10): ").strip() or "10"
        
        scrape_category_companies(category_url, category_name, int(max_pages))
    
    elif choice == '2':
        print("\nExemple: https://www.trustpilot.com/review/www.showroom.com")
        
        company_url = input("\nURL de l'entreprise: ").strip()
        company_name = input("Nom de l'entreprise (pour le fichier): ").strip()
        max_reviews = input("Nombre max d'avis (défaut=tous): ").strip()
        
        max_reviews = int(max_reviews) if max_reviews else None
        scrape_company_reviews(company_url, company_name, max_reviews)
    
    elif choice == '3':
        print("\nScénario complet:")
        print("1. Scraper les entreprises de la catégorie ATM")
        print("2. Trouver les entreprises avec >10000 avis")
        print("3. Scraper les avis de la première entreprise trouvée")
        
        confirm = input("\nContinuer? (y/n): ")
        if confirm.lower() != 'y':
            return
        
        # Étape 1: Scraper la catégorie ATM
        category_url = "https://www.trustpilot.com/categories/atm"
        companies = scrape_category_companies(category_url, "atm", max_pages=5)
        
        # Étape 2: Filtrer les entreprises avec >10000 avis
        big_companies = [
            c for c in companies 
            if c.get('total_reviews', 0) >= 10000
        ]
        
        print(f"\nFound {len(big_companies)} companies with >10000 reviews")
        
        if big_companies:
            # Étape 3: Scraper la première entreprise
            company = big_companies[0]
            print(f"\nScraping reviews for: {company.get('company_name')}")
            
            scrape_company_reviews(
                company_url=company.get('company_url'),
                company_name=company.get('company_name', 'company').replace(' ', '_'),
                max_reviews=None  # Tous les avis
            )
    
    elif choice == '4':
        print("\nAu revoir!")
        return
    
    else:
        print("\nChoix invalide")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruption par l'utilisateur")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
