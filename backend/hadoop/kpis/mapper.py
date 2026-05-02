#!/usr/bin/env python3
import sys
import csv
import random

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    try:
        is_return = int(row[4].strip())
        if is_return == 1:
            refund_amount = float(row[5].strip())
            risk_score = float(row[7].strip()) if row[7].strip() else 0.0
            print(f"Global_KPI\t{refund_amount},{risk_score}")
    except IndexError:
        continue
