# SpeakSpark

SpeakSpark helps English tutors find, save, create, and present speaking activities for CEFR levels A1-B2. It runs as one local tutor workspace, with no login or registration.

## Features

- Browse 36 built-in activities and your custom activities in **Library**, combining level, topic, and activity-type filters.
- Use Conversation Cards, Role-play Scenarios, and Speaking Challenges across eight predefined topics.
- Select matching activities in **Surprise Me**, without repeats until the current cycle finishes.
- Save activities in **Favorites** and create, edit, or delete custom activities in **My Activities**.
- Present an activity and its relevant guidance in **Focus Mode**, then return to the same context.

Built-in activities are read-only. Deleting a custom activity also removes its Favorite.

## Run locally

Install Python and Node.js with npm. The commands below use Windows PowerShell and the Python `py` launcher. Run them from the repository root; use your Python executable instead of `py` if needed.

Install dependencies:

```powershell
py -m pip install -r backend/requirements-dev.txt
npm --prefix frontend install
```

Start the backend in one terminal:

```powershell
py -m uvicorn app.main:app --app-dir backend --reload
```

Start the frontend in another terminal:

```powershell
npm --prefix frontend run dev
```

Open the frontend URL printed by Vite, normally **http://localhost:5173**. The backend runs at **http://127.0.0.1:8000**, with interactive API documentation at **http://127.0.0.1:8000/docs** and a health check at **http://127.0.0.1:8000/health**. Keep both terminals running; press Ctrl+C to stop each server.

The frontend sends `/api/*` requests through Vite's proxy to backend port 8000, removing the `/api` prefix. Keep that backend port for these development commands. See [frontend connection notes](frontend/README.md). A built static frontend needs the same API forwarding from its serving environment.

## Local data and architecture

The frontend uses React, TypeScript, Vite, and Tailwind CSS. The backend uses FastAPI and Pydantic, with SQLite through SQLAlchemy. The backend owns filtering, validation, custom CRUD, Favorites, and random selection; the frontend owns interaction and presentation.

Backend startup creates `backend/data/speakspark.db` and seeds the built-in library. Custom activities and Favorites persist there after closing the browser. Removing the database removes saved local data. There are no accounts, cloud synchronization, sharing, or student tracking.

Run one backend process for this workspace. Random-cycle history is held in that process and resets when it restarts; it is not a saved lesson session. Changing filters starts a fresh cycle, and exhaustion offers an explicit restart. See the [random API behavior](_docs/random-activity-api.md).

## Tests and build

Run from the repository root:

```powershell
py -m pytest -c backend/pyproject.toml backend/tests
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run test:e2e
```

The production frontend build is written to `frontend/dist`. The E2E command starts and cleans up its own frontend/backend with a temporary SQLite database. On Windows it uses installed Microsoft Edge by default; other platforms need Playwright Chromium installed with `npm --prefix frontend exec playwright install chromium`. See [E2E setup and browser options](_docs/e2e-tests.md).

## Project guide

- [Approved MVP specification](_docs/plan.md) and [architecture decisions](_docs/decisions.md).
- [Development workflow](_docs/process.md); GitHub Issues are the active backlog.
- [Backend tests](_docs/backend-tests.md), [frontend component tests](_docs/frontend-tests.md), and [browser E2E tests](_docs/e2e-tests.md).
- [Final MVP review and verification evidence](_docs/mvp-review.md).
