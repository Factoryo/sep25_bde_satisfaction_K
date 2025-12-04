"""
Script simple pour tester l'API ML localement
"""
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("Démarrage de l'API ML sur http://localhost:8001")
    print("Appuyez sur Ctrl+C pour arrêter\n")
    
    uvicorn.run(
        "api.ml_api:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="info"
    )
