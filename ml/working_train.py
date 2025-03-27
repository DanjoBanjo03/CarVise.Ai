import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import numpy as np
from warnings import filterwarnings
filterwarnings('ignore')

# ====================== DATA LOADING & VALIDATION ======================
def load_and_validate_data(path):
    """Load data with comprehensive validation checks"""
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise ValueError("Input CSV is empty")
        print(f"Initial data: {len(df)} rows")
        return df
    except Exception as e:
        raise ValueError(f"Data loading failed: {str(e)}")

df = load_and_validate_data('../scraping/data/car_prices.csv')

# ====================== FEATURE ENGINEERING ======================
def extract_year(title_series):
    """Robust year extraction from titles"""
    years = title_series.str.findall(r'(?:19|20)\d{2}').str[0]  # Finds 1900-2099
    return pd.to_numeric(years, errors='coerce')

def clean_numeric(col, dtype=float):
    """Clean numeric columns (price, kilometres)"""
    if col.dtype == object:
        return (
            col.str.replace(r'[^\d.]', '', regex=True)
            .replace('', np.nan)
            .astype(dtype)
        )
    return col.astype(dtype)

# Extract features
df['year'] = extract_year(df['title'])
df[['make', 'model']] = df['title'].str.extract(r'^\d{4}\s+(.+?)\s+(.+)$')

# Clean numericals
df['price'] = clean_numeric(df['price'])
df['kilometres'] = clean_numeric(df['kilometres'])

# Calculate age
current_year = pd.Timestamp.now().year
df['age'] = current_year - df['year']

# ====================== DATA CLEANING ======================
def filter_invalid_data(df):
    """Remove invalid rows with safeguards"""
    initial_rows = len(df)
    
    # Critical columns check
    df = df.dropna(subset=['year', 'price', 'kilometres'])
    
    # Year validity
    df = df[(df['year'] >= 1990) & (df['year'] <= current_year)]
    
    # Price validity
    df = df[(df['price'] >= 500) & (df['price'] <= 500000)]
    
    # Kilometres validity
    df = df[(df['kilometres'] >= 0) & (df['kilometres'] <= 500000)]
    
    print(f"Filtered {initial_rows - len(df)} invalid rows")
    return df

df = filter_invalid_data(df)

# ====================== FEATURE PROCESSING ======================
def process_features(df):
    """Handle specifications and categorical features"""
    # Auto-detect feature types
    spec_cols = [c for c in df.columns if c not in 
                ['url', 'title', 'price', 'year', 'make', 'model', 'age', 'kilometres']]
    
    numericals = ['age', 'kilometres']
    categoricals = []
    
    for col in spec_cols:
        try:
            df[col] = pd.to_numeric(df[col])
            numericals.append(col)
        except:
            df[col] = df[col].astype('category')
            categoricals.append(col)
    
    # Create dummy variables
    df = pd.get_dummies(
        df,
        columns=categoricals + ['make', 'model'],
        drop_first=True,
        dummy_na=True
    )
    
    return df, numericals

df, numerical_cols = process_features(df)

# ====================== MODEL TRAINING ======================
def train_model(X, y):
    """Train with automatic stratification handling"""
    # Check for stratification viability
    stratify_col = None
    if 'year' in X.columns:
        year_counts = X['year'].value_counts()
        if len(year_counts) >= 5 and year_counts.min() >= 2:
            stratify_col = X['year']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=stratify_col
    )
    
    # Model configuration
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    return model, X_test, y_test

# Prepare features
X = df.drop(['url', 'title', 'price'], axis=1)
y = df['price']

# Final data check
if len(df) < 100:
    raise ValueError(f"Only {len(df)} valid samples - need at least 100")

model, X_test, y_test = train_model(X, y)

# ====================== EVALUATION ======================
def evaluate_model(model, X_test, y_test):
    """Comprehensive model evaluation"""
    predictions = model.predict(X_test)
    
    print("\n=== Model Performance ===")
    print(f"MAE: ${mean_absolute_error(y_test, predictions):,.2f}")
    print(f"R² Score: {r2_score(y_test, predictions):.3f}")
    
    # Feature importance
    print("\nTop 10 Features:")
    fi = pd.Series(model.feature_importances_, index=X.columns)
    print(fi.sort_values(ascending=False).head(10))

evaluate_model(model, X_test, y_test)

# ====================== MODEL SAVING ======================
def save_model(model, features, numerical_cols):
    """Save model with complete metadata"""
    model_data = {
        'model': model,
        'features': list(features.columns),
        'numerical_cols': numerical_cols,
        'preprocessing': {
            'year_regex': r'(?:19|20)\d{2}',
            'required_cols': ['title', 'price', 'kilometres'],
            'min_values': {
                'price': 500,
                'kilometres': 0,
                'year': 1990
            }
        }
    }
    
    joblib.dump(model_data, "car_price_model_prod.pkl")
    print("\nModel saved with complete metadata")

save_model(model, X, numerical_cols)