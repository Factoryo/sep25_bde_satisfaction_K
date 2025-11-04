import sys
import os
import logging
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from scrapers.trustpilot_mass_scraper import TrustpilotMassScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mass_scraping.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def scrape_companies(company_list, delay=2.0, max_pages_per_company=200, reviews_per_company=5000, resume=True):
    """
    Scrape les entreprises passées en paramètre
    
    Args:
        company_list (list): Liste des noms d'entreprises à scraper
        delay (float): Délai entre les requêtes
        max_pages_per_company (int): Nombre max de pages par entreprise
        reviews_per_company (int): Nombre max de reviews par entreprise
        resume (bool): Reprendre le scraping là où il s'est arrêté
    
    Returns:
        dict: Résultats du scraping
    """
    print("SCRAPING TRUSTPILOT")
    print("=" * 50)
    print(f"{len(company_list)} entreprises à scraper")
    print(f"Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    scraper = TrustpilotMassScraper(
        delay=delay,                    
        max_pages_per_company=max_pages_per_company,    
        reviews_per_company=reviews_per_company      
    )

    try:
        results = scraper.scrape_companies(company_list, resume=resume)
        generate_final_report(results)
        return results
        
    except KeyboardInterrupt:
        print("\nScraping interrompu par l'utilisateur")
        return {}
    except Exception as e:
        print(f"\nErreur générale: {e}")
        return {}

def main():
    """Script principal pour le scraping massif (version standalone)"""
    
    COMPANIES = [
        "amazon.com",
        "apple.com", 
        "microsoft.com",
        "google.com",
        "facebook.com",
        "netflix.com",
        "tesla.com",
        "spotify.com",
        "airbnb.com",
        "uber.com",
    ]
    
    # Appelle la fonction réutilisable
    scrape_companies(COMPANIES)

def generate_final_report(results: dict):
    """Génère un rapport final du scraping"""
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
    
    report_file = f"data/scraping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nRAPPORT FINAL")
    print("=" * 50)
    print(f"Entreprises totales: {report['summary']['total_companies']}")
    print(f"Réussies: {report['summary']['successful_companies']}")
    print(f"Échecs: {report['summary']['failed_companies']}")
    print(f"Reviews totales: {report['summary']['total_reviews']}")
    print(f"Rapport sauvegardé: {report_file}")
    
    print(f"\nDÉTAIL PAR ENTREPRISE:")
    for company, data in report['companies_scraped'].items():
        status_icon = "✅" if data['status'] == 'completed' else "❌"
        print(f"  {status_icon} {company}: {data['reviews_count']} reviews")

if __name__ == "__main__":
    main()
