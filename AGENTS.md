# SpeakSpark

SpeakSpark is an MVP web app for English tutors to browse, filter, save, create, and present speaking activities for CEFR levels A1–B2. Preserve the approved MVP scope in [_docs/plan.md](_docs/plan.md).

## Approved architecture

- Frontend: React, TypeScript, Vite, and Tailwind CSS.
- Backend: Python, FastAPI, and Pydantic REST API.
- Persistence: SQLite with SQLAlchemy; built-in activities, custom activities, and Favorites are served and persisted through the backend.
- One local tutor workspace; no login, registration, authentication, user accounts, or cloud sync.
- Backend owns activity filtering, validation, CRUD, and random selection with repeat prevention and cycle reset. Frontend owns Focus Mode and presentation.
- Architecture decisions are documented in [_docs/decisions.md](_docs/decisions.md).

## Development commands

The application project and its command conventions are not established yet. Do not assume or invent commands; update this section when they are defined.

- Install dependencies: **pending**
- Run backend tests (`pytest`): **pending**
- Run frontend tests (`Vitest` + React Testing Library): **pending**
- Run end-to-end tests (`Playwright`): **pending**
- Run the backend and frontend: **pending**

## Essential rules

- Use the approved architecture and keep changes within the MVP; do not add features from the future-improvements or out-of-scope lists.
- Keep built-in activities read-only. Custom activity deletion must also remove its Favorites.
- Keep activity types and required/optional fields consistent with the plan.
- Add or update focused tests for behavior changes; report failures rather than hiding them.
- GitHub Issues are the only active backlog. Do not recreate a local task list; use [_docs/process.md](_docs/process.md) for the work process.
- Read [_docs/plan.md](_docs/plan.md) and [_docs/decisions.md](_docs/decisions.md) before making product or architecture changes. If they conflict, decisions.md takes precedence.
