"""
AI INVENTORY INTELLIGENCE
MODEL EVALUATION REPORT

Evaluates:
1. Demand prediction model
2. Price prediction model

Creates:
reports/model_evaluation_report.csv
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"

REPORT_DIR = BASE_DIR / "reports"

OUTPUT_FILE = (
    REPORT_DIR / "model_evaluation_report.csv"
)


# ============================================================
# HELPERS
# ============================================================

def safe_rmse(y_true, y_pred):
    return float(
        np.sqrt(
            mean_squared_error(
                y_true,
                y_pred,
            )
        )
    )


def percentage_error(mae, actual):
    if actual == 0:
        return 0.0

    return float(
        (mae / actual) * 100
    )


# ============================================================
# DEMAND MODEL EVALUATION
# ============================================================

def evaluate_demand_model():

    print()
    print("=" * 70)
    print("EVALUATING DEMAND MODEL")
    print("=" * 70)

    file_path = (
        DATA_DIR / "inventory_features.csv"
    )

    if not file_path.exists():

        print(
            "inventory_features.csv not found."
        )

        return None

    df = pd.read_csv(file_path)

    print(
        f"Dataset rows: {len(df)}"
    )

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    target_candidates = [
        "units_sold",
        "sales_velocity",
        "rolling_mean_7",
    ]

    target_column = None

    for column in target_candidates:

        if column in df.columns:

            target_column = column
            break

    if target_column is None:

        print(
            "Could not identify demand target."
        )

        return None

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    feature_candidates = [
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
    ]

    feature_columns = [
        column
        for column in feature_candidates
        if column in df.columns
    ]

    if len(feature_columns) < 3:

        print(
            "Not enough demand features available."
        )

        return None

    model_df = df[
        feature_columns + [target_column]
    ].copy()

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    for column in model_df.columns:

        model_df[column] = pd.to_numeric(
            model_df[column],
            errors="coerce",
        )

    model_df = model_df.dropna()

    if len(model_df) < 20:

        print(
            "Not enough valid rows for evaluation."
        )

        return None

    X = model_df[
        feature_columns
    ]

    y = model_df[
        target_column
    ]

    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
        )
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = safe_rmse(
        y_test,
        predictions,
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    mean_actual = float(
        np.mean(
            np.abs(y_test)
        )
    )

    mae_percentage = percentage_error(
        mae,
        mean_actual,
    )

    print()
    print(
        f"Target: {target_column}"
    )

    print(
        f"Features: {len(feature_columns)}"
    )

    print(
        f"MAE: {mae:.4f}"
    )

    print(
        f"RMSE: {rmse:.4f}"
    )

    print(
        f"R² Score: {r2:.4f}"
    )

    print(
        f"MAE %: {mae_percentage:.2f}%"
    )

    return {
        "model": "Demand Prediction",
        "target": target_column,
        "samples": len(model_df),
        "features": len(feature_columns),
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAE_Percent": mae_percentage,
    }


# ============================================================
# PRICE MODEL EVALUATION
# ============================================================

def evaluate_price_model():

    print()
    print("=" * 70)
    print("EVALUATING PRICE MODEL")
    print("=" * 70)

    file_path = (
        DATA_DIR / "price_predictions.csv"
    )

    if not file_path.exists():

        print(
            "price_predictions.csv not found."
        )

        return None

    df = pd.read_csv(file_path)

    print(
        f"Price prediction rows: {len(df)}"
    )

    # --------------------------------------------------------
    # Detect columns
    # --------------------------------------------------------

    prediction_column = None

    for column in [
        "predicted_price",
        "predicted_price_30d",
        "forecast_price",
        "price_prediction",
    ]:

        if column in df.columns:

            prediction_column = column
            break

    actual_column = None

    for column in [
        "price",
        "current_price",
        "actual_price",
        "historical_price",
    ]:

        if column in df.columns:

            actual_column = column
            break

    if (
        prediction_column is None
        or actual_column is None
    ):

        print(
            "Could not identify price columns."
        )

        return None

    actual = pd.to_numeric(
        df[actual_column],
        errors="coerce",
    )

    predicted = pd.to_numeric(
        df[prediction_column],
        errors="coerce",
    )

    valid = (
        actual.notna()
        & predicted.notna()
    )

    actual = actual[valid]
    predicted = predicted[valid]

    if len(actual) < 5:

        print(
            "Not enough valid price records."
        )

        return None

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = safe_rmse(
        actual,
        predicted,
    )

    r2 = r2_score(
        actual,
        predicted,
    )

    mean_actual = float(
        np.mean(
            np.abs(actual)
        )
    )

    mae_percentage = percentage_error(
        mae,
        mean_actual,
    )

    print()

    print(
        f"Actual price column: {actual_column}"
    )

    print(
        f"Predicted price column: {prediction_column}"
    )

    print(
        f"MAE: {mae:.4f}"
    )

    print(
        f"RMSE: {rmse:.4f}"
    )

    print(
        f"R² Score: {r2:.4f}"
    )

    print(
        f"MAE %: {mae_percentage:.2f}%"
    )

    return {
        "model": "Price Prediction",
        "target": actual_column,
        "samples": len(actual),
        "features": "ML Price Features",
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAE_Percent": mae_percentage,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("AI INVENTORY INTELLIGENCE")
    print("MODEL EVALUATION")
    print("=" * 70)

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    demand_result = (
        evaluate_demand_model()
    )

    if demand_result:

        results.append(
            demand_result
        )

    price_result = (
        evaluate_price_model()
    )

    if price_result:

        results.append(
            price_result
        )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    if not results:

        print()
        print(
            "No model evaluation results generated."
        )

        return

    report = pd.DataFrame(
        results
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 70)
    print("MODEL EVALUATION SUMMARY")
    print("=" * 70)

    print()

    print(
        report.to_string(
            index=False
        )
    )

    print()
    print(
        "Evaluation report saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print("=" * 70)
    print("MODEL EVALUATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()