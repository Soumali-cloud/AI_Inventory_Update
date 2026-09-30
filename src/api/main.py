from pathlib import Path
from typing import Optional
from src.api.price_routes import router as price_router
from src.api.decision_routes import router as decision_router
from src.api.evaluation_routes import router as evaluation_router

import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
    / "inventory"
)

DECISION_FILE = (
    REPORTS_DIR
    / "ai_inventory_decisions.csv"
)

SURGE_FILE = (
    REPORTS_DIR
    / "demand_surge_analysis.csv"
)

REORDER_FILE = (
    REPORTS_DIR
    / "reorder_recommendations.csv"
)

FORECAST_FILE = (
    PROJECT_ROOT
    / "reports"
    / "demand_model"
    / "future_demand_forecast.csv"
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Inventory Intelligence API",
    description=(
        "AI-powered inventory demand prediction, "
        "forecasting, stockout detection, "
        "overstock detection and reorder recommendations."
    ),
    
    version="1.0.0",
)
app.include_router(price_router)
app.include_router(decision_router)
app.include_router(evaluation_router)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA LOADING
# ============================================================

def load_decisions():

    if not DECISION_FILE.exists():

        raise FileNotFoundError(
            f"Decision file not found: {DECISION_FILE}"
        )

    return pd.read_csv(
        DECISION_FILE
    )


def load_surge():

    if not SURGE_FILE.exists():

        raise FileNotFoundError(
            f"Surge file not found: {SURGE_FILE}"
        )

    return pd.read_csv(
        SURGE_FILE
    )


def load_reorder():

    if not REORDER_FILE.exists():

        raise FileNotFoundError(
            f"Reorder file not found: {REORDER_FILE}"
        )

    return pd.read_csv(
        REORDER_FILE
    )


def load_forecast():

    if not FORECAST_FILE.exists():

        raise FileNotFoundError(
            f"Forecast file not found: {FORECAST_FILE}"
        )

    return pd.read_csv(
        FORECAST_FILE
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "application": "AI Inventory Intelligence",
        "status": "running",
        "version": "1.0.0",
        "description": (
            "AI-powered inventory prediction "
            "and decision support system."
        ),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Inventory Intelligence API",
    }


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    total_products = len(df)


    buy_now = len(
        df[
            df["ai_decision"]
            == "BUY NOW"
        ]
    )


    buy = len(
        df[
            df["ai_decision"]
            == "BUY"
        ]
    )


    increase_stock = len(
        df[
            df["ai_decision"]
            == "INCREASE STOCK"
        ]
    )


    reduce = len(
        df[
            df["ai_decision"]
            == "REDUCE"
        ]
    )


    monitor = len(
        df[
            df["ai_decision"]
            == "MONITOR"
        ]
    )


    hold = len(
        df[
            df["ai_decision"]
            == "HOLD"
        ]
    )


    critical_stockout = len(
        df[
            df["stockout_risk"]
            == "Critical"
        ]
    )


    high_stockout = len(
        df[
            df["stockout_risk"]
            == "High"
        ]
    )


    extreme_surge = len(
        df[
            df["demand_surge_level"]
            == "Extreme Surge"
        ]
    )


    high_surge = len(
        df[
            df["demand_surge_level"]
            == "High Surge"
        ]
    )


    total_reorder_units = int(
        df[
            "recommended_reorder_quantity"
        ].sum()
    )


    total_purchase_value = float(
        df[
            "recommended_purchase_value"
        ].sum()
    )


    average_inventory_health = float(
        df[
            "inventory_health_score"
        ].mean()
    )


    return {

        "total_products":
            total_products,

        "ai_decisions": {

            "buy_now":
                buy_now,

            "buy":
                buy,

            "increase_stock":
                increase_stock,

            "reduce":
                reduce,

            "monitor":
                monitor,

            "hold":
                hold,
        },

        "stockout_risk": {

            "critical":
                critical_stockout,

            "high":
                high_stockout,
        },

        "demand_surge": {

            "extreme":
                extreme_surge,

            "high":
                high_surge,
        },

        "reorder": {

            "total_units":
                total_reorder_units,

            "estimated_purchase_value":
                total_purchase_value,
        },

        "inventory_health": {

            "average_score":
                average_inventory_health,
        },
    }


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@app.get("/products")
def get_products(

    search: Optional[str] = Query(
        default=None
    ),

    category: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    if search:

        search_lower = (
            search.lower()
        )

        df = df[
            df[
                "product_name"
            ]
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
        ]


    if category:

        df = df[
            df[
                "category"
            ].str.lower()
            == category.lower()
        ]


    df = df.head(
        limit
    )


    return {
        "count": len(df),
        "products": df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@app.get("/products/{product_id}")
def get_product(
    product_id: str
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    result = df[
        df["product_id"].astype(str)
        == str(product_id)
    ]


    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Product '{product_id}' "
                "not found."
            ),
        )


    return result.iloc[
        0
    ].to_dict()


# ============================================================
# INVENTORY ENDPOINT
# ============================================================

@app.get("/inventory")
def get_inventory(

    status: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    if status:

        df = df[
            df[
                "inventory_status"
            ].str.lower()
            == status.lower()
        ]


    df = df.head(
        limit
    )


    return {
        "count": len(df),
        "inventory": df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# DEMAND SURGE ENDPOINT
# ============================================================

@app.get("/demand/surge")
def demand_surge(

    level: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):

    try:

        df = load_surge()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    if level:

        df = df[
            df[
                "demand_surge_level"
            ].str.lower()
            == level.lower()
        ]


    df = (
        df
        .sort_values(
            "demand_surge_percentage",
            ascending=False,
        )
        .head(limit)
    )


    return {
        "count": len(df),
        "surges": df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# REORDER RECOMMENDATIONS
# ============================================================

@app.get("/recommendations")
def recommendations(

    urgency: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    if urgency:

        df = df[
            df[
                "reorder_urgency"
            ].str.lower()
            == urgency.lower()
        ]


    df = (
        df
        .sort_values(
            "ai_decision_score",
            ascending=False,
        )
        .head(limit)
    )


    return {
        "count": len(df),
        "recommendations":
            df.to_dict(
                orient="records"
            ),
    }


# ============================================================
# AI DECISIONS
# ============================================================

@app.get("/ai/decisions")
def ai_decisions(

    decision: Optional[str] = Query(
        default=None
    ),

    priority: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    if decision:

        df = df[
            df[
                "ai_decision"
            ].str.lower()
            == decision.lower()
        ]


    if priority:

        df = df[
            df[
                "decision_priority"
            ].str.lower()
            == priority.lower()
        ]


    df = (
        df
        .sort_values(
            "ai_decision_score",
            ascending=False,
        )
        .head(limit)
    )


    return {
        "count": len(df),
        "decisions":
            df.to_dict(
                orient="records"
            ),
    }


# ============================================================
# FORECAST ENDPOINT
# ============================================================

@app.get("/forecast/{product_id}")
def product_forecast(
    product_id: str
):

    try:

        df = load_forecast()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    result = df[
        df["product_id"].astype(str)
        == str(product_id)
    ]


    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Forecast for product "
                f"'{product_id}' not found."
            ),
        )


    result = result.copy()


    if "date" in result.columns:

        result["date"] = (
            result["date"]
            .astype(str)
        )


    return {
        "product_id":
            product_id,

        "forecast_days":
            len(result),

        "forecast":
            result.to_dict(
                orient="records"
            ),
    }


# ============================================================
# PRODUCT ANALYTICS
# ============================================================

@app.get("/analytics/{product_id}")
def product_analytics(
    product_id: str
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    result = df[
        df["product_id"].astype(str)
        == str(product_id)
    ]


    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Product '{product_id}' "
                "not found."
            ),
        )


    row = result.iloc[
        0
    ]


    return {

        "product": {

            "id":
                row["product_id"],

            "name":
                row["product_name"],

            "category":
                row["category"],

        },

        "inventory": {

            "current":
                row["current_inventory"],

            "status":
                row["inventory_status"],

            "health_score":
                row["inventory_health_score"],

            "days_of_inventory":
                row["estimated_days_of_inventory"],

        },

        "demand": {

            "historical_daily":
                row["historical_daily_demand"],

            "forecast_7_day":
                row["forecast_7_day"],

            "forecast_30_day":
                row["forecast_30_day"],

            "surge_level":
                row["demand_surge_level"],

            "surge_percentage":
                row["demand_surge_percentage"],

        },

        "risk": {

            "stockout":
                row["stockout_risk"],

            "demand_risk_score":
                row["demand_risk_score"],

        },

        "recommendation": {

            "ai_decision":
                row["ai_decision"],

            "priority":
                row["decision_priority"],

            "confidence":
                row["decision_confidence"],

            "reorder_quantity":
                row[
                    "recommended_reorder_quantity"
                ],

            "action":
                row[
                    "ai_recommended_action"
                ],

        },
    }
# ============================================================
# DASHBOARD PRODUCTS
# ============================================================

@app.get("/dashboard/products")
def dashboard_products(
    limit: int = Query(
        default=30,
        ge=1,
        le=500,
    ),
):

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    products = []

    for _, row in df.head(limit).iterrows():

        products.append(
            {
                "product_id":
                    row["product_id"],

                "product_name":
                    row["product_name"],

                "category":
                    row["category"],

                "price":
                    float(row["price"]),

                "current_inventory":
                    int(row["current_inventory"]),

                "forecast_7_day":
                    float(row["forecast_7_day"]),

                "forecast_30_day":
                    float(row["forecast_30_day"]),

                "demand_surge":
                    row["demand_surge_level"],

                "stockout_risk":
                    row["stockout_risk"],

                "inventory_status":
                    row["inventory_status"],

                "ai_decision":
                    row["ai_decision"],

                "decision_priority":
                    row["decision_priority"],

                "decision_score":
                    float(
                        row["ai_decision_score"]
                    ),

                "reorder_quantity":
                    int(
                        row[
                            "recommended_reorder_quantity"
                        ]
                    ),

                "action":
                    row[
                        "ai_recommended_action"
                    ],
            }
        )

    return {
        "count": len(products),
        "products": products,
    }


# ============================================================
# DASHBOARD ALERTS
# ============================================================

@app.get("/dashboard/alerts")
def dashboard_alerts():

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    alerts = []


    # --------------------------------------------------------
    # Critical stockout alerts
    # --------------------------------------------------------

    critical_stockout = df[
        df["stockout_risk"]
        == "Critical"
    ]

    for _, row in critical_stockout.iterrows():

        alerts.append(
            {
                "type":
                    "STOCKOUT",

                "severity":
                    "CRITICAL",

                "product_id":
                    row["product_id"],

                "product_name":
                    row["product_name"],

                "message":
                    (
                        "Critical stockout risk. "
                        "Immediate replenishment "
                        "recommended."
                    ),

                "recommended_quantity":
                    int(
                        row[
                            "recommended_reorder_quantity"
                        ]
                    ),
            }
        )


    # --------------------------------------------------------
    # Extreme demand surge alerts
    # --------------------------------------------------------

    extreme_surge = df[
        df["demand_surge_level"]
        == "Extreme Surge"
    ]

    for _, row in extreme_surge.iterrows():

        alerts.append(
            {
                "type":
                    "DEMAND_SURGE",

                "severity":
                    "CRITICAL",

                "product_id":
                    row["product_id"],

                "product_name":
                    row["product_name"],

                "message":
                    (
                        "Extreme demand surge "
                        "detected. Increase "
                        "inventory immediately."
                    ),

                "recommended_quantity":
                    int(
                        row[
                            "recommended_reorder_quantity"
                        ]
                    ),
            }
        )


    # --------------------------------------------------------
    # High demand surge alerts
    # --------------------------------------------------------

    high_surge = df[
        df["demand_surge_level"]
        == "High Surge"
    ]

    for _, row in high_surge.iterrows():

        alerts.append(
            {
                "type":
                    "DEMAND_SURGE",

                "severity":
                    "HIGH",

                "product_id":
                    row["product_id"],

                "product_name":
                    row["product_name"],

                "message":
                    (
                        "High demand surge "
                        "detected. Monitor "
                        "inventory closely."
                    ),

                "recommended_quantity":
                    int(
                        row[
                            "recommended_reorder_quantity"
                        ]
                    ),
            }
        )


    # --------------------------------------------------------
    # Overstock alerts
    # --------------------------------------------------------

    overstock = df[
        df["ai_decision"]
        == "REDUCE"
    ]

    for _, row in overstock.iterrows():

        alerts.append(
            {
                "type":
                    "OVERSTOCK",

                "severity":
                    "MEDIUM",

                "product_id":
                    row["product_id"],

                "product_name":
                    row["product_name"],

                "message":
                    (
                        "Inventory appears "
                        "excessive. Consider "
                        "reducing replenishment."
                    ),

                "recommended_quantity":
                    0,
            }
        )


    # --------------------------------------------------------
    # Sort alerts
    # --------------------------------------------------------

    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }


    alerts.sort(
        key=lambda x:
            severity_order.get(
                x["severity"],
                99,
            )
    )


    return {
        "count": len(alerts),
        "alerts": alerts,
    }


# ============================================================
# INVENTORY HEALTH
# ============================================================

@app.get("/dashboard/inventory-health")
def inventory_health():

    try:

        df = load_decisions()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


    healthy = len(
        df[
            df[
                "inventory_status"
            ].str.lower()
            .isin(
                [
                    "healthy",
                    "optimal",
                ]
            )
        ]
    )


    low_stock = len(
        df[
            df[
                "stockout_risk"
            ]
            .isin(
                [
                    "Medium",
                    "High",
                    "Critical",
                ]
            )
        ]
    )


    overstocked = len(
        df[
            df[
                "ai_decision"
            ]
            == "REDUCE"
        ]
    )


    critical = len(
        df[
            df[
                "decision_priority"
            ]
            == "CRITICAL"
        ]
    )


    return {

        "total_products":
            len(df),

        "healthy":
            healthy,

        "low_stock":
            low_stock,

        "overstocked":
            overstocked,

        "critical":
            critical,

        "average_health_score":
            float(
                df[
                    "inventory_health_score"
                ].mean()
            ),
    }