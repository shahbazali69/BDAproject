#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)
header = next(reader, None)

for row in reader:
    try:
        category = row[3].strip()
        is_return = int(row[4].strip())
        if is_return == 1:
            refund_amount = float(row[5].strip())
            print(f"{category}\t{refund_amount}")
    except IndexError:
        continue
