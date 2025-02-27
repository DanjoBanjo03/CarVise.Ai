from fastapi import APIRouter
from ..services.recommender import CarRecommender

router = APIRouter()
recommender = CarRecommender()

@router.get("/")
async def get_recommendations(budget: float, seats: int):
    return recommender.recommend(budget, seats)