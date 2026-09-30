import os

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

REORDER_PATH = (
    "reports/inventory/reorder_recommendations.csv"
)

SURGE_PATH = (
    "reports/inventory/demand_surge_analysis.csv"
)

FORECAST_PATH = (
    "reports/demand_model/future_demand_forecast.csv"
)

OUTPUT_PATH = (
    "reports/inventory/ai_inventory_decisions.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    "reports/inventory",
    exist_ok=True,
)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("AI INVENTORY INTELLIGENCE")
print("AI INVENTORY DECISION ENGINE")
print("=" * 70)


# ============================================================
# LOAD REORDER DATA
# ============================================================

print("\nLoading reorder recommendations...")

reorder_df = pd.read_csv(
    REORDER_PATH
)

print(
    f"Reorder records: "
    f"{len(reorder_df):,}"
)


# ============================================================
# LOAD DEMAND SURGE DATA
# ============================================================

print("\nLoading demand surge analysis...")

surge_df = pd.read_csv(
    SURGE_PATH
)

print(
    f"Surge records: "
    f"{len(surge_df):,}"
)


# ============================================================
# LOAD FORECAST DATA
# ============================================================

print("\nLoading demand forecast...")

forecast_df = pd.read_csv(
    FORECAST_PATH,
    parse_dates=["date"],
)

print(
    f"Forecast records: "
    f"{len(forecast_df):,}"
)


# ============================================================
# VALIDATE REORDER COLUMNS
# ============================================================

required_reorder_columns = [
    "product_id",
    "product_name",
    "category",
    "price",
    "current_inventory",
    "average_daily_demand",
    "forecast_7_day",
    "forecast_14_day",
    "forecast_30_day",
    "lead_time_days",
    "lead_time_demand",
    "safety_stock",
    "reorder_point",
    "target_inventory",
    "recommended_reorder_quantity",
    "reorder_required",
    "reorder_urgency",
    "projected_inventory_after_reorder",
    "projected_days_after_reorder",
    "estimated_reorder_value",
    "inventory_status",
    "inventory_health_score",
]


missing_reorder = [
    column
    for column in required_reorder_columns
    if column not in reorder_df.columns
]


if missing_reorder:

    raise ValueError(
        "Missing columns in reorder file: "
        + str(missing_reorder)
    )


# ============================================================
# VALIDATE SURGE COLUMNS
# ============================================================

required_surge_columns = [
    "product_id",
    "historical_daily_demand",
    "historical_demand_growth",
    "forecast_daily_average",
    "demand_surge_percentage",
    "demand_surge_level",
    "stockout_risk",
    "demand_priority",
    "demand_risk_score",
]


missing_surge = [
    column
    for column in required_surge_columns
    if column not in surge_df.columns
]


if missing_surge:

    raise ValueError(
        "Missing columns in surge file: "
        + str(missing_surge)
    )


# ============================================================
# SELECT SURGE COLUMNS
# ============================================================

surge_columns = [
    "product_id",
    "historical_daily_demand",
    "historical_demand_growth",
    "forecast_daily_average",
    "demand_surge_percentage",
    "demand_surge_level",
    "stockout_risk",
    "demand_priority",
    "demand_risk_score",
]


surge_data = surge_df[
    surge_columns
].copy()


# ============================================================
# MERGE DATA
# ============================================================

print(
    "\nCombining inventory intelligence layers..."
)


df = reorder_df.merge(
    surge_data,
    on="product_id",
    how="left",
    suffixes=(
        "",
        "_surge",
    ),
)


# ============================================================
# NUMERIC CLEANING
# ============================================================

numeric_columns = [
    "price",
    "current_inventory",
    "average_daily_demand",
    "forecast_7_day",
    "forecast_14_day",
    "forecast_30_day",
    "lead_time_days",
    "lead_time_demand",
    "safety_stock",
    "reorder_point",
    "target_inventory",
    "recommended_reorder_quantity",
    "projected_inventory_after_reorder",
    "projected_days_after_reorder",
    "estimated_reorder_value",
    "inventory_health_score",
    "historical_daily_demand",
    "historical_demand_growth",
    "forecast_daily_average",
    "demand_surge_percentage",
    "demand_risk_score",
]


for column in numeric_columns:

    if column in df.columns:

        df[column] = (
            pd.to_numeric(
                df[column],
                errors="coerce",
            )
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(0)
        )


# ============================================================
# CATEGORICAL CLEANING
# ============================================================

categorical_columns = [
    "inventory_status",
    "reorder_required",
    "reorder_urgency",
    "demand_surge_level",
    "stockout_risk",
    "demand_priority",
]


for column in categorical_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .fillna("Unknown")
        )


# ============================================================
# ESTIMATED DAYS OF INVENTORY
# ============================================================

# This was the missing column in the previous version.
#
# Current inventory
# -----------------
# Forecast daily demand
#
# gives the estimated number of days
# the current stock can support.

df[
    "estimated_days_of_inventory"
] = np.where(
    df["forecast_daily_average"] > 0,

    (
        df["current_inventory"]
        / df["forecast_daily_average"]
    ),

    999,
)


df[
    "estimated_days_of_inventory"
] = (
    df[
        "estimated_days_of_inventory"
    ]
    .replace(
        [np.inf, -np.inf],
        np.nan,
    )
    .fillna(999)
)


# ============================================================
# INVENTORY PRESSURE
# ============================================================

def calculate_inventory_pressure(row):

    days = row[
        "estimated_days_of_inventory"
    ]

    reorder_point = row[
        "reorder_point"
    ]

    current_inventory = row[
        "current_inventory"
    ]

    # Completely empty inventory

    if current_inventory <= 0:

        return 100

    # Below reorder point

    if current_inventory <= reorder_point:

        if days <= 3:

            return 100

        elif days <= 7:

            return 90

        elif days <= 14:

            return 75

        else:

            return 60

    # Healthy inventory

    if days >= 60:

        return 5

    elif days >= 30:

        return 10

    elif days >= 21:

        return 15

    elif days >= 14:

        return 25

    return 40


df[
    "inventory_pressure_score"
] = df.apply(
    calculate_inventory_pressure,
    axis=1,
)


# ============================================================
# DEMAND PRESSURE
# ============================================================

def calculate_demand_pressure(row):

    surge = row[
        "demand_surge_level"
    ]

    percentage = row[
        "demand_surge_percentage"
    ]

    if surge == "Extreme Surge":

        return 100

    elif surge == "High Surge":

        return max(
            70,
            min(
                95,
                70 + percentage * 0.20,
            ),
        )

    elif surge == "Moderate Surge":

        return max(
            40,
            min(
                70,
                40 + percentage * 0.20,
            ),
        )

    elif surge == "Demand Decline":

        return 10

    return 25


df[
    "demand_pressure_score"
] = df.apply(
    calculate_demand_pressure,
    axis=1,
)


# ============================================================
# STOCKOUT PRESSURE
# ============================================================

def calculate_stockout_pressure(row):

    risk = row[
        "stockout_risk"
    ]

    if risk == "Critical":

        return 100

    elif risk == "High":

        return 80

    elif risk == "Medium":

        return 50

    elif risk == "Low":

        return 10

    return 0


df[
    "stockout_pressure_score"
] = df.apply(
    calculate_stockout_pressure,
    axis=1,
)


# ============================================================
# OVERSTOCK PRESSURE
# ============================================================

def calculate_overstock_pressure(row):

    inventory = row[
        "current_inventory"
    ]

    demand = row[
        "forecast_30_day"
    ]

    if demand <= 0:

        return 100

    coverage_ratio = (
        inventory / demand
    )

    if coverage_ratio >= 2.5:

        return 100

    elif coverage_ratio >= 2.0:

        return 80

    elif coverage_ratio >= 1.5:

        return 50

    elif coverage_ratio >= 1.25:

        return 25

    return 0


df[
    "overstock_pressure_score"
] = df.apply(
    calculate_overstock_pressure,
    axis=1,
)


# ============================================================
# AI DECISION SCORE
# ============================================================

def calculate_decision_score(row):

    demand_pressure = row[
        "demand_pressure_score"
    ]

    stockout_pressure = row[
        "stockout_pressure_score"
    ]

    inventory_pressure = row[
        "inventory_pressure_score"
    ]

    overstock_pressure = row[
        "overstock_pressure_score"
    ]

    score = (
        demand_pressure * 0.35
        +
        stockout_pressure * 0.35
        +
        inventory_pressure * 0.20
        -
        overstock_pressure * 0.20
    )

    return max(
        0,
        min(
            100,
            score,
        ),
    )


df[
    "ai_decision_score"
] = df.apply(
    calculate_decision_score,
    axis=1,
)


# ============================================================
# FINAL AI DECISION
# ============================================================

def determine_decision(row):

    score = row[
        "ai_decision_score"
    ]

    surge = row[
        "demand_surge_level"
    ]

    stockout = row[
        "stockout_risk"
    ]

    overstock = row[
        "overstock_pressure_score"
    ]

    reorder_quantity = row[
        "recommended_reorder_quantity"
    ]

    # --------------------------------------------------------
    # Critical stockout + strong demand
    # --------------------------------------------------------

    if (
        stockout == "Critical"
        and surge in [
            "Extreme Surge",
            "High Surge",
        ]
    ):

        return "BUY NOW"

    # --------------------------------------------------------
    # Extreme demand surge
    # --------------------------------------------------------

    if surge == "Extreme Surge":

        if reorder_quantity > 0:

            return "BUY NOW"

        return "INCREASE STOCK"

    # --------------------------------------------------------
    # Excessive inventory
    # --------------------------------------------------------

    if overstock >= 80:

        return "REDUCE"

    # --------------------------------------------------------
    # High decision score
    # --------------------------------------------------------

    if score >= 70:

        return "BUY"

    # --------------------------------------------------------
    # Medium decision score
    # --------------------------------------------------------

    if score >= 45:

        return "MONITOR"

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    return "HOLD"


df[
    "ai_decision"
] = df.apply(
    determine_decision,
    axis=1,
)


# ============================================================
# AI RECOMMENDED ACTION
# ============================================================

def generate_action(row):

    decision = row[
        "ai_decision"
    ]

    quantity = int(
        max(
            0,
            row[
                "recommended_reorder_quantity"
            ],
        )
    )

    product = row[
        "product_name"
    ]

    surge = row[
        "demand_surge_level"
    ]

    stockout = row[
        "stockout_risk"
    ]

    if decision == "BUY NOW":

        return (
            f"Urgently replenish {product}. "
            f"Recommended quantity: "
            f"{quantity} units."
        )

    if decision == "INCREASE STOCK":

        return (
            f"Increase inventory for "
            f"{product} because demand "
            f"is rising sharply."
        )

    if decision == "BUY":

        return (
            f"Replenish {product}. "
            f"Recommended quantity: "
            f"{quantity} units."
        )

    if decision == "REDUCE":

        return (
            f"Reduce replenishment for "
            f"{product} because inventory "
            f"is excessive."
        )

    if decision == "MONITOR":

        return (
            f"Monitor {product} closely "
            f"before placing another order."
        )

    return (
        f"Hold current inventory level "
        f"for {product}."
    )


df[
    "ai_recommended_action"
] = df.apply(
    generate_action,
    axis=1,
)


# ============================================================
# DECISION CONFIDENCE
# ============================================================

def calculate_confidence(row):

    score = row[
        "ai_decision_score"
    ]

    if score >= 80:

        return "Very High"

    elif score >= 65:

        return "High"

    elif score >= 45:

        return "Medium"

    return "Low"


df[
    "decision_confidence"
] = df.apply(
    calculate_confidence,
    axis=1,
)


# ============================================================
# DECISION PRIORITY
# ============================================================

def calculate_priority(row):

    decision = row[
        "ai_decision"
    ]

    if decision == "BUY NOW":

        return "CRITICAL"

    elif decision in [
        "BUY",
        "INCREASE STOCK",
    ]:

        return "HIGH"

    elif decision in [
        "MONITOR",
        "REDUCE",
    ]:

        return "MEDIUM"

    return "LOW"


df[
    "decision_priority"
] = df.apply(
    calculate_priority,
    axis=1,
)


# ============================================================
# RECOMMENDED PURCHASE VALUE
# ============================================================

df[
    "recommended_purchase_value"
] = (
    df[
        "recommended_reorder_quantity"
    ]
    * df[
        "price"
    ]
)


# ============================================================
# FINAL OUTPUT COLUMNS
# ============================================================

output_columns = [
    "product_id",
    "product_name",
    "category",

    "price",

    "current_inventory",

    "historical_daily_demand",
    "historical_demand_growth",

    "forecast_7_day",
    "forecast_14_day",
    "forecast_30_day",
    "forecast_daily_average",

    "lead_time_days",
    "lead_time_demand",
    "safety_stock",
    "reorder_point",

    "recommended_reorder_quantity",

    "estimated_days_of_inventory",

    "projected_days_after_reorder",

    "inventory_status",
    "inventory_health_score",

    "demand_surge_level",
    "demand_surge_percentage",

    "stockout_risk",

    "overstock_pressure_score",

    "demand_priority",
    "demand_risk_score",

    "inventory_pressure_score",
    "demand_pressure_score",
    "stockout_pressure_score",

    "ai_decision_score",

    "ai_decision",

    "decision_priority",
    "decision_confidence",

    "recommended_purchase_value",

    "ai_recommended_action",
]


# ============================================================
# CHECK OUTPUT COLUMNS
# ============================================================

missing_output_columns = [
    column
    for column in output_columns
    if column not in df.columns
]


if missing_output_columns:

    raise ValueError(
        "Missing output columns: "
        + str(missing_output_columns)
    )


df = df[
    output_columns
]


# ============================================================
# SORT BY PRIORITY
# ============================================================

priority_order = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}


df[
    "_priority_sort"
] = df[
    "decision_priority"
].map(
    priority_order
).fillna(4)


df = (
    df
    .sort_values(
        [
            "_priority_sort",
            "ai_decision_score",
        ],
        ascending=[
            True,
            False,
        ],
    )
    .drop(
        columns=[
            "_priority_sort"
        ]
    )
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "AI DECISION ENGINE COMPLETE"
)

print(
    "=" * 70
)


print(
    f"\nProducts analyzed: "
    f"{len(df)}"
)


# ============================================================
# AI DECISION SUMMARY
# ============================================================

print(
    "\nAI decisions:"
)

print(
    df[
        "ai_decision"
    ].value_counts()
)


# ============================================================
# PRIORITY SUMMARY
# ============================================================

print(
    "\nDecision priority:"
)

print(
    df[
        "decision_priority"
    ].value_counts()
)


# ============================================================
# STOCKOUT SUMMARY
# ============================================================

print(
    "\nStockout risk:"
)

print(
    df[
        "stockout_risk"
    ].value_counts()
)


# ============================================================
# DEMAND SURGE SUMMARY
# ============================================================

print(
    "\nDemand surge:"
)

print(
    df[
        "demand_surge_level"
    ].value_counts()
)


# ============================================================
# PURCHASE SUMMARY
# ============================================================

buy_products = df[
    df[
        "ai_decision"
    ].isin(
        [
            "BUY",
            "BUY NOW",
            "INCREASE STOCK",
        ]
    )
]


print(
    "\nProducts requiring additional inventory:"
)

print(
    len(
        buy_products
    )
)


print(
    "\nTotal recommended units:"
)

print(
    f"{buy_products['recommended_reorder_quantity'].sum():,}"
)


print(
    "\nEstimated purchase value:"
)

print(
    f"₹{buy_products['recommended_purchase_value'].sum():,.2f}"
)


# ============================================================
# CRITICAL DECISIONS
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "CRITICAL AI DECISIONS"
)

print(
    "=" * 70
)


critical = df[
    df[
        "decision_priority"
    ] == "CRITICAL"
]


if critical.empty:

    print(
        "\nNo critical decisions detected."
    )

else:

    print(
        critical[
            [
                "product_name",
                "current_inventory",
                "forecast_30_day",
                "demand_surge_level",
                "stockout_risk",
                "recommended_reorder_quantity",
                "ai_decision",
                "ai_decision_score",
                "ai_recommended_action",
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# TOP PRODUCTS TO BUY
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "TOP PRODUCTS TO BUY"
)

print(
    "=" * 70
)


top_buy = (
    buy_products
    .sort_values(
        "ai_decision_score",
        ascending=False,
    )
    .head(10)
)


if top_buy.empty:

    print(
        "\nNo purchase recommendations."
    )

else:

    print(
        top_buy[
            [
                "product_name",
                "current_inventory",
                "forecast_30_day",
                "recommended_reorder_quantity",
                "ai_decision",
                "ai_decision_score",
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# PRODUCTS TO REDUCE
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "PRODUCTS TO REDUCE"
)

print(
    "=" * 70
)


reduce_products = df[
    df[
        "ai_decision"
    ] == "REDUCE"
]


if reduce_products.empty:

    print(
        "\nNo products currently marked for reduction."
    )

else:

    print(
        reduce_products[
            [
                "product_name",
                "current_inventory",
                "forecast_30_day",
                "overstock_pressure_score",
                "ai_decision",
                "ai_recommended_action",
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# OUTPUT
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "OUTPUT FILE:"
)

print(
    OUTPUT_PATH
)

print(
    "=" * 70
)