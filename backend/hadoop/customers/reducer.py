#!/usr/bin/env python3
"""
Customers Reducer — Aggregates per-customer return statistics.

Input:  customer_id \t name|email|category|is_return|refund_amount|risk_score|return_date
        (sorted by customer_id)
Output: customer_id \t JSON with name, email, total_refunds_claimed,
        return_count, risk_score (avg), flagged_on, categories
"""

import sys
import json

current_id = None
name = ""
email = ""
total_refunds_claimed = 0.0
return_count = 0
risk_score_sum = 0.0
risk_score_count = 0
categories = set()
flagged_on = ""


def emit():
    """Print the aggregated record for the current customer."""
    avg_risk = round(risk_score_sum / risk_score_count, 2) if risk_score_count else 0.0
    result = {
        "name": name,
        "email": email,
        "total_refunds_claimed": round(total_refunds_claimed, 2),
        "return_count": return_count,
        "risk_score": avg_risk,
        "flagged_on": flagged_on,
        "categories": sorted(categories),
    }
    print(f"{current_id}\t{json.dumps(result)}")


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        customer_id, values = line.split("\t", 1)
        parts = values.split("|")
        r_name = parts[0]
        r_email = parts[1]
        r_category = parts[2]
        r_is_return = int(parts[3])
        r_refund = float(parts[4])
        r_risk = float(parts[5])
        r_date = parts[6]
    except (ValueError, IndexError):
        continue

    # If the customer changed, emit the previous customer's totals
    if current_id and current_id != customer_id:
        emit()
        # Reset accumulators
        total_refunds_claimed = 0.0
        return_count = 0
        risk_score_sum = 0.0
        risk_score_count = 0
        categories = set()
        flagged_on = ""

    current_id = customer_id
    name = r_name
    email = r_email

    if r_category:
        categories.add(r_category)

    if r_is_return == 1:
        return_count += 1
        total_refunds_claimed += r_refund
        risk_score_sum += r_risk
        risk_score_count += 1

        # Keep the first non-empty return_date
        if not flagged_on and r_date:
            flagged_on = r_date

# Emit the last customer
if current_id:
    emit()
