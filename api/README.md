### Medical Telegram Warehouse API

This folder contains the FastAPI application that exposes analytical endpoints for the Telegram data warehouse.

## Structure

* `main.py` — Defines API routes and ties them to CRUD functions. Endpoints include:

  * `/api/reports/top-products` — Top mentioned products across channels.
  * `/api/channels/{channel_name}/activity` — Posting activity and trends for a channel.
  * `/api/search/messages` — Search messages by keyword.
  * `/api/reports/visual-content` — Image usage statistics per channel.

* `crud.py` — Functions that interact with the database using SQLAlchemy. Handles query logic for endpoints.
* `schemas.py` — Pydantic models for request/response validation.
* `database.py` — Database connection and session setup using SQLAlchemy.
* `test.py` — Simple script to test API queries without running the server.

## Run API

Start the server:

```bash
uvicorn main:app --reload
```

API docs are available at `http://127.0.0.1:8000/docs`.

