import streamlit as st
import pandas as pd
import numpy as np
import pickle
import joblib  # Needed for loading .pkl models

# Load all models
models = {
    "Car": joblib.load(open("models/randcv_xgb_best_model_Car_Price_Prediction.pkl", "rb")),
    # "Mobile": joblib.load("models/mobile_model.pkl"),
    # "House": joblib.load("models/house_model.pkl")
}

st.title("Commodity Price Prediction System")

# Dropdown to select commodity
choice = st.selectbox("Select Commodity Type", ["Car", "Mobile", "House"])


def house_price_ui():
    st.header("🏠 House Price Predictor")

    locations = ["Location A", "Location B"]
    balconies = [1, 2, 3]
    bathrooms = [1, 2, 3]
    bhks = [1, 2, 3, 4]

    location = st.selectbox("Site Location", locations)
    balcony = st.selectbox("Number of Balconies", balconies)
    bathroom = st.selectbox("Number of Bathrooms", bathrooms)
    sqfeet = st.number_input("Total Square Feet", min_value=100.0)
    bhk = st.selectbox("BHK", bhks)

    if st.button("Predict Price"):
        input_data = np.array([[location, balcony, bathroom, sqfeet, bhk]])
        prediction = models["House"].predict(input_data)[0]
        st.success(f"Estimated House Price: ₹ {round(prediction, 2)}")


def mobile_price_ui():
    st.header("📱 Mobile Price Predictor")

    brands = ["Samsung", "Apple", "Realme"]
    names = ["Galaxy M13", "iPhone 14", "Narzo 50"]
    rams = ["4GB", "6GB", "8GB"]
    storages = ["64GB", "128GB", "256GB"]
    batteries = ["4000mAh", "5000mAh"]

    brand = st.selectbox("Brand", brands)
    name = st.selectbox("Product Name", names)
    ram = st.selectbox("RAM", rams)
    storage = st.selectbox("Internal Storage", storages)
    battery = st.selectbox("Battery Capacity", batteries)
    rear_camera = st.text_input("Rear Camera (MP)")
    front_camera = st.text_input("Front Camera (MP)")
    screen_size = st.text_input("Screen Size (inches)")

    if st.button("Predict Price"):
        input_data = np.array([[brand, name, ram, storage, battery,
                                rear_camera, front_camera, screen_size]])
        prediction = models["Mobile"].predict(input_data)[0]
        st.success(f"Estimated Mobile Price: ₹ {round(prediction, 2)}")


# Load respective form based on selection
if choice == "Car":
    st.subheader("🚗 Car Price Predictor")
    company = st.selectbox("Company", ["Toyota", "Honda City", "Maruti Wagon"])
    year = st.slider("Year", 2000, 2025, 2020)
    km_driven = st.number_input("Kilometers Driven")
    fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG"])
    transmission = st.selectbox("Transmission", ["Manual", "Automatic"])
    mileage = st.number_input("Mileage")
    engine = st.text_input("Engine (CC)")
    power = st.number_input("Horse Power")
    owner = st.selectbox("Owner Type", ["First", "Second", "Third"])
    seats = st.selectbox("Seats", [2, 4, 5, 7])

    if st.button("Predict"):
        input_df = pd.DataFrame([[company, year, km_driven, fuel, transmission, owner,
                                  mileage, engine, power, seats]],
                                columns=["Name", "Year", "Kilometers_Driven", "Fuel_Type",
                                         "Transmission", "Owner_Type", "Mileage", "Engine",
                                         "Power", "Seats"])
        prediction = models["Car"].predict(input_df)[0]
        st.success(f"Predicted Car Price: ₹{round(prediction, 2)}")

elif choice == "Mobile":
    mobile_price_ui()

elif choice == "House":
    house_price_ui()
