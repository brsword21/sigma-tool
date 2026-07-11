# Ceneo New-Price Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one current lowest Ceneo price for a new device as a benchmark beside ranked used listings.

**Architecture:** A dedicated Firecrawl-backed Ceneo adapter returns a typed benchmark and remains separate from `ListingSource`. The search orchestrator fetches it concurrently, stores it on the search run, and exposes it through the existing run endpoint without inserting it into listing ranking.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, httpx, Supabase/PostgreSQL, pytest

## Global Constraints

- Reuse `FIRECRAWL_API_KEY` and `FIRECRAWL_TIMEOUT_SECONDS`.
- Return at most one Ceneo benchmark per selected product.
- Never mix the new-price benchmark into used-listing ranking.
- Do not infer a price when Firecrawl does not provide a valid value.
- Preserve unrelated working-tree changes.

---

### Task 1: Ceneo benchmark adapter

**Files:**
- Create: `app/sources/ceneo.py`
- Modify: `app/domain/models.py`
- Test: `tests/sources/test_ceneo.py`

**Interfaces:**
- Consumes: `SearchQuery`, Firecrawl `/v1/search` response documents.
- Produces: `NewPriceBenchmark` and `CeneoFirecrawlSource.get_benchmark(query, retrieved_at)`.

- [ ] **Step 1: Write failing adapter tests** for structured prices, text fallback,
  cheapest valid product selection, non-Ceneo noise, and missing prices.
- [ ] **Step 2: Run `pytest tests/sources/test_ceneo.py -v`** and verify imports fail.
- [ ] **Step 3: Add the typed benchmark and minimal defensive adapter** with a restricted
  `site:ceneo.pl` query, `limit` bounded by the adapter, Ceneo host validation, Decimal price
  parsing, and controlled `SourceError` handling.
- [ ] **Step 4: Run `pytest tests/sources/test_ceneo.py -v`** and verify all adapter tests pass.

### Task 2: Persist benchmark on search runs

**Files:**
- Create: `supabase/migrations/004_ceneo_new_price_benchmark.sql`
- Modify: `app/repositories/protocols.py`
- Modify: `app/repositories/supabase.py`
- Modify: `tests/api/helpers.py`

**Interfaces:**
- Consumes: JSON-compatible `NewPriceBenchmark.model_dump(mode="json")`.
- Produces: optional `new_price_benchmark` argument on `SearchRunRepository.set_status` and
  the same key in `get()` results.

- [ ] **Step 1: Extend test repository expectations** so final run status can store the
  benchmark independently from recommendations.
- [ ] **Step 2: Add nullable JSONB column migration** using
  `alter table search_runs add column if not exists new_price_benchmark jsonb`.
- [ ] **Step 3: Extend repository protocol and Supabase update payload** without changing
  behavior when the optional argument is omitted.
- [ ] **Step 4: Run repository and API tests** to verify backward compatibility.

### Task 3: Orchestrate and expose the benchmark

**Files:**
- Modify: `app/orchestration/search.py`
- Modify: `app/bootstrap.py`
- Modify: `tests/api/helpers.py`
- Modify: `tests/api/test_happy_path.py`
- Modify: `tests/api/test_partial_failure.py`

**Interfaces:**
- Consumes: optional benchmark source exposing `source_name` and `get_benchmark`.
- Produces: `new_price_benchmark` on `GET /runs/{run_id}` and source success/error metadata.

- [ ] **Step 1: Write failing API tests** asserting benchmark output and Ceneo failure
  isolation while used recommendations remain available.
- [ ] **Step 2: Run the focused API tests** and verify the new assertions fail.
- [ ] **Step 3: Inject `CeneoFirecrawlSource` in bootstrap and gather its call concurrently**
  with research and listing collection. Add success/error metadata and persist the typed value.
- [ ] **Step 4: Run focused source and API tests** and verify success and partial-failure paths.

### Task 4: Documentation and complete verification

**Files:**
- Modify: `.env.example`
- Modify: `README.md`

**Interfaces:**
- Consumes: implemented behavior and migration name.
- Produces: setup and API behavior documentation for operators.

- [ ] **Step 1: Update documentation** to describe OLX listings plus the Ceneo new-price
  benchmark and require migration `004_ceneo_new_price_benchmark.sql`.
- [ ] **Step 2: Run `.venv/bin/ruff check app tests scripts`** and fix only introduced issues.
- [ ] **Step 3: Run `.venv/bin/pytest`** and confirm the complete suite passes.
- [ ] **Step 4: Review `git diff`** to ensure no unrelated user changes were overwritten.

## Self-review

- The plan covers extraction, typing, persistence, orchestration, API visibility, failure
  isolation, migration, documentation, and tests.
- Names are consistent: `NewPriceBenchmark`, `CeneoFirecrawlSource`,
  `new_price_benchmark`, and `get_benchmark`.
- No new external dependency or second ranking path is introduced.
