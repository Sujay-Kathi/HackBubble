# HackBubble — Project Context & Evolution Document

This document records the architectural decisions, system milestones, state machine definitions, and progress made during each development phase of **HackBubble**.

---

## 1. Project Overview & Rebranding
- **Original Working Title:** HackMate
- **Final Official Name:** HackBubble
- **GitHub Repository:** [https://github.com/Sujay-Kathi/HackBubble.git](https://github.com/Sujay-Kathi/HackBubble.git)
- **Primary Goal:** A hackathon discovery and two-sided team formation platform powered by AI candidate intelligence and hybrid explainable matching.

---

## 2. System Architecture & Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **API Framework** | Python 3.12+ / FastAPI | High performance, async REST API with OpenAPI documentation |
| **Data Validation** | Pydantic v2 / pydantic-settings | Strictly typed data schemas and environment management |
| **Relational Database** | PostgreSQL 16+ | Source of truth for users, teams, applications, memberships |
| **Vector Search** | pgvector (384 dimensions) | Storing and querying semantic embeddings (`all-MiniLM-L6-v2`) |
| **ORM & Migrations** | SQLAlchemy 2.0 (Async) + Alembic | Declarative async models and revisioned migrations |
| **Web Scraping** | Scrapling | Resilient, anti-detection web crawlers for hackathon platforms |
| **Resume Processing** | PyMuPDF + OCR fallback | PDF text extraction and document digitization |
| **AI Extraction & Summaries**| Schema-constrained LLM (OpenAI/Gemini) | Extraction of structured JSON from resume and grounded summaries |
| **Matching Engine** | Hybrid Scoring Engine | Hard constraints + weighted scoring (skills, vectors, experience) |

---

## 3. Phase Log & Implementation Status

### Phase 1: Environment, Database & Project Architecture (Completed ✅)
- **Date Completed:** 16 November 2026
- **Accomplishments:**
  1. Git repository initialized and configured with remote `https://github.com/Sujay-Kathi/HackBubble.git`.
  2. Created `.gitignore` and `README.md` reflecting **HackBubble**.
  3. Scaffolding of `backend/` with `pyproject.toml`, `.env.example`, and package setup managed via `uv`.
  4. Configured async SQLAlchemy 2.0 engine, sessionmaker, and dependency injection in `backend/app/database/session.py`.
  5. Implemented complete database models across 5 domain modules matching PRD and SRS specifications:
     - `app/models/user.py`: `User`, `UserProfile`, `UserSkill`, `UserProject`, `UserExperience`, `UserAchievement`.
     - `app/models/hackathon.py`: `Hackathon`, `HackathonSource`, `HackathonSourceRecord`, `SavedHackathon`, `ScrapeRun`.
     - `app/models/team.py`: `Team`, `TeamRole`, `TeamPreference`, `TeamIntelligence`, `TeamApplication`, `TeamInvitation`, `TeamMember`, `ScreeningAction` (with `Vector(384)`).
     - `app/models/resume.py`: `UserResume`, `CandidateIntelligence`, `CandidateEmbedding` (with `Vector(384)`).
     - `app/models/notification.py`: `Notification`, `NotificationDelivery`, `AuditLog`.
  6. Configured Alembic for async migrations with `pgvector` support, generating baseline migration `001_initial_schema.py`.
  7. Implemented application settings (`app/core/config.py`), security tokens (`app/core/security.py`), and unified error handling envelope (`app/core/exceptions.py`).
  8. Created FastAPI app (`app/main.py`) with CORS, lifespan, and `/api/v1/health` and `/` endpoints.
  9. Added and executed unit test suite (`tests/unit/test_health_and_core.py`) verifying health checks, settings, tokens, and metadata registration (5/5 tests passing).

---

### Phase 2: Authentication, Authorization & User Profile Management (Completed ✅)
- **Date Completed:** 16 November 2026
- **Accomplishments:**
  1. Implemented JWT authentication and authorization dependencies (`app/api/deps.py`), supporting contextual roles and account status validation.
  2. Built registration (`POST /api/v1/auth/register`), login (`POST /api/v1/auth/login`), and profile bootstrapping (`POST /api/v1/auth/profile/bootstrap`).
  3. Built full User Profile management endpoints in `app/api/v1/profiles.py`:
     - Profile retrieval and updating (`GET /api/v1/profiles/me`, `PATCH /api/v1/profiles/me`).
     - Skills CRUD (`POST`, `PATCH`, `DELETE /api/v1/profiles/me/skills`).
     - Projects CRUD (`POST`, `PATCH`, `DELETE /api/v1/profiles/me/projects`).
     - Experience CRUD (`POST`, `DELETE /api/v1/profiles/me/experience`).
     - Achievements CRUD (`POST`, `DELETE /api/v1/profiles/me/achievements`).
     - Profile privacy enforcement (`GET /api/v1/profiles/{user_id}`) respecting `public`, `registered_only`, and `private` visibility rules.
  4. Switched password hashing to direct `bcrypt` implementation with 72-byte safe truncation.
  5. Added comprehensive test suite in `tests/unit/test_auth_and_profiles.py` verifying registration, duplicate rejection, login, profile CRUD, and privacy rules (8/8 tests passing).

---

## 4. Key Architectural & Business Rules
1. **Contextual Roles:** Users do not have fixed global participant/leader roles. Any user can be a team leader for team X while being a participant applying to team Y.
2. **Two-Sided Recruitment:** A candidate is never an official team member merely because a leader shortlists them or the candidate accepts an invitation.
3. **Pessimistic Finalization:** Official membership is created only upon atomic leader finalization with pessimistic row locking (`SELECT FOR UPDATE`) and vacancy capacity checks.
4. **AI Explainability & Fairness:** Semantic scores are never treated as probabilities. Candidates receive score component breakdowns and evidence-grounded reasons.

---

## 5. Upcoming Phase: Phase 2
- **Phase 2: Authentication, Authorization & User Profile Management**
  - Bootstrap user profile after authentication (`/auth/profile/bootstrap`)
  - Authenticated user endpoints (`/profiles/me` GET & PATCH)
  - Profile sub-resources CRUD: Skills, Projects, Experience, Achievements
  - Privacy visibility filters and access guardrails
