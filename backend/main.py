from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, UploadFile

DB = Path("data/pulseboard.db")
DB.parent.mkdir(parents=True, exist_ok=True)
REQUIRED = {"deal_id", "company", "sector", "status", "value", "close_date"}

app = FastAPI(title="PulseBoard API", version="1.0.0")


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def validate(df: pd.DataFrame) -> dict[str, Any]:
    missing = sorted(REQUIRED - set(df.columns))
    duplicate_count = int(df["deal_id"].duplicated().sum()) if "deal_id" in df else 0
    invalid_value = int((pd.to_numeric(df["value"], errors="coerce").isna()).sum()) if "value" in df else len(df)
    invalid_dates = int(pd.to_datetime(df["close_date"], errors="coerce").isna().sum()) if "close_date" in df else len(df)
    return {
        "rows": len(df),
        "missing_columns": missing,
        "duplicate_deal_ids": duplicate_count,
        "invalid_values": invalid_value,
        "invalid_dates": invalid_dates,
        "valid": not missing and duplicate_count == 0 and invalid_value == 0 and invalid_dates == 0,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate")
async def validate_upload(file: UploadFile = File(...)):
    raw = await file.read()
    from io import BytesIO
    df = pd.read_excel(BytesIO(raw)) if file.filename.lower().endswith((".xlsx", ".xls")) else pd.read_csv(BytesIO(raw))
    return validate(normalize(df))


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    raw = await file.read()
    from io import BytesIO
    df = pd.read_excel(BytesIO(raw)) if file.filename.lower().endswith((".xlsx", ".xls")) else pd.read_csv(BytesIO(raw))
    df = normalize(df)
    result = validate(df)
    if not result["valid"]:
        return {"accepted": False, "validation": result}
    df["close_date"] = pd.to_datetime(df["close_date"]).dt.strftime("%Y-%m-%d")
    df["value"] = pd.to_numeric(df["value"])
    with sqlite3.connect(DB) as conn:
        df.to_sql("deals", conn, if_exists="replace", index=False)
    return {"accepted": True, "validation": result, "stored_rows": len(df)}


@app.get("/kpis")
def kpis():
    if not DB.exists():
        return {"records": 0, "total_value": 0, "avg_value": 0, "by_status": {}}
    with sqlite3.connect(DB) as conn:
        try:
            df = pd.read_sql_query("SELECT * FROM deals", conn)
        except Exception:
            return {"records": 0, "total_value": 0, "avg_value": 0, "by_status": {}}
    return {
        "records": int(len(df)),
        "total_value": float(df["value"].sum()),
        "avg_value": float(df["value"].mean()) if len(df) else 0,
        "by_status": df["status"].value_counts().to_dict(),
        "by_sector": df["sector"].value_counts().to_dict(),
    }
