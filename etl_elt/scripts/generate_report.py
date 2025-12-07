"""
Script pour générer un rapport complet après le scraping massif
"""
import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter
import statistics

def analyze_scraped_data():
    """Analyse données"""
    
    raw_dir = Path("data/raw")
    
    if not raw_dir.exists():
        print("❌ Aucune donnée trouvée dans data/raw/")
        return
    
    json_files = list(raw_dir.glob("*_reviews.json"))
    
    if not json_files:
        print("❌ Aucun fichier JSON trouvé")
        return
    
    print("=" * 80)
    print("📊 RAPPORT D'ANALYSE - SCRAPING MASSIF TRUSTPILOT")
    print("=" * 80)
    print(f"⏰ Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Statistiques globales
    total_companies = len(json_files)
    total_reviews = 0
    total_size_mb = 0
    
    companies_data = []
    all_stars = []
    all_trust_scores = []
    
    # Analyser chaque fichier
    for file_path in json_files:
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            total_size_mb += file_size_mb
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            company_info = data.get('company_info', {})
            reviews = data.get('reviews', [])
            
            company_name = company_info.get('company_name', file_path.stem)
            trust_score = company_info.get('trust_score')
            num_reviews = len(reviews)
            total_reviews += num_reviews
            
            # Collecter les notes
            stars_in_file = [r.get('stars') for r in reviews if r.get('stars')]
            all_stars.extend(stars_in_file)
            
            if trust_score:
                all_trust_scores.append(float(trust_score))
            
            # Distribution des étoiles pour cette entreprise
            stars_dist = Counter(stars_in_file)
            
            companies_data.append({
                'name': company_name,
                'reviews': num_reviews,
                'trust_score': trust_score,
                'size_mb': file_size_mb,
                'stars_dist': stars_dist,
                'file': file_path.name
            })
            
        except Exception as e:
            print(f"⚠️  Erreur lecture {file_path.name}: {e}")
    
    # Trier par nombre de reviews
    companies_data.sort(key=lambda x: x['reviews'], reverse=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1: STATISTIQUES GLOBALES
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                        📊 STATISTIQUES GLOBALES                          │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    print(f"🏢 Entreprises scrapées     : {total_companies}")
    print(f"📝 Reviews totales          : {total_reviews:,}")
    print(f"💾 Taille totale            : {total_size_mb:.2f} MB")
    print(f"📊 Moyenne reviews/entreprise: {total_reviews/total_companies:.0f}")
    
    if all_trust_scores:
        avg_trust = statistics.mean(all_trust_scores)
        print(f"⭐ Trust Score moyen        : {avg_trust:.2f}/5.0")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2: DISTRIBUTION DES NOTES
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                      ⭐ DISTRIBUTION DES NOTES                           │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    stars_counter = Counter(all_stars)
    total_rated = sum(stars_counter.values())
    
    for star in sorted(stars_counter.keys(), reverse=True):
        count = stars_counter[star]
        pct = (count / total_rated) * 100
        bar_length = int(pct / 2)
        bar = "█" * bar_length
        print(f"{star}★ : {bar:<50} {count:>8,} ({pct:>5.1f}%)")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3: TOP 10 ENTREPRISES
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                      🏆 TOP 10 ENTREPRISES (Reviews)                     │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    print(f"{'Rang':<6}{'Entreprise':<35}{'Reviews':<12}{'Trust Score':<12}{'Taille'}")
    print("-" * 80)
    
    for i, comp in enumerate(companies_data[:10], 1):
        trust_str = f"{comp['trust_score']}/5" if comp['trust_score'] else "N/A"
        print(f"{i:<6}{comp['name']:<35}{comp['reviews']:>10,}  {trust_str:<12}{comp['size_mb']:>6.1f} MB")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4: ENTREPRISES AVEC LE PLUS HAUT TRUST SCORE
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                   ⭐ TOP 10 PAR TRUST SCORE                              │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    companies_by_trust = [c for c in companies_data if c['trust_score']]
    companies_by_trust.sort(key=lambda x: float(x['trust_score']), reverse=True)
    
    print(f"{'Rang':<6}{'Entreprise':<40}{'Trust Score':<15}{'Reviews'}")
    print("-" * 80)
    
    for i, comp in enumerate(companies_by_trust[:10], 1):
        print(f"{i:<6}{comp['name']:<40}{comp['trust_score']}/5.0{'':<8}{comp['reviews']:>10,}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 5: RÉPARTITION PAR CATÉGORIE
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                     📦 RÉPARTITION PAR CATÉGORIE                         │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    categories = {
        'E-commerce': ['amazon', 'ebay', 'aliexpress', 'wish', 'etsy', 'walmart', 'target'],
        'Tech': ['apple', 'microsoft', 'google', 'samsung', 'dell', 'hp'],
        'Services': ['facebook', 'instagram', 'twitter', 'tiktok', 'netflix', 'spotify', 'zoom', 'paypal'],
        'Travel': ['booking', 'airbnb', 'expedia', 'tripadvisor', 'uber', 'lyft', 'ryanair'],
        'Fashion': ['asos', 'zara', 'nike', 'adidas'],
        'Finance': ['revolut', 'n26', 'coinbase'],
        'France': ['vinted', 'leboncoin', 'cdiscount', 'fnac', 'sncf', 'orange', 'showroomprive']
    }
    
    for cat_name, keywords in categories.items():
        cat_companies = [c for c in companies_data if any(kw in c['name'].lower() for kw in keywords)]
        cat_reviews = sum(c['reviews'] for c in cat_companies)
        
        if cat_companies:
            print(f"{cat_name:<15}: {len(cat_companies):>2} entreprises, {cat_reviews:>8,} reviews")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 6: LISTE COMPLÈTE
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                      📋 LISTE COMPLÈTE DES ENTREPRISES                   │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    for i, comp in enumerate(companies_data, 1):
        stars_summary = ", ".join([f"{s}★:{comp['stars_dist'][s]}" for s in sorted(comp['stars_dist'].keys(), reverse=True)])
        print(f"{i:>2}. {comp['name']:<35} {comp['reviews']:>6,} reviews  [{stars_summary}]")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 7: RECOMMANDATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n┌─────────────────────────────────────────────────────────────────────────┐")
    print("│                        💡 RECOMMANDATIONS                                │")
    print("└─────────────────────────────────────────────────────────────────────────┘\n")
    
    print("Prochaines étapes suggérées:\n")
    print("1. 🧹 NETTOYAGE DES DONNÉES")
    print("   - Supprimer les doublons éventuels")
    print("   - Normaliser les dates")
    print("   - Détecter et filtrer les langues\n")
    
    print("2. 📊 ANALYSE EXPLORATOIRE (EDA)")
    print("   - Tendances temporelles")
    print("   - Analyse de sentiment")
    print("   - Mots-clés fréquents\n")
    
    print("3. 🤖 MACHINE LEARNING")
    print("   - Entraîner un modèle de sentiment")
    print("   - Prédiction de satisfaction")
    print("   - Classification thématique\n")
    
    print("4. 📈 DASHBOARD STREAMLIT")
    print("   - Visualisations interactives")
    print("   - Comparaison entre entreprises")
    print("   - Analyse temps réel\n")
    
    print("5. 🔄 ORCHESTRATION AIRFLOW")
    print("   - Automatiser le scraping quotidien")
    print("   - Pipeline ETL complet")
    
    print("\n" + "=" * 80)
    print(f"📄 Pour sauvegarder ce rapport: python scripts/generate_report.py > rapport.txt")
    print("=" * 80)

if __name__ == "__main__":
    # Changer vers le bon répertoire si nécessaire
    if not Path("data").exists() and Path("../data").exists():
        os.chdir("..")
    
    analyze_scraped_data()
