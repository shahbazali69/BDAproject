#!/usr/bin/env python3
"""
reducer.py — Hadoop Streaming Reducer

Reads sorted mapper output from stdin.
Input format :  category \t orders,returns,refund_amount
Output format:  category \t total_orders,total_returns,total_refund_loss,return_rate

Aggregates per product category:
  - total_orders  : count of all transactions
  - total_returns : count of returned transactions
  - total_refunds : sum of refund amounts (revenue loss)
  - return_rate   : percentage of orders that were returned
"""

import sys

current_category = None
total_orders = 0
total_returns = 0
total_refunds = 0.0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        category, values = line.split("\t", 1)
        parts = values.split(",")
        orders = int(parts[0])
        returns = int(parts[1])
        refunds = float(parts[2])
    except (ValueError, IndexError):
        # Skip malformed lines
        continue

    # If the category changed, emit the previous category's totals
    if current_category and current_category != category:
        return_rate = round((total_returns / total_orders) * 100, 2) if total_orders else 0.0
        print(f"{current_category}\t{total_orders},{total_returns},{round(total_refunds, 2)},{return_rate}")
        total_orders = 0
        total_returns = 0
        total_refunds = 0.0

    current_category = category
    total_orders += orders
    total_returns += returns
    total_refunds += refunds

# Emit the last category
if current_category:
    return_rate = round((total_returns / total_orders) * 100, 2) if total_orders else 0.0
    print(f"{current_category}\t{total_orders},{total_returns},{round(total_refunds, 2)},{return_rate}")
