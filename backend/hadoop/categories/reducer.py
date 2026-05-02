#!/usr/bin/env python3
"""
Categories Reducer — Aggregates returns and refund loss per category.

Input:  product_category \t refund_amount  (sorted by category)
Output: product_category \t JSON with returns count and refund_loss
"""

import sys
import json

current_category = None
returns = 0
refund_loss = 0.0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        category, value = line.split("\t", 1)
        refund_amount = float(value)
    except (ValueError, IndexError):
        continue

    # If the category changed, emit the previous category's totals
    if current_category and current_category != category:
        result = {
            "returns": returns,
            "refund_loss": round(refund_loss, 2),
        }
        print(f"{current_category}\t{json.dumps(result)}")
        returns = 0
        refund_loss = 0.0

    current_category = category
    returns += 1
    refund_loss += refund_amount

# Emit the last category
if current_category:
    result = {
        "returns": returns,
        "refund_loss": round(refund_loss, 2),
    }
    print(f"{current_category}\t{json.dumps(result)}")
