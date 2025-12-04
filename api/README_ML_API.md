# ML API - Documentation

API FastAPI pour les prédictions de sentiment sur les avis Trustpilot.

## 🚀 Démarrage Rapide

### Prérequis
- Modèles ML entraînés dans `../scripts/ml/models/`
- Python 3.11+
- Dépendances installées

### Installation
```bash
pip install -r requirements_ml.txt
```

### Lancer l'API
```bash
uvicorn ml_api:app --reload --port 8001
```

L'API sera disponible sur http://localhost:8001

## 📖 Endpoints

### 🏥 Health Check
```http
GET /health
```

Vérifie que le modèle est correctement chargé.

**Réponse:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "LogisticRegression",
  "timestamp": "2024-12-04T15:30:00.123456"
}
```

### 🔮 Prédiction Simple
```http
POST /api/ml/predict
Content-Type: application/json
```

Prédit le sentiment d'un seul avis.

**Corps de la requête:**
```json
{
  "text": "Service excellent, livraison rapide et produit conforme à la description!",
  "title": "Très satisfait de mon achat"
}
```

**Réponse:**
```json
{
  "sentiment": "positif",
  "confidence": 0.92,
  "probabilities": {
    "positif": 0.92,
    "negatif": 0.05,
    "neutre": 0.03
  },
  "cleaned_text": "service excellent livraison rapide produit conforme description"
}
```

### 📦 Prédictions Batch
```http
POST /api/ml/predict-batch
Content-Type: application/json
```

Prédit le sentiment de plusieurs avis en une seule requête.

**Corps de la requête:**
```json
{
  "reviews": [
    {
      "text": "Service excellent!",
      "title": "Top"
    },
    {
      "text": "Très déçu, produit défectueux et service client inexistant",
      "title": "À éviter"
    },
    {
      "text": "Correct, sans plus",
      "title": "Moyen"
    }
  ]
}
```

**Réponse:**
```json
{
  "predictions": [
    {
      "sentiment": "positif",
      "confidence": 0.88,
      "probabilities": {"positif": 0.88, "negatif": 0.07, "neutre": 0.05}
    },
    {
      "sentiment": "negatif",
      "confidence": 0.91,
      "probabilities": {"positif": 0.04, "negatif": 0.91, "neutre": 0.05}
    },
    {
      "sentiment": "neutre",
      "confidence": 0.65,
      "probabilities": {"positif": 0.20, "negatif": 0.15, "neutre": 0.65}
    }
  ],
  "count": 3
}
```

### ℹ️ Informations du Modèle
```http
GET /api/ml/model-info
```

Retourne les métadonnées du modèle en production.

**Réponse:**
```json
{
  "model_name": "LogisticRegression",
  "f1_score": 0.87,
  "training_date": "2024-12-04T14:30:00",
  "dataset_size": 21795,
  "n_features": 5000,
  "sentiment_distribution": {
    "positif": 0.65,
    "negatif": 0.20,
    "neutre": 0.15
  }
}
```

### 📊 Performance des Modèles
```http
GET /api/ml/model-performance
```

Compare les performances de tous les modèles entraînés.

**Réponse:**
```json
{
  "models": {
    "LogisticRegression": {
      "f1": 0.87,
      "precision": 0.88,
      "recall": 0.86
    },
    "MultinomialNB": {
      "f1": 0.82,
      "precision": 0.81,
      "recall": 0.83
    },
    "RandomForest": {
      "f1": 0.84,
      "precision": 0.85,
      "recall": 0.83
    }
  },
  "best_model": "LogisticRegression"
}
```

## 💻 Exemples d'Utilisation

### cURL

#### Prédiction simple
```bash
curl -X POST http://localhost:8001/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Produit de très bonne qualité, je recommande vivement!",
    "title": "Excellent achat"
  }'
```

#### Health check
```bash
curl http://localhost:8001/health
```

### Python (requests)

```python
import requests

# Configuration
API_URL = "http://localhost:8001"

# 1. Vérifier la santé de l'API
health = requests.get(f"{API_URL}/health")
print(f"Status: {health.json()['status']}")

# 2. Prédiction simple
review = {
    "text": "Service client médiocre, délai de livraison non respecté",
    "title": "Déçu"
}

response = requests.post(
    f"{API_URL}/api/ml/predict",
    json=review
)

prediction = response.json()
print(f"Sentiment: {prediction['sentiment']}")
print(f"Confiance: {prediction['confidence']:.2%}")

# 3. Prédictions batch
reviews = [
    {"text": "Excellent produit!", "title": "Top"},
    {"text": "Très mauvais, à éviter", "title": "Nul"},
    {"text": "Correct", "title": "OK"}
]

response = requests.post(
    f"{API_URL}/api/ml/predict-batch",
    json={"reviews": reviews}
)

predictions = response.json()['predictions']
for i, pred in enumerate(predictions):
    print(f"Review {i+1}: {pred['sentiment']} ({pred['confidence']:.2%})")

# 4. Informations du modèle
model_info = requests.get(f"{API_URL}/api/ml/model-info").json()
print(f"Modèle: {model_info['model_name']}")
print(f"F1-Score: {model_info['f1_score']}")
print(f"Entraîné sur {model_info['dataset_size']} reviews")
```

### JavaScript (Fetch API)

```javascript
// Configuration
const API_URL = 'http://localhost:8001';

// Prédiction simple
async function predictSentiment(text, title) {
  const response = await fetch(`${API_URL}/api/ml/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, title })
  });
  
  return await response.json();
}

// Utilisation
predictSentiment(
  "Service excellent et livraison rapide!",
  "Très satisfait"
).then(result => {
  console.log(`Sentiment: ${result.sentiment}`);
  console.log(`Confiance: ${(result.confidence * 100).toFixed(1)}%`);
});

// Prédictions batch
async function predictBatch(reviews) {
  const response = await fetch(`${API_URL}/api/ml/predict-batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reviews })
  });
  
  return await response.json();
}

// Informations du modèle
async function getModelInfo() {
  const response = await fetch(`${API_URL}/api/ml/model-info`);
  return await response.json();
}
```

## 🔐 Codes d'État HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Requête réussie |
| 400 | Bad Request | Données invalides (texte vide, format incorrect) |
| 503 | Service Unavailable | Modèle non chargé |
| 500 | Internal Server Error | Erreur inattendue |

## ⚙️ Configuration

### Variables d'Environnement

```bash
# Port de l'API (défaut: 8001)
export ML_API_PORT=8001

# Chemin vers les modèles
export MODELS_PATH="../scripts/ml/models"
```

### Personnalisation du Prétraitement

Le texte subit les transformations suivantes :
1. Conversion en minuscules
2. Suppression des URLs
3. Suppression des adresses email
4. Suppression des caractères spéciaux
5. Normalisation des espaces

Pour modifier, éditer la fonction `clean_text()` dans `ml_api.py`.

## 🧪 Tests

### Test Unitaire (pytest)

```python
# test_ml_api.py
import pytest
from fastapi.testclient import TestClient
from ml_api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict():
    review = {
        "text": "Service excellent!",
        "title": "Top"
    }
    response = client.post("/api/ml/predict", json=review)
    assert response.status_code == 200
    assert "sentiment" in response.json()
    assert "confidence" in response.json()

def test_predict_empty_text():
    review = {"text": "", "title": ""}
    response = client.post("/api/ml/predict", json=review)
    assert response.status_code == 400
```

### Test de Charge (locust)

```python
# locustfile.py
from locust import HttpUser, task, between

class MLAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def predict(self):
        self.client.post("/api/ml/predict", json={
            "text": "Service excellent et livraison rapide!",
            "title": "Satisfait"
        })
    
    @task(1)
    def model_info(self):
        self.client.get("/api/ml/model-info")
    
    @task(1)
    def health(self):
        self.client.get("/health")
```

Lancer les tests :
```bash
locust -f locustfile.py --host=http://localhost:8001
```

## 🐛 Debugging

### Activer les Logs Détaillés

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Vérifier le Chargement des Modèles

```bash
# Vérifier que les fichiers existent
ls -lh ../scripts/ml/models/

# Logs de l'API au démarrage
uvicorn ml_api:app --log-level debug
```

### Problèmes Courants

**Erreur: "Modèles non chargés"**
- Vérifier que `sentiment_model_best.pkl` et `tfidf_vectorizer.pkl` existent
- Exécuter la cellule 24 du notebook pour générer les modèles

**Erreur: "Text cannot be empty"**
- S'assurer que le champ `text` contient au moins un caractère non-vide

**Erreur de prédiction**
- Vérifier que le texte est en français
- Vérifier la compatibilité des versions scikit-learn

## 📊 Monitoring en Production

### Métriques à Surveiller

1. **Latence** : Temps de réponse des prédictions
2. **Throughput** : Nombre de prédictions/seconde
3. **Distribution des sentiments** : Changements dans les prédictions
4. **Confiance moyenne** : Baisse = modèle incertain
5. **Erreurs 503** : Problème de chargement des modèles

### Intégration Prometheus

```python
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

# Métriques custom
predictions_counter = Counter(
    'ml_predictions_total',
    'Total predictions',
    ['sentiment']
)

prediction_duration = Histogram(
    'ml_prediction_duration_seconds',
    'Prediction duration'
)

# Instrumenter FastAPI
Instrumentator().instrument(app).expose(app)
```

## 🚀 Performance

### Benchmarks (machine locale)

| Métrique | Valeur |
|----------|--------|
| Latence prédiction simple | 10-50ms |
| Latence batch (100 reviews) | 500-800ms |
| Throughput | 100-200 req/s |
| Mémoire utilisée | ~100 MB |
| Taille modèle | ~5 MB |

### Optimisations

1. **Batch processing** : Utiliser `/predict-batch` pour plusieurs reviews
2. **Caching** : Cache les prédictions pour textes identiques
3. **Load balancing** : Multiple instances derrière nginx
4. **GPU** : Pour les modèles plus complexes (transformers)

## 📚 Documentation Interactive

Une fois l'API lancée, accéder à :
- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

Ces interfaces permettent de tester directement les endpoints.

## 🔗 Liens Utiles

- [Guide de Production Complet](../docs/ML_PRODUCTION_GUIDE.md)
- [Notebook ML](../notebooks/sentiment_analysis.ipynb)
- [Data Drift Monitor](../scripts/ml/data_drift_monitor.py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scikit-learn Docs](https://scikit-learn.org/)
