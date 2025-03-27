import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Sample data (replace with real dataset)
# data = {
#     'make': ['Honda', 'Toyota', 'Ford', 'Honda', 'Toyota'],
#     'model': ['Civic', 'Camry', 'Explorer', 'Accord', 'Rav4'],
#     'year': [2023, 2023, 2023, 2023, 2023],
#     'seats': [5, 5, 7, 5, 5],
#     'l/100km': [36, 34, 24, 32, 30],
#     'price': [25000, 28000, 35000, 27000, 32000]
# }
df = pd.read_csv('../scraping/data/car_prices.csv')

# Feature engineering
df = pd.get_dummies(df, columns=['make', 'model'])

# Train model
X = df.drop('price', axis=1)
y = df['price']
model = RandomForestRegressor()
model.fit(X, y)

# Save model
joblib.dump(model, "ml/models/recommendation_engine.pkl")
print("Model trained and saved!")