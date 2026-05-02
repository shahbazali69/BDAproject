#!/usr/bin/env python3
"""
export_to_mongo.py
Bridges Hadoop MapReduce output files into MongoDB collections.

Usage:
    python export_to_mongo.py <collection_name> <input_file>

Each line in the input file is expected as:
    Key \t JSON_String
"""

import sys
import json

from pymongo import MongoClient

# ── Configuration ────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bda_project"
BATCH_SIZE = 10_000


def main():
    if len(sys.argv) != 3:
        print("Usage: python export_to_mongo.py <collection_name> <input_file>")
        sys.exit(1)

    collection_name = sys.argv[1]
    input_file = sys.argv[2]

    # ── 1. Connect & Drop ────────────────────────────────────────────
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[collection_name]

    print(f"Connected to MongoDB at {MONGO_URI}")
    print(f"Dropping existing collection '{collection_name}'...")
    collection.drop()
    print(f"Collection dropped.\n")

    # ── 2. Read & Parse ──────────────────────────────────────────────
    documents = []
    total_inserted = 0

    print(f"Reading input file: {input_file}")

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                key, json_str = line.split("\t", 1)
                doc = json.loads(json_str)
            except (ValueError, json.JSONDecodeError) as e:
                print(f"  Skipping malformed line: {e}")
                continue

            # Inject the key field based on collection type
            if collection_name == "categories":
                doc["category"] = key
            elif collection_name == "customers":
                doc["customer_id"] = key

            documents.append(doc)

            # ── 3. Batch Insert ──────────────────────────────────────
            if len(documents) >= BATCH_SIZE:
                collection.insert_many(documents)
                total_inserted += len(documents)
                print(f"  Inserted batch of {len(documents):,} docs  |  Total: {total_inserted:,}")
                documents = []

    # Insert remaining documents
    if documents:
        collection.insert_many(documents)
        total_inserted += len(documents)
        print(f"  Inserted final batch of {len(documents):,} docs  |  Total: {total_inserted:,}")

    # ── 4. Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Export complete!")
    print(f"  Collection : {collection_name}")
    print(f"  Documents  : {total_inserted:,}")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
