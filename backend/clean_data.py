"""
clean_data.py
Reads the raw 1,000,000-row Ecommerce CSV in chunks, applies the same
transformation logic used by import_csv.py, and writes a cleaned CSV
ready for Hadoop MapReduce or any downstream pipeline.
"""

import os
import random
import time

import pandas as pd

# ── Configuration ────────────────────────────────────────────────────
CSV_INPUT = os.path.join(os.path.dirname(__file__), "..", "Ecommerce_Sales_Data.csv")
CSV_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "Cleaned_Ecommerce_Data.csv")
CHUNK_SIZE = 10_000

OUTPUT_COLUMNS = [
    "customer_id",
    "customer_name",
    "customer_email",
    "product_category",
    "return_status",
    "refund_amount",
    "return_date",
    "risk_score",
    "is_return",
]


def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Transform a raw chunk into the cleaned schema."""
    records = []

    for _, row in chunk.iterrows():
        is_return = 1 if row.get("returned") == "Yes" else 0

        risk_score = (
            round(random.uniform(40.0, 99.0), 2)
            if is_return
            else round(random.uniform(0.0, 30.0), 2)
        )

        customer_id = str(row.get("customer_id", ""))

        # Safely convert total_amount
        try:
            total_amount = float(row["total_amount"])
        except (ValueError, TypeError):
            total_amount = 0.0

        refund_amount = total_amount if is_return else 0.0

        # Handle NaN for request_date
        return_date = row.get("request_date", "")
        if pd.isna(return_date):
            return_date = ""

        records.append(
            {
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
        )

    return pd.DataFrame(records, columns=OUTPUT_COLUMNS)


def main():
    print(f"Input  : {os.path.abspath(CSV_INPUT)}")
    print(f"Output : {os.path.abspath(CSV_OUTPUT)}")
    print(f"Chunk  : {CHUNK_SIZE:,} rows\n")

    reader = pd.read_csv(CSV_INPUT, chunksize=CHUNK_SIZE)

    total_rows = 0
    chunk_number = 0
    start_time = time.time()

    for chunk in reader:
        chunk_number += 1
        cleaned = process_chunk(chunk)

        # First chunk writes header; subsequent chunks append without header
        if chunk_number == 1:
            cleaned.to_csv(CSV_OUTPUT, index=False, mode="w")
        else:
            cleaned.to_csv(CSV_OUTPUT, index=False, mode="a", header=False)

        total_rows += len(cleaned)
        elapsed = time.time() - start_time
        print(
            f"  Chunk {chunk_number:>4}: Wrote {len(cleaned):>6,} rows  |  "
            f"Total: {total_rows:>10,}  |  Elapsed: {elapsed:.1f}s"
        )

    # ── Final Stats ──────────────────────────────────────────────────
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"  Cleaning complete!")
    print(f"  Total rows written : {total_rows:,}")
    print(f"  Total chunks       : {chunk_number}")
    print(f"  Total time         : {total_time:.2f}s")
    print(f"  Avg speed          : {total_rows / total_time:,.0f} rows/s")
    print(f"  Output file        : {os.path.abspath(CSV_OUTPUT)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
