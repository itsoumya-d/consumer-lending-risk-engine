# Consumer Lending Risk & Underwriting Engine

High-throughput, deterministic risk decisioning and affordability assessment service for unsecured consumer lending (credit cards and personal loans).

## Features
- **Deterministic Affordability Checks**: Real-time Debt-to-Income (DTI) and disposable income stress testing against benchmark living costs.
- **Credit Risk Classification**: Automated categorization into risk tiers (Tier A, Tier B, Tier C, Rejected) driven by credit score and delinquency signals.
- **Risk-Adjusted Pricing & Limits**: Dynamic calculation of maximum credit limit allowances and risk-adjusted APR bands.
- **Hard Exclusion Policy Rules**: Fast-fail rejection gates for bankruptcies, CCJs (County Court Judgments), and under-age applicants.
- **RESTful API**: FastAPI endpoints with comprehensive input validation via Pydantic v2.

## Quickstart

```bash
pip install -r requirements.txt
pytest -v
uvicorn app.main:app --reload --port 8000
```
