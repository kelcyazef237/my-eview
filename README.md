# my-e-view

MYEVIEW — Cameroon-focused external digital-trust scoring platform ("FICO score for an organization's external cybersecurity posture").

## One-Command Setup

```bash
python setup.py
```

This installs all Python and Node dependencies, builds the frontend, runs database migrations, seeds reference data, and generates a secure SECRET_KEY. It is idempotent — re-running skips already-completed steps.

If PostgreSQL/Redis are not running yet:
```bash
python setup.py --docker-infra
```

## Stack

- **Backend:** Python 3.11+, FastAPI, PostgreSQL 15, Celery + Redis, SQLAlchemy + Alembic, Pydantic
- **Frontend:** Vite + React 18 + TypeScript + Tailwind CSS
- **Reports:** Jinja2 templates → HTML → WeasyPrint PDF
- **Collectors:** dnspython, httpx, ssl/cryptography, python-whois, ipwhois, beautifulsoup4, python-nmap (gated)

## Architecture

```
Public Lookup → API (FastAPI) → Celery orchestrator → Collectors → Raw Evidence (PostgreSQL)
                                                              ↓
                                              Normalization → Scoring Engine (pure function)
                                                              ↓
                                              Shield/Outlook → TIA Templates → Report
```

**Scoring:** 8 categories (7 scored), 27 vectors, 1000-point scale, 5-tier Shield rating.
Deterministic: same findings → same score, every time. Non-intrusive: DNS/TLS/HTTP only, no exploitation.

## API Key Requirements

| Feed | Key Required? | Notes |
|------|--------------|-------|
| AlienVault OTX (malware) | **YES** — free at https://otx.alienvault.com/ | Without it, the malware vector (60 pts) silently produces no data |
| PhishTank (phishing) | No | Public JSON feed |
| OpenPhish (phishing) | No | Public text feed |
| Abuse.ch Feodo (botnet) | No | Public CSV, cached locally |
| DNSBL (Spamhaus/SURBL) | No | Plain DNS queries |
| crt.sh (asset discovery) | No | Public CT log endpoint |

**Action required:** Set `OTX_API_KEY` in `backend/.env` after getting a free key from AlienVault.

## Running

### Docker Compose (recommended for deployment)

```bash
docker compose up -d
```

This starts: PostgreSQL, Redis, Backend API, Celery worker, Celery beat, Frontend (nginx).

### Manual

```bash
# Terminal 1 — API
cd backend && uvicorn app.main:app --reload

# Terminal 2 — Celery worker
cd backend && celery -A app.tasks.celery_app worker -l info --queues=celery,verified

# Terminal 3 — Celery beat
cd backend && celery -A app.tasks.celery_app beat -l info

# Terminal 4 — Frontend
cd frontend && npm run dev
```

## Testing

```bash
cd backend && pytest -q
```

76 tests covering: scoring determinism, shield/outlook mapping, normalization, TIA templates, portscan gating, report rendering.

## Project Structure

```
backend/
  app/
    api/            Routers: public, owner, ops, auth, verified, reports
    collectors/     DNS, TLS, HTTP, WHOIS, threat-intel, asset-discovery, portscan (gated)
    normalization/  Raw evidence → discrete states (PASS/WARN/FAIL/NA/NOT_OBSERVED)
    scoring/        Pure-function engine, rules_loader, shield_mapper, outlook_mapper
    tia/            Trust Impact Analysis template engine
    services/       JWT, rate-limiting, ownership verification, scan orchestrator
    tasks/          Celery tasks: passive_scan, full_report_cycle, feed_refresh, portscan
    reports/        Jinja2 templates + WeasyPrint PDF pipeline
    models/         SQLAlchemy models
    tests/          76 unit + integration tests
  config/
    scoring_rules_v1.yaml    1000-point ruleset (validated on startup)
    tia_templates_v1.yaml    Versioned TIA templates with clean/dirty variants
  alembic/         Migrations: initial schema + reference data seed
frontend/
  src/
    routes/         PublicLookup, OwnerDashboard, TechnicalDashboard, Verify, Report, Settings
    components/     Shield, ScoreGauge, CategoryCard, TIAPanel, TechnicalTable, ScoreHistoryChart
    api/            Typed API client
    types/          Shared TypeScript interfaces
setup.py            Idempotent deployment script
docker-compose.yml  Full stack: postgres, redis, backend, celery-worker, celery-beat, frontend
```

## License

Proprietary — Myescore.