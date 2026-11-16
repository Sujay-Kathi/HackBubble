# HackBubble

**HackBubble** is an intelligent hackathon discovery and team formation platform. It aggregates hackathons across multiple platforms, provides AI-driven candidate intelligence (resume parsing, grounded summaries, semantic skill & project vectors), and facilitates a two-sided team recruitment and screening workflow with explainable hybrid matching.

---

## 🛠 Tech Stack

- **Backend:** Python 3.14, FastAPI, Pydantic v2
- **Database:** PostgreSQL 16+ with `pgvector`
- **ORM / Migrations:** SQLAlchemy 2.0 (Async), Alembic
- **Scraper Engine:** Scrapling (dynamic web crawling, anti-detection, source adapters)
- **Document Processing:** PyMuPDF (fitz), OCR fallback
- **AI & Vector Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`), Structured LLM Extraction

---

## 📊 Project Status

| Phase | Scope | Status |
| :--- | :--- | :--- |
| 1 | Environment, database models, Alembic, core API | ✅ Complete |
| 2 | Authentication, JWT authorization, profile management | ✅ Complete |
| 3 | Hackathon aggregation, deduplication, catalog & bookmarks | ✅ Complete |
| 4 | Team formation, applications, screening, invitations, finalization | ✅ Complete |
| 5 | Resume upload, PyMuPDF/OCR, LLM extraction, grounded summaries | ✅ Complete |
| 6 | Vector embeddings, hybrid explainable matching, candidate queues | ✅ Complete |
| 7 | Notifications, admin moderation, Docker & production readiness | ✅ Complete |
| 8 | Filters, role lifecycle, audit logs, email delivery, workers, CLI, rate limiting, resume storage | ✅ Complete |

**Tests:** 71 passing (`cd backend && pytest`). Full phase history lives in [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md).

---

## 🚀 Architecture & Modules

```
hackbubble/
├── backend/
│   ├── app/
│   │   ├── api/             # API routes (v1)
│   │   ├── core/            # Config, security, exceptions, middleware
│   │   ├── database/        # Async session engine & base models
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   ├── services/        # Business logic services
│   │   ├── ai/              # Resume parsing, summaries, embeddings, matching
│   │   └── workers/         # Background tasks & schedulers
│   ├── alembic/             # Database migrations
│   └── pyproject.toml       # Dependencies & package configuration
├── scraper/                 # Scrapling source adapters and pipelines
├── docs/                    # PRD, SRS, architecture & context docs
└── tests/                   # Unit, integration, and API contract tests
```

---

## 📦 Getting Started

### 1. Prerequisites
- Python 3.12+ (Python 3.14 supported)
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- PostgreSQL with `pgvector` extension

### 2. Setup Backend
```bash
cd backend
uv venv
# On Windows:
.venv\Scripts\activate
# Install dependencies:
uv pip install -e .
# Configure environment (copy and edit as needed)
cp .env.example .env
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 4. Run Tests
```bash
cd backend
pytest
```

### 5. Docker (PostgreSQL + Backend)
```bash
docker compose up --build
```
The backend runs `alembic upgrade head` automatically before starting. Promote an admin account after registering:
```bash
cd backend
python -m app.cli promote-admin --email you@example.com
```

### 6. Operational Features
```bash
# Run a scraper adapter once (registered keys: mock_adapter, devfolio)
python -m app.cli run-scraper --adapter mock_adapter
python -m app.cli list-adapters
```
- **Background workers:** set `WORKERS_ENABLED=true` to run notification delivery, scheduled crawls, and embedding backfills inside the API process.
- **Email delivery:** configure `SMTP_HOST` (and credentials) to send notification emails; unconfigured SMTP marks deliveries as `skipped`.
- **Rate limiting:** set `RATE_LIMIT_ENABLED=true` for per-process in-memory limiting.
- **Admin APIs:** `/api/v1/admin/scraper/runs`, `/api/v1/admin/scraper/trigger`, `/api/v1/admin/audit-logs`, `/api/v1/admin/notifications/deliveries`.
