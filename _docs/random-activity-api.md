# Random activity API

`POST /random-activities/next?level=A1` draws from built-in and custom SQLite activities.
`level` is required (`A1`, `A2`, `B1`, `B2`). Optional query `type` accepts
`Conversation Cards`, `Role-play Scenarios`, or `Speaking Challenges`, matching the
library filters. Missing or invalid filters return 422 without advancing history.

Successful draws return HTTP 200 with `{"status":"selected","activity":...}`;
`activity` uses the same complete response as the library and detail endpoints.
Each remaining eligible record has equal probability, regardless of source.

For N eligible records, the first N requests return distinct activities. The next
request returns `{"status":"exhausted","activity":null}`. The following explicit
request starts another cycle. Empty pools return
`{"status":"no_matches","activity":null}`. Changing either filter immediately
starts a fresh cycle, including returning to previously used filters.

One cycle is shared by the local tutor workspace within a backend process. History
is held in memory and resets when the backend restarts; run one backend process for
this single-workspace MVP. The backend serializes concurrent selection transitions.
There is no client-side history or saved speaking session.

Empty requests remain `no_matches` on repetition. Each draw reads current SQLite
activities: a newly created matching custom activity becomes selectable immediately;
deleting the last matching custom activity produces `no_matches` on the next draw.
An empty pool never falls back to another level or type.

Moving from populated filters to empty filters and back starts fresh history.
Validation occurs before the selector runs, so invalid requests preserve the active
history even when they contain a different valid level plus an invalid type. These
requests also preserve the pending exhaustion boundary. Selection and all response
states only change in-memory selector history; activities and Favorites are read-only
during selection. CRUD retains its existing independent persistence behavior.
