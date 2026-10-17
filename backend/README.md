# Backend — AI-Powered Utility Platform

Django REST API for the AI-Powered Utility Platform.

## Stack

- Python 3.12
- Django 6.1
- Django REST Framework
- SimpleJWT (auth)
- Celery + Redis (background jobs)
- PostgreSQL (production), SQLite (local fallback)
- Pillow, pypdf, qrcode (tool processing)

## Folder Structure

```
backend/
  apps/          Feature-based Django apps (accounts, image_tools, pdf_tools, ...)
  config/        Project settings (base, development, production), URLs, Celery
  core/          Shared core logic
  services/      Domain services (ai, email, image, notification, payment, pdf, storage)
  shared/        Shared helpers (enums, exceptions, permissions, responses, validators, ...)
  workers/       Celery worker tasks (ai, cleanup, emails, image, pdf)
  requirements/  Python dependencies (base.txt)
  tests/         Test suite
  manage.py      Django management entry point
```

## Prerequisites

- Python 3.12
- PostgreSQL and Redis (or run `docker compose up db redis` from the repo root)

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt
cp ../.env.development .env    # or set the required environment variables
python manage.py migrate
python manage.py runserver
```

## Environment Variables

Required variables (see `../.env.example`):

- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `SECRET_KEY`
- `DEBUG`

## Running Workers

```bash
celery -A config worker -l info
```

## API

The API is served under `/api/v1/`. See `config/urls.py` for registered routes and `docs/08-api-design.md` for API conventions.

## Documentation

Always follow the project documentation (`../docs/`) — start with `docs/00-README_FOR_AI.md`.
