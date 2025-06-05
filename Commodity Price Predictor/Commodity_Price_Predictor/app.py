import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load datasets
car_data = pd.read_csv("data/Cleaned_Car_Details.csv")
mobile_data = pd.read_csv("data/Cleaned_Mobile_Details.csv")
house_data = pd.read_csv("data/Cleaned_House_Details.csv")

# Load models
models = {
    "Car": joblib.load("models/randcv_xgb_best_model_Car_Price_Prediction.pkl"),
    "Mobile": joblib.load("models/xgbost_grid_model_Mobile_Price_Prediction.pkl"),
    "House": joblib.load("models/xgb_grid_model_House_Price_Prediction.pkl")
}

# App title
st.title("🔮 Commodity Price Prediction System")

# Step 1: Commodity selector
choice = st.selectbox("Select Commodity Type", ["Select", "Car", "Mobile", "House"])


def car_price_ui():
    st.header("🚗 Car Price Predictor")

    companies = sorted(car_data["Name"].unique())
    fuels = car_data["Fuel_Type"].unique()
    transmissions = car_data["Transmission"].unique()
    owners = car_data["Owner_Type"].unique()
    seats = sorted(car_data["Seats"].dropna().unique().astype(int))

    company = st.selectbox("Company", companies)
    year = st.slider("Year", 2000, 2025, 2020)
    km_driven = st.number_input("Kilometers Driven")
    fuel = st.selectbox("Fuel Type", fuels)
    transmission = st.selectbox("Transmission", transmissions)
    mileage = st.number_input("Mileage (km/l)")
    engine = st.text_input("Engine (CC)")
    power = st.number_input("Power (bhp)")
    owner = st.selectbox("Owner Type", owners)
    seat = st.selectbox("Seats", seats)

    if st.button("Predict Car Price"):
        input_df = pd.DataFrame([[company, year, km_driven, fuel, transmission, owner,
                                  mileage, engine, power, seat]],
                                columns=["Name", "Year", "Kilometers_Driven", "Fuel_Type",
                                         "Transmission", "Owner_Type", "Mileage", "Engine",
                                         "Power", "Seats"])
        pred = models["Car"].predict(input_df)[0]
        st.success(f"Estimated Car Price: ₹{round(pred, 2)}")


def house_price_ui():
    st.header("🏠 House Price Predictor")

    locations = sorted(house_data["site_location"].unique())
    balconies = sorted(house_data["balcony"].dropna().unique().astype(int))
    bathrooms = sorted(house_data["bath"].dropna().unique().astype(int))
    bhks = sorted(house_data["size"].dropna().unique().astype(int))

    location = st.selectbox("Site Location", locations)
    balcony = st.selectbox("Number of Balconies", balconies)
    bathroom = st.selectbox("Number of Bathrooms", bathrooms)
    sqfeet = st.number_input("Total Square Feet", min_value=100.0)
    bhk = st.selectbox("BHK", bhks)

    if st.button("Predict House Price"):
        input_data = pd.DataFrame([[bhk, sqfeet, bathroom, balcony, location]],
                                  columns=["size", "total_sqft", "bath", "balcony", "site_location"])
        prediction = models["House"].predict(input_data)[0]
        final_price = np.expm1(prediction)  # inverse of log1p
        st.success(f"Estimated House Price: ₹ {round(final_price, 2)}")


def mobile_price_ui():
    st.header("📱 Mobile Price Predictor")

    brands = sorted(mobile_data["Brand"].unique())
    names = sorted(mobile_data["Product Name"].unique())
    rams = sorted(mobile_data["RAM"].unique())
    storages = sorted(mobile_data["Internal storage"].unique())
    batteries = sorted(mobile_data["Battery capacity (mAh)"].unique())

    brand = st.selectbox("Brand", brands)
    name = st.selectbox("Product Name", names)
    ram = st.selectbox("RAM (GB)", rams)
    storage = st.selectbox("Internal Storage (GB)", storages)
    battery = st.selectbox("Battery Capacity (mAh)", batteries)
    rear_camera = st.number_input("Rear Camera (MP)")
    front_camera = st.number_input("Front Camera (MP)")
    screen_size = st.number_input("Screen Size (inches)")

    if st.button("Predict Mobile Price"):
        input_data = pd.DataFrame([[brand, name, ram, storage, battery,
                                    rear_camera, front_camera, screen_size]],
                                  columns=["Brand", "Product Name", "RAM", "Internal storage",
                                           "Battery capacity (mAh)", "Rear camera", "Front camera",
                                           "Screen size (inches)"])
        prediction = models["Mobile"].predict(input_data)[0]
        st.success(f"Estimated Mobile Price: ₹ {round(prediction, 2)}")


# Show form based on choice
if choice == "Car":
    car_price_ui()
elif choice == "Mobile":
    mobile_price_ui()
elif choice == "House":
    house_price_ui()
