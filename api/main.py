from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Supply Chain Satisfaction API",
    description="API for analyzing customer satisfaction in supply chain",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Accueil"""
    return {
        "message": "Welcome to Supply Chain Satisfaction API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Santé"""
    return {"status": "healthy"}

@app.get("/api/stats", response_model=SatisfactionStats)
async def get_stats():
    """Statistiques"""
    # TODO
    return SatisfactionStats(
        average_rating=4.2,
        total_reviews=1000,
        positive_reviews=750,
        negative_reviews=150,
        neutral_reviews=100
    )

@app.get("/api/reviews", response_model=List[Review])
async def get_reviews(limit: int = 10, offset: int = 0):
    sample_reviews = [
        Review(
            id=1,
            company="Company A",
            rating=4.5,
            comment="Great service and fast delivery",
            date="2025-11-01"
        ),
        Review(
            id=2,
            company="Company B",
            rating=3.0,
            comment="Average experience",
            date="2025-11-02"
        )
    ]
    return sample_reviews[:limit]

@app.post("/api/reviews", response_model=Review)
async def create_review(review: Review):
    logger.info(f"Creating review for company: {review.company}")
    return review

@app.get("/api/companies")
async def get_companies():
    return {
        "companies": [
            {"name": "Company A", "review_count": 450},
            {"name": "Company B", "review_count": 350},
            {"name": "Company C", "review_count": 200}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
