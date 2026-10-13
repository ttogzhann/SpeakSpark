## 1. Set up the empty full-stack project with a passing test
Goal: Create the initial monorepo structure and confirm the app can run a basic backend test and frontend test.
Description: Set up the empty React + TypeScript + Vite frontend and the FastAPI backend with a minimal SQLite configuration, then add a basic smoke test for each side so the project starts from a clean, passing baseline.

## 2. Configure the frontend app shell and build pipeline
Goal: Establish the React + Vite frontend foundation for the MVP.
Description: Create the frontend project structure, TypeScript configuration, and Vite build setup. Confirm the app renders a basic placeholder page and that the dev/build flow is stable.

## 3. Configure the FastAPI backend and app bootstrap
Goal: Provide a working Python API entry point for the application.
Description: Set up the FastAPI app, basic configuration, and runtime startup path. Verify the backend boots successfully and responds to a minimal health endpoint.

## 4. Configure SQLite and SQLAlchemy for the local tutor workspace
Goal: Create the persistence layer for the MVP database.
Description: Define the SQLite database path, SQLAlchemy engine and session setup, and base models for the local app data. Confirm the backend can initialize the database schema cleanly.

## 5. Define the shared activity data model
Goal: Model the core activity structure used by all activity types.
Description: Create a shared activity schema that supports the required fields common to all activity types and the optional fields for Conversation Cards, Role-play scenarios, and Speaking Challenges.

## 6. Define the custom activity and favorite models
Goal: Add persistence models for tutor-created content and saved items.
Description: Model custom activities and favorites in the database, with the correct relationships needed for custom activity CRUD and favorite management while keeping the MVP single-user and unauthenticated.

## 7. Seed built-in activities into the local database
Goal: Populate the ready-made library that the MVP requires.
Description: Add the initial 36 built-in activities across the three supported activity types and the supported CEFR levels and topics, ensuring they are ready to be served by the API.

## 8. Build the backend endpoint to list all activities
Goal: Expose the library data through the API.
Description: Create the GET endpoint for retrieving activities from the database and ensure it returns built-in and custom items in a consistent structure for the frontend.

## 9. Build the backend endpoint to retrieve a single activity by ID
Goal: Support activity detail views.
Description: Implement the API route for fetching one activity by ID, including validation for missing records and correct presentation of optional fields based on activity type.

## 10. Implement backend filtering for level, topic, and activity type
Goal: Make the library filterable with the same rules as the MVP spec.
Description: Add query filtering by English level, topic, and activity type, and confirm that combined filters produce the expected activity set without exposing unsupported combinations.

## 11. Add backend validation for activity payloads
Goal: Enforce the required input rules for activities and custom entries.
Description: Define Pydantic models and validation rules for required and optional activity fields, including CEFR levels, topics, and supported activity types.

## 12. Implement custom activity creation in the backend
Goal: Allow tutors to create new activities through the API.
Description: Add the POST endpoint for creating a custom activity, validate the payload, save it to SQLite, and ensure built-in activities remain protected from modification.

## 13. Implement custom activity update in the backend
Goal: Support editing custom activities without allowing edits to built-ins.
Description: Add the PUT or PATCH route for updating a custom activity, ensure only custom records can be changed, and validate that updates preserve the required fields and activity-type structure.

## 14. Implement custom activity deletion in the backend
Goal: Support deleting custom activities safely.
Description: Add the delete endpoint for custom activities, ensure built-ins cannot be deleted, and remove any dependent favorite records for the deleted custom activity.

## 15. Implement favorites creation and removal endpoints
Goal: Support the Favorites feature through the backend API.
Description: Add endpoints for adding and removing favorites, ensure favorite entries are persisted in SQLite, and keep the behavior consistent for both built-in and custom activities.

## 16. Build the favorites listing endpoint
Goal: Expose the tutor’s saved activities through the API.
Description: Create the read route for the favorites list and ensure it returns only the relevant saved activities in the same library format needed by the frontend.

## 17. Implement the backend random activity selection engine
Goal: Add the core Surprise Me logic.
Description: Build the backend logic that selects a random eligible activity based on level and optional type filters, avoids repeats until the pool is exhausted, and resets cleanly when filters change or the cycle ends.

## 18. Handle empty-result and cycle-reset cases in the random selector
Goal: Make the random generator behave correctly in edge cases.
Description: Add the logic for when no activity matches a filter set, when all matches are exhausted, and when the user changes the level or type. Ensure the API returns the correct state and message for each scenario.

## 19. Build the frontend app shell and navigation
Goal: Create the page structure and route layout for the four main sections.
Description: Add the top-level shell with navigation for Library, Surprise Me, Favorites, and My Activities, while keeping the application simple and aligned with the four-section MVP structure.

## 20. Build the library page and activity cards
Goal: Display the activity library in the frontend.
Description: Create the UI for browsing the activity list, rendering cards for all activities, and presenting the key metadata needed by the tutor to decide which activity to open.

## 21. Build the library filter controls
Goal: Implement filtering by level, topic, and activity type.
Description: Add the frontend filter UI and connect it to the backend activity list API so the tutor can combine filters and view the subset of activities that match the selection.

## 22. Build the activity detail view and type-specific rendering
Goal: Display full activity instructions in the correct format.
Description: Create the detail page that shows the required fields and only the optional fields relevant to the selected activity type, matching the MVP spec for Conversation Cards, Role-play, and Speaking Challenges.

## 23. Build the Favorites page and favorite toggling
Goal: Support saving and removing favorite activities from the UI.
Description: Implement the Favorites page, favorite toggle controls, and ensure favorite state is reflected correctly in both the library and activity detail views.

## 24. Build the My Activities page and custom activity form
Goal: Enable creation and editing of tutor-created activities.
Description: Create the custom activity form, allow tutors to choose level, topic, type, and optional fields, and wire it to the backend custom activity endpoints.

## 25. Build the custom activity edit and delete flow
Goal: Complete custom activity management in the frontend.
Description: Implement the edit workflow for existing custom activities, include delete confirmation, and ensure any deleted custom activity is removed from favorites as required by the MVP.

## 26. Build the Surprise Me page and selection flow
Goal: Support the random prompt generator for live lesson use.
Description: Create the frontend flow for selecting filters, calling the backend random activity endpoint, showing the activity, and allowing the tutor to advance to the next non-repeating choice within the same cycle.

## 27. Build the Focus Mode UI
Goal: Provide the lesson display for one activity at a time.
Description: Implement the distraction-free Focus Mode overlay or full-screen view for a selected activity, hide non-essential navigation, and allow the tutor to exit and return to the previous screen without losing context.

## 28. Add backend tests for activity filtering, CRUD, and random selection
Goal: Verify the server-side MVP logic with automated tests.
Description: Write backend tests covering filtering behavior, custom activity creation/edit/delete, favorites logic, and the repeat-prevention and cycle-reset rules in the random activity generator.

## 29. Add frontend tests for key tutor flows
Goal: Validate the primary user interactions in the React app.
Description: Write frontend tests for filter usage, favorites toggling, custom activity creation, and the random activity flow to ensure the MVP behavior remains stable across changes.

## 30. Add end-to-end coverage for the core MVP journey
Goal: Validate the full tutor experience end-to-end.
Description: Write Playwright tests that cover the major user journey: browsing the library, filtering, opening an activity, using Surprise Me, saving favorites, creating a custom activity, and entering Focus Mode without authentication or additional user setup.

## 31. Final integration review and MVP compliance check
Goal: Confirm the project matches the approved MVP and approved architecture.
Description: Review the application against the plan and architecture decisions, verify that all required features remain present and no authentication, extra features, or unsupported flow has been introduced, and confirm the project is ready for implementation handoff.
