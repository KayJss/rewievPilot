# ReviewPilot

ReviewPilot is a small SaaS MVP for collecting customer feedback through location-specific links and turning responses into a simple business dashboard.

## Paid-product angle

The MVP already models three tiers:

| Plan | Locations | Feedback allowance |
| --- | ---: | ---: |
| Trial | 1 | 50 |
| Starter | 1 | 500 |
| Growth | 5 | 5000 |

A real commercial version can attach these limits to Stripe or iyzico subscriptions.

## Features

- Business workspace creation
- Multi-location model
- Unique feedback tokens
- 1–5 ratings
- Feedback categories
- Comments
- Dashboard metrics
- Recent feedback
- Lightweight insights
- Plan limits
- `/health` endpoint
- Service-layer tests

## Stack

Python 3.10+, FastAPI, SQLite, Jinja2, Vanilla CSS, unittest.

## Run

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Test

```bash
python -m unittest discover -s tests -v
```

## Roadmap

- Authentication
- Real QR generation
- Stripe / iyzico billing
- Billing-period usage limits
- Low-rating email alerts
- AI monthly summaries
- CSV/PDF export
- PostgreSQL + Alembic
- Docker deployment
- Rate limiting and audit logs

## License

Copyright © 2026 KayJss. **All Rights Reserved.**

This is proprietary source code. Public visibility does not grant permission to copy, modify, redistribute, host, sell, or use this project commercially or privately. See [`LICENSE`](LICENSE).
