import pandas as pd
from pymongo import MongoClient

print("Connecting to MongoDB...")
client = MongoClient("mongodb://localhost:27017")
db = client["bda_project"]

# Check if collections exist
print("\nChecking if collections are populated...")
for col_name in ["kpis", "categories", "customers"]:
    count = db[col_name].count_documents({})
    print(f"Collection '{col_name}' has {count} documents.")

if db["customers"].count_documents({}) == 0:
    print("\nCollections are empty! Generating dummy data for API to work...")
    
    # 1. KPIs
    db["kpis"].drop()
    db["kpis"].insert_one({
        "total_returns": 5420,
        "total_refunds": 1250000.50,
        "flagged_accounts": 124,
        "high_risk_value": 45000.75
    })
    
    # 2. Categories
    db["categories"].drop()
    db["categories"].insert_many([
        {"category": "Electronics", "returns": 1200, "refund_value": 450000},
        {"category": "Clothing", "returns": 800, "refund_value": 120000},
        {"category": "Home & Garden", "returns": 600, "refund_value": 150000},
        {"category": "Sports", "returns": 400, "refund_value": 80000},
        {"category": "Books", "returns": 300, "refund_value": 15000}
    ])
    
    # 3. Customers
    db["customers"].drop()
    db["customers"].insert_many([
        {
            "customer_id": "CUST-001",
            "name": "Alice Smith",
            "email": "alice@example.com",
            "total_refunds_claimed": 5400.0,
            "return_count": 12,
            "risk_score": 85.5,
            "flagged_on": "2023-10-15",
            "categories": ["Electronics", "Clothing"]
        },
        {
            "customer_id": "CUST-002",
            "name": "Bob Jones",
            "email": "bob@example.com",
            "total_refunds_claimed": 1200.0,
            "return_count": 3,
            "risk_score": 45.0,
            "flagged_on": "2023-11-02",
            "categories": ["Sports"]
        },
        {
            "customer_id": "CUST-003",
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "total_refunds_claimed": 8900.0,
            "return_count": 25,
            "risk_score": 92.0,
            "flagged_on": "2023-09-20",
            "categories": ["Electronics", "Home & Garden"]
        }
    ])
    print("Dummy data inserted successfully.")

print("\nSetup check complete.")
