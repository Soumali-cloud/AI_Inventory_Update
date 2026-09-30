"""
AI INVENTORY INTELLIGENCE
PRICE PREDICTION ENGINE

Predicts future product prices using:
- Historical prices
- Demand
- Seasonality
- Product characteristics

Output:
data/processed/price_predictions.csv
"""

from pathlib import Path

import warnings

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FILE DISCOVERY
# ============================================================

def find_price_data():

    possible_files = [

        RAW_DIR / "sales_data.csv",

        RAW_DIR / "historical_sales.csv",

        RAW_DIR / "inventory_data.csv",

        PROCESSED_DIR / "sales_data.csv",

    ]


    for file in possible_files:

        if file.exists():

            return file


    csv_files = list(
        RAW_DIR.glob("*.csv")
    )


    if csv_files:

        return csv_files[0]


    return None


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)

print("AI INVENTORY INTELLIGENCE")

print("PRICE PREDICTION ENGINE")

print("=" * 70)

print()


price_file = find_price_data()


if price_file is None:

    raise FileNotFoundError(
        "No CSV dataset found in data/raw."
    )


print(
    f"Loading historical data: {price_file.name}"
)


df = pd.read_csv(
    price_file
)


print(
    f"Records loaded: {len(df)}"
)

print()


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

df.columns = [

    str(column)
    .strip()
    .lower()
    .replace(" ", "_")
    .replace("-", "_")

    for column in df.columns

]


print("Available columns:")

print(
    ", ".join(df.columns)
)

print()


# ============================================================
# FIND IMPORTANT COLUMNS
# ============================================================

def find_column(
    candidates
):

    for candidate in candidates:

        if candidate in df.columns:

            return candidate


    return None


product_column = find_column(
    [
        "product_id",
        "product",
        "product_name",
        "sku",
        "item_id",
    ]
)


price_column = find_column(
    [
        "price",
        "product_price",
        "selling_price",
        "unit_price",
        "sale_price",
    ]
)


demand_column = find_column(
    [
        "demand",
        "sales",
        "units_sold",
        "quantity_sold",
        "sales_quantity",
        "quantity",
    ]
)


date_column = find_column(
    [
        "date",
        "order_date",
        "sales_date",
        "transaction_date",
    ]
)


category_column = find_column(
    [
        "category",
        "product_category",
    ]
)


# ============================================================
# VALIDATION
# ============================================================

if price_column is None:

    raise ValueError(
        "Price column was not found. "
        "Expected something like: price, product_price, selling_price."
    )


if product_column is None:

    raise ValueError(
        "Product column was not found."
    )


if date_column is None:

    raise ValueError(
        "Date column was not found."
    )


# ============================================================
# PREPARE DATA
# ============================================================

df[date_column] = pd.to_datetime(
    df[date_column],
    errors="coerce"
)


df[price_column] = pd.to_numeric(
    df[price_column],
    errors="coerce"
)


if demand_column:

    df[demand_column] = pd.to_numeric(
        df[demand_column],
        errors="coerce"
    )

else:

    df["demand_generated"] = 1.0

    demand_column = "demand_generated"


df = df.dropna(
    subset=[
        product_column,
        date_column,
        price_column,
    ]
)


df = df[
    df[price_column] > 0
]


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        product_column,
        date_column,
    ]
).reset_index(
    drop=True
)


# ============================================================
# SEASONAL FEATURES
# ============================================================

df["year"] = df[
    date_column
].dt.year


df["month"] = df[
    date_column
].dt.month


df["day"] = df[
    date_column
].dt.day


df["day_of_week"] = df[
    date_column
].dt.dayofweek


df["week_of_year"] = df[
    date_column
].dt.isocalendar().week.astype(
    int
)


df["quarter"] = df[
    date_column
].dt.quarter


df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)


# ============================================================
# DEMAND FEATURES
# ============================================================

df["demand_lag_1"] = (
    df.groupby(
        product_column
    )[demand_column]
    .shift(1)
)


df["demand_lag_7"] = (
    df.groupby(
        product_column
    )[demand_column]
    .shift(7)
)


df["demand_rolling_7"] = (
    df.groupby(
        product_column
    )[demand_column]
    .transform(
        lambda x:
        x.rolling(
            7,
            min_periods=1
        ).mean()
    )
)


df["price_lag_1"] = (
    df.groupby(
        product_column
    )[price_column]
    .shift(1)
)


df["price_rolling_7"] = (
    df.groupby(
        product_column
    )[price_column]
    .transform(
        lambda x:
        x.rolling(
            7,
            min_periods=1
        ).mean()
    )
)


# ============================================================
# PRICE CHANGE
# ============================================================

df["price_change"] = (

    df[price_column]

    /
    df["price_lag_1"]

    .replace(
        0,
        np.nan
    )

    - 1

)


# ============================================================
# CLEAN NUMERIC FEATURES
# ============================================================

feature_columns = [

    "month",

    "day",

    "day_of_week",

    "week_of_year",

    "quarter",

    "is_weekend",

    demand_column,

    "demand_lag_1",

    "demand_lag_7",

    "demand_rolling_7",

    "price_lag_1",

    "price_rolling_7",

    "price_change",

]


df[feature_columns] = (
    df[feature_columns]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    .fillna(0)
)


# ============================================================
# CHECK DATA SIZE
# ============================================================

print(
    f"Usable training records: {len(df)}"
)

print()


if len(df) < 20:

    print(
        "WARNING: Dataset contains very few records."
    )

    print(
        "The model will still run, but more historical data "
        "will improve price prediction accuracy."
    )

    print()


# ============================================================
# TRAINING DATA
# ============================================================

X = df[
    feature_columns
]


y = df[
    price_column
]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

if len(df) >= 10:

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
        )
    )

else:

    X_train = X

    X_test = X

    y_train = y

    y_test = y


# ============================================================
# MODEL
# ============================================================

print(
    "Training Random Forest price prediction model..."
)


model = RandomForestRegressor(

    n_estimators=250,

    max_depth=12,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1,

)


model.fit(
    X_train,
    y_train
)


print(
    "Model training completed."
)

print()


# ============================================================
# EVALUATION
# ============================================================

predictions = model.predict(
    X_test
)


mae = mean_absolute_error(
    y_test,
    predictions
)


rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)


print("=" * 70)

print("MODEL PERFORMANCE")

print("=" * 70)

print(
    f"MAE  : {mae:.2f}"
)

print(
    f"RMSE : {rmse:.2f}"
)

print()


# ============================================================
# CURRENT PRODUCT SNAPSHOTS
# ============================================================

latest = (

    df

    .sort_values(
        date_column
    )

    .groupby(
        product_column,
        as_index=False
    )

    .tail(1)

    .copy()

)


# ============================================================
# FUTURE PREDICTIONS
# ============================================================

prediction_rows = []


for _, row in latest.iterrows():

    product_id = row[
        product_column
    ]


    current_date = row[
        date_column
    ]


    current_price = float(
        row[
            price_column
        ]
    )


    current_demand = float(
        row[
            demand_column
        ]
    )


    # --------------------------------------------------------
    # Generate next 30 days
    # --------------------------------------------------------

    for day_number in range(
        1,
        31
    ):

        future_date = (
            current_date
            +
            pd.Timedelta(
                days=day_number
            )
        )


        future = row.copy()


        future["month"] = (
            future_date.month
        )


        future["day"] = (
            future_date.day
        )


        future["day_of_week"] = (
            future_date.dayofweek
        )


        future["week_of_year"] = (
            future_date.isocalendar().week
        )


        future["quarter"] = (
            future_date.quarter
        )


        future["is_weekend"] = int(
            future_date.dayofweek >= 5
        )


        # Demand estimate

        future_demand = max(

            current_demand,

            float(
                row[
                    "demand_rolling_7"
                ]
            ),

            0.0,

        )


        future[
            demand_column
        ] = future_demand


        # Build model input

        model_input = pd.DataFrame(
            [
                [
                    future[column]
                    for column
                    in feature_columns
                ]
            ],
            columns=feature_columns,
        )


        predicted_price = float(
            model.predict(
                model_input
            )[0]
        )


        predicted_price = max(
            predicted_price,
            0.01
        )


        prediction_rows.append({

            "product_id":
                product_id,

            "forecast_date":
                future_date.strftime(
                    "%Y-%m-%d"
                ),

            "current_price":
                round(
                    current_price,
                    2
                ),

            "predicted_price":
                round(
                    predicted_price,
                    2
                ),

            "predicted_demand":
                round(
                    future_demand,
                    2
                ),

            "price_change_percentage":
                round(
                    (
                        (
                            predicted_price
                            /
                            current_price
                        )
                        - 1
                    )
                    * 100,
                    2,
                ),

            "month":
                future_date.month,

            "quarter":
                future_date.quarter,

        })


# ============================================================
# OUTPUT
# ============================================================

predictions_df = pd.DataFrame(
    prediction_rows
)


# ============================================================
# OPTIONAL PRODUCT NAME
# ============================================================

if category_column:

    category_map = (

        df[
            [
                product_column,
                category_column,
            ]
        ]

        .drop_duplicates(
            product_column
        )

    )


    predictions_df = (
        predictions_df.merge(
            category_map,
            on="product_id",
            how="left",
        )
    )


# ============================================================
# SAVE
# ============================================================

output_file = (
    PROCESSED_DIR
    /
    "price_predictions.csv"
)


predictions_df.to_csv(
    output_file,
    index=False
)


print("=" * 70)

print("PRICE PREDICTION COMPLETED")

print("=" * 70)

print()

print(
    f"Products predicted: "
    f"{predictions_df['product_id'].nunique()}"
)

print(
    f"Forecast records: "
    f"{len(predictions_df)}"
)

print()

print(
    f"Output saved to:"
)

print(
    output_file
)

print()

print(
    "Sample predictions:"
)

print(
    predictions_df.head(10).to_string(
        index=False
    )
)

print()

print("=" * 70)