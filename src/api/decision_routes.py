from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/decisions",
    tags=["AI Decisions"],
)


BASE_DIR = Path(__file__).resolve().parents[2]

DECISION_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "unified_ai_decisions.csv"
)


def load_decisions():
    if not DECISION_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Unified AI decision file not found. "
                "Run unified_ai_engine.py first."
            ),
        )

    try:
        df = pd.read_csv(DECISION_FILE)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read AI decision file: {exc}",
        )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Unified AI decision file is empty.",
        )

    return df


def clean_dataframe(df):
    df = df.copy()

    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    df = df.where(
        pd.notnull(df),
        None,
    )

    return df.to_dict(
        orient="records"
    )


@router.get("/all")
def get_all_decisions():

    df = load_decisions()

    return {
        "status": "success",
        "count": len(df),
        "decisions": clean_dataframe(df),
    }


@router.get("/summary")
def get_decision_summary():

    df = load_decisions()

    decision_counts = (
        df["ai_decision"]
        .value_counts()
        .to_dict()
        if "ai_decision" in df.columns
        else {}
    )

    priority_counts = (
        df["decision_priority"]
        .value_counts()
        .to_dict()
        if "decision_priority" in df.columns
        else {}
    )

    critical_count = priority_counts.get(
        "CRITICAL",
        0,
    )

    high_count = priority_counts.get(
        "HIGH",
        0,
    )

    medium_count = priority_counts.get(
        "MEDIUM",
        0,
    )

    low_count = priority_counts.get(
        "LOW",
        0,
    )

    return {
        "status": "success",
        "total_products": len(df),
        "critical": critical_count,
        "high": high_count,
        "medium": medium_count,
        "low": low_count,
        "decision_distribution": decision_counts,
        "priority_distribution": priority_counts,
    }


@router.get("/{product_id}")
def get_product_decision(
    product_id: str,
):

    df = load_decisions()

    if "product_id" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="product_id column not found.",
        )

    matching = df[
        df["product_id"]
        .astype(str)
        .str.lower()
        == str(product_id).lower()
    ]

    if matching.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No AI decision found for "
                f"product: {product_id}"
            ),
        )

    return {
        "status": "success",
        "product_id": product_id,
        "decision": clean_dataframe(
            matching
        )[0],
    }