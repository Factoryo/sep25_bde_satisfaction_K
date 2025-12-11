from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import logging
import json
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trustpilot Reviews API",
    description="API pour accéder aux avis scrapés et aux stats",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_reviews_cache = None
_companies_cache = None

def load_reviews_from_files() -> List[dict]:
    """
    Charge les avis depuis les fichiers JSON scrapés.
    
    Les fichiers sont dans data/raw/ avec le format: {company}_reviews.json
    Cache pour éviter de relire les fichiers à chaque requête.
    """
    global _reviews_cache
    if _reviews_cache is not None:
        return _reviews_cache
    
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    all_reviews = []
    review_id = 1
    
    for json_file in data_dir.glob("*_reviews.json"):
        try:
            company_name = json_file.stem.replace('_reviews', '').replace('_', '.')
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if 'company_info' in data and data['company_info'].get('name'):
                    company_name = data['company_info']['name']
                
                reviews = data.get('reviews', [])
                for review in reviews:
                    content = review.get('content', '') or review.get('comment_text', '') or ''
                    title = review.get('title', '') or ''
                    
                    all_reviews.append({
                        'id': review_id,
                        'company': company_name,
                        'rating': float(review.get('rating', review.get('stars', 0))),
                        'comment': (title + ' ' + content).strip(),
                        'date': review.get('date', review.get('date_absolute', ''))
                    })
                    review_id += 1
        except Exception as e:
            logger.warning(f"Erreur lecture {json_file}: {e}")
    
    _reviews_cache = all_reviews
    logger.info(f"Chargé {len(all_reviews)} avis")
    return all_reviews

class Review(BaseModel):
    id: Optional[int] = None
    company: str
    rating: float
    comment: str
    date: Optional[str] = None

class SatisfactionStats(BaseModel):
    average_rating: float
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    neutral_reviews: int

@app.get("/")
async def root():
    return {
        "message": "Welcome to Supply Chain Satisfaction API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/stats", response_model=SatisfactionStats)
async def get_stats():
    reviews = load_reviews_from_files()
    
    if not reviews:
        return SatisfactionStats(
            average_rating=0, total_reviews=0,
            positive_reviews=0, negative_reviews=0, neutral_reviews=0
        )
    
    total = len(reviews)
    avg_rating = sum(r['rating'] for r in reviews) / total
    positive = sum(1 for r in reviews if r['rating'] >= 4)
    negative = sum(1 for r in reviews if r['rating'] <= 2)
    neutral = total - positive - negative
    
    return SatisfactionStats(
        average_rating=round(avg_rating, 2),
        total_reviews=total,
        positive_reviews=positive,
        negative_reviews=negative,
        neutral_reviews=neutral
    )

@app.get("/api/reviews", response_model=List[Review])
async def get_reviews(limit: int = 10, offset: int = 0, company: Optional[str] = None, shuffle: bool = True):
    reviews = load_reviews_from_files().copy()
    
    if company:
        reviews = [r for r in reviews if company.lower() in r['company'].lower()]
    
    if shuffle:
        random.shuffle(reviews)
    
    return [Review(**r) for r in reviews[offset:offset + limit]]

@app.post("/api/reviews", response_model=Review)
async def create_review(review: Review):
    logger.info(f"Creating review for company: {review.company}")
    return review

@app.get("/api/companies")
async def get_companies():
    reviews = load_reviews_from_files()
    company_counts = {}
    
    for r in reviews:
        company = r['company']
        company_counts[company] = company_counts.get(company, 0) + 1
    
    companies = [
        {"name": name, "review_count": count}
        for name, count in sorted(company_counts.items(), key=lambda x: -x[1])
    ]
    
    return {"companies": companies}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
