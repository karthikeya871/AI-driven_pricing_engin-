import streamlit as st
import pandas as pd
import joblib
import sqlite3
from datetime import datetime

# 1. Load the saved model
model = joblib.load('model/linear_model.pkl')

# 2. Setup SQLite Database connection
conn = sqlite3.connect('pricing_logs.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table to store inputs and predictions if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        qty REAL,
        freight_price REAL,
        product_weight_g REAL,
        product_score REAL,
        customers REAL,
        month INTEGER,
        year INTEGER,
        volume REAL,
        comp_1 REAL,
        comp_2 REAL,
        comp_3 REAL,
        lag_price REAL,
        category_encoded INTEGER,
        predicted_price REAL
    )
''')
conn.commit()

st.title("Dynamic Pricing Predictor & Database Logger")
st.write("Enter product details below. Every prediction will be saved to your local database.")

# Input fields for your 13 features
qty = st.number_input("Quantity Sold (qty)", min_value=1, value=12)
freight_price = st.number_input("Freight Price ($)", min_value=0.0, value=35.75)
product_weight_g = st.number_input("Product Weight (g)", min_value=1, value=980)
product_score = st.slider("Product Score", 1.0, 5.0, 4.2)
customers = st.number_input("Number of Customers", min_value=1, value=24)

month = st.slider("Month", 1, 12, 6)
year = st.selectbox("Year", [2017, 2018, 2019, 2020, 2021, 2022])
volume = st.number_input("Product Volume", min_value=0.0, value=1200.0)

comp_1 = st.number_input("Competitor 1 Price ($)", min_value=0.0, value=41.80)
comp_2 = st.number_input("Competitor 2 Price ($)", min_value=0.0, value=43.25)
comp_3 = st.number_input("Competitor 3 Price ($)", min_value=0.0, value=45.10)
lag_price = st.number_input("Previous Price / Lag Price ($)", min_value=0.0, value=42.60)
category_encoded = st.number_input("Category Encoded (Number)", min_value=0, value=1)

if st.button("Predict and Save to Database"):
    # Bundle inputs into a DataFrame
    input_data = pd.DataFrame([[
        qty, freight_price, product_weight_g, product_score, customers,
        month, year, volume, comp_1, comp_2, comp_3, lag_price, category_encoded
    ]], columns=[
        "qty", "freight_price", "product_weight_g", "product_score", "customers",
        "month", "year", "volume", "comp_1", "comp_2", "comp_3", "lag_price", "category_encoded"
    ])

    # Make prediction
    predicted_price = model.predict(input_data)[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save data into SQLite database
    cursor.execute('''
        INSERT INTO predictions (
            timestamp, qty, freight_price, product_weight_g, product_score, customers,
            month, year, volume, comp_1, comp_2, comp_3, lag_price, category_encoded, predicted_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp, qty, freight_price, product_weight_g, product_score, customers,
        month, year, volume, comp_1, comp_2, comp_3, lag_price, category_encoded, predicted_price
    ))
    conn.commit()

    # Display result
    st.success(f"Estimated Optimal Unit Price: ${predicted_price:.2f}")
    st.info("Prediction successfully logged to the database!")

# Optional: Display past logs inside the app
if st.checkbox("Show Past Prediction Logs"):
    history_df = pd.read_sql("SELECT * FROM predictions", conn)
    st.dataframe(history_df)