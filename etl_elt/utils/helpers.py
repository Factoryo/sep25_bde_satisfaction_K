"""Scraping utilitaire"""

import json
import re
import csv
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Nettoie le texte"""
    if not text:
        return ""
    
    # Espaces
    text = re.sub(r'\s+', ' ', text)
    # Nettoyage
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text.strip()

def parse_rating(rating_str: str) -> float:
    """Parsing"""
    try:
        # Formats
        if '/' in rating_str:
            numerator, denominator = rating_str.split('/')
            return float(numerator) / float(denominator) * 5
        else:
            return float(rating_str)
    except (ValueError, TypeError):
        logger.warning(f"Rating non parseable: {rating_str}")
        return 0.0

def save_to_csv(data: List[Dict], filename: str):
    """Sauvegarde du CSV"""
    if not data:
        logger.warning("Aucune donnée à sauvegarder en CSV")
        return
    
    fieldnames = data[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    logger.info(f"Données sauvegardées en CSV: {filename}")

def validate_company_name(company: str) -> bool:
    """Valide le nom"""
    # Domaine
    pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, company))

def generate_report(scraping_results: Dict[str, Any]) -> Dict[str, Any]:
    """Génère le rapport"""
    total_reviews = len(scraping_results.get('reviews', []))
    company_info = scraping_results.get('company_info', {})
    
    # Statistiques
    ratings = [review.get('rating', 0) for review in scraping_results.get('reviews', [])]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    report = {
        'scraping_date': datetime.now().isoformat(),
        'company_name': company_info.get('company_name', 'N/A'),
        'total_reviews': total_reviews,
        'average_rating': round(avg_rating, 2),
        'company_rating': company_info.get('rating', 'N/A'),
        'last_page_scraped': scraping_results.get('last_page_scraped', 0)
    }
    
    return report

def export_formats(data: Dict[str, Any], base_filename: str):
    """Export multi-format"""
    # JSON
    json_filename = f"{base_filename}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # CSV
    if data.get('reviews'):
        csv_filename = f"{base_filename}_reviews.csv"
        save_to_csv(data['reviews'], csv_filename)
    
    # Rapport
    report = generate_report(data)
    report_filename = f"{base_filename}_report.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Données exportées: {base_filename}*")