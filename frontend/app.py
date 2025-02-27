import streamlit as st
import requests

st.title("🚗 Carvise.ai - AI Car Buying Assistant")

# User Inputs
budget = st.slider("Your Budget ($)", 10000, 100000, 30000)
seats = st.number_input("Minimum Seats Needed", 2, 8, 5)

if st.button("Find My Car"):
    with st.spinner("Searching for the best options..."):
        # Call the FastAPI backend
        response = requests.get(
            "http://127.0.0.1:8000/recommendations",
            params={"budget": budget, "family_size": seats}
        )
        recommendations = response.json().get("recommendations", [])
    
    if recommendations:
        st.success(f"Found {len(recommendations)} matching cars!")
        for car in recommendations:
            st.write(f"### {car['make']} {car['model']}")
            st.write(f"**Price**: ${car['price']:,.2f}")
            st.write(f"**Seats**: {car['seats']}")
            st.write(f"**MPG**: {car['mpg']}")
            st.markdown("---")
    else:
        st.warning("No cars found matching your criteria. Try adjusting your budget or seats.")