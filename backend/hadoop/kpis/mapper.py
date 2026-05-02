#!/usr/bin/env python3
"""
KPIs Mapper — Emits refund and risk data for returned orders.

Input:  Cleaned_Ecommerce_Data.csv via stdin
Output: Global_KPI \t refund_amount,risk_score
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
            refund_amount = row[5]
            risk_score = row[7]
            print(f"Global_KPI\t{refund_amount},{risk_score}")
    except (IndexError, ValueError):
        continue
