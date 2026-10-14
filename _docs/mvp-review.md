# Final MVP integration review

Reviewed 2026-10-14 against `_docs/plan.md` and `_docs/decisions.md` (decisions take precedence), on implementation commit `f9c1634`. This is a review evidence artifact, not a backlog. No product changes were made during this review.

## Compliance evidence

| Criterion | Current implementation and verification evidence |
| --- | --- |
| 1. Approved stack and local workspace | `frontend/package.json`, `vite.config.ts`, `src/main.tsx`: React/TypeScript/Vite/Tailwind. `backend/requirements.txt`, `app/main.py`, `schemas/activity.py`: FastAPI/Pydantic. `database_config.py`, `models/`: SQLite/SQLAlchemy. Current frontend build and isolated startup/E2E checks pass. |
| 2. Complete MVP features | `Library.tsx` supplies backend-driven cards and combined filters; `SurpriseMe.tsx` supplies selection; `Favorites.tsx` supplies saved activities; `MyActivities.tsx`/`ActivityForm.tsx` supply custom CRUD; `ActivityDetail.tsx`/`ActivityContent.tsx` supply details; `FocusMode.tsx` supplies presentation. Current component suite and real desktop/mobile E2E journey pass. Individual CRUD/cycle acceptance was independently exercised in issues #25/#26 and remains covered by committed tests. |
| 3. Built-ins read-only/custom mutation cleanup | `app/main.py` rejects built-in updates/deletion and deletes related Favorites with custom records. `database.py` installs built-in protection triggers; `CustomActivity.favorites` also has delete-orphan cascade. UI exposes edit/delete only in the custom collection and guards manipulated built-in form selection. Current custom CRUD, persistence, Favorites contract and cross-feature tests pass. |
| 4. Random behavior | `app/random_selection.py` builds the eligible pool in SQL, shares equal record eligibility, prevents repeats with a process-local seen set, clears on filter change/exhaustion and returns explicit no_matches. `SurpriseMe.tsx` sends plural type/required level, clears stale display, and requires explicit restart. `test_random_selection.py`/`test_random_selection_transitions.py` and current UI/E2E tests pass. |
| 5. No authentication/accounts | Reviewed app routes, models and four-section shell: no login/register/auth routes, account model, tenant/user IDs or account setup. E2E opens Library immediately and follows the complete journey without credentials. |
| 6. No future-scope flows | Reviewed frontend components, API routes and model inventory: no AI generation, student profiles, saved speaking sessions, sharing, synchronization, progress tracking, recording or timers. Test-only E2E lifecycle routes exist only inside the separately launched test wrapper, not production `app.main`. |
| 7. Responsibility boundary | `Library.tsx` builds query parameters and renders backend results; it does not implement filter matching. Backend `main.py`/Pydantic handle validation/CRUD/Favorites; selector owns random/cycles; SQLAlchemy owns persisted data. Frontend owns navigation, forms, request UX and Focus Mode. Classifying the custom-only My Activities presentation does not replace backend activity filtering. |
| 8. Real browser reopen persistence | Independent QA supplied actual runtime command/result below: custom creation and Favorite survive closing the entire Edge browser and launching a new browser against the same isolated SQLite-backed server. This is distinct from the committed E2E's simpler page-reload check or React in-memory navigation. Backend persistence/cross-feature tests also reopen sessions/API clients. |
| 9. Local data-model scope | `models/__init__.py` exports only BuiltInActivity, CustomActivity and Favorite. Default SQLite path is backend-owned `backend/data/speakspark.db`; no user, device, session or cloud tables/services are present. Favorite membership is stored by activity ID, not browser storage. |
| 10. Handoff and scaffold baseline | Existing #1 is already closed; its scaffold was verified rather than recreated. Frontend/backend directories, Vite/TypeScript config, FastAPI health and SQLite configuration exist. Current `test_smoke.py` initializes an isolated DB, verifies `/health` and 36 seeds; `App.test.tsx` verifies the rendered/default workspace; frontend build and E2E verify runnable integration. Final commands below pass. No review mismatch requiring a scope-changing follow-up was found. |

## Current command results

All commands ran from the repository root against the current implementation. Runtime data/services were isolated.

| Command | Actual result |
| --- | --- |
| `py -m pytest -c backend/pyproject.toml backend/tests` | Exit 0; 120 passed, 2 existing FastAPI on_event deprecation warnings in 14.87s. Includes 3 unrelated untracked user tests. |
| `npm --prefix frontend test` | Exit 0; 67 passed in 9 files; duration 7.38s. Backend calls are mocked/fail-closed. |
| `npm --prefix frontend run build` | Exit 0; TypeScript passed; Vite built 25 modules in 520ms. |
| `npm --prefix frontend run test:e2e` | Exit 0; 2 passed in 15.0s (desktop1280px 5.5s, mobile375px 5.0s). Windows default installed Edge channel; no channel environment override. Runner owns temporary SQLite, new backend process/random state and dynamic-port frontend; it cleans them up. |
| Independent QA: `node "$env:TEMP/speakspark-qa19/qa31-persistence.cjs"` | QA-reported exit 0 in 9.26s: actual UI POST201 and Favorite; entire Edge browser closed/relaunched; same custom record and Favorite restored from the same QA-only SQLite backend. Favorites/detail/My Activities and membership checked; localStorage/sessionStorage empty; no auth. This is QA-provided evidence, not a claim that Engineer executed that command. |

The backend result does not depend on the user's untracked file for compliance: all mapped behaviors are in committed tests. The unchanged committed backend suite was separately verified in #28 with `git ls-files -- backend/tests/test_*.py` passed to pytest: 117 passed, 2 warnings in 22.32s. See `_docs/backend-tests.md`, `_docs/frontend-tests.md` and `_docs/e2e-tests.md` for reproducible coverage/commands. The unrelated test remains untouched and unstaged (SHA256 `DCEDBAD49C16F1326A38E4E3CE0C55433004362CBC5C1C3DE356AA68CE9E3DB1`).

## Practical limits and readiness

The app is one local tutor workspace without authentication or cloud synchronization. Run a single backend process: random history is process-local and resets on backend restart, as documented in `_docs/random-activity-api.md`; it is not a saved speaking session. Favorites/custom records persist in SQLite. Deleting the local database removes that data. A built static frontend needs the documented `/api` forwarding convention; Vite dev/preview already provides it. Browser E2E uses installed Edge on Windows or an installed Playwright Chromium elsewhere. Existing FastAPI startup deprecation warnings remain visible; no failures were suppressed.

The implementation matches the approved MVP and is ready for local handoff, subject to the independent final QA verdict on issue #31. No feature expansion, architecture rewrite or local backlog was introduced. Independent QA must publish its own criterion-by-criterion evidence before the issue is closed.
