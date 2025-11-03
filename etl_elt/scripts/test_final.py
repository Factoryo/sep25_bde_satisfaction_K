import sys
import os
import logging
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from scrapers.trustpilot_jsonld_scraper import TrustpilotJSONLDScraper

logging.basicConfig(level=logging.INFO)

def test_final():
    scraper = TrustpilotJSONLDScraper(max_pages=2, delay=2.0)
    
    print("TEST FINAL DU SCRAPER TRUSTPILOT")
    print("=" * 50)
    
    companies = ['amazon.com', 'apple.com']
    
    for company in companies:
        print(f"\nScraping: {company}")
        print("-" * 30)
        
        try:
            result = scraper.scrape_company(company)
            
            print(f"{len(result['reviews'])} reviews trouvées")
            print(f"Pages scrapées: {result['last_page_scraped']}")
            print(f"Infos entreprise: {result['company_info']}")
            
            if result['reviews']:
                print(f"\nEXEMPLES DE REVIEWS:")
                for i, review in enumerate(result['reviews'][:3], 1):
                    print(f"\n--- Review {i} ---")
                    print(f"Auteur: {review.get('author', 'N/A')}")
                    print(f"Note: {review.get('rating', 'N/A')}/5")
                    print(f"Date: {review.get('date_absolute', 'N/A')}")
                    print(f"Titre: {review.get('title', 'Sans titre')}")
                    print(f"Contenu: {review.get('content', 'N/A')[:100]}...")
                    print(f"Lien: {review.get('review_link', 'N/A')}")
                    if review['company_response']['exists']:
                        print(f"Réponse entreprise: OUI")

            filename = f"data/{company}_results.json"
            os.makedirs('data', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nRésultats sauvegardés dans: {filename}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_final()