#!/usr/bin/env python3
"""
mapper.py — Hadoop Streaming Mapper

Reads the ecommerce_returns_dataset.csv from stdin.
Emits:  category \t 1,is_return,refund_amount

Column indices (0-based):
  5  → Category
  9  → Return_Status
  12 → Refund_Amount
"""

import sys
import csv

reader = csv.reader(sys.stdin)

# Skip the header row
header = next(reader, None)

for row in reader:
    try:
        category = row[5].strip()
        return_status = row[9].strip()
        is_return = 1 if return_status == "Yes" else 0

        # Safely convert Refund_Amount to float
        try:
            refund_amount = float(row[12])
        except (ValueError, IndexError):
            refund_amount = 0.0

        print(f"{category}\t1,{is_return},{refund_amount}")

    except IndexError:
        # Skip malformed rows
        continue
