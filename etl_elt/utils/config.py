"""
Configuration du projet de scraping Trustpilot
"""

import os
from datetime import datetime

# Configuration du logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

# Configuration du scraper
SCRAPER_CONFIG = {
    'request_delay': 1.0,           # Délai entre les requêtes en secondes
    'max_pages_per_run': 10,        # Pages maximum par exécution
    'timeout': 30,                  # Timeout des requêtes
    'retry_attempts': 3,            # Tentatives de réessai
}

# Chemins des fichiers
PATHS = {
    'data_dir': 'data',
    'state_dir': 'data/scraping_state',
    'logs_dir': 'logs',
    'output_dir': 'output'
}

# Headers pour les requêtes
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Création des répertoires
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)