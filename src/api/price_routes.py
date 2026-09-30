from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/price",
    tags=["Price Prediction"],
)


BASE_DIR = Path(__file__).resolve().parents[2]

PRICE_FILE = BASE_DIR / "data" / "processed" / "price_predictions.csv"


def load_price_predictions():
    if not PRICE_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Price prediction file not found. "
                "Run src/inventory/price_prediction.py first."
            ),
        )

    try:
        df = pd.read_csv(PRICE_FILE)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read price prediction file: {exc}",
        )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Price prediction file is empty.",
        )

    return df


def clean_records(df):
    df = df.copy()

    # Convert dates to strings so FastAPI can return them as JSON.
    for column in df.columns:
        if "date" in column.lower():
            try:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce",
                ).dt.strftime("%Y-%m-%d")
            except Exception:
                pass

    # Replace NaN / infinity values.
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")


@router.get("/all")
def get_all_price_predictions():
    """
    Return all future price predictions.
    """

    df = load_price_predictions()

    return {
        "status": "success",
        "count": len(df),
        "predictions": clean_records(df),
    }


@router.get("/{product_id}")
def get_product_price_prediction(product_id: str):
    """
    Return price predictions for a specific product.
    """

    df = load_price_predictions()

    product_column = None

    possible_columns = [
        "product_id",
        "product",
        "product_name",
        "sku",
        "id",
    ]

    for column in possible_columns:
        if column in df.columns:
            product_column = column
            break

    if product_column is None:
        raise HTTPException(
            status_code=500,
            detail="No product identifier column found in price prediction data.",
        )

    matching = df[
        df[product_column].astype(str).str.lower()
        == str(product_id).lower()
    ].copy()

    if matching.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No price prediction found for product: {product_id}",
        )

    return {
        "status": "success",
        "product_id": product_id,
        "count": len(matching),
        "predictions": clean_records(matching),
    }


@router.get("/{product_id}/summary")
def get_product_price_summary(product_id: str):
    """
    Return a compact summary for a product:
    current price, predicted price and expected percentage change.
    """

    df = load_price_predictions()

    product_column = None

    for column in [
        "product_id",
        "product",
        "product_name",
        "sku",
        "id",
    ]:
        if column in df.columns:
            product_column = column
            break

    if product_column is None:
        raise HTTPException(
            status_code=500,
            detail="No product identifier column found.",
        )

    matching = df[
        df[product_column].astype(str).str.lower()
        == str(product_id).lower()
    ].copy()

    if matching.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No price prediction found for product: {product_id}",
        )

    # Detect prediction column.
    prediction_column = None

    for column in [
        "predicted_price",
        "predicted_price_30d",
        "forecast_price",
        "price_prediction",
    ]:
        if column in matching.columns:
            prediction_column = column
            break

    if prediction_column is None:
        raise HTTPException(
            status_code=500,
            detail="Predicted price column not found.",
        )

    # Detect current/actual price column.
    current_price_column = None

    for column in [
        "current_price",
        "price",
        "actual_price",
        "historical_price",
    ]:
        if column in matching.columns:
            current_price_column = column
            break

    if current_price_column is None:
        current_price = None
    else:
        current_price = pd.to_numeric(
            matching[current_price_column],
            errors="coerce",
        ).dropna()

        current_price = (
            float(current_price.iloc[-1])
            if not current_price.empty
            else None
        )

    predicted_prices = pd.to_numeric(
        matching[prediction_column],
        errors="coerce",
    ).dropna()

    if predicted_prices.empty:
        raise HTTPException(
            status_code=500,
            detail="No valid predicted prices found.",
        )

    first_predicted_price = float(predicted_prices.iloc[0])
    final_predicted_price = float(predicted_prices.iloc[-1])

    if current_price is not None and current_price != 0:
        expected_change = (
            (final_predicted_price - current_price)
            / current_price
        ) * 100
    else:
        expected_change = None

    return {
        "status": "success",
        "product_id": product_id,
        "current_price": current_price,
        "predicted_price": final_predicted_price,
        "first_predicted_price": first_predicted_price,
        "expected_change_percent": expected_change,
        "prediction_days": len(predicted_prices),
    }