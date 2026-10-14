# Backend test coverage

Run from the repository root:

```powershell
py -m pytest -c backend/pyproject.toml backend/tests
```

The committed suites cover the MVP areas below. Existing endpoint tests remain the primary contract coverage; cross-feature regressions exercise transitions between contracts.

| Area | Committed test files in `backend/tests` |
| --- | --- |
| Individual/combined filters, omitted/invalid filters, empty lists | `test_activity_list_endpoint.py` |
| Schema validation and custom create/update/delete, unknown IDs, built-in protection | `test_activity_model.py`, `test_custom_activity_creation.py`, `test_custom_activity_update.py`, `test_custom_activity_delete.py`, `test_single_activity_endpoint.py` |
| Both Favorite sources, duplicate add, removal, empty collections, deletion cleanup | `test_favorites_endpoints.py`, `test_favorites_listing_contract.py`, `test_mvp_cross_feature_regressions.py` |
| Matching random results, equal source eligibility, unique cycles/exhaustion/restart, filter changes, empty pools, invalid requests | `test_random_selection.py`, `test_random_selection_transitions.py` |
| Saved activity edits across filters/random/Favorites, atomic invalid nested updates, custom Favorite removal without activity deletion | `test_mvp_cross_feature_regressions.py` |
| SQLite configuration, seed/content contract and persistence | `test_database_config.py`, `test_persistence_models.py`, `test_builtin_activities.py`, `test_smoke.py` |

Database tests use pytest `tmp_path` SQLite files or isolated test databases, overriding `get_db` and restoring overrides in fixture cleanup. Random API fixtures provide a fresh `RandomActivitySelector` through its dependency override and restore previous overrides afterward. API tests do not enter application lifespan/startup against the developer database. Deterministic cycle assertions compare eligible sets rather than random ordering; tests that require a particular draw monkeypatch the choice function.

The user's unrelated untracked `test_favorites_listing.py` is not needed for any acceptance area. To verify the delivered files alone without moving or modifying unrelated tests, pass the tracked test paths to pytest (include a newly added test only after it is staged/committed):

```powershell
$backendTrackedTests = git ls-files -- backend/tests/test_*.py
py -m pytest -c backend/pyproject.toml $backendTrackedTests
```
