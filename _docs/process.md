# SpeakSpark Development Process

- GitHub Issues are the canonical tasks and the only active backlog. Do not create a parallel task list.
- Work on one issue at a time.
- Read the issue's acceptance criteria before starting and again before completing the task.
- Commit regularly as work progresses.
- Follow the approved product scope in [_docs/plan.md](./plan.md) and architecture decisions in [_docs/decisions.md](./decisions.md).

## Orchestrator

The main session is the orchestrator. It launches the PM, Engineer, and QA as separate subagents. It does not groom, implement, or test itself.

## Lifecycle

1. Pick the next open GitHub issue from the backlog.
2. PM grooms it.
3. Engineer implements it.
4. QA independently verifies it.
5. On QA FAIL, return to Engineer with the QA comment as input.
6. On QA PASS, close the issue.
7. Repeat until the backlog is empty.

## Rules

- Do not skip grooming.
- Engineer must not close issues.
- QA must not modify implementation code.
- QA must publish PASS/FAIL with evidence directly on the GitHub issue.
- Close an issue only after a recorded QA PASS.
- GitHub Issues are the only active backlog.
- Do not claim that subagents were launched unless the environment supports them.

## Roles

- PM - grooms each GitHub issue before implementation, following [_docs/team/pm.md](./team/pm.md).
- QA - when asked to "Test issue #N", explicitly activates the QA Engineer role, reads [_docs/team/qa-engineer.md](./team/qa-engineer.md), verifies each acceptance criterion, and publishes the PASS/FAIL verdict directly to the GitHub issue. The task is not complete until the comment is successfully published.
- Engineer - implements one groomed task, follows [_docs/team/software-engineer.md](./team/software-engineer.md).
