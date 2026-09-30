import os

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/processed/inventory_features.csv"

FORECAST_PATH = (
    "reports/demand_model/future_demand_forecast.csv"
)

OUTPUT_PATH = (
    "reports/inventory/inventory_analysis.csv"
)

os.makedirs(
    "reports/inventory",
    exist_ok=True,
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("AI INVENTORY INTELLIGENCE")
print("INVENTORY ANALYSIS ENGINE")
print("=" * 70)

print("\nLoading historical data...")

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

print(
    f"Historical records: {len(df):,}"
)


print("\nLoading demand forecasts...")

forecast_df = pd.read_csv(
    FORECAST_PATH,
    parse_dates=["date"],
)

print(
    f"Forecast records: {len(forecast_df):,}"
)


# ============================================================
# GET LATEST PRODUCT INFORMATION
# ============================================================

latest_data = (
    df.sort_values("date")
    .groupby("product_id")
    .tail(1)
    .copy()
)


# ============================================================
# CALCULATE FORECAST DEMAND
# ============================================================

forecast_summary = (
    forecast_df
    .groupby(
        [
            "product_id",
            "product_name",
            "category",
        ]
    )
    .agg(
        forecast_7_day_demand=(
            "predicted_demand",
            lambda x: x.head(7).sum(),
        ),
        forecast_14_day_demand=(
            "predicted_demand",
            lambda x: x.head(14).sum(),
        ),
        forecast_30_day_demand=(
            "predicted_demand",
            "sum",
        ),
        average_daily_forecast=(
            "predicted_demand",
            "mean",
        ),
    )
    .reset_index()
)


# ============================================================
# MERGE
# ============================================================

inventory_df = latest_data.merge(
    forecast_summary,
    on=[
        "product_id",
        "product_name",
        "category",
    ],
    how="left",
)


# ============================================================
# DAYS OF INVENTORY
# ============================================================

inventory_df[
    "estimated_days_of_inventory"
] = (
    inventory_df["inventory_level"]
    / inventory_df[
        "average_daily_forecast"
    ].replace(0, np.nan)
)


inventory_df[
    "estimated_days_of_inventory"
] = (
    inventory_df[
        "estimated_days_of_inventory"
    ]
    .replace(
        [np.inf, -np.inf],
        np.nan,
    )
    .fillna(999)
)


# ============================================================
# INVENTORY COVERAGE
# ============================================================

inventory_df[
    "inventory_coverage_ratio"
] = (
    inventory_df["inventory_level"]
    / inventory_df[
        "forecast_30_day_demand"
    ].replace(0, np.nan)
)


inventory_df[
    "inventory_coverage_ratio"
] = (
    inventory_df[
        "inventory_coverage_ratio"
    ]
    .replace(
        [np.inf, -np.inf],
        np.nan,
    )
    .fillna(999)
)


# ============================================================
# STOCKOUT RISK
# ============================================================

def calculate_stockout_risk(days):
    """Determine stockout risk."""

    if days <= 3:
        return "Critical"

    elif days <= 7:
        return "High"

    elif days <= 14:
        return "Medium"

    else:
        return "Low"


inventory_df[
    "stockout_risk"
] = inventory_df[
    "estimated_days_of_inventory"
].apply(
    calculate_stockout_risk
)


# ============================================================
# OVERSTOCK DETECTION
# ============================================================

def detect_overstock(row):
    """
    Detect excess inventory based on
    predicted 30-day demand.
    """

    inventory = row[
        "inventory_level"
    ]

    demand = row[
        "forecast_30_day_demand"
    ]

    if demand <= 0:
        return "Overstock"

    coverage = (
        inventory / demand
    )

    if coverage >= 2.0:
        return "Overstock"

    elif coverage >= 1.5:
        return "Potential Overstock"

    else:
        return "Normal"


inventory_df[
    "overstock_status"
] = inventory_df.apply(
    detect_overstock,
    axis=1,
)


# ============================================================
# DEMAND SURGE DETECTION
# ============================================================

def detect_demand_surge(row):
    """
    Compare recent demand with
    long-term demand.
    """

    growth = row.get(
        "demand_growth",
        0,
    )

    if growth >= 0.30:
        return "High Surge"

    elif growth >= 0.15:
        return "Moderate Surge"

    elif growth <= -0.20:
        return "Demand Decline"

    else:
        return "Stable"


inventory_df[
    "demand_trend"
] = inventory_df.apply(
    detect_demand_surge,
    axis=1,
)


# ============================================================
# INVENTORY STATUS
# ============================================================

def determine_status(row):
    """
    Determine overall inventory status.
    """

    stockout = row[
        "stockout_risk"
    ]

    overstock = row[
        "overstock_status"
    ]

    surge = row[
        "demand_trend"
    ]

    if stockout == "Critical":
        return "Critical Stockout Risk"

    if stockout == "High":
        return "Stockout Risk"

    if surge == "High Surge":
        return "Demand Surge"

    if overstock == "Overstock":
        return "Overstock"

    if overstock == "Potential Overstock":
        return "Potential Overstock"

    if stockout == "Medium":
        return "Low Stock"

    return "Healthy"


inventory_df[
    "inventory_status"
] = inventory_df.apply(
    determine_status,
    axis=1,
)


# ============================================================
# INVENTORY HEALTH SCORE
# ============================================================

def calculate_health_score(row):
    """
    Calculate inventory health score from 0 to 100.
    """

    score = 100

    # --------------------------------------------------------
    # Stockout penalty
    # --------------------------------------------------------

    stockout = row[
        "stockout_risk"
    ]

    if stockout == "Critical":
        score -= 50

    elif stockout == "High":
        score -= 35

    elif stockout == "Medium":
        score -= 15

    # --------------------------------------------------------
    # Overstock penalty
    # --------------------------------------------------------

    overstock = row[
        "overstock_status"
    ]

    if overstock == "Overstock":
        score -= 30

    elif overstock == "Potential Overstock":
        score -= 15

    # --------------------------------------------------------
    # Demand surge adjustment
    # --------------------------------------------------------

    surge = row[
        "demand_trend"
    ]

    if surge == "High Surge":
        score -= 10

    elif surge == "Moderate Surge":
        score -= 5

    # --------------------------------------------------------
    # Keep between 0 and 100
    # --------------------------------------------------------

    return max(
        0,
        min(
            100,
            score,
        ),
    )


inventory_df[
    "inventory_health_score"
] = inventory_df.apply(
    calculate_health_score,
    axis=1,
)


# ============================================================
# HEALTH CATEGORY
# ============================================================

def health_category(score):

    if score >= 80:
        return "Excellent"

    elif score >= 60:
        return "Healthy"

    elif score >= 40:
        return "Needs Attention"

    else:
        return "Critical"


inventory_df[
    "inventory_health"
] = inventory_df[
    "inventory_health_score"
].apply(
    health_category
)


# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

output_columns = [
    "date",
    "product_id",
    "product_name",
    "category",
    "price",
    "inventory_level",
    "sales_velocity",
    "demand_growth",
    "forecast_7_day_demand",
    "forecast_14_day_demand",
    "forecast_30_day_demand",
    "average_daily_forecast",
    "estimated_days_of_inventory",
    "inventory_coverage_ratio",
    "stockout_risk",
    "overstock_status",
    "demand_trend",
    "inventory_status",
    "inventory_health_score",
    "inventory_health",
]


inventory_df = inventory_df[
    output_columns
]


# ============================================================
# SAVE
# ============================================================

inventory_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("INVENTORY ANALYSIS COMPLETE")
print("=" * 70)

print(
    f"\nProducts analyzed:"
    f" {len(inventory_df)}"
)


print("\nInventory status:")

print(
    inventory_df[
        "inventory_status"
    ].value_counts()
)


print("\nStockout risk:")

print(
    inventory_df[
        "stockout_risk"
    ].value_counts()
)


print("\nOverstock status:")

print(
    inventory_df[
        "overstock_status"
    ].value_counts()
)


print("\nDemand trend:")

print(
    inventory_df[
        "demand_trend"
    ].value_counts()
)


print("\nAverage inventory health score:")

print(
    f"{inventory_df['inventory_health_score'].mean():.2f}/100"
)


# ============================================================
# CRITICAL PRODUCTS
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "PRODUCTS REQUIRING ATTENTION"
)

print(
    "=" * 70
)


attention = inventory_df[
    inventory_df[
        "inventory_status"
    ].isin(
        [
            "Critical Stockout Risk",
            "Stockout Risk",
            "Demand Surge",
            "Overstock",
        ]
    )
].copy()


if attention.empty:

    print(
        "\nNo critical inventory issues detected."
    )

else:

    print(
        attention[
            [
                "product_name",
                "inventory_level",
                "forecast_30_day_demand",
                "estimated_days_of_inventory",
                "inventory_status",
                "inventory_health_score",
            ]
        ]
        .sort_values(
            "inventory_health_score"
        )
        .to_string(
            index=False
        )
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)

print(
    f"Saved to:"
    f" {OUTPUT_PATH}"
)

print("=" * 70)