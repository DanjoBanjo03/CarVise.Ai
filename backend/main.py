from fastapi import FastAPI
from backend.services.recommender import CarRecommender
from fastapi import HTTPException


app = FastAPI(title="Carvise.ai API")
recommender = CarRecommender()

@app.get("/")
def read_root():
    return {"message": "Welcome to Carvise.ai!"}

@app.get("/recommendations")
def get_recommendations(budget: int, family_size: int):
    try:
        recommendations = recommender.recommend(budget, family_size)
        return {
            "status": "success",
            "count": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )