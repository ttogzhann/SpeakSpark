# Frontend component tests

Run from the repository root:

```powershell
npm --prefix frontend test
npm --prefix frontend run build
```

The existing Vitest, React Testing Library and jsdom suite covers primary tutor interactions. Earlier feature tests count toward coverage; this suite does not need duplicate tests for already covered contracts.

| Area | Files in `frontend/src` |
| --- | --- |
| Default/direct section URLs and current navigation | `App.test.tsx` |
| Backend-driven cards, combined/cleared filter queries, loading/empty/error and stale results | `Library.test.tsx` |
| Favorite membership, both sources, shared views, failed/pending mutations and stale list responses | `Favorites.test.tsx` |
| Creation payloads for all types, blank optional fields, invalid input, rejection, pending duplicate prevention | `ActivityForm.test.tsx` |
| Edit/cancel/read-only protection, rejected edits, named delete/cancel/failure/pending | `ActivityChanges.test.tsx` |
| Saved custom edits/deletion coordinated with Favorites across navigation | `SavedActivityFlow.test.tsx` |
| Required random level, optional type, selected/Next/exhausted/restart/no-match/error and stale filters | `SurpriseMe.test.tsx` |
| Single-detail endpoint, guidance applicability/empty fields, errors and stale IDs | `ActivityDetail.test.tsx` |
| Focus presentation, hidden controls, source/focus restoration and no extra requests | `FocusMode.test.tsx` |

Every backend response is provided by a per-test fetch mock. Shared setup installs a fail-closed fallback and fails any test that accidentally uses an unmocked request, preventing contact with a live backend or developer SQLite. Deferred promises explicitly exercise pending and out-of-order responses. Cleanup unmounts test views and restores globals; route tests reset their jsdom URL. Mock backend records exist only inside their test and require no persistent browser storage.

Component tests verify behavior and request contracts, not real CSS geometry or backend implementation. Browser acceptance and real persistence belong to the separate E2E/independent QA workflow.
