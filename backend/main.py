from fastapi import FastAPI
from backend.services.recommender import CarRecommender

app = FastAPI(title="Carvise.ai API")
recommender = CarRecommender()

@app.get("/")
def read_root():
    return {"message": "Welcome to Carvise.ai!"}

@app.get("/recommendations")
def get_recommendations(budget: int, family_size: int):
    recommendations = recommender.recommend(budget, family_size)
    return {"recommendations": recommendations}