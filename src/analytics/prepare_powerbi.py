from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "inventory"
    / "ai_inventory_decisions.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "powerbi"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "inventory_powerbi_master.csv"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("AI INVENTORY INTELLIGENCE")
print("POWER BI DATA PREPARATION")
print("=" * 70)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD AI DECISION DATA
# ============================================================

print("\nLoading AI inventory decisions...")


if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )


df = pd.read_csv(
    INPUT_FILE
)


print(
    f"Records loaded: {len(df):,}"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def ensure_numeric(
    column,
    default=0
):

    if column not in df.columns:

        df[column] = default

    df[column] = (
        pd.to_numeric(
            df[column],
            errors="coerce"
        )
        .fillna(default)
    )


# ============================================================
# CREATE / RECOVER AVERAGE DAILY DEMAND
# ============================================================

# The AI decision file may not contain
# average_daily_demand.
#
# Therefore we derive it from the available
# demand columns.

if "average_daily_demand" not in df.columns:

    if "forecast_daily_average" in df.columns:

        df["average_daily_demand"] = (
            pd.to_numeric(
                df[
                    "forecast_daily_average"
                ],
                errors="coerce"
            )
            .fillna(0)
        )

    elif "historical_daily_demand" in df.columns:

        df["average_daily_demand"] = (
            pd.to_numeric(
                df[
                    "historical_daily_demand"
                ],
                errors="coerce"
            )
            .fillna(0)
        )

    elif "forecast_30_day" in df.columns:

        df["average_daily_demand"] = (
            pd.to_numeric(
                df[
                    "forecast_30_day"
                ],
                errors="coerce"
            )
            .fillna(0)
            / 30
        )

    else:

        df["average_daily_demand"] = 0


# ============================================================
# ENSURE REQUIRED NUMERIC COLUMNS EXIST
# ============================================================

numeric_columns = [

    "price",

    "current_inventory",

    "average_daily_demand",

    "forecast_7_day",

    "forecast_14_day",

    "forecast_30_day",

    "forecast_daily_average",

    "historical_daily_demand",

    "historical_demand_growth",

    "lead_time_days",

    "lead_time_demand",

    "safety_stock",

    "reorder_point",

    "estimated_days_of_inventory",

    "projected_days_after_reorder",

    "inventory_health_score",

    "demand_surge_percentage",

    "demand_risk_score",

    "recommended_reorder_quantity",

    "recommended_purchase_value",

    "overstock_pressure_score",

    "inventory_pressure_score",

    "demand_pressure_score",

    "stockout_pressure_score",

    "ai_decision_score",
]


for column in numeric_columns:

    ensure_numeric(
        column
    )


# ============================================================
# DATE
# ============================================================

df["report_date"] = (
    pd.Timestamp
    .today()
    .normalize()
)


# ============================================================
# INVENTORY COVERAGE RATIO
# ============================================================

df[
    "inventory_coverage_ratio"
] = 0.0


valid_demand = (
    df[
        "forecast_30_day"
    ] > 0
)


df.loc[
    valid_demand,
    "inventory_coverage_ratio"
] = (
    df.loc[
        valid_demand,
        "current_inventory"
    ]
    /
    df.loc[
        valid_demand,
        "forecast_30_day"
    ]
)


# ============================================================
# DEMAND GROWTH CATEGORY
# ============================================================

def classify_growth(
    value
):

    if value >= 30:

        return "High Growth"

    elif value >= 10:

        return "Moderate Growth"

    elif value >= 0:

        return "Stable"

    elif value >= -10:

        return "Moderate Decline"

    return "High Decline"


df[
    "demand_growth_category"
] = (
    df[
        "historical_demand_growth"
    ]
    .apply(
        classify_growth
    )
)


# ============================================================
# INVENTORY RISK CATEGORY
# ============================================================

def classify_inventory_risk(
    row
):

    stockout = row.get(
        "stockout_risk",
        "Unknown"
    )

    decision = row.get(
        "ai_decision",
        "HOLD"
    )

    if stockout == "Critical":

        return "Critical"

    if stockout == "High":

        return "High"

    if decision == "REDUCE":

        return "Overstock"

    if stockout == "Medium":

        return "Medium"

    return "Low"


df[
    "inventory_risk_category"
] = df.apply(
    classify_inventory_risk,
    axis=1
)


# ============================================================
# REORDER VALUE CATEGORY
# ============================================================

def classify_reorder_value(
    value
):

    if value >= 100000:

        return "Very High"

    elif value >= 50000:

        return "High"

    elif value >= 10000:

        return "Medium"

    elif value > 0:

        return "Low"

    return "None"


df[
    "reorder_value_category"
] = (
    df[
        "recommended_purchase_value"
    ]
    .apply(
        classify_reorder_value
    )
)


# ============================================================
# AI ACTION CATEGORY
# ============================================================

def action_category(
    decision
):

    if decision in [
        "BUY",
        "BUY NOW",
        "INCREASE STOCK",
    ]:

        return "Increase Inventory"

    elif decision == "REDUCE":

        return "Reduce Inventory"

    elif decision == "MONITOR":

        return "Monitor"

    return "No Action"


df[
    "action_category"
] = (
    df[
        "ai_decision"
    ]
    .apply(
        action_category
    )
)


# ============================================================
# STOCKOUT FLAG
# ============================================================

df[
    "stockout_flag"
] = (
    df[
        "stockout_risk"
    ]
    .isin(
        [
            "Critical",
            "High",
        ]
    )
)


# ============================================================
# DEMAND SURGE FLAG
# ============================================================

df[
    "demand_surge_flag"
] = (
    df[
        "demand_surge_level"
    ]
    .isin(
        [
            "High Surge",
            "Extreme Surge",
        ]
    )
)


# ============================================================
# OVERSTOCK FLAG
# ============================================================

df[
    "overstock_flag"
] = (
    df[
        "ai_decision"
    ]
    == "REDUCE"
)


# ============================================================
# ROUND NUMERIC VALUES
# ============================================================

round_columns = [

    "price",

    "average_daily_demand",

    "forecast_7_day",

    "forecast_14_day",

    "forecast_30_day",

    "forecast_daily_average",

    "historical_daily_demand",

    "historical_demand_growth",

    "lead_time_demand",

    "safety_stock",

    "reorder_point",

    "estimated_days_of_inventory",

    "projected_days_after_reorder",

    "inventory_health_score",

    "demand_surge_percentage",

    "demand_risk_score",

    "recommended_purchase_value",

    "overstock_pressure_score",

    "inventory_pressure_score",

    "demand_pressure_score",

    "stockout_pressure_score",

    "ai_decision_score",

    "inventory_coverage_ratio",
]


for column in round_columns:

    if column in df.columns:

        df[column] = (
            pd.to_numeric(
                df[column],
                errors="coerce"
            )
            .fillna(0)
            .round(2)
        )


# ============================================================
# INTEGER COLUMNS
# ============================================================

integer_columns = [

    "current_inventory",

    "recommended_reorder_quantity",

]


for column in integer_columns:

    if column in df.columns:

        df[column] = (
            pd.to_numeric(
                df[column],
                errors="coerce"
            )
            .fillna(0)
            .round()
            .astype(int)
        )


# ============================================================
# POWER BI COLUMN ORDER
# ============================================================

powerbi_columns = [

    "report_date",

    "product_id",

    "product_name",

    "category",

    "price",

    "current_inventory",

    "average_daily_demand",

    "forecast_7_day",

    "forecast_14_day",

    "forecast_30_day",

    "forecast_daily_average",

    "historical_daily_demand",

    "historical_demand_growth",

    "demand_growth_category",

    "lead_time_days",

    "lead_time_demand",

    "safety_stock",

    "reorder_point",

    "estimated_days_of_inventory",

    "projected_days_after_reorder",

    "inventory_status",

    "inventory_health_score",

    "inventory_risk_category",

    "stockout_risk",

    "stockout_flag",

    "demand_surge_level",

    "demand_surge_percentage",

    "demand_surge_flag",

    "demand_priority",

    "demand_risk_score",

    "recommended_reorder_quantity",

    "recommended_purchase_value",

    "reorder_value_category",

    "overstock_pressure_score",

    "overstock_flag",

    "inventory_pressure_score",

    "demand_pressure_score",

    "stockout_pressure_score",

    "ai_decision_score",

    "ai_decision",

    "action_category",

    "decision_priority",

    "decision_confidence",

    "ai_recommended_action",

    "inventory_coverage_ratio",
]


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

missing_columns = [

    column

    for column in powerbi_columns

    if column not in df.columns

]


if missing_columns:

    print(
        "\nMissing columns detected:"
    )

    print(
        missing_columns
    )

    raise ValueError(
        "Power BI dataset cannot be created "
        "because required columns are missing."
    )


# ============================================================
# SELECT FINAL COLUMNS
# ============================================================

df = df[
    powerbi_columns
]


# ============================================================
# SORT
# ============================================================

priority_order = {

    "CRITICAL": 0,

    "HIGH": 1,

    "MEDIUM": 2,

    "LOW": 3,

}


df[
    "_priority_sort"
] = (
    df[
        "decision_priority"
    ]
    .map(
        priority_order
    )
    .fillna(4)
)


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
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "POWER BI DATASET CREATED"
)

print(
    "=" * 70
)

print(
    f"\nRows: {len(df):,}"
)

print(
    f"Columns: {len(df.columns):,}"
)


print(
    "\nAI decisions:"
)

print(
    df[
        "ai_decision"
    ].value_counts()
)


print(
    "\nStockout risk:"
)

print(
    df[
        "stockout_risk"
    ].value_counts()
)


print(
    "\nDemand surge:"
)

print(
    df[
        "demand_surge_level"
    ].value_counts()
)


print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)


print(
    "\nPower BI preparation complete."
)

print(
    "=" * 70
)