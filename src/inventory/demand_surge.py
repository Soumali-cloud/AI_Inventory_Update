import os

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

HISTORICAL_PATH = (
    "data/processed/inventory_features.csv"
)

INVENTORY_PATH = (
    "reports/inventory/reorder_recommendations.csv"
)

FORECAST_PATH = (
    "reports/demand_model/future_demand_forecast.csv"
)

OUTPUT_PATH = (
    "reports/inventory/demand_surge_analysis.csv"
)


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
print("DEMAND SURGE DETECTION")
print("=" * 70)


print("\nLoading historical data...")

historical_df = pd.read_csv(
    HISTORICAL_PATH,
    parse_dates=["date"],
)

print(
    f"Historical records: "
    f"{len(historical_df):,}"
)


print("\nLoading inventory data...")

inventory_df = pd.read_csv(
    INVENTORY_PATH
)

print(
    f"Inventory records: "
    f"{len(inventory_df):,}"
)


print("\nLoading forecast data...")

forecast_df = pd.read_csv(
    FORECAST_PATH,
    parse_dates=["date"],
)

print(
    f"Forecast records: "
    f"{len(forecast_df):,}"
)


# ============================================================
# GET LATEST HISTORICAL RECORD PER PRODUCT
# ============================================================

print(
    "\nExtracting latest historical demand information..."
)


latest_history = (
    historical_df
    .sort_values("date")
    .groupby("product_id")
    .tail(1)
    .copy()
)


# ============================================================
# SELECT HISTORICAL DEMAND FEATURES
# ============================================================

historical_features = latest_history[
    [
        "product_id",
        "sales_velocity",
        "demand_growth",
        "rolling_mean_7",
        "rolling_mean_30",
        "units_sold",
    ]
].copy()


historical_features = (
    historical_features
    .rename(
        columns={
            "sales_velocity":
                "historical_daily_demand",

            "demand_growth":
                "historical_demand_growth",

            "rolling_mean_7":
                "historical_7_day_average",

            "rolling_mean_30":
                "historical_30_day_average",

            "units_sold":
                "last_day_units_sold",
        }
    )
)


# ============================================================
# FORECAST SUMMARY
# ============================================================

print(
    "\nCalculating future demand statistics..."
)


forecast_df = forecast_df.sort_values(
    [
        "product_id",
        "date",
    ]
)


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

        peak_forecast=(
            "predicted_demand",
            "max",
        ),

        minimum_forecast=(
            "predicted_demand",
            "min",
        ),
    )
    .reset_index()
)


# ============================================================
# MERGE ALL DATA
# ============================================================

print(
    "\nCombining historical, inventory and forecast data..."
)


df = inventory_df.merge(
    historical_features,
    on="product_id",
    how="left",
)


df = df.merge(
    forecast_summary,
    on=[
        "product_id",
        "product_name",
        "category",
    ],
    how="left",
    suffixes=(
        "",
        "_forecast",
    ),
)


# ============================================================
# HANDLE NUMERIC VALUES
# ============================================================

numeric_columns = [
    "historical_daily_demand",
    "historical_demand_growth",
    "historical_7_day_average",
    "historical_30_day_average",
    "last_day_units_sold",
    "forecast_7_day",
    "forecast_14_day",
    "forecast_30_day",
    "forecast_daily_average",
    "peak_forecast",
    "minimum_forecast",
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
# HISTORICAL DEMAND GROWTH
# ============================================================

df[
    "historical_demand_growth"
] = (
    df[
        "historical_demand_growth"
    ].clip(
        lower=-1,
        upper=3,
    )
)


# ============================================================
# FORECAST VS HISTORICAL DEMAND
# ============================================================

df[
    "forecast_vs_historical_change"
] = np.where(
    df["historical_daily_demand"] > 0,

    (
        (
            df["forecast_daily_average"]
            - df["historical_daily_demand"]
        )
        / df["historical_daily_demand"]
    ),

    0,
)


df[
    "forecast_vs_historical_change"
] = (
    df[
        "forecast_vs_historical_change"
    ]
    .replace(
        [np.inf, -np.inf],
        np.nan,
    )
    .fillna(0)
    .clip(
        lower=-1,
        upper=5,
    )
)


# ============================================================
# DEMAND SURGE SCORE
# ============================================================

# 60% historical demand growth
# 40% future forecast increase

df[
    "demand_surge_score"
] = (
    (
        df[
            "historical_demand_growth"
        ]
        * 0.60
    )
    +
    (
        df[
            "forecast_vs_historical_change"
        ]
        * 0.40
    )
)


# ============================================================
# DEMAND SURGE PERCENTAGE
# ============================================================

df[
    "demand_surge_percentage"
] = (
    df[
        "demand_surge_score"
    ]
    * 100
)


# ============================================================
# DEMAND SURGE CLASSIFICATION
# ============================================================

def classify_surge(score):

    if score >= 0.50:

        return "Extreme Surge"

    elif score >= 0.30:

        return "High Surge"

    elif score >= 0.15:

        return "Moderate Surge"

    elif score <= -0.20:

        return "Demand Decline"

    else:

        return "Stable"


df[
    "demand_surge_level"
] = (
    df[
        "demand_surge_score"
    ]
    .apply(
        classify_surge
    )
)


# ============================================================
# STOCKOUT RISK
# ============================================================

def calculate_stockout_risk(row):

    inventory = row[
        "current_inventory"
    ]

    daily_demand = row[
        "forecast_daily_average"
    ]

    if daily_demand <= 0:

        return "Low"

    days = (
        inventory
        / daily_demand
    )

    if days <= 3:

        return "Critical"

    elif days <= 7:

        return "High"

    elif days <= 14:

        return "Medium"

    else:

        return "Low"


df[
    "stockout_risk"
] = df.apply(
    calculate_stockout_risk,
    axis=1,
)


# ============================================================
# ESTIMATED DAYS OF INVENTORY
# ============================================================

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
# DEMAND PRIORITY
# ============================================================

def calculate_priority(row):

    surge = row[
        "demand_surge_level"
    ]

    stockout = row[
        "stockout_risk"
    ]

    if (
        surge == "Extreme Surge"
        and stockout in [
            "Critical",
            "High",
        ]
    ):

        return "CRITICAL"

    if surge == "Extreme Surge":

        return "VERY HIGH"

    if (
        surge == "High Surge"
        and stockout in [
            "Critical",
            "High",
        ]
    ):

        return "VERY HIGH"

    if surge == "High Surge":

        return "HIGH"

    if surge == "Moderate Surge":

        return "MEDIUM"

    if surge == "Demand Decline":

        return "LOW"

    return "NORMAL"


df[
    "demand_priority"
] = df.apply(
    calculate_priority,
    axis=1,
)


# ============================================================
# DEMAND RISK SCORE
# ============================================================

def calculate_risk_score(row):

    score = 0

    surge = row[
        "demand_surge_level"
    ]

    stockout = row[
        "stockout_risk"
    ]

    # Demand component

    if surge == "Extreme Surge":

        score += 50

    elif surge == "High Surge":

        score += 35

    elif surge == "Moderate Surge":

        score += 20

    # Stockout component

    if stockout == "Critical":

        score += 50

    elif stockout == "High":

        score += 35

    elif stockout == "Medium":

        score += 15

    return min(
        score,
        100,
    )


df[
    "demand_risk_score"
] = df.apply(
    calculate_risk_score,
    axis=1,
)


# ============================================================
# BUSINESS ACTION
# ============================================================

def generate_action(row):

    surge = row[
        "demand_surge_level"
    ]

    priority = row[
        "demand_priority"
    ]

    stockout = row[
        "stockout_risk"
    ]

    reorder_quantity = int(
        max(
            0,
            row[
                "recommended_reorder_quantity"
            ],
        )
    )

    if priority == "CRITICAL":

        return (
            "URGENT: Demand surge with "
            f"stockout risk — order "
            f"{reorder_quantity} units"
        )

    if surge == "Extreme Surge":

        return (
            "Extreme demand surge — "
            "increase inventory immediately"
        )

    if surge == "High Surge":

        return (
            "High demand surge — "
            "increase replenishment"
        )

    if surge == "Moderate Surge":

        return (
            "Moderate demand increase — "
            "monitor and prepare inventory"
        )

    if stockout == "Critical":

        return (
            f"Critical stockout risk — "
            f"order {reorder_quantity} units"
        )

    if stockout == "High":

        return (
            f"High stockout risk — "
            f"place reorder of {reorder_quantity} units"
        )

    if surge == "Demand Decline":

        return (
            "Demand declining — "
            "reduce replenishment"
        )

    return (
        "Demand stable — "
        "continue normal inventory planning"
    )


df[
    "recommended_action"
] = df.apply(
    generate_action,
    axis=1,
)


# ============================================================
# OUTPUT COLUMNS
# ============================================================

output_columns = [
    "product_id",
    "product_name",
    "category",

    "current_inventory",

    "historical_daily_demand",
    "historical_7_day_average",
    "historical_30_day_average",
    "last_day_units_sold",

    "historical_demand_growth",

    "forecast_7_day",
    "forecast_14_day",
    "forecast_30_day",

    "forecast_daily_average",
    "peak_forecast",
    "minimum_forecast",

    "forecast_vs_historical_change",

    "demand_surge_score",
    "demand_surge_percentage",

    "demand_surge_level",

    "estimated_days_of_inventory",

    "stockout_risk",

    "demand_priority",

    "demand_risk_score",

    "recommended_reorder_quantity",

    "recommended_action",
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

print(
    "\n" + "=" * 70
)

print(
    "DEMAND SURGE ANALYSIS COMPLETE"
)

print(
    "=" * 70
)


print(
    f"\nProducts analyzed: "
    f"{len(df)}"
)


# ============================================================
# SURGE LEVEL SUMMARY
# ============================================================

print(
    "\nDemand surge levels:"
)

print(
    df[
        "demand_surge_level"
    ].value_counts()
)


# ============================================================
# PRIORITY SUMMARY
# ============================================================

print(
    "\nDemand priorities:"
)

print(
    df[
        "demand_priority"
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
# TOP SURGE PRODUCTS
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "TOP DEMAND SURGE PRODUCTS"
)

print(
    "=" * 70
)


top_surge = (
    df
    .sort_values(
        "demand_surge_percentage",
        ascending=False,
    )
    .head(10)
)


print(
    top_surge[
        [
            "product_name",
            "historical_daily_demand",
            "forecast_daily_average",
            "historical_demand_growth",
            "forecast_vs_historical_change",
            "demand_surge_percentage",
            "demand_surge_level",
            "demand_priority",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# CRITICAL PRODUCTS
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "CRITICAL DEMAND RISKS"
)

print(
    "=" * 70
)


critical = df[
    df[
        "demand_priority"
    ].isin(
        [
            "CRITICAL",
            "VERY HIGH",
            "HIGH",
        ]
    )
].sort_values(
    "demand_risk_score",
    ascending=False,
)


if critical.empty:

    print(
        "\nNo critical demand risks detected."
    )

else:

    print(
        critical[
            [
                "product_name",
                "demand_surge_level",
                "stockout_risk",
                "demand_risk_score",
                "recommended_reorder_quantity",
                "recommended_action",
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# SAVE CONFIRMATION
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