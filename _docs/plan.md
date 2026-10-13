# SpeakSpark — MVP Specification

## 1. Project Overview

**Project Name:** SpeakSpark  
**Project Type:** Web Application  
**Target Users:** English Tutors  
**Project Status:** MVP Planning Complete

### Project Description

SpeakSpark is a web application designed to help English tutors find, organize, and present engaging speaking activities for their students.

The application provides a library of ready-made speaking activities, allows tutors to create their own activities, save favorites, and randomly select activities based on English proficiency level.

Tutors can use SpeakSpark both when preparing lessons and during live speaking practice.

### Main Goal

To make English speaking practice easier to prepare, more interactive, and more engaging without requiring tutors to create every activity from scratch.

---

## 2. Target Users

SpeakSpark is designed for English tutors who teach students at CEFR levels A1–B2.

Only tutors interact directly with the application.

Students participate in activities guided by their tutors and do not require accounts.

### Usage Scenarios

- **Before Lessons:** Tutors browse activities, save favorites, and prepare speaking exercises.
- **During Lessons:** Tutors quickly find activities, generate random prompts, and display activities using Focus Mode.

---

## 3. Core MVP Features

### 3.1 Activity Library

The application provides a shared library containing both ready-made and tutor-created speaking activities.

Tutors can:

- Browse all available activities.
- Filter activities by English level (A1, A2, B1, B2).
- Filter activities by topic.
- Filter activities by activity type.
- Combine multiple filters.
- Open an activity to view its complete instructions.

### 3.2 Speaking Activity Types

All activities share a common structure but may contain different additional information.

**Conversation Cards**
- Main discussion question.
- Optional follow-up questions.

**Role-play Scenarios**
- Real-life speaking situation.
- Participant roles and objectives.
- Optional useful phrases.

**Speaking Challenges**
- Creative speaking tasks.
- Optional instructions and supporting prompts.

Every activity includes a title, English level, topic, activity type, and speaking prompt.

### 3.3 Random Activity Generator

Tutors can generate a random speaking activity.

**How it works:**

1. Select an English level (required).
2. Optionally select an activity type.
3. Click "Surprise Me".
4. The application displays a randomly selected matching activity.
5. Click "Next" to receive another activity.

**Rules:**

- Activities must match the selected filters.
- Activities cannot repeat until all matching activities have been displayed.
- After all eligible activities are shown, the tutor can restart the selection cycle.
- Changing filters starts a new selection cycle.
- If no activities match the filters, display a helpful message.
- Ready-made and custom activities have equal chances of selection.

### 3.4 Favorites

Tutors can save activities they find useful.

Features:

- Add an activity to Favorites.
- Remove an activity from Favorites.
- View saved activities in a dedicated Favorites section.
- Open favorite activities directly.
- Favorites work for both ready-made and custom activities.
- Favorites remain saved after closing and reopening the browser on the same device.

### 3.5 Custom Activities

Tutors can create their own speaking activities.

Features:

- Create a custom activity.
- Select its English level.
- Choose an existing topic.
- Select an activity type.
- Enter a title and speaking prompt.
- Add optional follow-up questions, role instructions, or useful phrases.
- Edit existing custom activities.
- Delete custom activities with confirmation.

Custom activities appear in the main library and work with filters, Favorites, Random Activity, and Focus Mode.

Built-in activities cannot be edited or deleted.

Deleting a custom activity also removes it from Favorites.

### 3.6 Focus Mode

Focus Mode provides a distraction-free view for displaying activities during lessons.

Features:

- Display one activity prominently.
- Show its speaking prompt clearly.
- Display relevant optional guidance.
- Hide unnecessary navigation and interface elements.
- Exit Focus Mode and return to the previous view.

Focus Mode is available for both ready-made and custom activities.

---

## 4. Activity Content

Each activity includes:

**Required information:**
- Title
- English level
- Topic
- Activity type
- Speaking prompt

**Optional information:**
- Follow-up questions
- Useful phrases
- Participant roles
- Additional instructions

Optional fields are displayed only when relevant.

### Example Activity

**Title:** At the Airport  
**Level:** A2  
**Topic:** Travel  
**Type:** Role-play

**Prompt:** You missed your flight. Speak to an airline employee and ask for help.

**Roles:**
- Student: Passenger
- Tutor: Airline employee

**Useful Phrases:**
- Excuse me, could you help me?
- Is there another flight?
- What should I do now?

---

## 5. Pre-made Activity Library

The MVP will include 36 ready-made activities:

- 12 Conversation Cards
- 12 Role-play Scenarios
- 12 Speaking Challenges

Supported English levels:

- A1 — Beginner
- A2 — Elementary
- B1 — Intermediate
- B2 — Upper Intermediate

### Initial Topics

1. Daily Life
2. Travel
3. Food
4. Education
5. Work
6. Hobbies
7. Technology
8. Relationships

For the MVP, tutors choose from these predefined topics when creating custom activities.

---

## 6. Application Navigation

The application has four main sections.

### Library
Browse all ready-made and custom activities, apply filters, and open activity details.

### Surprise Me
Generate random speaking activities based on English level and optional activity type.

### Favorites
Access and manage saved activities.

### My Activities
Create, edit, and delete tutor-created activities.

Focus Mode is accessed from an individual activity rather than through a separate navigation section.

---

## 7. User Accounts and Data

The MVP does not require registration or login.

Tutors can use the application immediately.

Custom activities and Favorites are saved in the same browser so they remain available after the browser is closed and reopened.

Saved information is not automatically synchronized between different devices or browsers.

Clearing browser data may remove locally saved information.

User accounts and cloud synchronization are planned as possible future improvements.

---

## 8. User Experience and Design

SpeakSpark should have a clean, modern, and friendly interface.

### Design Principles

- Simple and intuitive navigation.
- Clear activity cards.
- Readable typography.
- Minimal distractions.
- Easy-to-understand filters.
- Comfortable presentation during lessons.
- Responsive layout for desktop and mobile devices.

The application should prioritize desktop use while remaining usable on mobile devices.

---

## 9. MVP User Journey

1. A tutor opens SpeakSpark.
2. The tutor browses the Activity Library.
3. They filter activities by level, topic, and type.
4. They open an activity to review its instructions.
5. During the lesson, they select B1 and Role-play in Surprise Me.
6. SpeakSpark randomly selects a matching activity.
7. The tutor opens Focus Mode and guides the student through the task.
8. The tutor saves the activity to Favorites.
9. They select another random activity without receiving a repeat from the current cycle.
10. After the lesson, the tutor creates a custom speaking activity for future use.

---

## 10. Out of Scope for MVP

The following features will not be included in the initial version:

- Student accounts
- Tutor authentication
- Saved speaking sessions
- AI-generated speaking activities
- AI conversation partners
- Automatic pronunciation assessment
- Audio or video recording
- Student progress tracking
- Sharing activities between tutors
- File uploads
- Cloud synchronization

These may be considered for future versions.

---

## 11. MVP Success Criteria

The MVP will be considered complete when tutors can:

- Browse ready-made speaking activities.
- Filter activities by level, topic, and type.
- Generate random activities based on level and optional type.
- Receive non-repeating activities during a random selection cycle.
- Save and remove Favorites.
- Create, edit, and delete custom activities.
- Access custom activities through all relevant features.
- Display activities in Focus Mode.
- Retain Favorites and custom activities after reopening the browser on the same device.

The application should remain easy to understand and usable without additional instructions.

---

## 12. Product Decisions and Rationale

**Decision 1: Tutors only**

Reason: Avoids unnecessary student accounts and complicated user permissions.

**Decision 2: Both preparation and live lesson use**

Reason: Makes the application useful throughout the teaching process.

**Decision 3: Three activity types in one shared library**

Reason: Provides variety without creating three separate systems.

**Decision 4: Combined library filters**

Reason: Allows tutors to find activities suitable for specific students.

**Decision 5: Favorites and Random Activity**

Reason: Supports both planned and spontaneous speaking practice.

**Decision 6: Avoid random activity repeats**

Reason: Keeps lessons varied and prevents the same prompts from appearing repeatedly.

**Decision 7: Guided activity content**

Reason: Provides enough information for tutors to conduct speaking practice effectively.

**Decision 8: Both ready-made and custom activities**

Reason: Combines convenience with flexibility for different teaching needs.

**Decision 9: No login for MVP**

Reason: Reduces development complexity and allows immediate use.

**Decision 10: Regular Cards and Focus Mode**

Reason: Supports both browsing and presenting activities.

**Decision 11: Separate Library, Favorites, and My Activities sections**

Reason: Makes navigation clearer without creating separate activity systems.

**Decision 12: No saved speaking sessions**

Reason: Favorites and Random Activity already provide the essential functionality for the MVP.

**Decision 13: Predefined topics and 36 pre-made activities**

Reason: Provides enough content to demonstrate all features while keeping content preparation manageable.

---

## 13. Future Improvements

Potential features for later versions:

- Tutor accounts and synchronization
- Student profiles
- Saved speaking sessions
- AI-generated activities
- Custom topic management
- Student performance tracking
- Activity sharing
- Larger activity library
- Lesson timers

These improvements should not delay the completion of the MVP.

---

## 14. Final Product Scope

SpeakSpark is a focused English speaking activity tool, not a complete tutoring management platform.

Its main value is helping tutors quickly discover, personalize, save, and present speaking activities.

The MVP includes an activity library, combined filters, a non-repeating random activity generator, Favorites, custom activity management, and Focus Mode.

The product should remain small enough for beginner-friendly development while offering meaningful functionality suitable for AI-native development workflows.

**End of MVP Specification.**
