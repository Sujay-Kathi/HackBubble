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

### Phase 3: Hackathon Aggregation Engine & Catalog Discovery (Completed ✅)
- **Date Completed:** 16 November 2026
- **Accomplishments:**
  1. Implemented canonical hackathon data schema in `app/schemas/hackathon.py` matching SRS section 6.3.
  2. Built extensible scraper architecture (`scraper/core/`):
     - `base_scraper.py`: Abstract crawler defining fetch, extract, normalize, and validate steps.
     - `normalizer.py`: URL canonicalization (stripping UTM/trackers), date parsing (ISO & timestamps), mode normalization (`online`, `offline`, `hybrid`), and dynamic event status computation (`registration_open`, `ongoing`, `completed`).
     - `validator.py`: Integrity validation enforcing valid URLs, schemas, date ranges, and title requirements.
  3. Created source adapters in `scraper/sources/`:
     - `mock.py`: Realistic mock adapter for testing, continuous integration, and pipeline verification.
     - `devfolio.py`: Integration adapter for fetching hackathon listings from Devfolio's open public API.
  4. Implemented `HackathonService` with tiered deduplication:
     - Deduplication Tier 1: `source_name` + `source_event_id`.
     - Deduplication Tier 2: Canonical `event_url`.
     - Deduplication Tier 3: Case-insensitive composite matching (`title` + `organizer`).
     - Automated updates of event status, deadlines, and `last_scraped_at` timestamps on repeated crawl cycles.
  5. Built public catalog and bookmarking API endpoints in `app/api/v1/hackathons.py`:
     - `GET /api/v1/hackathons`: Filter by query, mode, status, theme, with cursor/offset pagination.
     - `GET /api/v1/hackathons/{id}`: Detailed event page with source attribution and user bookmark flag.
     - `POST /api/v1/hackathons/{id}/bookmark` & `DELETE /api/v1/hackathons/{id}/bookmark`: Idempotent bookmarking.
     - `GET /api/v1/hackathons/saved`: Listing current user's saved events.
     - `POST /api/v1/hackathons/admin/scrape-trigger`: On-demand manual/cron scrape invocation endpoint.
  6. Added tests in `tests/unit/test_hackathons_and_scraper.py` verifying normalization, validation, scraper ingestion, deduplication, catalog search, and bookmarking (12/12 tests passing).

---

### Phase 4: Team Formation Core & Application / Screening State Machine (Completed ✅)
- **Date Completed:** 16 November 2026
- **Accomplishments:**
  1. Built complete team lifecycle models and transitions: `draft` $\rightarrow$ `open` $\rightarrow$ `paused` $\rightarrow$ `full` $\rightarrow$ `closed` $\rightarrow$ `cancelled`.
  2. Implemented role vacancy management (`TeamRole`) capturing mandatory skills, preferred skills, priority, and capacity counts.
  3. Built team discovery endpoint (`GET /api/v1/teams/discover`) with filtering by hackathon, role, and skills.
  4. Implemented participant application lifecycle (`TeamApplication`) with duplicate prevention and withdrawal safeguards (`POST /api/v1/teams/{id}/applications`, `POST /api/v1/applications/{id}/withdraw`, `GET /api/v1/applications/me`).
  5. Implemented leader candidate screening workflow (`POST /api/v1/teams/{id}/screening-actions`) persisting swipe actions (`shortlist`, `reject`, `revisit`) with multi-pass support.
  6. Implemented invitation response workflow (`POST /api/v1/teams/{id}/invitations/{id}/respond`) verifying candidate acceptance marks interest without premature membership assignment.
  7. Implemented pessimistic concurrency-safe finalization transaction (`POST /api/v1/teams/{id}/finalize`) with `with_for_update()` row locking, capacity checks, atomic `TeamMember` creation, role vacancy decrements, and automatic status transition to `full`.
  8. Added integration test in `tests/unit/test_team_formation.py` verifying the full end-to-end team formation lifecycle (13/13 tests passing).

---

### Phase 5: Candidate Intelligence & Resume Processing Subsystem (Completed ✅)
- **Date Completed:** 16 November 2026
- **Accomplishments:**
  1. Implemented private resume upload pipeline (`POST /api/v1/profiles/me/resumes`) with SHA-256 deduplication and 10MB file limit enforcement.
  2. Implemented PyMuPDF text extractor (`ResumeTextExtractor`) with automatic heuristic quality detection triggering OCR fallback for scanned/low-yield PDFs.
  3. Built schema-constrained LLM structured extraction service (`LLMResumeParser`) parsing raw text into strict `ParsedResumeDraftSchema` (education, skills, domains, experience, projects, achievements) with intelligent offline heuristic fallback.
  4. Built mandatory human-in-the-loop review workflow (`GET /profiles/me/resumes/{id}/draft` and `POST /profiles/me/resumes/{id}/confirm`), committing user-verified claims into profile tables (`user_skills`, `user_projects`, `user_experience`, `user_achievements`).
  5. Built grounded summarizer (`GroundedSummarizer`) creating concise, unhallucinated profile and project summaries labeled as `[AI-Generated Summary]` and stored in `CandidateIntelligence`.
  6. Added tests in `tests/unit/test_resume_and_ai.py` verifying PDF text extraction, structured extraction, grounded summary generation, and the complete upload $\rightarrow$ parse $\rightarrow$ draft $\rightarrow$ confirm workflow (16/16 tests passing).

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
