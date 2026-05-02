#!/usr/bin/env python3
"""
Customers Mapper — Emits per-row customer detail keyed by customer_id.

Input:  Cleaned_Ecommerce_Data.csv via stdin
Output: customer_id \t name|email|category|is_return|refund_amount|risk_score|return_date
"""

import sys
import csv

reader = csv.reader(sys.stdin)

# Skip header
header = next(reader, None)

for row in reader:
    try:
        customer_id = row[0].strip()
        customer_name = row[1].strip()
        customer_email = row[2].strip()
        product_category = row[3].strip()
        is_return = row[8].strip()
        refund_amount = row[5].strip()
        risk_score = row[7].strip()
        return_date = row[6].strip()

        value = f"{customer_name}|{customer_email}|{product_category}|{is_return}|{refund_amount}|{risk_score}|{return_date}"
        print(f"{customer_id}\t{value}")
    except IndexError:
        continue
