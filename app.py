import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import random

st.set_page_config(page_title="Agri Blockchain Dashboard", layout="wide")

st.title("🌾 Agri Dual-Ledger Blockchain System")

st.markdown("AI + Blockchain platform for transparent agricultural supply chains")

# Load dataset
data = pd.read_csv("data/cleaned/rice_west_bengal_cleaned.csv")

# Prediction simulation
data["Predicted_Yield"] = data["Yield"] * 0.98
data["FraudScore"] = abs(data["Yield"] - data["Predicted_Yield"])

threshold = 50
data["Fraud_Flag"] = data["FraudScore"] > threshold

# KPI METRICS
st.header("System Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Records", len(data))
col2.metric("Fraud Cases", data["Fraud_Flag"].sum())
col3.metric("Average Yield", round(data["Yield"].mean(),2))

# Dataset preview
st.header("Dataset Preview")

st.dataframe(data.head())

# Fraud table
st.header("🚨 Fraud Detection")

fraud_cases = data[data["Fraud_Flag"] == True]

if len(fraud_cases) > 0:
    st.error(f"{len(fraud_cases)} suspicious records detected")
    st.dataframe(fraud_cases.head())
else:
    st.success("No fraud detected")

# Yield chart
st.header("📊 Yield vs Predicted Yield")

fig, ax = plt.subplots()

ax.scatter(data["Yield"], data["Predicted_Yield"])
ax.set_xlabel("Actual Yield")
ax.set_ylabel("Predicted Yield")

st.pyplot(fig)

# Blockchain example
st.header("⛓ Blockchain Transaction Example")

col1, col2 = st.columns(2)

public_data = {
    "Crop": "Rice",
    "District": "Malda",
    "Yield": 1040,
    "Market Price": 2100
}

private_data = {
    "Farmer_ID": "WB10234",
    "Bank": "XXXX1234",
    "Subsidy": 5000
}

with col1:
    st.subheader("Public Ledger")
    st.json(public_data)

with col2:
    st.subheader("Private Ledger")
    st.json(private_data)

st.success("Transaction stored securely on Dual-Ledger Blockchain")
st.header("⚡ Real-Time Fraud Detection Simulation")

placeholder = st.empty()

for i in range(5):
    
    simulated_yield = random.randint(800, 2500)
    predicted_yield = simulated_yield * random.uniform(0.9, 1.05)
    
    fraud_score = abs(simulated_yield - predicted_yield)
    
    transaction = {
        "Crop": "Rice",
        "District": random.choice(["Malda", "Murshidabad", "Hooghly", "Nadia"]),
        "Actual_Yield": simulated_yield,
        "Predicted_Yield": round(predicted_yield,2),
        "FraudScore": round(fraud_score,2)
    }

    with placeholder.container():
        st.subheader("Incoming Agricultural Transaction")
        st.json(transaction)

        if fraud_score > 50:
            st.error("🚨 Fraud Risk Detected — Stored on Blockchain")
        else:
            st.success("✔ Transaction Verified")

    time.sleep(2)