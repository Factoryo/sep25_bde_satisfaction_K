"""
API FastAPI pour l'analyse de sentiment - Modèles ML
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import joblib
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentiment Analysis ML API",
    description="API de prédiction de sentiment basée sur les avis Trustpilot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger les modèles au démarrage - utiliser chemin absolu
base_dir = Path(__file__).parent.parent
models_dir = base_dir / "scripts" / "ml" / "models"
MODEL = None
VECTORIZER = None
METADATA = None

def clean_text(text: str) -> str:
    """
    Nettoie le texte pour la prédiction
    """
    if not text:
        return ""
    
    # Convertir en minuscules
    text = text.lower()
    
    # Supprimer les URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Supprimer les emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Garder uniquement les lettres et espaces
    text = re.sub(r'[^a-zA-Zàâäéèêëïîôùûüÿç\s]', ' ', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

@app.on_event("startup")
async def load_models():
    """Charger les modèles au démarrage de l'API"""
    global MODEL, VECTORIZER, METADATA
    
    try:
        logger.info(f"Chargement des modèles depuis: {models_dir}")
        
        model_path = models_dir / "sentiment_model_best.pkl"
        vectorizer_path = models_dir / "tfidf_vectorizer.pkl"
        metadata_path = models_dir / "models_metadata.json"
        
        if not model_path.exists():
            logger.error(f"Modèle non trouvé: {model_path}")
            logger.error("Exécutez d'abord le notebook pour entraîner et sauvegarder les modèles")
            return
        
        logger.info(f"Chargement du modèle: {model_path}")
        MODEL = joblib.load(model_path)
        
        logger.info(f"Chargement du vectoriseur: {vectorizer_path}")
        VECTORIZER = joblib.load(vectorizer_path)
        
        if metadata_path.exists():
            import json
            logger.info(f"Chargement des métadonnées: {metadata_path}")
            with open(metadata_path, 'r', encoding='utf-8') as f:
                METADATA = json.load(f)
        
        logger.info("✓ Modèles chargés avec succès!")
        if METADATA:
            logger.info(f"  Meilleur modèle: {METADATA.get('best_model')}")
            logger.info(f"  F1-Score: {METADATA.get('best_f1_score', 0):.4f}")
            logger.info(f"  Dataset size: {METADATA.get('dataset_size')}")
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement des modèles: {e}")
        logger.exception("Détails de l'erreur:")
        # Ne pas lever l'exception pour permettre à l'API de démarrer

# Pydantic models
class ReviewInput(BaseModel):
    text: str
    title: Optional[str] = ""

class SentimentPrediction(BaseModel):
    sentiment: str
    confidence: float
    probabilities: Dict[str, float]
    cleaned_text: str

class ModelInfo(BaseModel):
    model_name: str
    f1_score: float
    training_date: str
    dataset_size: int
    n_features: int
    sentiment_distribution: Dict[str, int]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "API d'Analyse de Sentiment - Trustpilot",
        "version": "1.0.0",
        "status": "running" if MODEL is not None else "models_not_loaded",
        "endpoints": {
            "predict": "/api/ml/predict",
            "model_info": "/api/ml/model-info",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if MODEL is not None else "unhealthy",
        "model_loaded": MODEL is not None,
        "vectorizer_loaded": VECTORIZER is not None
    }

@app.post("/api/ml/predict", response_model=SentimentPrediction)
async def predict_sentiment(review: ReviewInput):
    """
    Prédire le sentiment d'un avis client
    
    - **text**: Le contenu de l'avis
    - **title**: Le titre de l'avis (optionnel)
    """
    if MODEL is None or VECTORIZER is None:
        raise HTTPException(
            status_code=503,
            detail="Modèles non chargés. Veuillez entraîner les modèles d'abord."
        )
    
    try:
        # Combiner titre et texte
        full_text = f"{review.title} {review.text}".strip()
        
        # Nettoyer le texte
        cleaned = clean_text(full_text)
        
        if not cleaned:
            raise HTTPException(
                status_code=400,
                detail="Le texte est vide après nettoyage"
            )
        
        # Vectoriser
        text_vectorized = VECTORIZER.transform([cleaned])
        
        # Prédire
        prediction = MODEL.predict(text_vectorized)[0]
        
        # Obtenir les probabilités
        probabilities = {}
        confidence = 0.0
        
        if hasattr(MODEL, 'predict_proba'):
            probas = MODEL.predict_proba(text_vectorized)[0]
            classes = MODEL.classes_
            
            probabilities = {
                cls: float(prob) for cls, prob in zip(classes, probas)
            }
            
            # Confidence = probabilité de la classe prédite
            confidence = float(probas[list(classes).index(prediction)])
        
        return SentimentPrediction(
            sentiment=prediction,
            confidence=confidence,
            probabilities=probabilities,
            cleaned_text=cleaned[:200] + "..." if len(cleaned) > 200 else cleaned
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/predict-batch", response_model=List[SentimentPrediction])
async def predict_batch(reviews: List[ReviewInput]):
    """
    Prédire le sentiment de plusieurs avis en batch
    """
    if MODEL is None or VECTORIZER is None:
        raise HTTPException(
            status_code=503,
            detail="Modèles non chargés"
        )
    
    results = []
    for review in reviews:
        try:
            result = await predict_sentiment(review)
            results.append(result)
        except Exception as e:
            logger.error(f"Erreur pour un avis: {e}")
            # Continuer avec les autres avis
            results.append(SentimentPrediction(
                sentiment="Erreur",
                confidence=0.0,
                probabilities={},
                cleaned_text=str(e)
            ))
    
    return results

@app.get("/api/ml/model-info", response_model=ModelInfo)
async def get_model_info():
    """
    Obtenir les informations sur le modèle en production
    """
    if METADATA is None:
        raise HTTPException(
            status_code=503,
            detail="Métadonnées non disponibles"
        )
    
    return ModelInfo(
        model_name=METADATA.get('best_model', 'Unknown'),
        f1_score=METADATA.get('best_f1_score', 0.0),
        training_date=METADATA.get('training_date', 'Unknown'),
        dataset_size=METADATA.get('dataset_size', 0),
        n_features=METADATA.get('n_features', 0),
        sentiment_distribution=METADATA.get('sentiment_distribution', {})
    )

@app.get("/api/ml/model-performance")
async def get_model_performance():
    """
    Obtenir les performances détaillées de tous les modèles
    """
    if METADATA is None or 'models_performance' not in METADATA:
        raise HTTPException(
            status_code=503,
            detail="Données de performance non disponibles"
        )
    
    return {
        "best_model": METADATA.get('best_model'),
        "best_f1_score": METADATA.get('best_f1_score'),
        "all_models": METADATA.get('models_performance', {}),
        "training_date": METADATA.get('training_date')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
