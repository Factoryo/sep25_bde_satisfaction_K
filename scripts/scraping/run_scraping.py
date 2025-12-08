"""
Script pour lancer le scraping manuellement.
Détecte automatiquement les entreprises déjà scrapées et les ignore.

Usage:
    python scripts/scraping/run_scraping.py                    # Scrape toutes les nouvelles
    python scripts/scraping/run_scraping.py --force            # Force le re-scraping
    python scripts/scraping/run_scraping.py --company amazon.com  # Une seule entreprise
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "etl_elt"))

import json
import argparse
from datetime import datetime

# Liste des entreprises à scraper
COMPANIES = [
    # E-commerce
    "amazon.com", "amazon.co.uk", "ebay.com", "aliexpress.com",
    "cdiscount.com", "fnac.com", "wish.com", "etsy.com",
    "vinted.fr", "leboncoin.fr", "showroomprive.com",
    # Mode
    "zara.com", "hm.com", "asos.com", "nike.com", "adidas.com",
    # Tech
    "apple.com", "microsoft.com", "google.com", "samsung.com",
    "dell.com", "hp.com",
    # Voyage
    "booking.com", "airbnb.com", "expedia.com", "ryanair.com",
    "tripadvisor.com", "sncf.com",
    # Services
    "uber.com", "ubereats.com", "deliveroo.com", "doordash.com", "lyft.com",
    # Streaming
    "netflix.com", "spotify.com", "zoom.us",
    # Finance
    "paypal.com", "revolut.com", "n26.com", "coinbase.com",
    # Telecom
    "orange.fr", "freemobile.fr", "bouyguestelecom.fr",
    "verizon.com", "att.com", "t-mobile.com",
    # Social
    "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
    # Retail
    "walmart.com", "target.com",
    # === NOUVELLES ENTREPRISES (pour atteindre 60) ===
    # Livraison / Logistique
    "ups.com", "fedex.com", "dhl.com",
    # E-commerce FR
    "darty.com", "boulanger.com",
    # Voyage
    "easyjet.com", "lufthansa.com",
    # Services
    "klarna.com"
]


def get_existing_companies(data_dir: Path) -> set:
    """Retourne les entreprises déjà scrapées"""
    existing = set()
    for f in data_dir.glob("*_reviews.json"):
        # Convertit le nom de fichier en nom d'entreprise
        company = f.stem.replace('_reviews', '').replace('_', '.')
        # Cas spéciaux
        if company == "amazon.co.uk":
            company = "amazon.co.uk"  # Garder tel quel
        existing.add(company)
    return existing


def run_scraping(companies: list, data_dir: Path, force: bool = False):
    """Lance le scraping pour les entreprises spécifiées"""
    from scrapers.trustpilot_jsonld_scraper import TrustpilotJSONLDScraper
    
    # Vérifier ce qui existe déjà
    existing = get_existing_companies(data_dir)
    
    if not force:
        to_scrape = [c for c in companies if c not in existing]
        skipped = len(companies) - len(to_scrape)
        if skipped > 0:
            print(f"⏭️  {skipped} entreprises déjà scrapées (ignorées)")
    else:
        to_scrape = companies
        print("⚠️  Mode force: re-scraping de toutes les entreprises")
    
    if not to_scrape:
        print("✅ Toutes les entreprises ont déjà été scrapées!")
        print(f"   Fichiers existants: {len(existing)}")
        return
    
    print(f"\n🚀 Scraping de {len(to_scrape)} entreprise(s)...\n")
    
    scraper = TrustpilotJSONLDScraper(delay=3.0, max_pages=50)
    
    results = {
        'date': datetime.now().isoformat(),
        'success': [],
        'failed': [],
        'total_reviews': 0
    }
    
    for i, company in enumerate(to_scrape, 1):
        print(f"[{i}/{len(to_scrape)}] {company}...")
        
        try:
            # Scraper les avis (utilise scrape_company avec le nom de l'entreprise)
            reviews = scraper.scrape_company(company)
            
            if reviews and reviews.get('reviews'):
                # Sauvegarder
                filename = company.replace('.', '_') + '_reviews.json'
                output_path = data_dir / filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(reviews, f, ensure_ascii=False, indent=2)
                
                n_reviews = len(reviews.get('reviews', []))
                results['success'].append(company)
                results['total_reviews'] += n_reviews
                print(f"   ✅ {n_reviews} avis sauvegardés")
            else:
                results['failed'].append(company)
                print(f"   ❌ Aucun avis récupéré")
                
        except Exception as e:
            results['failed'].append(company)
            print(f"   ❌ Erreur: {e}")
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print("=" * 50)
    print(f"   Succès: {len(results['success'])}")
    print(f"   Échecs: {len(results['failed'])}")
    print(f"   Total avis: {results['total_reviews']}")
    
    if results['failed']:
        print(f"\n   Entreprises en échec:")
        for c in results['failed']:
            print(f"      - {c}")
    
    # Sauvegarder le log
    log_path = ROOT_DIR / "logs" / f"scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📝 Log sauvegardé: {log_path}")


def main():
    parser = argparse.ArgumentParser(description="Scraping Trustpilot")
    parser.add_argument('--force', action='store_true', 
                        help="Force le re-scraping même si déjà fait")
    parser.add_argument('--company', type=str, 
                        help="Scraper une seule entreprise (ex: amazon.com)")
    parser.add_argument('--list', action='store_true',
                        help="Affiche la liste des entreprises")
    parser.add_argument('--status', action='store_true',
                        help="Affiche le statut du scraping")
    
    args = parser.parse_args()
    
    data_dir = ROOT_DIR / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    if args.list:
        print("📋 Liste des entreprises configurées:")
        for c in COMPANIES:
            print(f"   - {c}")
        print(f"\nTotal: {len(COMPANIES)} entreprises")
        return
    
    if args.status:
        existing = get_existing_companies(data_dir)
        missing = set(COMPANIES) - existing
        
        print("📊 Statut du scraping:")
        print(f"   Scrapées: {len(existing)}/{len(COMPANIES)}")
        print(f"   Manquantes: {len(missing)}")
        
        if missing:
            print("\n   Entreprises manquantes:")
            for c in sorted(missing):
                print(f"      - {c}")
        return
    
    if args.company:
        companies = [args.company]
    else:
        companies = COMPANIES
    
    run_scraping(companies, data_dir, force=args.force)


if __name__ == "__main__":
    main()
