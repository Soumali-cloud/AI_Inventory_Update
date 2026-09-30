import os

import joblib
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/processed/inventory_features.csv"

MODEL_PATH = "models/demand_prediction_model.joblib"

OUTPUT_PATH = "reports/demand_model/future_demand_forecast.csv"


# ============================================================
# MODEL FEATURES
# ============================================================

FEATURES = [
    "price",
    "discount",
    "promotion",
    "holiday",
    "day_of_week",
    "month",
    "year",
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
    "price_change",
    "rating",
    "reviews",
]


# ============================================================
# LOAD DATA AND MODEL
# ============================================================

print("=" * 70)
print("AI INVENTORY INTELLIGENCE")
print("FUTURE DEMAND FORECASTING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

print(
    f"Dataset loaded: {len(df):,} rows"
)


print("\nLoading trained demand model...")

model = joblib.load(
    MODEL_PATH
)

print("Demand model loaded successfully.")


# ============================================================
# FORECAST FUNCTION
# ============================================================

def forecast_product(
    product_id: str,
    days: int = 30,
) -> pd.DataFrame:
    """
    Forecast future demand for one product.

    Parameters
    ----------
    product_id : str
        Product identifier.

    days : int
        Number of future days.

    Returns
    -------
    pd.DataFrame
        Future demand predictions.
    """

    # --------------------------------------------------------
    # Get product history
    # --------------------------------------------------------

    product_df = df[
        df["product_id"] == product_id
    ].copy()

    if product_df.empty:

        raise ValueError(
            f"Product {product_id} not found."
        )

    product_df = product_df.sort_values(
        "date"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Product information
    # --------------------------------------------------------

    product_name = product_df[
        "product_name"
    ].iloc[-1]

    category = product_df[
        "category"
    ].iloc[-1]

    price = product_df[
        "price"
    ].iloc[-1]

    discount = product_df[
        "discount"
    ].iloc[-1]

    promotion = product_df[
        "promotion"
    ].iloc[-1]

    rating = product_df[
        "rating"
    ].iloc[-1]

    reviews = product_df[
        "reviews"
    ].iloc[-1]

    # --------------------------------------------------------
    # Historical demand
    # --------------------------------------------------------

    historical_sales = (
        product_df[
            "units_sold"
        ]
        .tolist()
    )

    historical_prices = (
        product_df[
            "price"
        ]
        .tolist()
    )

    # --------------------------------------------------------
    # Last date
    # --------------------------------------------------------

    last_date = product_df[
        "date"
    ].max()

    # --------------------------------------------------------
    # Future predictions
    # --------------------------------------------------------

    forecasts = []

    for i in range(1, days + 1):

        future_date = (
            last_date
            + pd.Timedelta(days=i)
        )

        # ====================================================
        # CALENDAR FEATURES
        # ====================================================

        day_of_week = (
            future_date.dayofweek
        )

        month = future_date.month

        year = future_date.year

        day = future_date.day

        week = (
            future_date.isocalendar().week
        )

        week = int(week)

        quarter = (
            future_date.quarter
        )

        day_of_year = (
            future_date.dayofyear
        )

        is_weekend = int(
            day_of_week >= 5
        )

        # ====================================================
        # HOLIDAY
        # ====================================================

        holiday = 0

        if (
            (month == 1 and day == 26)
            or (month == 8 and day == 15)
            or (month == 10 and day in [20, 21])
            or (month == 12 and day == 25)
        ):

            holiday = 1

        # ====================================================
        # LAG FEATURES
        # ====================================================

        lag_1 = (
            historical_sales[-1]
        )

        lag_7 = (
            historical_sales[-7]
            if len(historical_sales) >= 7
            else np.mean(historical_sales)
        )

        lag_14 = (
            historical_sales[-14]
            if len(historical_sales) >= 14
            else np.mean(historical_sales)
        )

        lag_30 = (
            historical_sales[-30]
            if len(historical_sales) >= 30
            else np.mean(historical_sales)
        )

        # ====================================================
        # ROLLING FEATURES
        # ====================================================

        last_7 = historical_sales[-7:]

        last_14 = historical_sales[-14:]

        last_30 = historical_sales[-30:]

        rolling_mean_7 = np.mean(
            last_7
        )

        rolling_mean_14 = np.mean(
            last_14
        )

        rolling_mean_30 = np.mean(
            last_30
        )

        rolling_std_7 = np.std(
            last_7
        )

        # ====================================================
        # SALES VELOCITY
        # ====================================================

        sales_velocity = (
            rolling_mean_7
        )

        # ====================================================
        # DEMAND GROWTH
        # ====================================================

        if rolling_mean_30 != 0:

            demand_growth = (
                rolling_mean_7
                - rolling_mean_30
            ) / rolling_mean_30

        else:

            demand_growth = 0

        # ====================================================
        # PRICE CHANGE
        # ====================================================

        previous_price = (
            historical_prices[-1]
        )

        if previous_price != 0:

            price_change = (
                price
                - previous_price
            ) / previous_price

        else:

            price_change = 0

        # ====================================================
        # FEATURE VECTOR
        # ====================================================

        features = pd.DataFrame(
            [
                {
                    "price": price,
                    "discount": discount,
                    "promotion": promotion,
                    "holiday": holiday,
                    "day_of_week": day_of_week,
                    "month": month,
                    "year": year,
                    "day": day,
                    "week": week,
                    "quarter": quarter,
                    "day_of_year": day_of_year,
                    "is_weekend": is_weekend,
                    "lag_1": lag_1,
                    "lag_7": lag_7,
                    "lag_14": lag_14,
                    "lag_30": lag_30,
                    "rolling_mean_7": rolling_mean_7,
                    "rolling_mean_14": rolling_mean_14,
                    "rolling_mean_30": rolling_mean_30,
                    "rolling_std_7": rolling_std_7,
                    "sales_velocity": sales_velocity,
                    "demand_growth": demand_growth,
                    "price_change": price_change,
                    "rating": rating,
                    "reviews": reviews,
                }
            ]
        )

        # ====================================================
        # PREDICT
        # ====================================================

        predicted_demand = model.predict(
            features[FEATURES]
        )[0]

        predicted_demand = max(
            0,
            predicted_demand,
        )

        predicted_demand = round(
            predicted_demand,
            2,
        )

        # ====================================================
        # STORE FORECAST
        # ====================================================

        forecasts.append(
            {
                "date": future_date,
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "predicted_demand": predicted_demand,
                "price": price,
                "discount": discount,
                "promotion": promotion,
                "holiday": holiday,
            }
        )

        # ====================================================
        # ADD PREDICTION TO HISTORY
        # ====================================================

        historical_sales.append(
            predicted_demand
        )

        historical_prices.append(
            price
        )

    return pd.DataFrame(
        forecasts
    )


# ============================================================
# FORECAST ALL PRODUCTS
# ============================================================

print("\nGenerating 30-day forecasts...")

all_forecasts = []

product_ids = (
    df["product_id"]
    .unique()
)

for product_id in product_ids:

    print(
        f"Forecasting {product_id}..."
    )

    forecast = forecast_product(
        product_id,
        days=30,
    )

    all_forecasts.append(
        forecast
    )


# ============================================================
# COMBINE FORECASTS
# ============================================================

forecast_df = pd.concat(
    all_forecasts,
    ignore_index=True,
)


# ============================================================
# SAVE FORECAST
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True,
)

forecast_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FORECAST COMPLETE")
print("=" * 70)

print(
    f"Products forecasted: "
    f"{forecast_df['product_id'].nunique()}"
)

print(
    f"Forecast days per product: 30"
)

print(
    f"Total forecast records: "
    f"{len(forecast_df):,}"
)

print(
    f"\nForecast saved to:"
    f"\n{OUTPUT_PATH}"
)


# ============================================================
# TOP PRODUCTS BY FORECASTED DEMAND
# ============================================================

print(
    "\nTop 10 products by predicted "
    "30-day demand:"
)

top_products = (
    forecast_df
    .groupby(
        [
            "product_id",
            "product_name",
        ]
    )["predicted_demand"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(10)
)

print(
    top_products.to_string()
)


# ============================================================
# DAILY TOTAL FORECAST
# ============================================================

daily_forecast = (
    forecast_df
    .groupby("date")[
        "predicted_demand"
    ]
    .sum()
)

print(
    "\nAverage predicted daily demand:"
)

print(
    f"{daily_forecast.mean():.2f} units"
)

print(
    "\nPeak predicted demand day:"
)

peak_date = (
    daily_forecast.idxmax()
)

peak_value = (
    daily_forecast.max()
)

print(
    f"{peak_date.date()} "
    f"→ {peak_value:.2f} units"
)