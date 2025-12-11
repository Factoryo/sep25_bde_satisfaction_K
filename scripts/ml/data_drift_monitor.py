"""
Détection du data drift sur les avis Trustpilot.
J'utilise le test de Kolmogorov-Smirnov pour comparer les distributions.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class DataDriftMonitor:
    
    def __init__(self, es_host='localhost', es_port=9200):
        self.es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])
        self.reports_dir = Path('../docs/data_drift_reports')
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self, index_name='trustpilot_reviews', days_back=30):
        """Récupère les avis depuis Elasticsearch"""
        print(f"Chargement des données des {days_back} derniers jours...")
        
        try:
            response = self.es.search(
                index=index_name,
                scroll='2m',
                size=1000,
                body={"query": {"match_all": {}}}
            )
            
            reviews = []
            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            reviews.extend(hits)
            
            while len(hits) > 0:
                response = self.es.scroll(scroll_id=scroll_id, scroll='2m')
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
                reviews.extend(hits)
            
            df = pd.DataFrame([hit['_source'] for hit in reviews])
            
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                df['date'] = df['created_at']
            elif 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            else:
                df['date'] = datetime.now()
            
            print(f"{len(df)} avis chargés")
            return df
            
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return pd.DataFrame()
    
    def split_data_by_time(self, df, split_ratio=0.7):
        """Split données"""
        df_sorted = df.sort_values('date')
        split_idx = int(len(df_sorted) * split_ratio)
        
        df_reference = df_sorted.iloc[:split_idx]
        df_current = df_sorted.iloc[split_idx:]
        
        print(f"\nDonnées de référence: {len(df_reference)} avis")
        print(f"  Période: {df_reference['date'].min()} à {df_reference['date'].max()}")
        print(f"\nDonnées courantes: {len(df_current)} avis")
        print(f"  Période: {df_current['date'].min()} à {df_current['date'].max()}")
        
        return df_reference, df_current
    
    def detect_rating_drift(self, df_ref, df_curr):
        """Dridt ratings"""
        print("\n" + "="*80)
        print("ANALYSE DE DÉRIVE - RATINGS")
        print("="*80)
        
        ref_ratings = df_ref['rating'].value_counts(normalize=True).sort_index()
        curr_ratings = df_curr['rating'].value_counts(normalize=True).sort_index()
        
        print("\nDistribution des ratings:")
        print("\n  Référence:")
        for rating, pct in ref_ratings.items():
            print(f"    {rating}★: {pct:.2%}")
        
        print("\n  Courant:")
        for rating, pct in curr_ratings.items():
            print(f"    {rating}★: {pct:.2%}")
        
        # Test KS
        ks_statistic, ks_pvalue = stats.ks_2samp(df_ref['rating'], df_curr['rating'])
        
        print(f"\nTest de Kolmogorov-Smirnov:")
        print(f"   Statistique: {ks_statistic:.4f}")
        print(f"   P-value: {ks_pvalue:.4f}")
        
        drift_detected = ks_pvalue < 0.05
        
        if drift_detected:
            print(f"   DÉRIVE DÉTECTÉE (p < 0.05)")
        else:
            print(f"   Pas de dérive significative (p >= 0.05)")
        
        mean_ref = df_ref['rating'].mean()
        mean_curr = df_curr['rating'].mean()
        mean_change = mean_curr - mean_ref
        
        print(f"\nMoyennes:")
        print(f"   Référence: {mean_ref:.2f}★")
        print(f"   Courant: {mean_curr:.2f}★")
        print(f"   Changement: {mean_change:+.2f}★ ({(mean_change/mean_ref)*100:+.1f}%)")
        
        return {
            'ks_statistic': float(ks_statistic),
            'ks_pvalue': float(ks_pvalue),
            'drift_detected': drift_detected,
            'mean_reference': float(mean_ref),
            'mean_current': float(mean_curr),
            'mean_change': float(mean_change),
            'distribution_reference': ref_ratings.to_dict(),
            'distribution_current': curr_ratings.to_dict()
        }
    
    def detect_text_length_drift(self, df_ref, df_curr):
        """Drift longueur"""
        print("\n" + "="*80)
        print("ANALYSE DE DÉRIVE - LONGUEUR DES TEXTES")
        print("="*80)
        
        df_ref['text_length'] = df_ref['content'].fillna('').str.len()
        df_curr['text_length'] = df_curr['content'].fillna('').str.len()
        
        # Statistiques
        ref_mean = df_ref['text_length'].mean()
        curr_mean = df_curr['text_length'].mean()
        change = curr_mean - ref_mean
        
        print(f"\nLongueur moyenne des avis:")
        print(f"   Référence: {ref_mean:.0f} caractères")
        print(f"   Courant: {curr_mean:.0f} caractères")
        print(f"   Changement: {change:+.0f} caractères ({(change/ref_mean)*100:+.1f}%)")
        
        # Test statistique
        ks_statistic, ks_pvalue = stats.ks_2samp(
            df_ref['text_length'].dropna(),
            df_curr['text_length'].dropna()
        )
        
        drift_detected = ks_pvalue < 0.05
        
        if drift_detected:
            print(f"   Dérive détectée dans la longueur des textes")
        else:
            print(f"   Pas de dérive")
        
        return {
            'ks_statistic': float(ks_statistic),
            'ks_pvalue': float(ks_pvalue),
            'drift_detected': drift_detected,
            'mean_reference': float(ref_mean),
            'mean_current': float(curr_mean),
            'mean_change': float(change)
        }
    
    def detect_company_distribution_drift(self, df_ref, df_curr):
        print("\n" + "="*80)
        print("ANALYSE DE DÉRIVE - DISTRIBUTION DES ENTREPRISES")
        print("="*80)
        
        ref_companies = df_ref['company_name'].value_counts(normalize=True)
        curr_companies = df_curr['company_name'].value_counts(normalize=True)
        
        print("\nTop 5 entreprises - Référence:")
        for comp, pct in ref_companies.head(5).items():
            print(f"   {comp}: {pct:.2%}")
        
        print("\nTop 5 entreprises - Courant:")
        for comp, pct in curr_companies.head(5).items():
            print(f"   {comp}: {pct:.2%}")
        
        ref_set = set(ref_companies.index)
        curr_set = set(curr_companies.index)
        
        new_companies = curr_set - ref_set
        missing_companies = ref_set - curr_set
        
        if new_companies:
            print(f"\nNouvelles entreprises ({len(new_companies)}): {', '.join(list(new_companies)[:5])}")
        
        if missing_companies:
            print(f"\nEntreprises disparues ({len(missing_companies)}): {', '.join(list(missing_companies)[:5])}")
        
        return {
            'new_companies': list(new_companies),
            'missing_companies': list(missing_companies),
            'n_new': len(new_companies),
            'n_missing': len(missing_companies),
            'top_5_reference': ref_companies.head(5).to_dict(),
            'top_5_current': curr_companies.head(5).to_dict()
        }
    
    def generate_visualization(self, df_ref, df_curr, report_data):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        viz_path = self.reports_dir / f'drift_visualization_{timestamp}.png'
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Distribution des ratings
        ax1 = axes[0, 0]
        ref_dist = pd.Series(report_data['rating_drift']['distribution_reference'])
        curr_dist = pd.Series(report_data['rating_drift']['distribution_current'])
        
        x = np.arange(len(ref_dist))
        width = 0.35
        ax1.bar(x - width/2, ref_dist.values, width, label='Référence', alpha=0.8)
        ax1.bar(x + width/2, curr_dist.values, width, label='Courant', alpha=0.8)
        ax1.set_xlabel('Rating (étoiles)')
        ax1.set_ylabel('Proportion')
        ax1.set_title('Distribution des Ratings')
        ax1.set_xticks(x)
        ax1.set_xticklabels(ref_dist.index)
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. Évolution temporelle des ratings
        ax2 = axes[0, 1]
        df_combined = pd.concat([
            df_ref.assign(period='Référence'),
            df_curr.assign(period='Courant')
        ])
        df_combined['date_binned'] = pd.to_datetime(df_combined['date']).dt.to_period('W')
        weekly_avg = df_combined.groupby(['date_binned', 'period'])['rating'].mean().unstack()
        
        if not weekly_avg.empty:
            weekly_avg.plot(ax=ax2, marker='o')
            ax2.set_title('Évolution des Ratings au Fil du Temps')
            ax2.set_xlabel('Semaine')
            ax2.set_ylabel('Rating Moyen')
            ax2.legend()
            ax2.grid(alpha=0.3)
        
        # 3. Distribution de la longueur des textes
        ax3 = axes[1, 0]
        ax3.hist(df_ref['content'].fillna('').str.len(), bins=50, alpha=0.5, label='Référence', density=True)
        ax3.hist(df_curr['content'].fillna('').str.len(), bins=50, alpha=0.5, label='Courant', density=True)
        ax3.set_xlabel('Longueur du texte (caractères)')
        ax3.set_ylabel('Densité')
        ax3.set_title('Distribution de la Longueur des Textes')
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        # 4. Résumé des dérives détectées
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        drift_summary = []
        drift_summary.append("RÉSUMÉ DES DÉRIVES DÉTECTÉES\n")
        drift_summary.append("="*40 + "\n\n")
        
        if report_data['rating_drift']['drift_detected']:
            drift_summary.append("Dérive RATINGS détectée\n")
            drift_summary.append(f"   p-value: {report_data['rating_drift']['ks_pvalue']:.4f}\n")
            drift_summary.append(f"   Δ moyenne: {report_data['rating_drift']['mean_change']:+.2f}★\n\n")
        else:
            drift_summary.append("Pas de dérive RATINGS\n\n")
        
        if report_data['text_length_drift']['drift_detected']:
            drift_summary.append("Dérive LONGUEUR TEXTE détectée\n")
            drift_summary.append(f"   Δ moyenne: {report_data['text_length_drift']['mean_change']:+.0f} chars\n\n")
        else:
            drift_summary.append("Pas de dérive LONGUEUR TEXTE\n\n")
        
        if report_data['company_drift']['n_new'] > 0 or report_data['company_drift']['n_missing'] > 0:
            drift_summary.append(f"Changements ENTREPRISES:\n")
            drift_summary.append(f"   Nouvelles: {report_data['company_drift']['n_new']}\n")
            drift_summary.append(f"   Disparues: {report_data['company_drift']['n_missing']}\n")
        
        ax4.text(0.1, 0.5, ''.join(drift_summary), fontsize=11, family='monospace',
                verticalalignment='center')
        
        plt.tight_layout()
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\nVisualisation sauvégardée: {viz_path}")
        return str(viz_path)
    
    def generate_report(self):
        """Génère rapport"""
        print("\n" + "="*80)
        print("GÉNÉRATION DU RAPPORT DE DATA DRIFT")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Données
        df = self.load_data()
        
        if df.empty:
            print("Aucune donnée disponible")
            return None
        
        # Split
        df_ref, df_curr = self.split_data_by_time(df)
        
        # Analyses de dérive
        rating_drift = self.detect_rating_drift(df_ref, df_curr)
        text_length_drift = self.detect_text_length_drift(df_ref, df_curr)
        company_drift = self.detect_company_distribution_drift(df_ref, df_curr)
        
        # Rapport complet
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_reviews': len(df),
                'reference_size': len(df_ref),
                'current_size': len(df_curr),
                'reference_period': {
                    'start': str(df_ref['date'].min()),
                    'end': str(df_ref['date'].max())
                },
                'current_period': {
                    'start': str(df_curr['date'].min()),
                    'end': str(df_curr['date'].max())
                }
            },
            'rating_drift': rating_drift,
            'text_length_drift': text_length_drift,
            'company_drift': company_drift,
            'overall_drift_detected': (
                rating_drift['drift_detected'] or 
                text_length_drift['drift_detected']
            )
        }
        
        # Viz
        viz_path = self.generate_visualization(df_ref, df_curr, report)
        report['visualization_path'] = viz_path
        
        # Save JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.reports_dir / f'data_drift_report_{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*80)
        print("RAPPORT GÉNÉRÉ")
        print("="*80)
        print(f"Rapport JSON: {report_path}")
        print(f"Visualisation: {viz_path}")
        
        # Résumé
        print("\n" + "="*80)
        print("RÉSUMÉ EXÉCUTIF")
        print("="*80)
        
        if report['overall_drift_detected']:
            print("\nALERTE: DÉRIVE DES DONNÉES DÉTECTÉE")
            print("\nActions recommandées:")
            print("   1. Réentraîner les modèles avec les nouvelles données")
            print("   2. Ajuster les hyperparamètres si nécessaire")
            print("   3. Vérifier la qualité des prédictions en production")
        else:
            print("\nAUCUNE DÉRIVE SIGNIFICATIVE DÉTECTÉE")
            print("\nLes modèles en production restent valides.")
        
        return report

if __name__ == "__main__":
    
    monitor = DataDriftMonitor()
    report = monitor.generate_report()
    
    if report:
        print("\nRapport de data drift généré")
    else:
        print("\nÉchec de la génération du rapport")
