#!/usr/bin/env python3
import sys
import csv
import random

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    try:
        customer_id = row[1].strip()
        category = row[3].strip()
        returned = row[11].strip()
        request_date = row[12].strip()
        total_amount = row[14].strip()
        
        is_return = 1 if returned == "1" else 0
        
        try:
            total_float = float(total_amount)
        except ValueError:
            total_float = 0.0
            
        refund_amount = total_float if is_return else 0.0
        risk_score = round(random.uniform(40.0, 99.0), 2) if is_return else round(random.uniform(0.0, 30.0), 2)
        
        customer_name = f"Customer {customer_id}"
        customer_email = f"{customer_id.lower()}@example.com"
        
        print(f"{customer_id}\t{customer_name}|{customer_email}|{category}|{is_return}|{refund_amount}|{risk_score}|{request_date}")
    except IndexError:
        continue
