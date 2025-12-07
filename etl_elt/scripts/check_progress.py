import os
import json
from datetime import datetime
from pathlib import Path

def check_scraping_progress():
    """Vérifie progression"""
    
    print("📊 ÉTAT DU SCRAPING MASSIF")
    print("=" * 70)
    
    # Chemins
    raw_dir = Path("data/raw")
    test_dir = Path("data/test")
    
    # Statistiques
    stats = {
        'production': {
            'files': 0,
            'total_reviews': 0,
            'companies': []
        },
        'test': {
            'files': 0,
            'total_reviews': 0,
            'companies': []
        }
    }
    
    # Analyser les fichiers de production
    if raw_dir.exists():
        json_files = list(raw_dir.glob("*_reviews.json"))
        stats['production']['files'] = len(json_files)
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    reviews = data.get('reviews', [])
                    company = data.get('company_info', {}).get('company_name', file.stem)
                    
                    stats['production']['total_reviews'] += len(reviews)
                    stats['production']['companies'].append({
                        'name': company,
                        'reviews': len(reviews),
                        'file': file.name,
                        'size_mb': file.stat().st_size / (1024 * 1024)
                    })
            except Exception as e:
                print(f"⚠️  Erreur lecture {file.name}: {e}")
    
    # Analyser les fichiers de test
    if test_dir.exists():
        json_files = list(test_dir.glob("*_test.json"))
        stats['test']['files'] = len(json_files)
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    reviews = data.get('reviews', [])
                    company = data.get('company_info', {}).get('company_name', file.stem)
                    
                    stats['test']['total_reviews'] += len(reviews)
                    stats['test']['companies'].append({
                        'name': company,
                        'reviews': len(reviews),
                        'file': file.name
                    })
            except Exception as e:
                print(f"⚠️  Erreur lecture {file.name}: {e}")
    
    # Affichage Production
    print(f"\n🏭 PRODUCTION (data/raw/)")
    print("-" * 70)
    print(f"📁 Fichiers: {stats['production']['files']}")
    print(f"📝 Reviews totales: {stats['production']['total_reviews']:,}")
    
    if stats['production']['companies']:
        print(f"\n🏢 Entreprises scrapées:")
        # Trier par nombre de reviews
        companies = sorted(stats['production']['companies'], 
                         key=lambda x: x['reviews'], reverse=True)
        
        for comp in companies[:20]:  # Afficher top 20
            print(f"  • {comp['name']:<30} {comp['reviews']:>6,} reviews  "
                  f"({comp['size_mb']:.1f} MB)")
        
        if len(companies) > 20:
            print(f"  ... et {len(companies) - 20} autres entreprises")
        
        # Statistiques globales
        total_size = sum(c['size_mb'] for c in companies)
        avg_reviews = stats['production']['total_reviews'] / len(companies)
        
        print(f"\n📊 Statistiques:")
        print(f"  • Taille totale: {total_size:.1f} MB")
        print(f"  • Moyenne par entreprise: {avg_reviews:.0f} reviews")
        
        # Progression
        target_companies = 60
        target_reviews_total = target_companies * 10000
        progress_pct = (len(companies) / target_companies) * 100
        reviews_pct = (stats['production']['total_reviews'] / target_reviews_total) * 100
        
        print(f"\n🎯 Progression:")
        print(f"  • Entreprises: {len(companies)}/{target_companies} ({progress_pct:.1f}%)")
        print(f"  • Reviews: {stats['production']['total_reviews']:,}/{target_reviews_total:,} ({reviews_pct:.1f}%)")
    else:
        print("  ❌ Aucune donnée de production trouvée")
    
    # Affichage Test
    print(f"\n\n🧪 TEST (data/test/)")
    print("-" * 70)
    print(f"📁 Fichiers: {stats['test']['files']}")
    print(f"📝 Reviews totales: {stats['test']['total_reviews']:,}")
    
    if stats['test']['companies']:
        print(f"\n🏢 Entreprises testées:")
        for comp in stats['test']['companies']:
            print(f"  • {comp['name']:<30} {comp['reviews']:>6,} reviews")
    else:
        print("  ℹ️  Aucune donnée de test trouvée")
    
    # Rapports
    print(f"\n\n📄 RAPPORTS")
    print("-" * 70)
    
    # Rapports de scraping
    report_files = list(Path("data").glob("scraping_report_*.json"))
    if report_files:
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        print(f"📊 Dernier rapport: {latest_report.name}")
        
        try:
            with open(latest_report, 'r', encoding='utf-8') as f:
                report = json.load(f)
                summary = report.get('summary', {})
                
                print(f"  • Généré: {report.get('generated_at', 'N/A')}")
                print(f"  • Entreprises totales: {summary.get('total_companies', 0)}")
                print(f"  • Réussies: {summary.get('successful_companies', 0)}")
                print(f"  • Échecs: {summary.get('failed_companies', 0)}")
                print(f"  • Reviews totales: {summary.get('total_reviews', 0):,}")
        except Exception as e:
            print(f"  ⚠️  Erreur lecture rapport: {e}")
    else:
        print("  ℹ️  Aucun rapport trouvé")
    
    # Rapports de test
    test_reports = list(Path("data/test").glob("test_report_*.json")) if test_dir.exists() else []
    if test_reports:
        latest_test = max(test_reports, key=lambda p: p.stat().st_mtime)
        print(f"\n🧪 Dernier rapport de test: {latest_test.name}")
    
    # Logs
    print(f"\n\n📋 LOGS")
    print("-" * 70)
    
    log_file = Path("logs/mass_scraping.log")
    if log_file.exists():
        log_size = log_file.stat().st_size / (1024 * 1024)
        log_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        print(f"📝 logs/mass_scraping.log")
        print(f"  • Taille: {log_size:.1f} MB")
        print(f"  • Dernière modification: {log_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Lire les dernières lignes
        print(f"\n  📄 Dernières lignes:")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-5:]:
                    print(f"    {line.rstrip()}")
        except Exception as e:
            print(f"  ⚠️  Erreur lecture logs: {e}")
    else:
        print("  ℹ️  Aucun log trouvé")
    
    print(f"\n{'='*70}")
    print(f"⏰ Rapport généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

if __name__ == "__main__":
    # Changer vers le répertoire etl_elt si nécessaire
    if not Path("data").exists() and Path("../data").exists():
        os.chdir("..")
    
    check_scraping_progress()
