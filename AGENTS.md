# SQLBot Agent Instructions

## Project overview

SQLBot is a FastAPI + Vue 3 ChatBI system. The main question-answering flow is coordinated by `backend/apps/chat/task/llm.py` and exposed through Web, embedded assistant, and MCP entry points.

## Agent skills

### Issue tracker

Issues and specifications are tracked in GitHub Issues for `elthereal-star/SQLBot`. Use `gh` for issue operations. Pull requests are not treated as a triage request surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default labels `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository. Read the root `CONTEXT.md` and relevant ADRs under `docs/adr/` when they exist. See `docs/agents/domain.md`.

## Working conventions

- Read the relevant source and tests before changing implementation.
- Preserve existing user changes and avoid unrelated refactors.
- Prefer focused changes with tests covering changed behavior.
- Do not create pull requests against the upstream `dataease/SQLBot` repository.
- Push changes only to the user's fork when explicitly requested.
- Do not claim performance or accuracy improvements without a reproducible baseline.

## Common commands

- Backend tests: `cd backend; pytest`
- Frontend development: `cd frontend; npm run dev`
- Frontend build: `cd frontend; npm run build`
- Container startup: `docker compose up -d`
