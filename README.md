# Saathiya

Saathiya is an internal tool for matchmakers. A matchmaker signs in, manages a roster of
clients, opens a full biodata profile, reviews ranked match suggestions, records notes from
calls and meetings, and sends an introduction email.

## Live application

The application is live at **https://serene-charisma-production-6dd4.up.railway.app**

No setup is required to use it. Sign in with one of the sample accounts below. The API
documentation is available at https://mvp-production-f385.up.railway.app/docs, and the
introduction emails sent by the Send Match action can be viewed in the demo inbox at
https://mailpit-production-e4f3.up.railway.app.

| Role       | Username | Password   | Access                                                         |
| ---------- | -------- | ---------- | -------------------------------------------------------------- |
| Admin      | `admin`  | `admin123` | Read-only oversight of all clients; configures the AI provider |
| Matchmaker | `priya`  | `priya123` | Works only the clients assigned to this matchmaker             |
| Matchmaker | `rahul`  | `rahul123` | Works only the clients assigned to this matchmaker             |

The admin is a read-only overseer who configures AI but does not act on individual clients.
Each matchmaker can view the full roster but can act only on their own assigned clients.

## What it does

The dashboard lists clients with their key details and supports live filters (gender, state,
city, language, religion, marital status, age range, journey stage, and verification) that
are derived from the actual data rather than hardcoded; selecting a state narrows the city
options to that state. Opening a client shows their complete biodata, journey stage,
verification, notes, and matches in one place.

The matching engine produces ranked, gender-specific suggestions from the opposite-gender
client base, each shown with a compatibility tier and the specific reasons behind it. A
matchmaker can shortlist a candidate (reversible), send an editable introduction email (a
one-way action, delivered to a local inbox in the demo), and then record the outcome. An
optional AI layer adds match explanations, drafted introduction emails, and a grounded
assistant that answers questions about a client and their candidates.

## Technology

| Layer          | Technology                                                     |
| -------------- | -------------------------------------------------------------- |
| Frontend       | Vue 3, Pinia, Vue Router, Tailwind CSS                         |
| Backend        | FastAPI, SQLAlchemy 2.0, Pydantic v2                           |
| Database       | PostgreSQL 16 (psycopg 3 driver)                               |
| Authentication | JWT (HS256, PyJWT), Argon2id password hashing                  |
| AI             | Provider-agnostic LLM layer (OpenAI, Anthropic, or Gemini)     |
| Email          | SMTP, using Mailpit as a local inbox in the demo environment   |
| Deployment     | Docker (database, backend, frontend, and mail run as services) |

## Matching logic

Matching is deterministic and weighted, with no AI involved in the ranking, so the same
inputs always produce the same ordered result. The logic is gender-specific: the engine uses
two rule sets, one for a male client matching women and one for a female client matching men,
each summing to 100.

The weighting reflects the priorities that drive matchmaking in the Indian context.
Community (religion and caste) is the dominant signal, together accounting for 41 of the 100
points; economics, mother tongue and home region, the current city, marital-status fit,
family intent, and lifestyle form the tiers below it. Scoring is soft rather than
exclusionary: a lower-weighted attribute such as a different community reduces a match's
position but never removes it, so cross-community matches still surface. The weights are
isolated in a single configuration file and can be re-tuned without code changes, and the
engine only ranks and suggests, leaving the final decision to the matchmaker. The
approximate weighting by factor group (out of 100) is:

| Factor group                                 | Male client | Female client |
| -------------------------------------------- | :---------: | :-----------: |
| Religion and community                       |     41      |      41       |
| Economics (income, education and profession) |      9      |      10       |
| Mother tongue and home region                |      8      |       7       |
| Current city and relocation                  |      7      |      10       |
| Children and family intent                   |      9      |       6       |
| Marital-status compatibility                 |      7      |       7       |
| Lifestyle (diet, smoking, drinking)          |      9      |      12       |
| Age                                          |      6      |       3       |
| Height and shared interests                  |      4      |       4       |

Before scoring, every candidate must pass hard gates (opposite gender, an age window, and
availability) and is drawn from the opposite-gender client base. Each suggestion is then
placed in a tier and shown with the specific reasons that produced it.

## Artificial intelligence

The AI layer is provider-agnostic and optional. It is used in three additive ways: to
explain why a ranked match fits, to draft a personalised introduction email that the
matchmaker can edit before sending, and to power a grounded assistant that answers questions
using only the data it is given. The matches themselves are identical with or without AI,
because the language model never participates in ranking. Provider API keys are encrypted at
rest with AES-256-GCM, masked in the interface, and never displayed again after saving.

## Running locally

Docker is the only prerequisite. From the repository root:

```bash
docker compose up --build
```

Once the services are healthy, open:

| Service              | URL                        |
| -------------------- | -------------------------- |
| Application          | http://localhost:5173      |
| API documentation    | http://localhost:8000/docs |
| Mail inbox (Mailpit) | http://localhost:8025      |

## What happens on first run

On the first start, the database is created and seeded automatically with the matchmaker
accounts and a set of client profiles, so the application is usable immediately with no
manual steps. AI features remain off until an administrator configures a provider: until
then, the application uses built-in text templates, and, as noted above, the match rankings
are the same whether or not AI is enabled.

## Configuring AI (optional)

Sign in as the administrator and open AI Settings. Choose a provider, paste an API key, load
the available models (fetched live from the provider), choose one, and save. The key is
encrypted before storage and is never shown again.

## Deployment

The application deploys to Railway or Render; a `render.yaml` blueprint is included for the
latter. Both backend and frontend build from their Dockerfiles. The backend reads the
platform-provided `PORT` and accepts a standard `postgresql://` connection string; the
frontend bakes `VITE_API_BASE_URL` in at build time.

Railway: create a project from this repository and add a PostgreSQL database. Add a service
with root directory `backend` and set `DATABASE_URL` (referencing the database), `JWT_SECRET`,
and `CORS_ORIGINS` (the frontend URL); Railway injects `PORT`. Add a second service with root
directory `frontend` and set the build variable `VITE_API_BASE_URL` to the backend URL
followed by `/api`.

Render: use the `render.yaml` blueprint (New, then Blueprint). It provisions the database, the
backend as a Docker service, and the frontend as a static site. After the first deploy, set
`CORS_ORIGINS` on the backend to the frontend URL, and `VITE_API_BASE_URL` on the frontend to
the backend URL followed by `/api`.

## Project structure

```
.
├── backend/
│   └── app/
│       ├── core/        # security (JWT, password hashing) and key encryption
│       ├── models/      # SQLAlchemy ORM models
│       ├── schemas/     # Pydantic request and response models
│       ├── routers/     # auth, customers, matches, notes, team, notifications, settings, chat
│       ├── services/    # matching engine and weights, LLM layer, mailer, activity log
│       ├── seed/        # generator for culturally coherent client profiles
│       └── main.py
├── frontend/
│   └── src/
│       ├── views/       # pages: login, dashboard, customer detail, settings
│       ├── components/  # reusable interface components
│       ├── stores/      # Pinia state
│       ├── api/         # backend API clients
│       └── router/
└── docker-compose.yml
```

## Environment variables

Defaults are suitable for local development; override them in a hosted environment.

| Variable                      | Purpose                                       | Default                    |
| ----------------------------- | --------------------------------------------- | -------------------------- |
| `JWT_SECRET`                  | Token signing secret                          | development value          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime, in minutes             | 480 (eight hours)          |
| `ENCRYPTION_KEY`              | Base64 32-byte AES key for encrypting AI keys | derived development key    |
| `DATABASE_URL`                | PostgreSQL connection string                  | provided by Docker Compose |
| `CORS_ORIGINS`                | Allowed frontend origins                      | http://localhost:5173      |
| `SMTP_HOST`, `SMTP_PORT`      | Outgoing mail server                          | Mailpit                    |
