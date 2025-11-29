import os
import json
import glob
from datetime import datetime

def monitor_progress():
    """Affiche la progression du scraping"""
    
    progress_files = glob.glob("data/progress/*_progress.json")
    batch_files = glob.glob("data/companies/*_batch_*.json")
    
    print("MONITORING DU SCRAPING")
    print("=" * 50)
    
    if not progress_files:
        print("Aucun fichier de progression trouvé")
        return
    
    total_reviews = 0
    completed_companies = 0
    in_progress_companies = 0
    
    for progress_file in progress_files:
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        company = progress['company']
        status = progress.get('status', 'unknown')
        reviews = progress.get('total_reviews', 0)
        
        status_icon = "✅" if status == 'completed' else "🔄"
        
        print(f"{status_icon} {company}:")
        print(f"   📝 Reviews: {reviews}")
        print(f"   📊 Statut: {status}")
        if 'last_update' in progress:
            last_update = datetime.fromisoformat(progress['last_update'])
            print(f"   ⏰ Dernière mise à jour: {last_update.strftime('%H:%M:%S')}")
        print()
        
        total_reviews += reviews
        if status == 'completed':
            completed_companies += 1
        else:
            in_progress_companies += 1

    batches_per_company = {}
    for batch_file in batch_files:
        filename = os.path.basename(batch_file)
        company = filename.split('_batch_')[0]
        batches_per_company[company] = batches_per_company.get(company, 0) + 1
    
    print(f"STATISTIQUES GLOBALES:")
    print(f"Entreprises complétées: {completed_companies}")
    print(f"Entreprises en cours: {in_progress_companies}")
    print(f"Reviews totales: {total_reviews}")
    print(f"Lots sauvegardés: {len(batch_files)}")
    
    if batches_per_company:
        print(f"\nLOTS PAR ENTREPRISE:")
        for company, batches in batches_per_company.items():
            print(f"   {company}: {batches} lots")

if __name__ == "__main__":
    monitor_progress()