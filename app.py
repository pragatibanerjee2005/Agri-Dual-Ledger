from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

DATA_PATH = Path("data/cleaned/rice_west_bengal_cleaned.csv")
FRAUD_THRESHOLD = 50
LEDGER_DISTRICTS = ["Malda", "Murshidabad", "Hooghly", "Nadia", "Burdwan", "Howrah"]


def load_dataset() -> pd.DataFrame:
    """Read and enrich the agriculture dataset for dashboards and APIs."""
    if not DATA_PATH.exists():
        return pd.DataFrame(
            columns=[
                "Year",
                "State Name",
                "District",
                "Area",
                "Production",
                "Yield",
                "Predicted_Yield",
                "FraudScore",
                "Fraud_Flag",
            ]
        )

    df = pd.read_csv(DATA_PATH)
    df["Predicted_Yield"] = (df["Yield"] * 0.98).round(2)
    df["FraudScore"] = (df["Yield"] - df["Predicted_Yield"]).abs().round(2)
    df["Fraud_Flag"] = df["FraudScore"] > FRAUD_THRESHOLD
    return df


def dashboard_overview(df: pd.DataFrame) -> dict[str, Any]:
    total_records = int(len(df))
    fraud_cases = int(df["Fraud_Flag"].sum()) if not df.empty else 0
    avg_yield = round(float(df["Yield"].mean()), 2) if not df.empty else 0
    verified_cases = total_records - fraud_cases

    return {
        "total_records": total_records,
        "fraud_cases": fraud_cases,
        "verified_cases": verified_cases,
        "average_yield": avg_yield,
        "fraud_rate": round((fraud_cases / total_records * 100), 2) if total_records else 0,
    }


def yearly_analytics(df: pd.DataFrame) -> dict[str, list[Any]]:
    if df.empty:
        return {"years": [], "avg_yield": [], "avg_predicted_yield": [], "fraud_counts": []}

    grouped = (
        df.groupby("Year", as_index=False)
        .agg(
            avg_yield=("Yield", "mean"),
            avg_predicted_yield=("Predicted_Yield", "mean"),
            fraud_counts=("Fraud_Flag", "sum"),
        )
        .sort_values("Year")
    )
    return {
        "years": grouped["Year"].astype(int).tolist(),
        "avg_yield": grouped["avg_yield"].round(2).tolist(),
        "avg_predicted_yield": grouped["avg_predicted_yield"].round(2).tolist(),
        "fraud_counts": grouped["fraud_counts"].astype(int).tolist(),
    }


def top_districts(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    grouped = (
        df.groupby("District", as_index=False)
        .agg(average_yield=("Yield", "mean"), records=("District", "count"))
        .sort_values("average_yield", ascending=False)
        .head(8)
    )
    grouped["average_yield"] = grouped["average_yield"].round(2)
    return grouped.to_dict(orient="records")


def build_live_transaction() -> dict[str, Any]:
    actual_yield = random.randint(800, 2500)
    predicted_yield = round(actual_yield * random.uniform(0.9, 1.05), 2)
    fraud_score = round(abs(actual_yield - predicted_yield), 2)
    risk = "high" if fraud_score > FRAUD_THRESHOLD else "low"
    confidence = round(max(50, 100 - (fraud_score * 0.8)), 2)

    return {
        "transaction_id": f"TXN-{random.randint(100000, 999999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "crop": "Rice",
        "district": random.choice(LEDGER_DISTRICTS),
        "actual_yield": actual_yield,
        "predicted_yield": predicted_yield,
        "fraud_score": fraud_score,
        "risk_level": risk,
        "ai_confidence": confidence,
        "ledger_hash": f"0x{random.getrandbits(64):016x}",
    }


def build_mock_ledger() -> list[dict[str, Any]]:
    return [
        {
            "block_id": idx + 1,
            "transaction_id": f"AGRI-{1000 + idx}",
            "district": random.choice(LEDGER_DISTRICTS),
            "crop": "Rice",
            "public_record": {
                "yield": random.randint(900, 2400),
                "market_price": random.randint(1800, 2600),
            },
            "private_record": {
                "farmer_id": f"WB{random.randint(10000, 99999)}",
                "subsidy_amount": random.randint(1000, 6000),
            },
            "status": random.choice(["verified", "pending", "audited"]),
            "block_hash": f"0x{random.getrandbits(96):024x}",
        }
        for idx in range(8)
    ]


@app.route("/")
def home() -> str:
    return render_template("index.html", active_page="home")


@app.route("/overview")
def overview_page() -> str:
    return render_template("overview.html", active_page="overview")


@app.route("/dashboard")
def dashboard_page() -> str:
    return render_template("dashboard.html", active_page="dashboard")


@app.route("/tracking")
def tracking_page() -> str:
    return render_template("tracking.html", active_page="tracking")


@app.route("/fraud-insights")
def fraud_insights_page() -> str:
    return render_template("fraud.html", active_page="fraud")


@app.route("/ledger")
def ledger_page() -> str:
    return render_template("ledger.html", active_page="ledger")


@app.route("/analytics")
def analytics_page() -> str:
    return render_template("analytics.html", active_page="analytics")


@app.route("/contact")
def contact_page() -> str:
    return render_template("contact.html", active_page="contact")


@app.route("/api/overview")
def api_overview():
    df = load_dataset()
    return jsonify(dashboard_overview(df))


@app.route("/api/fraud")
def api_fraud():
    df = load_dataset()
    fraud_df = df[df["Fraud_Flag"]] if not df.empty else df
    return jsonify(
        {
            "threshold": FRAUD_THRESHOLD,
            "cases": fraud_df[["Year", "District", "Yield", "Predicted_Yield", "FraudScore"]]
            .head(25)
            .to_dict(orient="records"),
        }
    )


@app.route("/api/analytics")
def api_analytics():
    df = load_dataset()
    return jsonify(
        {
            "yearly": yearly_analytics(df),
            "top_districts": top_districts(df),
        }
    )


@app.route("/api/tracking")
def api_tracking():
    transactions = [build_live_transaction() for _ in range(10)]
    return jsonify({"supply_chain_feed": transactions})


@app.route("/api/ledger")
def api_ledger():
    return jsonify({"ledger_records": build_mock_ledger()})


@app.route("/api/live-transaction")
def api_live_transaction():
    return jsonify(build_live_transaction())


if __name__ == "__main__":
    app.run(debug=True)