import os

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INVENTORY_PATH = (
    "reports/inventory/inventory_analysis.csv"
)

FORECAST_PATH = (
    "reports/demand_model/future_demand_forecast.csv"
)

OUTPUT_PATH = (
    "reports/inventory/reorder_recommendations.csv"
)

# Default supplier lead time
DEFAULT_LEAD_TIME = 7

# Safety stock multiplier
SAFETY_STOCK_DAYS = 5


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    "reports/inventory",
    exist_ok=True,
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("AI INVENTORY INTELLIGENCE")
print("REORDER RECOMMENDATION ENGINE")
print("=" * 70)


print("\nLoading inventory analysis...")

inventory_df = pd.read_csv(
    INVENTORY_PATH
)

print(
    f"Inventory records: "
    f"{len(inventory_df):,}"
)


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
# CALCULATE FORECAST DEMAND
# ============================================================

forecast_summary = (
    forecast_df
    .groupby(
        "product_id"
    )
    .agg(
        forecast_7_day=(
            "predicted_demand",
            lambda x: x.head(7).sum(),
        ),
        forecast_14_day=(
            "predicted_demand",
            lambda x: x.head(14).sum(),
        ),
        forecast_30_day=(
            "predicted_demand",
            "sum",
        ),
        forecast_daily_average=(
            "predicted_demand",
            "mean",
        ),
    )
    .reset_index()
)


# ============================================================
# MERGE FORECAST
# ============================================================

df = inventory_df.merge(
    forecast_summary,
    on="product_id",
    how="left",
    suffixes=(
        "",
        "_forecast",
    ),
)


# ============================================================
# LEAD TIME
# ============================================================

# In a real system, lead time would come
# from supplier/vendor data.

# For our first version we use
# a realistic default of 7 days.

df["lead_time_days"] = (
    DEFAULT_LEAD_TIME
)


# ============================================================
# DAILY DEMAND
# ============================================================

df[
    "average_daily_demand"
] = (
    df[
        "forecast_daily_average"
    ]
)


# ============================================================
# LEAD TIME DEMAND
# ============================================================

df[
    "lead_time_demand"
] = (
    df["average_daily_demand"]
    * df["lead_time_days"]
)


# ============================================================
# DEMAND VARIABILITY
# ============================================================

# Estimate demand variability
# using historical rolling standard deviation.

historical_variability = (
    inventory_df[
        [
            "product_id",
            "sales_velocity",
        ]
    ]
    .copy()
)


# Use a conservative estimate of
# daily demand variability.

df[
    "demand_std"
] = (
    df[
        "average_daily_demand"
    ]
    * 0.20
)


# ============================================================
# SAFETY STOCK
# ============================================================

# Safety stock protects against
# unexpected demand increases.

df[
    "safety_stock"
] = (
    df["demand_std"]
    * np.sqrt(
        df["lead_time_days"]
    )
    * 1.65
)


df[
    "safety_stock"
] = (
    df[
        "safety_stock"
    ].clip(lower=0)
)


# ============================================================
# REORDER POINT
# ============================================================

df[
    "reorder_point"
] = (
    df["lead_time_demand"]
    + df["safety_stock"]
)


# ============================================================
# TARGET INVENTORY
# ============================================================

# We want enough inventory to cover
# lead time plus an additional safety period.

df[
    "target_inventory"
] = (
    df["average_daily_demand"]
    * (
        df["lead_time_days"]
        + SAFETY_STOCK_DAYS
    )
    + df["safety_stock"]
)


# ============================================================
# CURRENT INVENTORY
# ============================================================

df[
    "current_inventory"
] = (
    df["inventory_level"]
)


# ============================================================
# REORDER QUANTITY
# ============================================================

df[
    "recommended_reorder_quantity"
] = (
    df["target_inventory"]
    - df["current_inventory"]
)


df[
    "recommended_reorder_quantity"
] = (
    df[
        "recommended_reorder_quantity"
    ]
    .clip(lower=0)
)


# Round orders to whole units.

df[
    "recommended_reorder_quantity"
] = np.ceil(
    df[
        "recommended_reorder_quantity"
    ]
).astype(int)


# ============================================================
# REORDER REQUIRED
# ============================================================

df[
    "reorder_required"
] = np.where(
    df["current_inventory"]
    <= df["reorder_point"],
    "Yes",
    "No",
)


# ============================================================
# REORDER URGENCY
# ============================================================

def determine_urgency(row):

    days = row[
        "estimated_days_of_inventory"
    ]

    reorder = row[
        "reorder_required"
    ]

    if reorder == "No":
        return "None"

    if days <= 3:
        return "Critical"

    elif days <= 7:
        return "High"

    elif days <= 14:
        return "Medium"

    return "Low"


df[
    "reorder_urgency"
] = df.apply(
    determine_urgency,
    axis=1,
)


# ============================================================
# BUSINESS RECOMMENDATION
# ============================================================

def recommendation(row):

    urgency = row[
        "reorder_urgency"
    ]

    quantity = row[
        "recommended_reorder_quantity"
    ]

    overstock = row[
        "overstock_status"
    ]

    demand_trend = row[
        "demand_trend"
    ]

    if overstock == "Overstock":

        return (
            "Do not reorder — "
            "excess inventory"
        )

    if demand_trend == "High Surge":

        if quantity > 0:

            return (
                f"Urgently increase stock — "
                f"order {quantity} units"
            )

    if urgency == "Critical":

        return (
            f"URGENT — order "
            f"{quantity} units immediately"
        )

    if urgency == "High":

        return (
            f"Place reorder soon — "
            f"order {quantity} units"
        )

    if urgency == "Medium":

        return (
            f"Plan reorder — "
            f"order {quantity} units"
        )

    if urgency == "Low":

        return (
            f"Monitor inventory — "
            f"consider ordering {quantity} units"
        )

    return "No reorder required"


df[
    "business_recommendation"
] = df.apply(
    recommendation,
    axis=1,
)


# ============================================================
# INVENTORY COVERAGE AFTER REORDER
# ============================================================

df[
    "projected_inventory_after_reorder"
] = (
    df["current_inventory"]
    + df[
        "recommended_reorder_quantity"
    ]
)


df[
    "projected_days_after_reorder"
] = (
    df[
        "projected_inventory_after_reorder"
    ]
    / df[
        "average_daily_demand"
    ].replace(
        0,
        np.nan,
    )
)


df[
    "projected_days_after_reorder"
] = (
    df[
        "projected_days_after_reorder"
    ]
    .replace(
        [np.inf, -np.inf],
        np.nan,
    )
    .fillna(999)
)


# ============================================================
# REORDER COST ESTIMATE
# ============================================================

df[
    "estimated_reorder_value"
] = (
    df[
        "recommended_reorder_quantity"
    ]
    * df["price"]
)


# ============================================================
# OUTPUT COLUMNS
# ============================================================

output_columns = [
    "date",
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
    "demand_std",
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
    "demand_trend",
    "business_recommendation",
]


df = df[
    output_columns
]


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

print("\n" + "=" * 70)
print("REORDER ANALYSIS COMPLETE")
print("=" * 70)


print(
    f"\nProducts analyzed:"
    f" {len(df)}"
)


print("\nReorder required:")

print(
    df[
        "reorder_required"
    ].value_counts()
)


print("\nReorder urgency:")

print(
    df[
        "reorder_urgency"
    ].value_counts()
)


print(
    "\nTotal recommended reorder units:"
)

print(
    f"{df['recommended_reorder_quantity'].sum():,}"
)


print(
    "\nEstimated reorder value:"
)

print(
    f"₹{df['estimated_reorder_value'].sum():,.2f}"
)


# ============================================================
# CRITICAL REORDERS
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "URGENT REORDER RECOMMENDATIONS"
)

print(
    "=" * 70
)


urgent = df[
    df[
        "reorder_urgency"
    ].isin(
        [
            "Critical",
            "High",
        ]
    )
].copy()


if urgent.empty:

    print(
        "\nNo urgent reorders detected."
    )

else:

    print(
        urgent[
            [
                "product_name",
                "current_inventory",
                "average_daily_demand",
                "estimated_reorder_value",
                "reorder_urgency",
                "recommended_reorder_quantity",
                "business_recommendation",
            ]
        ]
        .sort_values(
            "reorder_urgency"
        )
        .to_string(
            index=False
        )
    )


# ============================================================
# TOP REORDER QUANTITIES
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "TOP 10 REORDER QUANTITIES"
)

print(
    "=" * 70
)


top_reorders = (
    df.sort_values(
        "recommended_reorder_quantity",
        ascending=False,
    )
    .head(10)
)


print(
    top_reorders[
        [
            "product_name",
            "current_inventory",
            "forecast_30_day",
            "reorder_point",
            "recommended_reorder_quantity",
            "reorder_required",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# COMPLETE
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    f"Recommendations saved to:"
    f"\n{OUTPUT_PATH}"
)

print("=" * 70)