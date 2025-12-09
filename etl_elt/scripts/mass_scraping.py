import sys
import os
import logging
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from scrapers.trustpilot_reviews_scraper import TrustpilotReviewsScraper

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mass_scraping.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    """Scraping de masse"""
    
    # Entreprises
    COMPANIES = [
        # E-commerce
        "amazon.com",
        "amazon.co.uk",
        "ebay.com",
        "aliexpress.com",
        "wish.com",
        "etsy.com",
        "walmart.com",
        "target.com",
        
        # Tech
        "apple.com",
        "microsoft.com",
        "google.com",
        "samsung.com",
        "dell.com",
        "hp.com",
        
        # Services
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "tiktok.com",
        "netflix.com",
        "spotify.com",
        "zoom.us",
        "paypal.com",
        
        # Voyage
        "booking.com",
        "airbnb.com",
        "expedia.com",
        "tripadvisor.com",
        "uber.com",
        "lyft.com",
        "ryanair.com",
        
        # Mode
        "asos.com",
        "zara.com",
        "hm.com",
        "nike.com",
        "adidas.com",
        
        # Livraison
        "ubereats.com",
        "deliveroo.com",
        "doordash.com",
        
        # Telecom
        "verizon.com",
        "att.com",
        "t-mobile.com",
        
        # Finance
        "revolut.com",
        "n26.com",
        "coinbase.com",
        
        # Entreprises françaises
        "showroomprive.com",
        "vinted.fr",
        "leboncoin.fr",
        "cdiscount.com",
        "fnac.com",
        "sncf.com",
        "orange.fr",
        "freemobile.fr",
        "bouyguestelecom.fr"
    ]
    
    print("Scraping de masse démarré")
    print("=" * 60)
    print(f"{len(COMPANIES)} entreprises à scraper")
    print(f"Objectif: 10,000+ reviews par entreprise")
    print(f"Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Stratégie: Multi-filtres par étoiles (5★ → 1★)")
    print("=" * 60)
    
    # Dossiers
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    results = {}
    
    # Scraping
    for i, company_domain in enumerate(COMPANIES, 1):
        print(f"\n{'='*60}")
        print(f"Entreprise {i}/{len(COMPANIES)}: {company_domain}")
        print(f"{'='*60}")
        
        # Vérifie si déjà scrapé
        output_file = f"data/raw/{company_domain.replace('.', '_')}_reviews.json"
        if os.path.exists(output_file):
            print(f"Déjà scrapé, fichier existant: {output_file}")
            continue
        
        try:
            # URL
            company_url = f"https://fr.trustpilot.com/review/{company_domain}"
            
            # Créer un scraper
            scraper = TrustpilotReviewsScraper(delay=2.0)
            
            # Scrape
            print(f"Démarrage du scraping avec multi-filtres...")
            reviews = scraper.scrape_all_reviews(
                company_url=company_url,
                use_filters=True, 
                max_reviews=10000
            )
            
            # Save
            output_file = f"data/raw/{company_domain.replace('.', '_')}_reviews.json"
            
            # Data
            output_data = {
                'company_info': scraper.company_info,
                'reviews': reviews,
                'scraped_at': datetime.now().isoformat(),
                'total_reviews': len(reviews)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            results[company_domain] = {
                'status': 'completed',
                'total_reviews': len(reviews),
                'company_info': scraper.company_info,
                'output_file': output_file
            }
            
            print(f"{company_domain}: {len(reviews)} reviews scrapées")
            print(f"Sauvegardé dans: {output_file}")
            
            # Pause
            if i < len(COMPANIES):
                import time
                import random
                pause = random.uniform(5.0, 10.0)
                print(f"Pause de {pause:.1f}s avant la prochaine entreprise...")
                time.sleep(pause)
                
        except Exception as e:
            logging.error(f"Erreur sur {company_domain}: {e}")
            results[company_domain] = {
                'status': 'failed',
                'error': str(e),
                'total_reviews': 0
            }
            continue
    
    # Démarrer le scraping
    try:
        # Rapport
        generate_final_report(results)
        
    except KeyboardInterrupt:
        print("\nScraping interrompu par l'utilisateur")
        generate_final_report(results)
    except Exception as e:
        print(f"\nErreur générale: {e}")
        logging.error(f"Erreur générale: {e}", exc_info=True)

def generate_final_report(results: dict):
    """Rapport final"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'companies_scraped': {},
        'summary': {
            'total_companies': len(results),
            'successful_companies': 0,
            'failed_companies': 0,
            'total_reviews': 0
        }
    }
    
    for company, result in results.items():
        status = result.get('status', 'unknown')
        reviews_count = result.get('total_reviews', 0)
        
        report['companies_scraped'][company] = {
            'status': status,
            'reviews_count': reviews_count,
            'company_info': result.get('company_info', {})
        }
        
        if status == 'completed':
            report['summary']['successful_companies'] += 1
            report['summary']['total_reviews'] += reviews_count
        elif status == 'failed':
            report['summary']['failed_companies'] += 1
    
    # Save
    report_file = f"data/scraping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Afficher le résumé
    print(f"\nRAPPORT FINAL")
    print("=" * 50)
    print(f"Total entreprises: {report['summary']['total_companies']}")
    print(f"Réussites: {report['summary']['successful_companies']}")
    print(f"Échecs: {report['summary']['failed_companies']}")
    print(f"Total avis: {report['summary']['total_reviews']}")
    print(f"Rapport sauvegardé: {report_file}")
    
    # Détail
    print(f"\nDÉTAIL PAR ENTREPRISE:")
    for company, data in report['companies_scraped'].items():
        status_icon = "✅" if data['status'] == 'completed' else "❌"
        print(f"  {status_icon} {company}: {data['reviews_count']} reviews")

if __name__ == "__main__":
    main()
