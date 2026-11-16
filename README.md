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
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.
