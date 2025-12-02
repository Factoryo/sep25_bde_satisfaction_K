import sys
import os
import logging
import json
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from scrapers.trustpilot_reviews_scraper import TrustpilotReviewsScraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    """Script de test pour le scraping de quelques entreprises"""
    
    # Liste de test avec seulement 3 entreprises
    TEST_COMPANIES = [
        "apple.com",
        "amazon.com",
        "booking.com"
    ]
    
    print("TEST SCRAPING MASSIF TRUSTPILOT")
    print("=" * 60)
    print(f"{len(TEST_COMPANIES)} entreprises a tester")
    print(f"Objectif: ~1000 reviews par entreprise (pour test)")
    print(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Strategie: Multi-filtres par etoiles (5* -> 1*)")
    print("=" * 60)
    
    # Créer les répertoires nécessaires
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/test", exist_ok=True)
    
    results = {}
    
    # Scraper chaque entreprise avec la stratégie multi-filtres
    for i, company_domain in enumerate(TEST_COMPANIES, 1):
        print(f"\n{'='*60}")
        print(f"Entreprise {i}/{len(TEST_COMPANIES)}: {company_domain}")
        print(f"{'='*60}")
        
        try:
            # Construire l'URL Trustpilot
            company_url = f"https://fr.trustpilot.com/review/{company_domain}"
            
            # Créer un scraper
            scraper = TrustpilotReviewsScraper(delay=1.5)
            
            # Scraper avec la stratégie multi-filtres (limité à 1000 pour test)
            print(f"Demarrage du scraping avec multi-filtres...")
            reviews = scraper.scrape_all_reviews(
                company_url=company_url,
                use_filters=True, 
                max_reviews=1000
            )
            
            # Sauvegarder les résultats
            output_file = f"data/test/{company_domain.replace('.', '_')}_test.json"
            
            # Construire le fichier avec infos complètes
            output_data = {
                'company_info': scraper.company_info,
                'reviews': reviews,
                'scraped_at': datetime.now().isoformat(),
                'total_reviews': len(reviews)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            company_info = scraper.company_info
            
            results[company_domain] = {
                'status': 'completed',
                'total_reviews': len(reviews),
                'company_info': company_info,
                'output_file': output_file
            }
            
            print(f"[OK] {company_domain}: {len(reviews)} reviews scrapees")
            print(f"Note moyenne: {company_info.get('trust_score', 'N/A')}")
            print(f"Total avis disponibles: {company_info.get('total_reviews', 'N/A')}")
            print(f"Sauvegarde dans: {output_file}")
            
            # Pause entre les entreprises
            if i < len(TEST_COMPANIES):
                import time
                import random
                pause = random.uniform(3.0, 5.0)
                print(f"Pause de {pause:.1f}s avant la prochaine entreprise...")
                time.sleep(pause)
                
        except Exception as e:
            logging.error(f"[ERREUR] Erreur sur {company_domain}: {e}", exc_info=True)
            results[company_domain] = {
                'status': 'failed',
                'error': str(e),
                'total_reviews': 0
            }
            continue
    
    # Générer un rapport de test
    print(f"\n{'='*60}")
    print("RAPPORT DE TEST")
    print("=" * 60)
    
    total_reviews = sum(r.get('total_reviews', 0) for r in results.values())
    successful = sum(1 for r in results.values() if r.get('status') == 'completed')
    
    print(f"[OK] Entreprises reussies: {successful}/{len(TEST_COMPANIES)}")
    print(f"Reviews totales: {total_reviews}")
    print(f"Moyenne par entreprise: {total_reviews/len(TEST_COMPANIES):.0f}")
    
    print(f"\nDETAIL:")
    for company, data in results.items():
        status_icon = "[OK]" if data.get('status') == 'completed' else "[X]"
        reviews = data.get('total_reviews', 0)
        print(f"  {status_icon} {company}: {reviews} reviews")
    
    # Sauvegarder le rapport
    report_file = f"data/test/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nRapport sauvegarde: {report_file}")
    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
