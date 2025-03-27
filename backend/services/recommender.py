import pandas as pd

class CarRecommender:
    def __init__(self):
        # Mock data (replace with real data or ML model predictions)
        self.cars = [
            {"make": "Honda", "model": "Civic", "price": 25000, "seats": 5, "l/100km": 36},
            {"make": "Toyota", "model": "Camry", "price": 28000, "seats": 5, "l/100km": 34},
            {"make": "Ford", "model": "Explorer", "price": 35000, "seats": 7, "l/100km": 24},
            {"make": "Honda", "model": "Accord", "price": 27000, "seats": 5, "l/100km": 32},
            {"make": "Toyota", "model": "Rav4", "price": 32000, "seats": 5, "l/100km": 30},
            {"make": "Hyundai", "model": "Tucson", "price": 29000, "seats": 5, "l/100km": 28},
            {"make": "Chevrolet", "model": "Equinox", "price": 31000, "seats": 5, "l/100km": 26},
            {"make": "Subaru", "model": "Outback", "price": 34000, "seats": 5, "l/100km": 25},
            {"make": "Jeep", "model": "Grand Cherokee", "price": 38000, "seats": 5, "l/100km": 23},
            {"make": "Ford", "model": "F-150", "price": 45000, "seats": 5, "l/100km": 20}]

    def recommend(self, budget: float, seats: int):
        # Filter cars based on budget and seats
        filtered_cars = [
            car for car in self.cars
            if car["price"] <= budget and car["seats"] >= seats
        ]
        return filtered_cars