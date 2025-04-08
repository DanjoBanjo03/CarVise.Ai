import streamlit as st
import requests

st.title("🚗 Carvise.ai - AI Car Buying Assistant")

# User Inputs
budget = st.slider("Your Budget ($)", 10000, 100000, 30000)
seats = st.number_input("Minimum Seats Needed", 2, 8, 5)

if st.button("Find My Car"):
    with st.spinner("Searching for the best options..."):
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
                st.warning("No cars found matching your criteria")
                st.stop()
                
            st.success(f"Found {len(recommendations)} matching cars!")
            for car in recommendations:
                st.write(f"### {car.get('make', 'Unknown')} {car.get('model', 'Unknown')}")
                st.write(f"**Price**: ${car.get('predicted_price', 'N/A'):,.2f}")
                st.write(f"**Year**: {car.get('year', 'N/A')}")
                st.write(f"**Mileage**: {car.get('kilometres', 'N/A'):,.0f} km")
                st.write(f"**Seats**: {car.get('seats', 'N/A')}")
                st.markdown("---")
                
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")