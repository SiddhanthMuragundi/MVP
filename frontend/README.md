# TDC Matchmaker — Frontend (Vue)

Vue 3 + Vite + Pinia + Vue Router + Tailwind. Talks to the FastAPI backend in `../backend`.

## Setup

```bash
npm install
cp .env.example .env      # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev               # http://localhost:5173
```

Make sure the backend is running first (`cd ../backend && docker compose up`).

## Scripts

- `npm run dev` — dev server with HMR
- `npm run build` — production build to `dist/`
- `npm run preview` — serve the production build
- `npm run typecheck` — `vue-tsc` type check

## Seeded logins

| Role | Username | Password |
|------|----------|----------|
| Matchmaker | `priya` | `priya123` |
| Admin | `admin` | `admin123` |

Admins additionally see the **Settings** page to configure the LLM provider/key/model.

## Structure

- `src/api/` — the only backend-aware layer (axios + JWT interceptor, per-resource modules)
- `src/stores/auth.ts` — Pinia auth/session store
- `src/router/` — routes + auth/admin guards
- `src/views/` — Login, Dashboard, CustomerDetail, Settings
- `src/components/` — design-system atoms + feature components (MatchCard, ChatPanel, …)
- `src/lib/format.ts` — labels and stage/tier colors
- `tailwind.config.js` — the maroon/gold matrimonial theme
