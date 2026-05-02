#!/usr/bin/env python3
"""
KPIs Reducer — Aggregates global return statistics.

Input:  Global_KPI \t refund_amount,risk_score  (sorted)
Output: Global_KPI \t JSON with total_refund_loss, total_returns,
        flagged_accounts, high_risk_accounts, avg_refund_value
"""

import sys
import json

total_refund_loss = 0.0
total_returns = 0
flagged_accounts = 0    # risk_score >= 60
high_risk_accounts = 0  # risk_score >= 80

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        key, values = line.split("\t", 1)
        parts = values.split(",")
        refund_amount = float(parts[0])
        risk_score = float(parts[1])
    except (ValueError, IndexError):
        continue

    total_refund_loss += refund_amount
    total_returns += 1

    if risk_score >= 60:
        flagged_accounts += 1
    if risk_score >= 80:
        high_risk_accounts += 1

avg_refund_value = round(total_refund_loss / total_returns, 2) if total_returns else 0.0

result = {
    "total_refund_loss": round(total_refund_loss, 2),
    "total_returns": total_returns,
    "flagged_accounts": flagged_accounts,
    "high_risk_accounts": high_risk_accounts,
    "avg_refund_value": avg_refund_value,
}

print(f"Global_KPI\t{json.dumps(result)}")
