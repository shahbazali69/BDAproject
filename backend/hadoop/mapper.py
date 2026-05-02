#!/usr/bin/env python3
"""
mapper.py — Hadoop Streaming Mapper

Reads the Ecommerce_Sales_Data.csv from stdin.
Emits:  category \t 1,is_return,refund_amount

Column indices (0-based) for the 1M-row dataset:
   3  → category
  11  → returned
  14  → total_amount
"""

import sys
import csv

reader = csv.reader(sys.stdin)

# Skip the header row
header = next(reader, None)

for row in reader:
    try:
        category = row[3].strip()
        returned = row[11].strip()
        total_amount = row[14].strip()

        is_return = 1 if returned == "Yes" else 0

        # Safely convert total_amount to float
        try:
            refund_amount = float(total_amount) if is_return else 0.0
        except (ValueError, IndexError):
            refund_amount = 0.0

        print(f"{category}\t1,{is_return},{refund_amount}")

    except IndexError:
        # Skip malformed rows
        continue
