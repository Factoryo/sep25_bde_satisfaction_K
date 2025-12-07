import requests
import time
import sys
from pathlib import Path

API_URL = "http://localhost:8002"
TIMEOUT = 10

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def test_health_check():
    print_info("Test 1/7: Health Check")
    try:
        response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code} (attendu: 200)")
            return False
        
        data = response.json()
        
        if data.get('status') != 'healthy':
            print_error(f"Status: {data.get('status')} (attendu: healthy)")
            return False
        
        if not data.get('model_loaded'):
            print_error("Modèle non chargé")
            return False
        
        print_success(f"Health check OK - Modèle: {data.get('model_name')}")
        return True
        
    except requests.RequestException as e:
        print_error(f"Erreur de connexion: {e}")
        return False

def test_predict_single():
    print_info("Test 2/7: Prédiction Simple")
    
    test_cases = [
        {
            "input": {
                "text": "Service excellent, livraison rapide et produit de qualité!",
                "title": "Très satisfait"
            },
            "expected_sentiment": "positif",
            "description": "Avis positif"
        },
        {
            "input": {
                "text": "Produit défectueux, service client absent, je déconseille fortement",
                "title": "Très déçu"
            },
            "expected_sentiment": "negatif",
            "description": "Avis négatif"
        },
        {
            "input": {
                "text": "Correct, sans plus, correspond à la description",
                "title": "Moyen"
            },
            "expected_sentiment": "neutre",
            "description": "Avis neutre"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{API_URL}/api/ml/predict",
                json=test_case["input"],
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                print_error(f"  Test {i} - Status: {response.status_code}")
                continue
            
            data = response.json()
            
            required_fields = ['sentiment', 'confidence', 'probabilities', 'cleaned_text']
            if not all(field in data for field in required_fields):
                print_error(f"  Test {i} - Champs manquants dans la réponse")
                continue
            
            predicted = data['sentiment']
            expected = test_case['expected_sentiment']
            confidence = data['confidence']
            
            if predicted == expected:
                print_success(f"  Test {i} ({test_case['description']}): {predicted} (confiance: {confidence:.2%})")
                success_count += 1
            else:
                print_warning(f"  Test {i} ({test_case['description']}): prédit {predicted}, attendu {expected}")
                
        except requests.RequestException as e:
            print_error(f"  Test {i} - Erreur: {e}")
    
    if success_count == len(test_cases):
        print_success(f"Tous les tests de prédiction réussis ({success_count}/{len(test_cases)})")
        return True
    else:
        print_warning(f"Prédictions: {success_count}/{len(test_cases)} réussies")
        return success_count > 0

def test_predict_batch():
    print_info("Test 3/7: Prédictions Batch")
    
    reviews = [
        {"text": "Excellent produit, je recommande!", "title": "Top"},
        {"text": "Très mauvais, à éviter absolument", "title": "Nul"},
        {"text": "Correct sans plus", "title": "OK"}
    ]
    
    try:
        response = requests.post(
            f"{API_URL}/api/ml/predict-batch",
            json={"reviews": reviews},
            timeout=TIMEOUT * 2
        )
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if data.get('count') != len(reviews):
            print_error(f"Nombre de prédictions: {data.get('count')} (attendu: {len(reviews)})")
            return False
        
        predictions = data.get('predictions', [])
        
        if len(predictions) != len(reviews):
            print_error(f"Longueur prédictions: {len(predictions)}")
            return False
        
        print_success(f"Batch de {len(reviews)} prédictions réussi")
        for i, pred in enumerate(predictions, 1):
            print(f"    Review {i}: {pred['sentiment']} ({pred['confidence']:.2%})")
        
        return True
        
    except requests.RequestException as e:
        print_error(f"Erreur: {e}")
        return False

def test_model_info():
    print_info("Test 4/7: Informations du Modèle")
    
    try:
        response = requests.get(f"{API_URL}/api/ml/model-info", timeout=TIMEOUT)
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        required_fields = ['model_name', 'f1_score', 'training_date', 'dataset_size']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_error(f"Champs manquants: {', '.join(missing_fields)}")
            return False
        
        print_success(f"Modèle: {data['model_name']}")
        print(f"    F1-Score: {data['f1_score']:.3f}")
        print(f"    Dataset: {data['dataset_size']:,} reviews")
        print(f"    Entraîné le: {data['training_date']}")
        
        return True
        
    except requests.RequestException as e:
        print_error(f"Erreur: {e}")
        return False

def test_model_performance():
    print_info("Test 5/7: Performance des Modèles")
    
    try:
        response = requests.get(f"{API_URL}/api/ml/model-performance", timeout=TIMEOUT)
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if 'models' not in data or 'best_model' not in data:
            print_error("Champs 'models' ou 'best_model' manquants")
            return False
        
        models = data['models']
        
        if not models:
            print_error("Aucun modèle dans la réponse")
            return False
        
        print_success(f"Meilleur modèle: {data['best_model']}")
        
        for model_name, metrics in models.items():
            print(f"    {model_name}:")
            print(f"      F1: {metrics.get('f1', 0):.3f}")
            print(f"      Precision: {metrics.get('precision', 0):.3f}")
            print(f"      Recall: {metrics.get('recall', 0):.3f}")
        
        return True
        
    except requests.RequestException as e:
        print_error(f"Erreur: {e}")
        return False

def test_error_handling():
    print_info("Test 6/7: Gestion des Erreurs")
    
    try:
        response = requests.post(
            f"{API_URL}/api/ml/predict",
            json={"text": "", "title": ""},
            timeout=TIMEOUT
        )
        
        if response.status_code != 400:
            print_error(f"Texte vide devrait retourner 400, reçu: {response.status_code}")
            return False
        
        print_success("Gestion texte vide: OK")
        
    except requests.RequestException as e:
        print_error(f"Erreur: {e}")
        return False
    
    try:
        response = requests.post(
            f"{API_URL}/api/ml/predict",
            json={"wrong_field": "test"},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [400, 422]:
            print_error(f"JSON invalide devrait retourner 400/422, reçu: {response.status_code}")
            return False
        
        print_success("Gestion JSON invalide: OK")
        return True
        
    except requests.RequestException as e:
        print_error(f"Erreur: {e}")
        return False

def test_performance():
    print_info("Test 7/7: Performance")
    
    test_review = {
        "text": "Produit de bonne qualité, livraison rapide",
        "title": "Satisfait"
    }
    
    n_requests = 10
    durations = []
    
    print(f"  Envoi de {n_requests} requêtes...")
    
    for i in range(n_requests):
        try:
            start = time.time()
            response = requests.post(
                f"{API_URL}/api/ml/predict",
                json=test_review,
                timeout=TIMEOUT
            )
            duration = (time.time() - start) * 1000  # en ms
            
            if response.status_code == 200:
                durations.append(duration)
            else:
                print_warning(f"  Requête {i+1} échouée: {response.status_code}")
                
        except requests.RequestException as e:
            print_warning(f"  Requête {i+1} échouée: {e}")
    
    if not durations:
        print_error("Aucune requête réussie")
        return False
    
    avg_duration = sum(durations) / len(durations)
    min_duration = min(durations)
    max_duration = max(durations)
    
    print_success(f"Performance sur {len(durations)} requêtes:")
    print(f"    Moyenne: {avg_duration:.1f}ms")
    print(f"    Min: {min_duration:.1f}ms")
    print(f"    Max: {max_duration:.1f}ms")
    print(f"    Throughput: {1000/avg_duration:.1f} req/s")
    
    if avg_duration > 1000:
        print_warning("  Latence élevée (>1s)")
        return False
    
    return True

def check_prerequisites():
    print_info("Vérification des prérequis...")
    
    script_dir = Path(__file__).parent
    models_dir = script_dir.parent / "scripts" / "ml" / "models"
    
    if not models_dir.exists():
        print_error(f"Répertoire des modèles introuvable: {models_dir}")
        return False
    
    required_files = [
        "sentiment_model_best.pkl",
        "tfidf_vectorizer.pkl",
        "models_metadata.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not (models_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print_error(f"Fichiers manquants: {', '.join(missing_files)}")
        print_info("Exécutez la cellule 24 du notebook pour générer les modèles")
        return False
    
    print_success("Tous les fichiers de modèles présents")
    return True

def main():
    print("\n" + "="*70)
    print("TESTS DE VALIDATION - ML API")
    print("="*70 + "\n")
    
    print(f"URL de l'API: {API_URL}")
    print(f"Timeout: {TIMEOUT}s\n")
    
    if not check_prerequisites():
        print("\n" + "="*70)
        print_error("ÉCHEC: Prérequis non satisfaits")
        print("="*70 + "\n")
        sys.exit(1)
    
    print()
    
    tests = [
        ("Health Check", test_health_check),
        ("Prédiction Simple", test_predict_single),
        ("Prédictions Batch", test_predict_batch),
        ("Informations Modèle", test_model_info),
        ("Performance Modèles", test_model_performance),
        ("Gestion d'Erreurs", test_error_handling),
        ("Performance", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print_error(f"Exception dans {test_name}: {e}")
            results.append((test_name, False))
            print()
    
    # Résumé
    print("="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print_success(f"TOUS LES TESTS RÉUSSIS ({passed}/{total})")
        print("="*70 + "\n")
        print_success("L'API ML est prête pour la production")
        sys.exit(0)
    else:
        print_warning(f"TESTS RÉUSSIS: {passed}/{total}")
        print("="*70 + "\n")
        
        if passed >= total * 0.7:
            print_warning("Certains tests ont échoué, mais l'API est fonctionnelle")
            sys.exit(0)
        else:
            print_error("Trop de tests ont échoué, vérifier la configuration")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrompus par l'utilisateur")
        sys.exit(1)
