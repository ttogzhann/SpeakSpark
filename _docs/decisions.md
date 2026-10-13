# Decisions

This document records the product and architecture decisions for SpeakSpark. Where this file and `_docs/plan.md` disagree, this file wins.

## 1. MVP scope: full-stack app with a single local tutor workspace

SpeakSpark will ship as a full-stack web application for a single local tutor workspace.

Reasoning:
- The product requires a full-stack architecture, not a browser-only frontend.
- The app serves built-in and custom activities from the backend.
- Favorites and custom activities must persist in SQLite through the backend API.
- The MVP does not include registration, login, authentication, or user accounts.
- This is intentionally a single-user local workspace, not a multi-user, multi-tenant, or cloud-synced product.

This keeps the product simple, locally developed, and aligned with the MVP requirements while still preserving a clean separation between frontend, backend, and persistence.

## 2. Frontend architecture: React + TypeScript + Vite

We will build the frontend as a React + TypeScript single-page application using Vite.

Reasoning:
- The UI is rich and interactive: filtering, random activity generation, favorites, custom CRUD, and Focus Mode all live in the browser.
- A modern frontend stack is the right choice for the interactive flow required by the tutor experience.
- The frontend owns the user experience and display logic, while the backend owns data validation and persistence.
- Focus Mode is a frontend concern and should not be implemented in the database or API layer.

## 3. Backend architecture: Python + FastAPI + Pydantic

We will implement the backend in Python using FastAPI and Pydantic.

Reasoning:
- The backend is responsible for serving activity data and handling persistence for favorites and custom activities.
- FastAPI is a lightweight, modern API framework that fits the MVP cleanly.
- Pydantic provides clear validation for activity payloads, filters, and CRUD operations.
- The backend is the correct place for activity filtering, validation, and random selection business rules.

## 4. Database architecture: SQLite + SQLAlchemy

We will use SQLite as the local database and SQLAlchemy as the ORM layer.

Reasoning:
- The MVP is designed around a single local tutor workspace, not a hosted multi-user system.
- SQLite is the simplest database choice for a locally developed MVP with no auth or cloud sync requirements.
- SQLAlchemy gives a clean Python model layer for persistence without introducing unnecessary infrastructure.
- The database stores built-in activities, custom activities, favorites, and the local workspace state.

## 5. Persistence model: backend-driven storage for favorites and custom activities

Favorites and custom activities will be stored in SQLite through the backend API.

Reasoning:
- The browser is not the persistence layer for the final architecture.
- Favorites and custom activities must remain available after reloads and browser reopen events in the local workspace.
- The backend is responsible for ensuring that custom activity deletion also removes the related favorite entries.
- This keeps the data model consistent and preserves the same product behavior without adding authentication.

## 6. Business logic placement

The following responsibilities belong in the backend:
- activity filtering by level, topic, and type
- validation of activity payloads
- CRUD for custom activities
- favorites persistence and lookup
- random activity selection
- repeat prevention within a selection cycle
- cycle reset behavior after exhaustion or filter change
- no-match handling for empty result sets

The following responsibilities belong in the frontend:
- layout and navigation
- interactive filtering controls
- UX for favorite toggling
- custom activity forms
- Focus Mode presentation
- rendering the selected activity to the tutor

This separation keeps the architecture simple and matches the MVP product boundaries.

## 7. Single-user limitation and product constraints

The MVP is intentionally a single-user application without authentication.

Implications:
- there is no login or registration flow
- there are no user accounts or role-based access
- there is no cloud synchronization or multi-device data sharing
- all persisted data is local to the single mentor workspace on this device
- clearing the local database or app data removes saved content

This is a limitation of the MVP, but it is an intentional product decision and not an incomplete implementation.

## 8. Chosen stack and version check

The following versions were checked against the official package registries on 2026-10-13. These are the latest stable versions available at the time of writing, and no newer versions were found in the checked registries for the selected stack.

| Concern | Choice | Version checked | Verified source |
| --- | --- | --- | --- |
| Frontend framework | React | 19.3.0 | npm registry |
| Type safety | TypeScript | 7.0.2 | npm registry |
| Build tooling | Vite | 8.3.4 | npm registry |
| Styling | Tailwind CSS | 4.3.3 | npm registry |
| API framework | FastAPI | 0.143.0 | PyPI |
| Validation | Pydantic | 2.14.1 | PyPI |
| Database ORM | SQLAlchemy | 2.1.4 | PyPI |
| Local database | SQLite | current system default; no separate package version required | SQLite project |
| Backend testing | pytest | 9.1.1 | PyPI |
| Frontend test runner | Vitest | 5.0.4 | npm registry |
| Frontend component testing | @testing-library/react | 16.3.3 | npm registry |
| End-to-end testing | Playwright | 1.63.0 | npm registry |
| ASGI server | Uvicorn | 0.54.0 | PyPI |

## 9. Why this stack is the right fit for SpeakSpark

- React 19.3.0 gives us the current stable frontend platform for a polished, interactive tutor experience.
- TypeScript 7.0.2 keeps the activity model strict as the app grows, especially around filter combinations and shared activity fields.
- Vite 8.3.4 keeps the frontend development workflow fast and lightweight.
- Tailwind CSS 4.3.3 gives a clean style system suitable for a lesson-focused and distraction-free interface.
- FastAPI 0.143.0 is a modern Python service layer that fits the product without adding unnecessary complexity.
- Pydantic 2.14.1 provides reliable validation for API payloads and shared activity data models.
- SQLAlchemy 2.1.4 supports a simple local persistence layer for the MVP and is a clean place to grow from a single local workspace.
- SQLite is appropriate because the MVP is a single-user app with a local workspace and no remote account model.
- pytest 9.1.1, Vitest 5.0.4, and Playwright 1.63.0 give a full testing stack without overengineering the project.

## 10. Decision summary

We choose the following architecture for the MVP:
- React + TypeScript + Vite
- Tailwind CSS
- FastAPI + Pydantic
- SQLite + SQLAlchemy
- pytest for backend tests
- Vitest + React Testing Library for frontend tests
- Playwright for end-to-end testing

This is the simplest full-stack architecture that satisfies all MVP requirements while still keeping the product easy to build and maintain in a local development workflow.

## 11. Future migration path

If the product later grows beyond the single local workspace, the app can be extended to support user accounts, remote persistence, cloud sync, shared libraries, or multi-device data access. That would require introducing authentication, a production database, and more deployment infrastructure. The current architecture intentionally stays small, local, and explicit so the MVP remains fast to build and simple to reason about.
