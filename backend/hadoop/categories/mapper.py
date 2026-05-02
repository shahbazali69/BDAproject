#!/usr/bin/env python3
"""
Categories Mapper — Emits refund amounts keyed by product category.

Input:  Cleaned_Ecommerce_Data.csv via stdin
Output: product_category \t refund_amount
"""

import sys
import csv

reader = csv.reader(sys.stdin)

# Skip header
header = next(reader, None)

for row in reader:
    try:
        is_return = int(row[8])
        if is_return == 1:
            product_category = row[3].strip()
            refund_amount = row[5]
            print(f"{product_category}\t{refund_amount}")
    except (IndexError, ValueError):
        continue
