import streamlit as st
import requests
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Carvise.ai - AI Car Buying Assistant",
    page_icon="🚗",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        margin-bottom: 2rem !important;
        text-align: center;
    }
    .car-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .car-title {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #1E3A8A !important;
        margin-bottom: 0.5rem !important;
    }
    .car-price {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #2563EB !important;
        margin-bottom: 1rem !important;
    }
    .car-detail {
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        color: #4B5563 !important;
    }
    .success-message {
        background-color: #DCFCE7;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    .section-divider {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# App header with logo
st.markdown('<h1 class="main-header">🚗 Carvise.ai - AI Car Buying Assistant</h1>', unsafe_allow_html=True)

# Create two columns for the inputs
col1, col2 = st.columns(2)

with col1:
    # User Inputs with better styling
    budget = st.slider(
        "Your Budget ($)",
        min_value=10000,
        max_value=100000,
        value=30000,
        step=1000,
        format="$%d"
    )

with col2:
    seats = st.number_input(
        "Minimum Seats Needed",
        min_value=2,
        max_value=8,
        value=5,
        step=1
    )

# Add some space
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Find My Car button
if st.button("Find My Car"):
    with st.spinner("🔍 Searching for the perfect car for you..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/recommendations",
                params={"budget": budget, "family_size": seats},
                timeout=5
            )
            
            if response.status_code != 200:
                st.error(f"API Error ({response.status_code}): {response.text}")
                st.stop()
                
            data = response.json()
            
            if not isinstance(data.get("recommendations"), list):
                st.error("Invalid response format from server")
                st.stop()
                
            recommendations = data["recommendations"]
            
            if not recommendations:
                st.warning("No cars found matching your criteria. Try adjusting your budget or seat requirements.")
                st.stop()
            
            # Success message
            st.markdown(f"<div class='success-message'>✅ Found {len(recommendations)} matching cars!</div>", unsafe_allow_html=True)
            
            # Display results in a more visually appealing way
            for car in recommendations:
                make = car.get('make', 'Unknown')
                model = car.get('model', 'Unknown')
                price = car.get('predicted_price', 0)
                year = car.get('year', 'N/A')
                mileage = car.get('kilometres', 0)
                car_seats = car.get('seats', 'N/A')
                
                # Create a card for each car
                st.markdown(f"""
                <div class="car-card">
                    <div class="car-title">{make} {model}</div>
                    <div class="car-price">${price:,.2f}</div>
                    <div class="car-detail">🗓️ <strong>Year:</strong> {year}</div>
                    <div class="car-detail">🛣️ <strong>Mileage:</strong> {mileage:,.0f} km</div>
                    <div class="car-detail">👥 <strong>Seats:</strong> {car_seats}</div>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

# Add footer
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.8rem;">
    Powered by Carvise.ai | © 2023 All Rights Reserved
</div>
""", unsafe_allow_html=True)
