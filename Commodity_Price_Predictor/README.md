# 📊 Commodity Price Prediction System

A unified and interactive **Streamlit web app** that predicts prices for three major commodities — **cars, mobile phones, and houses** — using advanced machine learning models. 

---

![image](https://github.com/user-attachments/assets/388bdd33-ff44-4324-af62-0b8aec7f2ef1)


## 🚀 Project Motivation

In the fast-evolving markets of **automobiles**, **real estate**, and **electronics**, price fluctuations are driven by multiple dynamic factors. Whether you're a:

- **Buyer** trying to get the best deal,
- **Seller** aiming to set competitive prices, or
- **Analyst** studying market behavior,

having an intelligent prediction system can offer significant **insight and value**.

This project is designed to help users **estimate fair market prices** using historical data and machine learning, all through an easy-to-use web interface.

---

## 🧠 Machine Learning Models

Each commodity has its own dedicated pipeline:

### 🏠 House Price Predictor
- Features: Size, Total Sqft, Bath, Balcony, Site Location
- Preprocessing: OneHotEncoding + MinMaxScaler
- Model: XGBoost Regressor (tuned using GridSearchCV)
- Target transformed using `log1p` for better distribution

### 📱 Mobile Price Predictor
- Features: Brand, Product Name, RAM, Storage, Battery, Cameras, Screen Size
- Preprocessing: OneHotEncoding for categorical fields
- Model: XGBoost Regressor (GridSearchCV-tuned)

### 🚗 Car Price Predictor
- Features: Brand, Year, Fuel, Transmission, Mileage, Engine, Power, Owner Type, Seats
- Preprocessing: Label Encoding + Feature Engineering
- Model: RandomizedSearchCV-tuned XGBoost Regressor

---

## 💡 Key Features

- 🔮 **Price prediction for:**
  - 🏠 Houses
  - 📱 Mobiles
  - 🚗 Cars
- 📊 Interactive dropdowns auto-populated from actual dataset values
- 🔍 Clean, modular design with routing to specific predictor pages
- ⚙️ Models include Linear Regression, XGBoost, Gradient Boosting, ElasticNet, etc.
- 💻 Hosted live using **Render**

---

![image](https://github.com/user-attachments/assets/dce5b20c-77a0-4cdd-afd5-679658369ca1)

![image](https://github.com/user-attachments/assets/9e39051d-3d6d-4f77-9fcf-212a5f261ac1)

![image](https://github.com/user-attachments/assets/9473613d-45a8-4d03-8516-91860361c49e)


🌍 Live Demo
Access the live app here: https://commodity-price-predictor-deployment.onrender.com

---

## 🔍 Features

✅ Unified dashboard with dropdown selection for **Car**, **Mobile**, and **House** predictors  
✅ Dynamically generated input fields from dataset column values (not hardcoded)  
✅ Price prediction using top-performing models (XGBoost, ElasticNet, etc.)  
✅ Clean, modular UI with Streamlit  
✅ Models trained and optimized using GridSearchCV and RandomizedSearchCV  
✅ Ready for production deployment on Render
---

## 🧠 Tech Stack

| Component           | Tech Used                                              |
|--------------------|---------------------------------------------------------|
| Frontend UI        | Streamlit                                               |
| Backend Logic      | Python                                                  |
| ML Models          | XGBoost, GradientBoosting, ElasticNet, RandomForest     |
| Preprocessing      | scikit-learn (OneHotEncoder, MinMaxScaler, ColumnTransformer) |
| Model Persistence  | Joblib, Pickle                                          |
| Routing Logic      | Streamlit page logic with dynamic UI rendering          |
| Deployment         | Render                                                  |

---
