from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import random

app = FastAPI(title="BDA Fraud Analytics API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MongoDB ───────────────────────────────────────────────────────────────────
try:
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
    client.admin.command("ping")          # test connection
    db = client["bda_project"]
    collection = db["ecommerce_returns"]
    MONGO_LIVE = True
    print("✅  MongoDB connected successfully.")
except Exception:
    MONGO_LIVE = False
    print("⚠️   MongoDB unavailable – falling back to realistic mock data.")


# ── Mock Data ─────────────────────────────────────────────────────────────────
MOCK_KPIS = {
    "total_refund_loss": 4_872_340.75,
    "total_returns": 187_412,
    "flagged_accounts": 3_219,
    "fraud_rate_pct": 8.7,
    "avg_refund_value": 25.99,
    "high_risk_accounts": 412,
}

MOCK_CATEGORY_RETURNS = [
    {"category": "Fashion",         "returns": 52_400, "refund_loss": 1_320_000, "return_rate": 34.2},
    {"category": "Electronics",     "returns": 38_900, "refund_loss": 1_890_000, "return_rate": 22.1},
    {"category": "Home & Garden",   "returns": 27_600, "refund_loss":   690_000, "return_rate": 18.7},
    {"category": "Sports",          "returns": 21_300, "refund_loss":   430_000, "return_rate": 15.3},
    {"category": "Beauty",          "returns": 18_200, "refund_loss":   310_000, "return_rate": 12.8},
    {"category": "Books & Media",   "returns": 14_800, "refund_loss":   112_000, "return_rate": 9.4},
    {"category": "Toys & Games",    "returns": 14_212, "refund_loss":   120_340, "return_rate": 10.1},
]

RISK_LEVELS = ["High", "High", "High", "Medium", "Medium", "Low"]
ALL_CATEGORIES = ["Electronics", "Fashion", "Home & Garden", "Sports", "Beauty", "Toys & Games"]
MOCK_CUSTOMERS = [
    {
        "customer_id": f"USR-{10000 + i}",
        "name": name,
        "email": f"{name.lower().replace(' ', '.')}@example.com",
        "total_refunds_claimed": round(random.uniform(800, 9800), 2),
        "return_count": random.randint(12, 87),
        "risk_score": round(random.uniform(60, 99), 1),
        "risk_level": RISK_LEVELS[i % len(RISK_LEVELS)],
        "flagged_on": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "categories": random.sample(ALL_CATEGORIES, k=random.randint(1, 3)),
    }
    for i, name in enumerate([
        "Amara Okafor", "Liam Fitzgerald", "Zara Ahmed", "Marcus Webb",
        "Priya Sharma", "Tyler Brooks", "Mei-Ling Xu", "Rafael Morales",
        "Sofia Andersen", "James Thornton", "Aisha Nkosi", "Daniel Kim",
        "Elena Volkov", "Omar Khalil", "Chloe Dumont",
    ])
]


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
    if not MONGO_LIVE:
        return MOCK_KPIS

    pipeline = [
        {"$match": {"return_status": "Yes"}},
        {
            "$group": {
                "_id": None,
                "total_refund_loss":   {"$sum": "$refund_amount"},
                "total_returns":       {"$sum": 1},
                "flagged_accounts":    {"$sum": {"$cond": [{"$gte": ["$risk_score", 60]}, 1, 0]}},
                "high_risk_accounts":  {"$sum": {"$cond": [{"$gte": ["$risk_score", 80]}, 1, 0]}},
                "avg_refund_value":    {"$avg": "$refund_amount"},
            }
        }
    ]
    result = list(collection.aggregate(pipeline))
    if not result:
        return MOCK_KPIS

    r = result[0]
    total = r.get("total_returns", 1)
    flagged = r.get("flagged_accounts", 0)
    return {
        "total_refund_loss":  round(r.get("total_refund_loss", 0), 2),
        "total_returns":      total,
        "flagged_accounts":   flagged,
        "fraud_rate_pct":     round((flagged / total) * 100, 1) if total else 0,
        "avg_refund_value":   round(r.get("avg_refund_value", 0), 2),
        "high_risk_accounts": r.get("high_risk_accounts", 0),
    }


@app.get("/api/category-returns")
async def get_category_returns():
    if not MONGO_LIVE:
        return MOCK_CATEGORY_RETURNS

    pipeline = [
        {"$match": {"return_status": "Yes"}},
        {
            "$group": {
                "_id":          "$product_category",
                "returns":      {"$sum": 1},
                "refund_loss":  {"$sum": "$refund_amount"},
            }
        },
        {"$sort": {"returns": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    if not result:
        return MOCK_CATEGORY_RETURNS

    total = sum(r["returns"] for r in result) or 1
    return [
        {
            "category":    r["_id"] or "Unknown",
            "returns":     r["returns"],
            "refund_loss": round(r["refund_loss"], 2),
            "return_rate": round((r["returns"] / total) * 100, 1),
        }
        for r in result
    ]


@app.get("/api/customers")
async def get_customers(
    search: str = Query("", description="Search filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(15, ge=1, le=100, description="Items per page"),
    risk: str = Query("all", description="Risk level filter"),
):
    if not MONGO_LIVE:
        # ── Mock data path ────────────────────────────────────────────────
        filtered = MOCK_CUSTOMERS
        if search:
            s = search.lower()
            filtered = [
                c for c in filtered
                if s in c["name"].lower()
                or s in c["email"].lower()
                or s in c["customer_id"].lower()
                or any(s in cat.lower() for cat in c.get("categories", []))
            ]
        if risk and risk != "all":
            filtered = [c for c in filtered if _risk_level(c["risk_score"]) == risk]
        # Sort by return_count descending
        filtered = sorted(filtered, key=lambda c: c["return_count"], reverse=True)
        total = len(filtered)
        start = (page - 1) * limit
        sliced = filtered[start : start + limit]
        return {"total": total, "page": page, "limit": limit, "data": sliced}

    # ── MongoDB path ──────────────────────────────────────────────────
    pipeline = [
        {
            "$group": {
                "_id":                  "$customer_id",
                "name":                 {"$first": "$customer_name"},
                "email":                {"$first": "$customer_email"},
                "total_refunds_claimed":{"$sum": "$refund_amount"},
                "return_count":         {"$sum": {"$cond": [{"$eq": ["$return_status", "Yes"]}, 1, 0]}},
                "risk_score":           {"$avg": "$risk_score"},
                "flagged_on":           {"$first": "$return_date"},
                "categories":           {"$addToSet": "$product_category"},
            }
        },
    ]

    # Optional search filter (after grouping)
    if search:
        search_regex = {"$regex": re.escape(search), "$options": "i"}
        pipeline.append({
            "$match": {
                "$or": [
                    {"name":       search_regex},
                    {"email":      search_regex},
                    {"_id":        search_regex},
                    {"categories": search_regex},
                ]
            }
        })

    # Optional risk filter
    if risk and risk != "all":
        if risk == "High":
            pipeline.append({"$match": {"risk_score": {"$gte": 80}}})
        elif risk == "Medium":
            pipeline.append({"$match": {"risk_score": {"$gte": 50, "$lt": 80}}})
        elif risk == "Low":
            pipeline.append({"$match": {"risk_score": {"$lt": 50}}})

    # Facet for total count + paginated data
    pipeline.append({
        "$facet": {
            "metadata": [{"$count": "total"}],
            "data": [
                {"$sort": {"return_count": -1}},
                {"$skip": (page - 1) * limit},
                {"$limit": limit},
            ]
        }
    })

    result = list(collection.aggregate(pipeline))
    if not result:
        return {"total": 0, "page": page, "limit": limit, "data": []}

    facet = result[0]
    total = facet["metadata"][0]["total"] if facet["metadata"] else 0
    data = [
        {
            "customer_id":           r["_id"],
            "name":                  r.get("name", "Unknown"),
            "email":                 r.get("email", ""),
            "total_refunds_claimed": round(r.get("total_refunds_claimed", 0), 2),
            "return_count":          r.get("return_count", 0),
            "risk_score":            round(r.get("risk_score", 0), 1),
            "risk_level":            _risk_level(r.get("risk_score", 0)),
            "flagged_on":            str(r.get("flagged_on", ""))[:10],
            "categories":            r.get("categories", []),
        }
        for r in facet["data"]
    ]
    return {"total": total, "page": page, "limit": limit, "data": data}


@app.get("/")
async def root():
    return {"message": "BDA Fraud Analytics API is running.", "mongo_live": MONGO_LIVE}
