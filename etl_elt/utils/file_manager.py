import json
import os
from datetime import datetime
from typing import Dict, Any

class ScrapingStateManager:
    def __init__(self, state_file: str = "scraping_state.json"):
        self.state_file = state_file
        self.state_dir = "data/scraping_state"
        os.makedirs(self.state_dir, exist_ok=True)
        
    def save_state(self, company: str, last_page: int, total_reviews: int):
        """Sauvegarde état"""
        state = {
            'company': company,
            'last_page': last_page,
            'total_reviews': total_reviews,
            'last_update': datetime.now().isoformat()
        }
        
        file_path = os.path.join(self.state_dir, self.state_file)
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> Dict[str, Any]:
        """Charge état"""
        file_path = os.path.join(self.state_dir, self.state_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def clear_state(self):
        """Efface état"""
        file_path = os.path.join(self.state_dir, self.state_file)
        if os.path.exists(file_path):
            os.remove(file_path)