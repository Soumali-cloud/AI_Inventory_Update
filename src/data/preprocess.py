import os

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/raw/inventory_sales.csv"
OUTPUT_PATH = "data/processed/inventory_features.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data(path: str) -> pd.DataFrame:
    """Load raw inventory and sales data."""

    print("\nLoading dataset...")

    df = pd.read_csv(path)

    print(f"Loaded {len(df):,} rows.")

    return df


# ============================================================
# DATA VALIDATION
# ============================================================

def validate_data(df: pd.DataFrame) -> None:
    """Validate the raw dataset."""

    print("\n" + "=" * 60)
    print("DATA VALIDATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    print(f"\nRows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]}")

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\nMissing values:")

    missing = df.isnull().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values found.")
    else:
        print(missing)

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicates = df.duplicated().sum()

    print(f"\nDuplicate rows: {duplicates}")

    # --------------------------------------------------------
    # Negative values
    # --------------------------------------------------------

    print("\nNegative values:")

    numeric_columns = [
        "price",
        "discount",
        "units_sold",
        "inventory_level",
        "rating",
        "reviews",
    ]

    for column in numeric_columns:

        if column in df.columns:

            count = (df[column] < 0).sum()

            print(f"{column}: {count}")

    # --------------------------------------------------------
    # Date range
    # --------------------------------------------------------

    print("\nDate range:")

    print(
        f"{df['date'].min()} → {df['date'].max()}"
    )

    # --------------------------------------------------------
    # Products
    # --------------------------------------------------------

    print(
        f"\nUnique products: "
        f"{df['product_id'].nunique()}"
    )

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    print(
        f"Unique categories: "
        f"{df['category'].nunique()}"
    )


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the dataset."""

    print("\n" + "=" * 60)
    print("CLEANING DATA")
    print("=" * 60)

    df = df.copy()

    # --------------------------------------------------------
    # Convert date
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    # Remove rows with invalid dates
    df = df.dropna(
        subset=["date"]
    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(
        f"Duplicate rows removed: {removed}"
    )

    # --------------------------------------------------------
    # Ensure numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "price",
        "discount",
        "units_sold",
        "inventory_level",
        "rating",
        "reviews",
        "promotion",
        "holiday",
        "day_of_week",
        "month",
        "year",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Fill numeric missing values
    # --------------------------------------------------------

    for column in numeric_columns:

        if df[column].isnull().any():

            df[column] = df[column].fillna(
                df[column].median()
            )

    # --------------------------------------------------------
    # Clip invalid values
    # --------------------------------------------------------

    df["price"] = df["price"].clip(
        lower=0
    )

    df["discount"] = df["discount"].clip(
        lower=0,
        upper=1,
    )

    df["units_sold"] = df["units_sold"].clip(
        lower=0
    )

    df["inventory_level"] = df[
        "inventory_level"
    ].clip(lower=0)

    df["rating"] = df["rating"].clip(
        lower=0,
        upper=5,
    )

    df["reviews"] = df["reviews"].clip(
        lower=0
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        ["product_id", "date"]
    ).reset_index(drop=True)

    return df


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create machine-learning features."""

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)

    df = df.copy()

    # ========================================================
    # TIME FEATURES
    # ========================================================

    df["day"] = df["date"].dt.day

    df["week"] = df["date"].dt.isocalendar().week.astype(int)

    df["quarter"] = df["date"].dt.quarter

    df["day_of_year"] = df[
        "date"
    ].dt.dayofyear

    df["is_weekend"] = (
        df["date"].dt.dayofweek >= 5
    ).astype(int)

    # ========================================================
    # LAG FEATURES
    # ========================================================

    print("Creating lag features...")

    grouped = df.groupby(
        "product_id"
    )["units_sold"]

    df["lag_1"] = grouped.shift(1)

    df["lag_7"] = grouped.shift(7)

    df["lag_14"] = grouped.shift(14)

    df["lag_30"] = grouped.shift(30)

    # ========================================================
    # ROLLING FEATURES
    # ========================================================

    print("Creating rolling-demand features...")

    df["rolling_mean_7"] = (
        df.groupby("product_id")[
            "units_sold"
        ]
        .transform(
            lambda x: x.shift(1)
            .rolling(7)
            .mean()
        )
    )

    df["rolling_mean_14"] = (
        df.groupby("product_id")[
            "units_sold"
        ]
        .transform(
            lambda x: x.shift(1)
            .rolling(14)
            .mean()
        )
    )

    df["rolling_mean_30"] = (
        df.groupby("product_id")[
            "units_sold"
        ]
        .transform(
            lambda x: x.shift(1)
            .rolling(30)
            .mean()
        )
    )

    # ========================================================
    # ROLLING STANDARD DEVIATION
    # ========================================================

    df["rolling_std_7"] = (
        df.groupby("product_id")[
            "units_sold"
        ]
        .transform(
            lambda x: x.shift(1)
            .rolling(7)
            .std()
        )
    )

    # ========================================================
    # SALES VELOCITY
    # ========================================================

    df["sales_velocity"] = (
        df["rolling_mean_7"]
    )

    # ========================================================
    # DEMAND GROWTH
    # ========================================================

    df["demand_growth"] = (
        (
            df["rolling_mean_7"]
            - df["rolling_mean_30"]
        )
        / df["rolling_mean_30"].replace(
            0,
            np.nan,
        )
    )

    # ========================================================
    # PRICE CHANGE
    # ========================================================

    df["previous_price"] = (
        df.groupby("product_id")[
            "price"
        ].shift(1)
    )

    df["price_change"] = (
        (
            df["price"]
            - df["previous_price"]
        )
        / df["previous_price"].replace(
            0,
            np.nan,
        )
    )

    # ========================================================
    # REVENUE
    # ========================================================

    df["revenue"] = (
        df["price"]
        * df["units_sold"]
    )

    # ========================================================
    # DAYS OF INVENTORY
    # ========================================================

    df["days_of_inventory"] = (
        df["inventory_level"]
        / df["sales_velocity"].replace(
            0,
            np.nan,
        )
    )

    # ========================================================
    # DEMAND CATEGORY
    # ========================================================

    df["demand_category"] = pd.qcut(
        df["units_sold"],
        q=4,
        labels=[
            "Low",
            "Medium",
            "High",
            "Very High",
        ],
        duplicates="drop",
    )

    # ========================================================
    # HANDLE INFINITE VALUES
    # ========================================================

    df = df.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    # ========================================================
    # FILL FEATURE MISSING VALUES
    # ========================================================

    feature_columns = [
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_30",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_30",
        "rolling_std_7",
        "sales_velocity",
        "demand_growth",
        "previous_price",
        "price_change",
        "days_of_inventory",
    ]

    for column in feature_columns:

        if column in df.columns:

            df[column] = (
                df.groupby("product_id")[
                    column
                ]
                .transform(
                    lambda x: x.fillna(
                        x.median()
                    )
                )
            )

            df[column] = df[column].fillna(0)

    return df


# ============================================================
# SAVE DATA
# ============================================================

def save_data(
    df: pd.DataFrame,
    path: str,
) -> None:
    """Save processed dataset."""

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True,
    )

    df.to_csv(
        path,
        index=False,
    )

    print(
        f"\nProcessed dataset saved to:"
    )

    print(path)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("AI INVENTORY INTELLIGENCE")
    print("DATA PREPROCESSING PIPELINE")
    print("=" * 60)

    # Load
    df = load_data(
        INPUT_PATH
    )

    # Validate
    validate_data(df)

    # Clean
    df = clean_data(df)

    # Features
    df = create_features(df)

    # Save
    save_data(
        df,
        OUTPUT_PATH,
    )

    # Final information
    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)

    print(
        f"Final rows: {len(df):,}"
    )

    print(
        f"Final columns: {len(df.columns)}"
    )

    print("\nNew features:")

    new_features = [
        "day",
        "week",
        "quarter",
        "day_of_year",
        "is_weekend",
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_30",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_mean_30",
        "rolling_std_7",
        "sales_velocity",
        "demand_growth",
        "previous_price",
        "price_change",
        "revenue",
        "days_of_inventory",
        "demand_category",
    ]

    for feature in new_features:
        print(f"  ✓ {feature}")


if __name__ == "__main__":
    main()