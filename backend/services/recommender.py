import pandas as pd
import joblib
from pathlib import Path
import numpy as np

class CarRecommender:
    def __init__(self):
        # Path resolution
        base_dir = Path(__file__).parent.parent.parent
        model_path = base_dir / "ml" / "car_price_model_prod.pkl"
        data_path = base_dir / "scraping" / "data" / "car_prices.csv"
        
        # Load model and data
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.feature_columns = model_data['features']
        self.preprocess_params = model_data.get('preprocessing', {})
        
        # Load and preprocess data
        self.raw_data = pd.read_csv(data_path)
        self._preprocess_data()
        
        # Add seat data (if missing)
        if 'seats' not in self.processed_data.columns:
            self._estimate_seats()
    
    def _preprocess_data(self):
        """Replicate exact training preprocessing"""
        df = self.raw_data.copy()

        title_data = self._parse_title(df['title'])
        df = pd.concat([df, title_data], axis=1)
        
        # 1. Extract year
        year_regex = self.preprocess_params.get('year_regex', r'.*(\d{4}).*')
        df['year'] = pd.to_numeric(
        df['title'].str.extract(year_regex, expand=False),
        errors='coerce'
    )
        
        # 2. Clean numericals
        df['kilometres'] = (
            df['kilometres']
            .astype(str)
            .str.replace(r'[^\d.]', '', regex=True)
            .astype(float)
        )
        
        # 3. Calculate age
        current_year = pd.Timestamp.now().year
        df['age'] = current_year - df['year']
        
        # 4. Handle categoricals (same as training)
        categorical_cols = []
        for col in df.select_dtypes(include=['object']).columns:
            if col not in ['url', 'title']:
                categorical_cols.append(col)
        
        self.processed_data = pd.get_dummies(
            df,
            columns=categorical_cols,
            drop_first=True
        )
        
        # Ensure all training features exist using bulk operations
        missing_features = list(set(self.feature_columns) - set(self.processed_data.columns))
        if missing_features:
            # Add all missing features at once
            self.processed_data = pd.concat([
                self.processed_data,
                pd.DataFrame(0, columns=missing_features, index=self.processed_data.index)
            ], axis=1)

        # Validate year extraction
        if df['year'].isnull().mean() > 0.3:
            raise ValueError("Over 30% of years failed to extract - check title format")
    
        # Ensure numeric conversion
        df['kilometres'] = pd.to_numeric(df['kilometres'], errors='coerce')
    
    def _estimate_seats(self):
        """Estimate seats based on vehicle type"""
        # Simple heuristic - can be replaced with actual seat data
        self.processed_data['seats'] = np.where(
            self.processed_data['title'].str.contains('SUV|Crossover|Minivan', case=False), 
            7,  # SUVs/Minivans
            5   # Sedans/others
        )
    
    def recommend(self, budget: float, seats: int):
        """Generate recommendations"""
        # 1. Predict prices
        X = self.processed_data[self.feature_columns]
        self.processed_data['predicted_price'] = self.model.predict(X)
        
        # 2. Filter results
        valid_mask = (
            (self.processed_data['predicted_price'] <= budget) &
            (self.processed_data['seats'] >= seats)
        )
        valid_cars = self.processed_data[valid_mask].copy()
        
        # 3. Create make_model safely
        valid_cars['make_model'] = (
            valid_cars['title']
            .str.extract(r'\d{4}\s+(.+)$', expand=False)  # Capture everything after year
            .fillna('Unknown Make/Model')
        )
        
        # 4. Split make_model with fallbacks
        split_result = valid_cars['make_model'].str.split(n=1, expand=True)
        valid_cars['make'] = split_result[0].fillna('Unknown')
        valid_cars['model'] = split_result[1].fillna('Model')
        
        return valid_cars[[
            'title', 'make', 'model', 'year', 
            'predicted_price', 'kilometres', 'seats'
        ]].to_dict(orient='records')
    
    def _parse_title(self, title_series):
        """Robust make/model extraction from titles"""
        # Pattern matches: Year Make Model (rest of title)
        pattern = r'^\s*(\d{4})\s+([a-zA-Z]+)\s+([a-zA-Z\-]+)\s*(.*)$'
        extracted = title_series.str.extract(pattern)
        
        return pd.DataFrame({
            'year': pd.to_numeric(extracted[0], errors='coerce'),
            'make': extracted[1].str.strip(),
            'model': extracted[2].str.strip() + ' ' + extracted[3].str.strip()
        })
    
