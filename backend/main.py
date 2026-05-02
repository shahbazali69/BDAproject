"""
main.py — BDA Fraud Analytics API (Hadoop-First Batch Architecture)

All endpoints read from pre-calculated MongoDB collections populated
by the Hadoop MapReduce pipeline via export_to_mongo.py.

Collections:
  - kpis       : single document with global KPI metrics
  - categories : one document per product category
  - customers  : one document per customer
"""

import re

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

app = FastAPI(title="BDA Fraud Analytics API", version="2.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MongoDB ───────────────────────────────────────────────────────────────────
client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
db = client["bda_project"]

kpis_col = db["kpis"]
categories_col = db["categories"]
customers_col = db["customers"]

print("✅  MongoDB collections configured: kpis, categories, customers")


# ── Helpers ───────────────────────────────────────────────────────────────────
def _risk_level(score: float) -> str:
    if score >= 80:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/kpis")
async def get_kpis():
    """Return pre-calculated global KPIs from the Hadoop kpis collection."""
    doc = kpis_col.find_one({})
    if not doc:
        return {}
    doc.pop("_id", None)
    
    total = doc.get("total_returns", 1)
    doc["fraud_rate_pct"] = round((doc.get("flagged_accounts", 0) / total) * 100, 1) if total else 0
    
    return doc


@app.get("/api/category-returns")
async def get_category_returns():
    """Return top 10 categories by return count with calculated return rates."""
    results = list(categories_col.find().sort("returns", -1).limit(10))

    if not results:
        return []

    total = sum(r.get("returns", 0) for r in results) or 1

    data = []
    for r in results:
        r.pop("_id", None)
        r["return_rate"] = round((r.get("returns", 0) / total) * 100, 1)
        data.append(r)

    return data


@app.get("/api/customers")
async def get_customers(
    search: str = Query("", description="Search filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(15, ge=1, le=100, description="Items per page"),
    risk: str = Query("all", description="Risk level filter: High, Medium, Low, or all"),
):
    """Return paginated, filterable customer data from the Hadoop customers collection."""

    # ── Build query filter ────────────────────────────────────────────
    query = {}

    if search:
        search_regex = {"$regex": re.escape(search), "$options": "i"}
        query["$or"] = [
            {"name": search_regex},
            {"email": search_regex},
            {"customer_id": search_regex},
        ]

    if risk and risk != "all":
        if risk == "High":
            query["risk_score"] = {"$gte": 80}
        elif risk == "Medium":
            query["risk_score"] = {"$gte": 50, "$lt": 80}
        elif risk == "Low":
            query["risk_score"] = {"$lt": 50}

    # ── Count & Fetch ─────────────────────────────────────────────────
    total = customers_col.count_documents(query)

    results = list(
        customers_col.find(query)
        .sort("return_count", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    # ── Format output ─────────────────────────────────────────────────
    data = []
    for r in results:
        score = r.get("risk_score", 0)
        data.append({
            "customer_id":           r.get("customer_id", ""),
            "name":                  r.get("name", "Unknown"),
            "email":                 r.get("email", ""),
            "total_refunds_claimed": round(r.get("total_refunds_claimed", 0), 2),
            "return_count":          r.get("return_count", 0),
            "risk_score":            round(score, 1),
            "risk_level":            _risk_level(score),
            "flagged_on":            str(r.get("flagged_on", ""))[:10],
            "categories":            r.get("categories", []),
        })

    return {"total": total, "page": page, "limit": limit, "data": data}


@app.get("/")
async def root():
    return {"message": "BDA Fraud Analytics API is running.", "version": "2.0.0"}
