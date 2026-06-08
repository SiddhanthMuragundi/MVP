# TDC Matchmaker — Backend

FastAPI service for the TDC Matchmaker tool: matchmaker auth, client management,
journey tracking, notes, a gender-specific matching engine, and an admin-managed,
provider-agnostic AI layer (match explanations, intro emails, and a chat assistant).

## Stack

- FastAPI + Uvicorn
- PostgreSQL + SQLAlchemy 2.0 (psycopg 3 driver)
- Argon2id password hashing, JWT auth (PyJWT), RBAC (admin / matchmaker)
- AES-256-GCM encryption for stored LLM API keys
- LLM providers (OpenAI / Anthropic / Gemini) called over HTTP, with a no-key fallback

## Run with Docker (recommended)

```bash
cp .env.example .env       # optional: defaults work out of the box
docker compose up --build
```

API: http://localhost:8000  ·  Interactive docs: http://localhost:8000/docs

The database is seeded automatically on first boot (idempotent).

## Run locally without Docker

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Point DATABASE_URL at a running Postgres, then:
uvicorn app.main:app --reload
```

## Seeded login credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Matchmaker | `priya` | `priya123` |

The admin can additionally open the LLM settings to configure a provider/key/model.

## Configuring AI (optional)

AI features work without a key (deterministic templates). To enable real LLM output,
log in as **admin** and call `PUT /api/settings/llm` with a provider, API key, and model
(`GET /api/settings/llm/models` lists what's available for a provider). The key is stored
encrypted and never returned to clients.

## Key endpoints

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/auth/login` | returns JWT |
| GET | `/api/customers` | dashboard list (filters: `search`, `stage`, `verified`) |
| GET | `/api/customers/{id}` | full biodata + notes |
| PATCH | `/api/customers/{id}/stage` | update journey stage |
| POST | `/api/customers/{id}/notes` | add a note |
| GET | `/api/customers/{id}/matches` | ranked matches with AI explanations |
| POST | `/api/customers/{id}/matches/{candidate_id}/assign` | shortlist a match |
| POST | `/api/matches/send` | mock "Send Match" email |
| GET/PUT | `/api/settings/llm` | admin-only LLM config |
| GET | `/api/settings/llm/models` | admin-only live model list |
| POST | `/api/chat` | Match Assistant (search / ask / draft) |

## Tests

```bash
pip install pytest
pytest
```
