#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    try:
        category = row[3].strip()
        returned = row[11].strip()
        total_amount = row[14].strip()
        
        is_return = 1 if returned == "1" else 0
        if is_return == 1:
            try:
                refund_amount = float(total_amount)
            except ValueError:
                refund_amount = 0.0
            print(f"{category}\t{refund_amount}")
    except IndexError:
        continue
