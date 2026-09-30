from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/evaluation",
    tags=["Model Evaluation"],
)


BASE_DIR = Path(__file__).resolve().parents[2]

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "model_evaluation_report.csv"
)


def load_evaluation_report():

    if not REPORT_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Model evaluation report not found. "
                "Run model_evaluation.py first."
            ),
        )

    try:

        df = pd.read_csv(
            REPORT_FILE
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not read evaluation report: {exc}"
            ),
        )

    if df.empty:

        raise HTTPException(
            status_code=404,
            detail="Model evaluation report is empty.",
        )

    return df


def clean_records(df):

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
def get_model_evaluation():

    df = load_evaluation_report()

    return {
        "status": "success",
        "count": len(df),
        "models": clean_records(df),
    }


@router.get("/{model_name}")
def get_model_evaluation_by_name(
    model_name: str,
):

    df = load_evaluation_report()

    if "model" not in df.columns:

        raise HTTPException(
            status_code=500,
            detail="Model column not found.",
        )

    matching = df[
        df["model"]
        .astype(str)
        .str.lower()
        .str.replace(
            " ",
            "-",
        )
        == model_name.lower()
    ]

    if matching.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Model evaluation not found: "
                f"{model_name}"
            ),
        )

    return {
        "status": "success",
        "model": clean_records(
            matching
        )[0],
    }