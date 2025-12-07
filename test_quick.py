"""Test simple de l'API ML"""
import requests
import json

API_URL = "http://localhost:8001"

print("Test de l'API ML\n")
print("=" * 60)

# Test 1: Health check
print("\n1. Test Health Check...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   PASS")
except Exception as e:
    print(f"   FAIL: {e}")

# Test 2: Prédiction simple - positif
print("\n2. Test Prédiction Positive...")
try:
    data = {
        "text": "Excellent service, livraison rapide et produit de qualité!",
        "title": "Très satisfait"
    }
    response = requests.post(f"{API_URL}/api/ml/predict", json=data, timeout=5)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Sentiment: {result.get('sentiment')}")
    print(f"   Confiance: {result.get('confidence'):.2%}")
    print("   PASS")
except Exception as e:
    print(f"   FAIL: {e}")

# Test 3: Prédiction simple - négatif
print("\n3. Test Prédiction Négative...")
try:
    data = {
        "text": "Service horrible, produit défectueux, je déconseille!",
        "title": "Très déçu"
    }
    response = requests.post(f"{API_URL}/api/ml/predict", json=data, timeout=5)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Sentiment: {result.get('sentiment')}")
    print(f"   Confiance: {result.get('confidence'):.2%}")
    print("   PASS")
except Exception as e:
    print(f"   FAIL: {e}")

# Test 4: Informations du modèle
print("\n4. Test Informations Modèle...")
try:
    response = requests.get(f"{API_URL}/api/ml/model-info", timeout=5)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Modèle: {result.get('model_name')}")
    print(f"   F1-Score: {result.get('f1_score'):.4f}")
    print(f"   Dataset: {result.get('dataset_size')} reviews")
    print("   PASS")
except Exception as e:
    print(f"   FAIL: {e}")

print("\n" + "=" * 60)
print("Tests terminés!")
print("\nAccédez à la documentation interactive:")
print(f"   http://localhost:8002/docs")
