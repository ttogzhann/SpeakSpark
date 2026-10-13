# SpeakSpark Development Process

- GitHub Issues are the canonical tasks and the only active backlog. Do not create a parallel task list.
- Work on one issue at a time.
- Read the issue's acceptance criteria before starting and again before completing the task.
- Commit regularly as work progresses.
- Follow the approved product scope in [_docs/plan.md](./plan.md) and architecture decisions in [_docs/decisions.md](./decisions.md).

## Roles

- PM - grooms each GitHub issue before implementation, following [_docs/team/pm.md](./team/pm.md).
- QA - when asked to "Test issue #N", explicitly activates the QA Engineer role, reads [_docs/team/qa-engineer.md](./team/qa-engineer.md), verifies each acceptance criterion, and publishes the PASS/FAIL verdict directly to the GitHub issue. The task is not complete until the comment is successfully published.
- Engineer - implements one groomed task, follows [_docs/team/software-engineer.md](./team/software-engineer.md).
