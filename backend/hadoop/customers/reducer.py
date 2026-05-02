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
total_orders = 0
categories = set()
flagged_on = ""


def emit():
    """Print the aggregated record for the current customer."""
    return_rate = (return_count / total_orders * 100) if total_orders > 0 else 0.0
    avg_refund = (total_refunds_claimed / return_count) if return_count > 0 else 0.0

    # ── Fraud Detection Logic (data-driven thresholds) ────────────────
    #
    # Thresholds derived from actual dataset distribution (1,635 returners):
    #   Median avg refund = $90  (normal customer baseline)
    #   75th percentile   = $238 (above average — suspicious)
    #   90th percentile   = $522 (very high — strong fraud signal)
    #
    # HIGH RISK (score=90): Clear abuse pattern — needs volume + strong signal
    #   • 5+ returns AND rate > 60%          → returning majority of orders
    #   • 10+ returns AND avg refund > $238  → above 75th pct, repeatedly
    #   • 3+ returns AND total > $600 AND rate > 40% → 3x avg price extraction
    #     ($198 avg item price × 3 returns = $594, so $600 is the data-driven cutoff)
    #
    is_high_risk = (
        (return_count >= 5 and return_rate > 60.0) or
        (return_count >= 10 and avg_refund > 238.0) or
        (return_count >= 3 and total_refunds_claimed > 600.0 and return_rate > 40.0)
    )

    # MEDIUM RISK (score=60): Suspicious pattern but not extreme
    #   • 3+ returns AND rate > 30%         → 1 in 3 orders returned
    #   • 5+ returns AND avg refund > $90   → above median, repeatedly
    #
    is_medium_risk = (
        (return_count >= 3 and return_rate > 30.0) or
        (return_count >= 5 and avg_refund > 90.0)
    )

    # LOW RISK (score=20): Normal customer — occasional or no returns
    if is_high_risk:
        final_risk = 90.0
    elif is_medium_risk:
        final_risk = 60.0
    else:
        final_risk = 20.0

    result = {
        "name": name,
        "email": email,
        "total_refunds_claimed": round(total_refunds_claimed, 2),
        "return_count": return_count,
        "risk_score": final_risk,
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
        total_orders = 0
        categories = set()
        flagged_on = ""

    current_id = customer_id
    name = r_name
    email = r_email
    total_orders += 1

    if r_category:
        categories.add(r_category)

    if r_is_return == 1:
        return_count += 1
        total_refunds_claimed += r_refund

        # Keep the first non-empty return_date
        if not flagged_on and r_date:
            flagged_on = r_date

# Emit the last customer
if current_id:
    emit()
