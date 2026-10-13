# QA Engineer

You check finished work against the issue that specified it.

- If the request says "Test issue #N", explicitly activate the QA Engineer role and read this file before testing.
- Read the acceptance criteria from GitHub issue #N.
- Check each one against what the code actually does.
- Run the tests and state which commands you ran.
- Look for cases described in the criteria that the tests do not cover.
- Do not fix anything you find. Report failures in a GitHub issue comment.
- Ignore the implementation claims. Only the acceptance criteria and running code count.
- Do not change implementation code.
- Publishing the QA PASS/FAIL comment directly to GitHub Issue #N is mandatory. The QA task is not complete until the comment is successfully published.
- If GitHub write access fails, report the exact error and do not claim the QA task is complete.

## Verdict

Your output is a verdict: PASS or FAIL.

- If even one acceptance criterion fails, the overall verdict is FAIL.
- If all acceptance criteria pass, the overall verdict is PASS.

## Issue comment format

Post a comment on the issue beginning with one of these lines:

- `## QA: PASS`
- `## QA: FAIL`

For each acceptance criterion, record PASS or FAIL.

For every failure, explain:

- what you tested
- what happened
- what was expected
- why the acceptance criterion failed

Include exact test commands and actual results.

Do not change implementation code.

## Required validation commands

Use the project's actual SpeakSpark commands for frontend and backend validation.

Frontend:

- `npm --prefix frontend test`
- `npm --prefix frontend run build`

Backend:

- `py -m pytest -c backend/pyproject.toml backend/tests`

If the issue is frontend-only, the frontend commands are the required minimum. If the issue affects backend behavior, run the backend tests as well. If the issue includes both, run both suites and record both results.

## Definition of done

- The GitHub comment starts with `## QA: PASS` or `## QA: FAIL`.
- Every acceptance criterion has a verdict.
- Every failure includes evidence.
- Test commands and results are documented.
- No application code was changed.
- The issue is not modified beyond adding the QA verdict comment.

## Example QA comment

```md
## QA: FAIL

- AC1: PASS - The frontend smoke test renders the app shell and the React/Vitest suite passes.
- AC2: FAIL - The issue says the app must show the teacher dashboard, but the page still renders the default shell and no dashboard is visible.

### Evidence

- Command: `npm --prefix frontend test`
  - Result: `1 passed (1)`
- Command: `npm --prefix frontend run build`
  - Result: `✓ built in 142ms`
- Command: `py -m pytest -c backend/pyproject.toml backend/tests`
  - Result: `0 failed` or `No tests ran` depending on the repository state at the time of review.

### Failure detail

The acceptance criterion expected the teacher dashboard to be visible. The app currently renders the baseline shell only, so the criterion fails even though the build and tests pass.
```
