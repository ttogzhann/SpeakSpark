# Browser E2E tests

Install the documented backend dependencies and frontend dependencies first. From the repository root:

```powershell
py -m pip install -r backend/requirements-dev.txt
npm --prefix frontend install
npm --prefix frontend run test:e2e
```

Windows uses installed Microsoft Edge (`msedge`) by default. Other platforms use Playwright Chromium; install it with `npm --prefix frontend exec playwright install chromium`. Set `E2E_BROWSER_CHANNEL` to choose an installed supported channel, or `E2E_PYTHON` to select a Python executable with the backend dependencies.

The command owns its services: it creates a fresh OS temporary directory and SQLite database, starts a separate Python backend on a free loopback port, and starts Vite on another free loopback port with its API proxy pointing only at that backend. It never reuses a developer backend/frontend. The test-only Python wrapper substitutes the database engine/session factory before importing the app, so application startup seeds only the temporary SQLite database. No production database setting is changed.

One real-browser tutor journey runs at 1280px and 375px: enter Library without accounts, combine filters and read details, use required-level/optional-type Surprise Me, save and view a Favorite, create a custom activity and find it in Library, enter/exit Focus Mode, and reload its persisted details. It does not mock API responses or duplicate component tests.

The runner exits with Playwright's failure code, shuts down its owned Vite/backend in `finally`, and removes its temporary database. It resolves the Python interpreter before launching so Windows' `py` launcher does not hide a server child. Interrupting an active test requests termination and then follows the same cleanup. Screenshots/traces from failed tests remain under ignored `frontend/test-results/e2e` for review.

Pass Playwright arguments through npm, for example `npm --prefix frontend run test:e2e -- --project=desktop` or `--headed`. Configuration follows [Playwright projects](https://playwright.dev/docs/test-projects) and [browser channels](https://playwright.dev/docs/browsers).
