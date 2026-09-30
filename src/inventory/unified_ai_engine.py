"""
AI INVENTORY INTELLIGENCE
UNIFIED AI BUSINESS DECISION ENGINE

Combines:
1. Inventory intelligence
2. Demand signals
3. Stockout risk
4. Demand surge
5. Price prediction

Output:
data/processed/unified_ai_decisions.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"

INVENTORY_FILE = DATA_DIR / "inventory_features.csv"
PRICE_FILE = DATA_DIR / "price_predictions.csv"

OUTPUT_FILE = DATA_DIR / "unified_ai_decisions.csv"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(df, candidates):
    """
    Find the first matching column from a list of candidates.
    """

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def numeric_value(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        number = float(value)

        if np.isfinite(number):
            return number

    except (TypeError, ValueError):
        pass

    return default


def clean_numeric_series(series):
    """
    Convert a pandas series to numeric values.
    """

    return pd.to_numeric(
        series,
        errors="coerce",
    )


# ============================================================
# LOAD INVENTORY DATA
# ============================================================

def load_inventory_data():

    if not INVENTORY_FILE.exists():

        raise FileNotFoundError(
            f"Inventory file not found:\n{INVENTORY_FILE}"
        )

    df = pd.read_csv(INVENTORY_FILE)

    if df.empty:

        raise ValueError(
            "inventory_features.csv is empty."
        )

    print()
    print("Inventory dataset loaded successfully.")

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # Verify required product identifier
    # --------------------------------------------------------

    product_column = find_column(
        df,
        [
            "product_id",
            "product",
            "sku",
            "id",
        ],
    )

    if product_column is None:

        raise ValueError(
            "Could not find product_id column "
            "in inventory_features.csv."
        )

    if product_column != "product_id":

        df = df.rename(
            columns={
                product_column: "product_id"
            }
        )

    df["product_id"] = (
        df["product_id"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Product name
    # --------------------------------------------------------

    product_name_column = find_column(
        df,
        [
            "product_name",
            "product",
            "name",
        ],
    )

    if product_name_column:

        df["product_name"] = (
            df[product_name_column]
            .astype(str)
        )

    else:

        df["product_name"] = (
            df["product_id"]
        )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    category_column = find_column(
        df,
        [
            "category",
            "product_category",
        ],
    )

    if category_column:

        df["category"] = (
            df[category_column]
            .astype(str)
        )

    else:

        df["category"] = "Unknown"

    return df


# ============================================================
# LOAD PRICE PREDICTIONS
# ============================================================

def load_price_data():

    if not PRICE_FILE.exists():

        print()
        print(
            "WARNING: price_predictions.csv not found."
        )

        print(
            "The unified engine will continue "
            "without price predictions."
        )

        return pd.DataFrame()

    df = pd.read_csv(PRICE_FILE)

    if df.empty:

        print(
            "WARNING: price_predictions.csv is empty."
        )

        return pd.DataFrame()

    product_column = find_column(
        df,
        [
            "product_id",
            "product",
            "sku",
            "id",
        ],
    )

    if product_column is None:

        print(
            "WARNING: No product identifier found "
            "in price predictions."
        )

        return pd.DataFrame()

    if product_column != "product_id":

        df = df.rename(
            columns={
                product_column: "product_id"
            }
        )

    df["product_id"] = (
        df["product_id"]
        .astype(str)
        .str.strip()
    )

    print()
    print(
        f"Price prediction records: {len(df)}"
    )

    return df


# ============================================================
# BUILD PRICE SUMMARY
# ============================================================

def build_price_summary(price_df):

    if price_df.empty:

        return pd.DataFrame(
            columns=[
                "product_id",
                "predicted_price",
                "price_change_percent",
            ]
        )

    predicted_column = find_column(
        price_df,
        [
            "predicted_price",
            "predicted_price_30d",
            "forecast_price",
            "price_prediction",
        ],
    )

    if predicted_column is None:

        print(
            "WARNING: Could not find predicted price column."
        )

        return pd.DataFrame(
            columns=[
                "product_id",
                "predicted_price",
                "price_change_percent",
            ]
        )

    price_df[predicted_column] = clean_numeric_series(
        price_df[predicted_column]
    )

    # --------------------------------------------------------
    # Detect current/historical price
    # --------------------------------------------------------

    current_column = find_column(
        price_df,
        [
            "current_price",
            "price",
            "actual_price",
            "historical_price",
        ],
    )

    if current_column:

        price_df[current_column] = clean_numeric_series(
            price_df[current_column]
        )

    # --------------------------------------------------------
    # Sort by date if available
    # --------------------------------------------------------

    date_column = find_column(
        price_df,
        [
            "date",
            "prediction_date",
            "forecast_date",
            "future_date",
            "ds",
        ],
    )

    if date_column:

        price_df["_sort_date"] = pd.to_datetime(
            price_df[date_column],
            errors="coerce",
        )

        price_df = price_df.sort_values(
            [
                "product_id",
                "_sort_date",
            ]
        )

    # --------------------------------------------------------
    # Create one summary row per product
    # --------------------------------------------------------

    summary_rows = []

    for product_id, group in price_df.groupby(
        "product_id"
    ):

        group = group.copy()

        predictions = (
            group[predicted_column]
            .dropna()
            .tolist()
        )

        if not predictions:
            continue

        final_prediction = float(
            predictions[-1]
        )

        # ----------------------------------------------------
        # Current price
        # ----------------------------------------------------

        current_price = None

        if current_column:

            current_values = (
                group[current_column]
                .dropna()
                .tolist()
            )

            if current_values:

                current_price = float(
                    current_values[-1]
                )

        # ----------------------------------------------------
        # If current price isn't available from the
        # prediction dataset, leave it as None.
        # The inventory dataset will provide the actual price.
        # ----------------------------------------------------

        summary_rows.append(
            {
                "product_id": str(product_id),
                "price_prediction": final_prediction,
                "price_prediction_start": float(
                    predictions[0]
                ),
                "price_current_from_prediction": current_price,
            }
        )

    return pd.DataFrame(summary_rows)


# ============================================================
# PREPARE INVENTORY SIGNALS
# ============================================================

def prepare_inventory_signals(df):

    # --------------------------------------------------------
    # Current inventory
    # --------------------------------------------------------

    inventory_column = find_column(
        df,
        [
            "inventory_level",
            "current_inventory",
            "inventory",
            "stock",
        ],
    )

    if inventory_column:

        df["current_inventory"] = clean_numeric_series(
            df[inventory_column]
        )

    else:

        df["current_inventory"] = 0

    # --------------------------------------------------------
    # Demand
    #
    # Your dataset already has sales_velocity.
    # This is the best direct demand signal available.
    # --------------------------------------------------------

    demand_column = find_column(
        df,
        [
            "sales_velocity",
            "average_daily_demand",
            "rolling_mean_7",
            "units_sold",
        ],
    )

    if demand_column:

        df["average_daily_demand"] = clean_numeric_series(
            df[demand_column]
        )

    else:

        df["average_daily_demand"] = 0

    # --------------------------------------------------------
    # Days of inventory
    # --------------------------------------------------------

    days_column = find_column(
        df,
        [
            "days_of_inventory",
            "estimated_days_of_inventory",
        ],
    )

    if days_column:

        df["estimated_days_of_inventory"] = (
            clean_numeric_series(
                df[days_column]
            )
        )

    else:

        demand = df[
            "average_daily_demand"
        ].replace(
            0,
            np.nan,
        )

        df["estimated_days_of_inventory"] = (
            df["current_inventory"]
            / demand
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

    # --------------------------------------------------------
    # Demand growth
    # --------------------------------------------------------

    growth_column = find_column(
        df,
        [
            "demand_growth",
            "sales_growth",
            "growth",
        ],
    )

    if growth_column:

        df["demand_growth_percent"] = (
            clean_numeric_series(
                df[growth_column]
            )
        )

    else:

        df["demand_growth_percent"] = 0

    # --------------------------------------------------------
    # Demand category
    # --------------------------------------------------------

    demand_category_column = find_column(
        df,
        [
            "demand_category",
        ],
    )

    if demand_category_column:

        df["demand_category_clean"] = (
            df[demand_category_column]
            .astype(str)
            .str.lower()
        )

    else:

        df["demand_category_clean"] = "normal"

    # --------------------------------------------------------
    # Stockout risk
    #
    # Derived directly from days of inventory.
    # --------------------------------------------------------

    def calculate_stockout_risk(days):

        days = numeric_value(
            days,
            999,
        )

        if days <= 3:
            return "Critical"

        if days <= 7:
            return "High"

        if days <= 14:
            return "Medium"

        return "Low"

    df["stockout_risk"] = (
        df[
            "estimated_days_of_inventory"
        ].apply(
            calculate_stockout_risk
        )
    )

    # --------------------------------------------------------
    # Demand surge
    # --------------------------------------------------------

    def calculate_demand_surge(row):

        growth = numeric_value(
            row.get(
                "demand_growth_percent"
            )
        )

        category = str(
            row.get(
                "demand_category_clean",
                ""
            )
        ).lower()

        if growth >= 20:

            return "High"

        if growth >= 10:

            return "Medium"

        if category in [
            "high",
            "very high",
            "surge",
            "increasing",
        ]:

            return "High"

        return "Normal"

    df["demand_surge"] = df.apply(
        calculate_demand_surge,
        axis=1,
    )

    # --------------------------------------------------------
    # Current price
    # --------------------------------------------------------

    price_column = find_column(
        df,
        [
            "price",
            "current_price",
        ],
    )

    if price_column:

        df["current_price"] = clean_numeric_series(
            df[price_column]
        )

    else:

        df["current_price"] = np.nan

    return df


# ============================================================
# DECISION ENGINE
# ============================================================

def calculate_decision(row):

    demand = numeric_value(
        row.get(
            "average_daily_demand"
        )
    )

    inventory = numeric_value(
        row.get(
            "current_inventory"
        )
    )

    days_inventory = numeric_value(
        row.get(
            "estimated_days_of_inventory"
        ),
        999,
    )

    stockout_risk = str(
        row.get(
            "stockout_risk",
            ""
        )
    ).lower()

    demand_surge = str(
        row.get(
            "demand_surge",
            ""
        )
    ).lower()

    demand_growth = numeric_value(
        row.get(
            "demand_growth_percent"
        )
    )

    price_change = numeric_value(
        row.get(
            "expected_price_change_percent"
        )
    )

    # ========================================================
    # DECISION 1
    # CRITICAL STOCKOUT
    # ========================================================

    if (
        stockout_risk == "critical"
        and demand > 0
    ):

        return (
            "URGENTLY REPLENISH",
            "Inventory is critically low relative to current demand.",
            96,
        )

    # ========================================================
    # DECISION 2
    # HIGH STOCKOUT RISK
    # ========================================================

    if (
        stockout_risk == "high"
        and demand > 0
    ):

        return (
            "REPLENISH SOON",
            "Inventory coverage is low and the product may stock out soon.",
            90,
        )

    # ========================================================
    # DECISION 3
    # DEMAND SURGE + LIMITED INVENTORY
    # ========================================================

    if (
        demand_surge == "high"
        and days_inventory < 21
    ):

        return (
            "INCREASE STOCK",
            "Demand is accelerating while inventory coverage remains limited.",
            87,
        )

    # ========================================================
    # DECISION 4
    # STRONG DEMAND GROWTH
    # ========================================================

    if (
        demand_growth >= 20
        and days_inventory < 30
    ):

        return (
            "INCREASE STOCK",
            "Strong demand growth suggests additional inventory may be required.",
            84,
        )

    # ========================================================
    # DECISION 5
    # EXCESS INVENTORY
    # ========================================================

    if (
        days_inventory >= 60
        and demand <= 1
    ):

        return (
            "REDUCE INVENTORY",
            "Inventory coverage is very high compared with current demand.",
            86,
        )

    # ========================================================
    # DECISION 6
    # HIGH INVENTORY
    # ========================================================

    if (
        days_inventory >= 45
        and demand <= 2
    ):

        return (
            "REDUCE INVENTORY",
            "High inventory coverage and relatively weak demand indicate overstock risk.",
            80,
        )

    # ========================================================
    # DECISION 7
    # PRICE INCREASE
    # ========================================================

    if (
        price_change >= 8
        and demand > 0
        and days_inventory < 45
    ):

        return (
            "CONSIDER PRICE INCREASE",
            "AI predicts upward price movement while demand remains active.",
            79,
        )

    # ========================================================
    # DECISION 8
    # PROMOTION
    # ========================================================

    if (
        price_change <= -8
        and days_inventory >= 30
    ):

        return (
            "CONSIDER PROMOTION",
            "Expected price pressure combined with high inventory suggests promotional action.",
            77,
        )

    # ========================================================
    # DECISION 9
    # HEALTHY INVENTORY
    # ========================================================

    if (
        days_inventory >= 14
        and days_inventory <= 45
        and demand > 0
    ):

        return (
            "MAINTAIN STOCK",
            "Inventory coverage appears balanced relative to current demand.",
            72,
        )

    # ========================================================
    # DEFAULT
    # ========================================================

    return (
        "MONITOR",
        "No major demand, inventory, or price signal requires immediate action.",
        60,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "AI INVENTORY INTELLIGENCE"
    )

    print(
        "UNIFIED AI BUSINESS DECISION ENGINE"
    )

    print("=" * 70)

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # LOAD INVENTORY
    # ========================================================

    inventory_df = load_inventory_data()

    # ========================================================
    # PREPARE INVENTORY SIGNALS
    # ========================================================

    inventory_df = prepare_inventory_signals(
        inventory_df
    )

    # ========================================================
    # LOAD PRICE PREDICTIONS
    # ========================================================

    price_df = load_price_data()

    price_summary = build_price_summary(
        price_df
    )

    # ========================================================
    # MERGE PRICE INTELLIGENCE
    # ========================================================

    if not price_summary.empty:

        inventory_df = inventory_df.merge(
            price_summary,
            on="product_id",
            how="left",
        )

    else:

        inventory_df[
            "price_prediction"
        ] = np.nan

        inventory_df[
            "price_prediction_start"
        ] = np.nan

        inventory_df[
            "price_current_from_prediction"
        ] = np.nan

    # ========================================================
    # CALCULATE EXPECTED PRICE CHANGE
    # ========================================================

    inventory_df[
        "expected_price_change_percent"
    ] = np.nan

    valid_price_mask = (
        inventory_df[
            "current_price"
        ].notna()
        &
        inventory_df[
            "price_prediction"
        ].notna()
        &
        (
            inventory_df[
                "current_price"
            ] != 0
        )
    )

    inventory_df.loc[
        valid_price_mask,
        "expected_price_change_percent",
    ] = (
        (
            inventory_df.loc[
                valid_price_mask,
                "price_prediction",
            ]
            -
            inventory_df.loc[
                valid_price_mask,
                "current_price",
            ]
        )
        /
        inventory_df.loc[
            valid_price_mask,
            "current_price",
        ]
    ) * 100

    # ========================================================
    # CALCULATE AI DECISIONS
    # ========================================================

    decisions = inventory_df.apply(
        calculate_decision,
        axis=1,
    )

    inventory_df[
        "ai_decision"
    ] = decisions.apply(
        lambda result: result[0]
    )

    inventory_df[
        "ai_explanation"
    ] = decisions.apply(
        lambda result: result[1]
    )

    inventory_df[
        "ai_confidence_score"
    ] = decisions.apply(
        lambda result: result[2]
    )

    # ========================================================
    # DECISION PRIORITY
    # ========================================================

    def priority(score):

        score = numeric_value(score)

        if score >= 90:
            return "CRITICAL"

        if score >= 80:
            return "HIGH"

        if score >= 70:
            return "MEDIUM"

        return "LOW"

    inventory_df[
        "decision_priority"
    ] = inventory_df[
        "ai_confidence_score"
    ].apply(
        priority
    )

    # ========================================================
    # SELECT OUTPUT COLUMNS
    # ========================================================

    preferred_columns = [
        "product_id",
        "product_name",
        "category",
        "current_inventory",
        "average_daily_demand",
        "demand_growth_percent",
        "estimated_days_of_inventory",
        "stockout_risk",
        "demand_surge",
        "demand_category_clean",
        "current_price",
        "price_prediction",
        "expected_price_change_percent",
        "ai_decision",
        "ai_explanation",
        "ai_confidence_score",
        "decision_priority",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in inventory_df.columns
    ]

    output_df = inventory_df[
        available_columns
    ].copy()

    # ========================================================
    # REMOVE DUPLICATE PRODUCT SNAPSHOTS
    #
    # inventory_features may contain multiple historical
    # records for the same product.
    #
    # Keep the latest record for the decision dashboard.
    # ========================================================

    if "date" in inventory_df.columns:

        temp = inventory_df.copy()

        temp["_decision_date"] = pd.to_datetime(
            temp["date"],
            errors="coerce",
        )

        latest_indices = (
            temp.sort_values(
                "_decision_date"
            )
            .groupby(
                "product_id"
            )
            .tail(1)
            .index
        )

        output_df = output_df.loc[
            output_df.index.intersection(
                latest_indices
            )
        ]

    # ========================================================
    # SAVE OUTPUT
    # ========================================================

    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print(
        f"Products analyzed: {len(output_df)}"
    )

    print()

    print(
        "AI Decision Distribution:"
    )

    print(
        output_df[
            "ai_decision"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Decision Priority:"
    )

    print(
        output_df[
            "decision_priority"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Sample AI Decisions:"
    )

    display_columns = [
        column
        for column in [
            "product_id",
            "product_name",
            "current_inventory",
            "average_daily_demand",
            "estimated_days_of_inventory",
            "stockout_risk",
            "demand_surge",
            "current_price",
            "price_prediction",
            "ai_decision",
            "ai_confidence_score",
        ]
        if column in output_df.columns
    ]

    print(
        output_df[
            display_columns
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    print()

    print("=" * 70)

    print(
        "UNIFIED AI ENGINE COMPLETED"
    )

    print("=" * 70)

    print()

    print(
        "Output saved to:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()