#!/usr/bin/env python3
import sys
import csv
import random

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    try:
        customer_id = row[0].strip()
        category = row[3].strip()
        is_return = int(row[4].strip())
        request_date = row[6].strip()
        refund_amount = float(row[5].strip())
        risk_score = float(row[7].strip()) if row[7].strip() else 0.0
        
        customer_name = row[1].strip()
        customer_email = row[2].strip()
        
        print(f"{customer_id}\t{customer_name}|{customer_email}|{category}|{is_return}|{refund_amount}|{risk_score}|{request_date}")
    except IndexError:
        continue
