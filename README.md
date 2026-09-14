# PulseBoard — Portfolio Data Pipeline & Ops Dashboard

PulseBoard is a portfolio-operations data pipeline that ingests heterogeneous CSV/Excel files, validates and normalizes records, persists clean data, and exposes KPI reporting through a FastAPI service and React dashboard.

## Features
- CSV and Excel ingestion with schema normalization.
- Validation for required fields, data types, dates, and duplicate records.
- SQLite persistence for a lightweight reproducible demo; PostgreSQL can be configured for deployment.
- FastAPI endpoints for portfolio records, validation results, and KPI summaries.
- React dashboard with asynchronous API loading, filters, KPI cards, and charts.
- Batch reconciliation report for measuring rejected rows and data-quality trends.

## Pipeline
`CSV/XLSX → parser → schema validation → normalization → SQLite/PostgreSQL → FastAPI → React dashboard`

## Run backend
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

The sample dataset is synthetic. Reported performance figures are target/demo measurements and should be reproduced with the benchmark script before being presented as production results.
