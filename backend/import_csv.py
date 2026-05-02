"""
import_csv.py
Safely imports a 1,000,000-row Ecommerce CSV into local MongoDB
using chunked reads and bulk inserts.
"""

import os
import random
import time

import pandas as pd
from pymongo import MongoClient

# ── Configuration ────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bda_project"
COLLECTION_NAME = "ecommerce_returns"
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "Ecommerce_Sales_Data.csv")
CHUNK_SIZE = 10_000


def main():
    # ── 1. Setup & Drop ──────────────────────────────────────────────
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print(f"Connected to MongoDB at {MONGO_URI}")
    print(f"Dropping existing collection '{COLLECTION_NAME}'...")
    collection.drop()
    print("Collection dropped.\n")

    # ── 2. Chunked Reading ───────────────────────────────────────────
    total_inserted = 0
    chunk_number = 0
    start_time = time.time()

    print(f"Reading CSV: {os.path.abspath(CSV_PATH)}")
    print(f"Chunk size : {CHUNK_SIZE:,}\n")

    reader = pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE)

    for chunk in reader:
        chunk_number += 1
        documents = []

        # ── 3. Processing each Chunk ─────────────────────────────────
        for _, row in chunk.iterrows():
            is_return = row.get("returned") == "Yes"

            risk_score = round(random.uniform(40, 99), 2) if is_return else round(random.uniform(0, 30), 2)

            customer_id = str(row.get("customer_id", ""))

            # Handle NaN for total_amount
            try:
                total_amount = float(row["total_amount"])
            except (ValueError, TypeError):
                total_amount = 0.0

            refund_amount = total_amount if is_return else 0.0

            # Handle NaN for request_date
            return_date = row.get("request_date", "")
            if pd.isna(return_date):
                return_date = ""

            doc = {
                "customer_id": customer_id,
                "customer_name": f"Customer {customer_id}",
                "customer_email": f"{customer_id.lower()}@example.com",
                "product_category": row.get("category", ""),
                "return_status": row.get("returned", ""),
                "refund_amount": refund_amount,
                "return_date": str(return_date),
                "risk_score": risk_score,
                "is_return": is_return,
            }

            documents.append(doc)

        # ── 4. Insert ────────────────────────────────────────────────
        if documents:
            collection.insert_many(documents)
            total_inserted += len(documents)

        # ── 5. Console Output (per chunk) ────────────────────────────
        elapsed = time.time() - start_time
        print(
            f"  Chunk {chunk_number:>4}: Inserted {len(documents):>6,} rows  |  "
            f"Total so far: {total_inserted:>10,}  |  Elapsed: {elapsed:.1f}s"
        )

    # ── Final Stats ──────────────────────────────────────────────────
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"  Import complete!")
    print(f"  Total rows inserted : {total_inserted:,}")
    print(f"  Total chunks        : {chunk_number}")
    print(f"  Total time          : {total_time:.2f}s")
    print(f"  Avg speed           : {total_inserted / total_time:,.0f} rows/s")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
