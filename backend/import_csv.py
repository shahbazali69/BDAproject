"""
import_csv.py — Imports ecommerce_returns_dataset.csv into MongoDB.

Usage:
    cd backend
    python import_csv.py
"""

import pandas as pd
from pymongo import MongoClient
import random
import os

# ── Config ────────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "ecommerce_returns_dataset.csv")
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bda_project"
COLLECTION_NAME = "ecommerce_returns"


def main():
    # ── Connect to MongoDB ────────────────────────────────────────────────
    print("⏳  Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("✅  Connected to MongoDB.")

    # ── Read CSV ──────────────────────────────────────────────────────────
    csv_abs = os.path.abspath(CSV_PATH)
    print(f"📄  Reading CSV: {csv_abs}")
    df = pd.read_csv(csv_abs)
    print(f"    → {len(df)} rows, {len(df.columns)} columns")

    # ── Drop existing collection to prevent duplicates ────────────────────
    collection.drop()
    print("🗑️   Dropped existing collection.")

    # ── Build documents ───────────────────────────────────────────────────
    documents = []
    for _, row in df.iterrows():
        is_return = str(row.get("Return_Status", "")).strip() == "Yes"

        # Risk score: returns get higher scores, non-returns get low scores
        if is_return:
            risk_score = round(random.uniform(40.0, 99.0), 1)
        else:
            risk_score = round(random.uniform(0.0, 30.0), 1)

        # Refund amount — handle NaN
        refund = row.get("Refund_Amount", 0)
        try:
            refund = float(refund)
        except (ValueError, TypeError):
            refund = 0.0
        if pd.isna(refund):
            refund = 0.0

        # Return date — handle NaT / NaN
        return_date = row.get("Return_Date", "")
        if pd.isna(return_date):
            return_date = ""
        else:
            return_date = str(return_date).strip()

        # Customer email — generated from name
        name = str(row.get("Customer_Name", "Unknown")).strip()
        email = name.lower().replace(" ", ".") + "@example.com"

        documents.append({
            "customer_id":      str(row.get("Customer_ID", "")).strip(),
            "customer_name":    name,
            "customer_email":   email,
            "product_category": str(row.get("Category", "")).strip(),
            "return_status":    str(row.get("Return_Status", "")).strip(),
            "refund_amount":    round(refund, 2),
            "return_date":      return_date,
            "risk_score":       risk_score,
        })

    # ── Bulk insert ───────────────────────────────────────────────────────
    print(f"📥  Inserting {len(documents)} documents...")
    result = collection.insert_many(documents)
    print(f"✅  Successfully inserted {len(result.inserted_ids)} documents into {DB_NAME}.{COLLECTION_NAME}")

    # ── Quick stats ───────────────────────────────────────────────────────
    total = collection.count_documents({})
    returns = collection.count_documents({"return_status": "Yes"})
    print(f"    → Total documents: {total}")
    print(f"    → Returns (Return_Status=Yes): {returns}")
    print(f"    → Non-returns: {total - returns}")


if __name__ == "__main__":
    main()
