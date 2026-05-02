#!/usr/bin/env python3
import sys
import csv
import random

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    try:
        returned = row[11].strip()
        total_amount = row[14].strip()
        
        is_return = 1 if returned == "1" else 0
        if is_return == 1:
            try:
                refund_amount = float(total_amount)
            except ValueError:
                refund_amount = 0.0
            
            risk_score = round(random.uniform(40.0, 99.0), 2)
            print(f"Global_KPI\t{refund_amount},{risk_score}")
    except IndexError:
        continue
