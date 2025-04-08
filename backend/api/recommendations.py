from fastapi import APIRouter
from ..services.recommender import CarRecommender

router = APIRouter()
recommender = CarRecommender()

@router.get("/")
async def get_recommendations(budget: float, seats: int):
    try:
        recommendations = recommender.recommend(budget, seats)
        return {
            "count": len(recommendations),
            "results": recommendations
        }
    except Exception as e:
        return {"error": str(e)}