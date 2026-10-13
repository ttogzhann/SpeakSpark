# Decisions

This document records the product and architecture decisions for SpeakSpark. Where this file and `_docs/plan.md` disagree, this file wins.

## 1. MVP scope: browser-local, single-user, no backend in v1

SpeakSpark will ship as a client-only web app for tutors, without authentication, cloud sync, or server-side persistence in the MVP.

Reasoning:
- The product requirement explicitly says tutors use the app immediately without login.
- Custom activities and Favorites must persist on the same device after reload.
- The MVP does not require multi-user data, synchronization, or cloud storage.
- A browser-local first version minimizes operational complexity and keeps the product focused on lesson preparation and live use.

This keeps the product small, fast to ship, and easy to reason about while still covering the complete MVP feature set.

## 2. Frontend architecture: React + TypeScript + Vite for the app shell

We will build the MVP as a single-page application using React and TypeScript.

Reasoning:
- The UI is rich and interactive: filtering, random selection, favorites, custom CRUD, and Focus Mode all live in the browser.
- A SPA is a better fit than a server-rendered app for a lesson-focused, highly interactive tool.
- A client-first architecture keeps the MVP lean and avoids premature backend work.
- The interaction logic is more complex than the persistence layer, and it belongs in the client.

## 3. State and persistence model: localStorage with explicit client-side domain logic

We will persist Favorites and custom activities in browser localStorage and rebuild application state at startup.

Reasoning:
- The product requirement is same-device persistence after browser restart.
- No server or auth layer is needed for the MVP.
- The hard logic is in the client state model, not in backend APIs.
- localStorage is enough to satisfy the product decision and keeps the system simpler than a database-backed app.

Custom activity deletion must also remove the matching favorite entries so the local state remains consistent.

## 4. Chosen stack and verified versions

The following versions were checked against the public npm registry on 2026-10-13. These are the current stable package versions available at the time of writing, and no newer stable versions were available in the registry when checked.

| Concern | Choice | Version checked | Status |
| --- | --- | --- | --- |
| UI framework | React | 19.3.0 | latest stable available in the npm registry on 2026-10-13 |
| Type safety | TypeScript | 7.0.2 | latest stable available in the npm registry on 2026-10-13 |
| Build tooling | Vite | 8.3.4 | latest stable available in the npm registry on 2026-10-13 |
| Styling | Tailwind CSS | 4.3.3 | latest stable available in the npm registry on 2026-10-13 |
| State management | Zustand | 5.0.15 | latest stable available in the npm registry on 2026-10-13 |
| Routing | React Router DOM | 7.18.4 | latest stable available in the npm registry on 2026-10-13 |
| Test runner | Vitest | 5.0.4 | latest stable available in the npm registry on 2026-10-13 |
| Component testing | @testing-library/react | 16.3.3 | latest stable available in the npm registry on 2026-10-13 |

## 5. Why this stack is the right fit for SpeakSpark

- React 19.3.0 gives us the current stable frontend platform with strong component ergonomics and a mature ecosystem.
- TypeScript 7.0.2 keeps the app safe as the activity model grows, especially for shared field definitions across activity types.
- Vite 8.3.4 is the current stable build tool and gives the fastest developer workflow with low config overhead.
- Tailwind CSS 4.3.3 is the modern styling choice for a clean, distraction-free, lesson-friendly interface.
- Zustand 5.0.15 is lightweight and appropriate for a small client-side app without the overhead of a more opinionated state system.
- React Router DOM 7.18.4 is the current routing option if the app needs URL-driven screens or deep-linkable views.
- Vitest 5.0.4 and @testing-library/react 16.3.3 give a modern, fast test setup for the activity logic and UI interactions.

## 6. Decision summary

We choose the following architecture for the MVP:
- React 19.3.0
- TypeScript 7.0.2
- Vite 8.3.4
- Tailwind CSS 4.3.3
- Zustand 5.0.15
- React Router DOM 7.18.4
- Vitest 5.0.4
- @testing-library/react 16.3.3
- localStorage-based persistence

This is the simplest architecture that still satisfies all MVP requirements without introducing backend complexity before it is needed.

## 7. Future migration path

If the product later needs accounts, cloud sync, sharing, analytics, or multi-device data, the app can evolve into a server-backed system without rewriting the core activity model and UX. The current architecture is intentionally narrow and deliberately optimizes for clarity, speed, and low complexity in the MVP.
