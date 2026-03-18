# Multi-Tenant Restaurant App with Django

<!-- START doctoc -->
<!-- END doctoc -->

[![Restaurant Tests](https://github.com/delitamakanda/restaurant/actions/workflows/restaurant_tests.yml/badge.svg?branch=main&event=push)](https://github.com/delitamakanda/restaurant/actions/workflows/restaurant_tests.yml)

## Table of Contents

- [Introduction](#introduction)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Logging](#logging)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Introduction

A Django-based multi-tenant REST API for managing restaurants, menus, meals, products, categories, orders, and users. The application exposes a read-only JSON API that serves data to front-end clients and supports webhook integrations.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.9+ |
| Framework | Django 4.2 |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL (via `psycopg2-binary`) |
| File Storage | Google Cloud Storage (`django-storages`) |
| Secrets | Google Cloud Secret Manager |
| WSGI Server | Gunicorn |
| Static Files | WhiteNoise |
| Logging | `structlog` + `python-json-logger` |
| Testing | pytest + pytest-django |
| CORS | `django-cors-headers` |

---

## Features

- **Multi-tenant architecture** — each restaurant is owned by a user and isolated accordingly.
- **REST API** — JSON endpoints for restaurants, menus, meals, products, categories, tags, users, and orders.
- **Pagination** — all list endpoints support `page` and `per_page` query parameters.
- **Search** — most list endpoints accept a `search` query parameter for filtering.
- **CSV export** — restaurants can be exported as a CSV file.
- **Webhook support** — receives and stores incoming webhook payloads with token-based authentication.
- **DDoS protection middleware** — rate-limits requests per IP (1000 requests per 60-second window).
- **Metrics middleware** — logs query count and response time for every request.
- **Soft deletes** — restaurants use a custom `AppManager` that excludes soft-deleted records.
- **Structured logging** — all logs are emitted in a structured format using `structlog`.

---

## Data Models

### User
Extends Django's `AbstractUser` with `contact_number` and `contact_email` fields.

### Restaurant
Core entity. Has a name, image URL, owning user, address, and many-to-many relationships with `Schedule`, `Category`, and `Menu`. Supports soft-delete.

### Category
Represents a restaurant category (e.g. Italian, Sushi). Includes a position for ordering and a default image URL.

### Menu
A named collection of `Meal` objects with a description.

### Meal
A named collection of `Product` objects with an ordering field.

### Product
An individual item with a name, price, image, description, and an optional `Supplement`.

### Supplement
An add-on for a product (e.g. extra sauce), with a name and price.

### Tags
Free-form labels associated with a `Restaurant`.

### Schedule
Opening hours for a restaurant, with day-of-week choices (MON–SUN) and begin/end times.

### Address
Delivery or location address linked to a `User`, with fields for street, locality, postal code, country, lat/lng, and timezone.

### Order / OrderItem
Tracks a customer order placed at a restaurant. Statuses: Canceled, Waiting for payment, In progress, Delivery in progress, Delivered, Waiting for consumer.

### WebhookMessage
Stores raw webhook payloads received via the webhook endpoint.

---

## API Endpoints

All endpoints are read-only (`GET`) unless noted otherwise.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root — lists all available endpoints |
| GET | `/hello` | Health-check / hello world |
| GET | `/api/restaurants/` | List all restaurants (paginated, searchable, filterable by category) |
| GET | `/api/restaurants/<id>/` | Get a single restaurant by UUID |
| GET | `/api/restaurants/csv/` | Download all restaurants as a CSV file |
| GET | `/api/categories/` | List all categories |
| GET | `/api/products/` | List all products (paginated, searchable) |
| GET | `/api/meals/` | List all meals (paginated, searchable) |
| GET | `/api/menus/` | List all menus (paginated, searchable) |
| GET | `/api/tags/` | List all tags |
| GET | `/api/users/` | List all users (paginated, searchable) |
| POST | `/api/webhook/` | Receive a webhook payload (requires `Webhook-Token` header) |

### Query Parameters

| Parameter | Endpoints | Description |
|-----------|-----------|-------------|
| `page` | restaurants, products, meals, menus, users | Page number (default: 1) |
| `per_page` | restaurants, products, meals, menus, users | Items per page |
| `search` | restaurants, products, meals, menus, users | Case-insensitive name filter |
| `categories` | restaurants | Filter by category UUID (repeatable) |

### Live API

[https://restaurantapi.applikuapp.com/](https://restaurantapi.applikuapp.com/)

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```dotenv
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:////path/to/db.sqlite3
STORAGE_BUCKET_NAME=your-gcs-bucket
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
WEBHOOK_TOKEN=your-webhook-token
```

| Variable | Description | Required |
|----------|-------------|----------|
| `DEBUG` | Enable/disable Django debug mode | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | Yes |
| `DATABASE_URL` | Database connection string (SQLite or PostgreSQL) | Yes |
| `STORAGE_BUCKET_NAME` | Google Cloud Storage bucket name | No |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | No |
| `WEBHOOK_TOKEN` | Token used to authenticate webhook requests | Yes (set a strong, random value in production) |

---

## Getting Started

### Prerequisites

- Python 3.9 or higher (3.10, 3.11, and 3.12 are also supported)
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/delitamakanda/restaurant.git
cd restaurant

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings
```

### Database Setup

```bash
python manage.py migrate
python manage.py adminuser   # Creates the default admin user (change credentials immediately after first login)
```

### Running the Development Server

```bash
python manage.py runserver
```

The API will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Running Tests

```bash
pytest
```

Tests are located in `coreapp/tests.py` and the `tests/` directory. The test suite uses `pytest-django` and requires no external services.

---

## Logging

The application uses [`structlog`](https://www.structlog.org/) for structured logging and `python-json-logger` for JSON-formatted output.

**Example usage:**

```python
import structlog

logger = structlog.getLogger()
logger.info('hello world', key='value', more=[1, 2, 3])
# 2023-06-25 21:15:19 [info     ] hello world    key=value more=[1, 2, 3]
```

Log levels and formats are configured in `logging.conf` and `restaurant/settings.py`.

---

## Deployment

The application is configured for deployment on [Heroku](https://heroku.com)-compatible platforms using a `Procfile`:

```
web:     gunicorn restaurant.wsgi --log-file -
release: bash release.sh   # runs migrations + creates admin user
```

### Production Settings

Set `DEBUG=False` and provide a PostgreSQL `DATABASE_URL` in your environment. The production settings module is located at `restaurant/settings_production.py`.

### Google Cloud Storage

To use GCS for media/static files, set `STORAGE_BUCKET_NAME` and `GOOGLE_CLOUD_PROJECT` in your environment and ensure the service account has the required permissions.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m "feat: add my feature"`.
4. Push to the branch: `git push origin feature/my-feature`.
5. Open a pull request.

Please make sure all tests pass before submitting a PR.
