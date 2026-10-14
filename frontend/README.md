# Running the frontend locally

From the repository root, start the existing backend with:

```powershell
py -m uvicorn app.main:app --app-dir backend --reload
```

Start the frontend in another terminal:

```powershell
npm --prefix frontend run dev
```

The frontend requests `/api/activities` on its own origin. Vite proxies `/api/*` to `http://127.0.0.1:8000/*`, removing the `/api` prefix. The same proxy is configured for Vite preview. Keep the backend running on port 8000. This avoids cross-origin browser requests while retaining the separate development commands.

The built static bundle requires a server that provides the same `/api` forwarding convention; Vite's development proxy is not embedded in the bundle.

Section URLs use hashes: `/#/library`, `/#/surprise-me`, `/#/favorites`, and `/#/my-activities`. Library cards open `/#/library/<encoded activity ID>`. Details request `/api/activities/<encoded activity ID>` independently of the Library collection, show the required fields and applicable optional guidance, and provide a link back to Library. Direct loading and refreshing a detail URL work through the same endpoint.
