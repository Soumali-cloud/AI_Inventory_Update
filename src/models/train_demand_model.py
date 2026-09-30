import json
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/processed/inventory_features.csv"

MODEL_DIR = "models"

REPORT_DIR = "reports/demand_model"

BEST_MODEL_PATH = (
    "models/demand_prediction_model.joblib"
)

METRICS_PATH = (
    "reports/demand_model/model_metrics.json"
)

PREDICTIONS_PATH = (
    "reports/demand_model/predictions.csv"
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True,
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True,
)


# ============================================================
# FEATURES
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


TARGET = "units_sold"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("AI INVENTORY INTELLIGENCE")
print("DEMAND PREDICTION MODEL")
print("=" * 70)

print("\nLoading processed dataset...")

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

print(
    f"Dataset shape: {df.shape}"
)


# ============================================================
# PREPARE DATA
# ============================================================

print("\nPreparing data...")

df = df.sort_values(
    "date"
).reset_index(drop=True)


# Remove rows with missing ML features

df = df.dropna(
    subset=FEATURES + [TARGET]
).reset_index(drop=True)


print(
    f"Rows after cleaning: {len(df):,}"
)


# ============================================================
# TIME-BASED TRAIN TEST SPLIT
# ============================================================

print("\nCreating time-based train/test split...")

unique_dates = sorted(
    df["date"].unique()
)

split_index = int(
    len(unique_dates) * 0.80
)

split_date = unique_dates[split_index]

train_df = df[
    df["date"] < split_date
].copy()

test_df = df[
    df["date"] >= split_date
].copy()


print(
    f"Training period:"
    f" {train_df['date'].min().date()}"
    f" → {train_df['date'].max().date()}"
)

print(
    f"Testing period:"
    f" {test_df['date'].min().date()}"
    f" → {test_df['date'].max().date()}"
)

print(
    f"\nTraining rows: {len(train_df):,}"
)

print(
    f"Testing rows : {len(test_df):,}"
)


# ============================================================
# X AND Y
# ============================================================

X_train = train_df[FEATURES]

y_train = train_df[TARGET]

X_test = test_df[FEATURES]

y_test = test_df[TARGET]


# ============================================================
# BASELINE MODEL
# ============================================================

print("\n" + "=" * 70)
print("BASELINE MODEL")
print("=" * 70)

# Predict using the 7-day rolling mean

baseline_predictions = test_df[
    "rolling_mean_7"
].values

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions,
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions,
    )
)

print(
    f"Baseline MAE  : {baseline_mae:.4f}"
)

print(
    f"Baseline RMSE : {baseline_rmse:.4f}"
)


# ============================================================
# RANDOM FOREST
# ============================================================

print("\n" + "=" * 70)
print("TRAINING RANDOM FOREST")
print("=" * 70)

random_forest = RandomForestRegressor(
    n_estimators=150,
    max_depth=18,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)

random_forest.fit(
    X_train,
    y_train,
)

rf_predictions = random_forest.predict(
    X_test
)

rf_mae = mean_absolute_error(
    y_test,
    rf_predictions,
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        rf_predictions,
    )
)

print(
    f"Random Forest MAE  : {rf_mae:.4f}"
)

print(
    f"Random Forest RMSE : {rf_rmse:.4f}"
)


# ============================================================
# XGBOOST
# ============================================================

print("\n" + "=" * 70)
print("TRAINING XGBOOST")
print("=" * 70)

xgb_model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1,
)

xgb_model.fit(
    X_train,
    y_train,
)

xgb_predictions = xgb_model.predict(
    X_test
)

xgb_mae = mean_absolute_error(
    y_test,
    xgb_predictions,
)

xgb_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        xgb_predictions,
    )
)

print(
    f"XGBoost MAE  : {xgb_mae:.4f}"
)

print(
    f"XGBoost RMSE : {xgb_rmse:.4f}"
)


# ============================================================
# MAPE FUNCTION
# ============================================================

def calculate_mape(
    actual,
    predicted,
):
    """
    Calculate Mean Absolute Percentage Error.
    """

    actual = np.array(actual)

    predicted = np.array(predicted)

    mask = actual != 0

    if mask.sum() == 0:
        return 0.0

    return np.mean(
        np.abs(
            (
                actual[mask]
                - predicted[mask]
            )
            / actual[mask]
        )
    ) * 100


# ============================================================
# MAPE
# ============================================================

baseline_mape = calculate_mape(
    y_test,
    baseline_predictions,
)

rf_mape = calculate_mape(
    y_test,
    rf_predictions,
)

xgb_mape = calculate_mape(
    y_test,
    xgb_predictions,
)


# ============================================================
# MODEL COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

results = pd.DataFrame(
    {
        "Model": [
            "Baseline",
            "Random Forest",
            "XGBoost",
        ],
        "MAE": [
            baseline_mae,
            rf_mae,
            xgb_mae,
        ],
        "RMSE": [
            baseline_rmse,
            rf_rmse,
            xgb_rmse,
        ],
        "MAPE": [
            baseline_mape,
            rf_mape,
            xgb_mape,
        ],
    }
)

print(
    results.to_string(
        index=False
    )
)


# ============================================================
# SELECT BEST MODEL
# ============================================================

best_index = results[
    "MAE"
].idxmin()

best_model_name = results.loc[
    best_index,
    "Model",
]

print(
    f"\nBest model based on MAE:"
    f" {best_model_name}"
)


if best_model_name == "XGBoost":

    best_model = xgb_model

    best_predictions = xgb_predictions

elif best_model_name == "Random Forest":

    best_model = random_forest

    best_predictions = rf_predictions

else:

    # Baseline isn't an ML model,
    # but we still save the result metadata.

    best_model = xgb_model

    best_predictions = xgb_predictions


# ============================================================
# SAVE BEST MODEL
# ============================================================

joblib.dump(
    best_model,
    BEST_MODEL_PATH,
)

print(
    f"\nBest model saved to:"
    f" {BEST_MODEL_PATH}"
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics = {
    "baseline": {
        "MAE": float(baseline_mae),
        "RMSE": float(baseline_rmse),
        "MAPE": float(baseline_mape),
    },
    "random_forest": {
        "MAE": float(rf_mae),
        "RMSE": float(rf_rmse),
        "MAPE": float(rf_mape),
    },
    "xgboost": {
        "MAE": float(xgb_mae),
        "RMSE": float(xgb_rmse),
        "MAPE": float(xgb_mape),
    },
    "best_model": best_model_name,
}

with open(
    METRICS_PATH,
    "w",
) as file:

    json.dump(
        metrics,
        file,
        indent=4,
    )


# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_results = test_df[
    [
        "date",
        "product_id",
        "product_name",
        "category",
        "units_sold",
    ]
].copy()

prediction_results[
    "predicted_units_sold"
] = best_predictions

prediction_results[
    "prediction_error"
] = (
    prediction_results["units_sold"]
    - prediction_results["predicted_units_sold"]
)

prediction_results.to_csv(
    PREDICTIONS_PATH,
    index=False,
)


# ============================================================
# ACTUAL VS PREDICTED CHART
# ============================================================

print(
    "\nCreating actual vs predicted chart..."
)

plot_data = (
    prediction_results
    .groupby("date")[
        [
            "units_sold",
            "predicted_units_sold",
        ]
    ]
    .sum()
    .reset_index()
)

plt.figure(
    figsize=(14, 6)
)

plt.plot(
    plot_data["date"],
    plot_data["units_sold"],
    label="Actual Demand",
)

plt.plot(
    plot_data["date"],
    plot_data["predicted_units_sold"],
    label="Predicted Demand",
)

plt.title(
    "Actual vs Predicted Daily Demand"
)

plt.xlabel("Date")

plt.ylabel("Units Sold")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{REPORT_DIR}/actual_vs_predicted.png",
    dpi=150,
)

plt.close()


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print(
    "Creating feature importance chart..."
)

if hasattr(
    best_model,
    "feature_importances_",
):

    importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": (
                best_model
                .feature_importances_
            ),
        }
    )

    importance = importance.sort_values(
        "importance",
        ascending=True,
    )

    plt.figure(
        figsize=(10, 8)
    )

    plt.barh(
        importance["feature"],
        importance["importance"],
    )

    plt.title(
        "Demand Prediction Feature Importance"
    )

    plt.xlabel(
        "Importance"
    )

    plt.ylabel(
        "Feature"
    )

    plt.tight_layout()

    plt.savefig(
        f"{REPORT_DIR}/feature_importance.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# TOP PREDICTIONS
# ============================================================

print("\nTop predicted demand records:")

top_predictions = (
    prediction_results
    .sort_values(
        "predicted_units_sold",
        ascending=False,
    )
    .head(10)
)

print(
    top_predictions[
        [
            "date",
            "product_name",
            "units_sold",
            "predicted_units_sold",
        ]
    ].to_string(index=False)
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("DEMAND MODEL TRAINING COMPLETE")
print("=" * 70)

print(
    f"\nBest model: {best_model_name}"
)

print(
    f"MAE: {results.loc[best_index, 'MAE']:.4f}"
)

print(
    f"RMSE: {results.loc[best_index, 'RMSE']:.4f}"
)

print(
    f"MAPE: {results.loc[best_index, 'MAPE']:.2f}%"
)

print(
    f"\nModel file:"
    f" {BEST_MODEL_PATH}"
)

print(
    f"Metrics file:"
    f" {METRICS_PATH}"
)

print(
    f"Predictions file:"
    f" {PREDICTIONS_PATH}"
)

print(
    f"Charts:"
    f" {REPORT_DIR}"
)