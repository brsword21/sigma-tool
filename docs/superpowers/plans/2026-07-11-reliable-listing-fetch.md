# Reliable Listing Fetch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the listing-fetch stage reliably return matching OLX offers instead of silently normalizing irrelevant web-search results.

**Architecture:** Upgrade only the OLX adapter to Firecrawl Search v2, constrain results with the API's domain and country fields, and keep budget filtering inside the application. Validate product identity and accessories at the source boundary, while retaining the orchestrator's exact-variant verification as defense in depth.

**Tech Stack:** Python 3.12, FastAPI, httpx, Firecrawl Search v2, pytest, React, TypeScript

## Global Constraints

- Preserve strict rejection of accessories and unrelated models.
- Do not include budget in the external web-search query.
- Do not change the database schema.
- Preserve partial-failure and stale-cache fallbacks.
- Keep existing user changes in `frontend/src/App.tsx` and CSS.

---

### Task 1: Define the Firecrawl v2 contract

**Files:**
- Modify: `tests/sources/test_firecrawl.py`
- Modify: `app/sources/firecrawl.py`

**Interfaces:**
- `OlxFirecrawlSource.search(SearchQuery) -> list[RawListing]`
- Firecrawl endpoint: `POST /v2/search`

- [ ] Add failing tests for `/v2/search`, `includeDomains=["olx.pl"]`, `country="PL"`, and a query that excludes budget.
- [ ] Add v2 `{data: {web: [...]}}` response coverage.
- [ ] Implement the request and response contract.
- [ ] Run the focused source tests.

### Task 2: Reject irrelevant source records early

**Files:**
- Modify: `app/product_matching.py`
- Modify: `app/sources/firecrawl.py`
- Modify: `tests/sources/test_firecrawl.py`
- Modify: `tests/ranking/test_engine.py`

**Interfaces:**
- Produce: `matches_product_title(title: str, expected_model: str) -> bool`

- [ ] Add failing tests for unrelated phones, exact models, suffix variants, and accessories.
- [ ] Reuse canonical product matching at the source and ranking boundaries.
- [ ] Raise `SourceError` when Firecrawl succeeds technically but returns no matching priced offers.
- [ ] Verify orchestrator partial/failure behavior remains controlled.

### Task 3: Show honest progress

**Files:**
- Modify: `frontend/src/App.tsx`
- Reuse: `frontend/src/components/SearchProgress.tsx`

- [ ] Replace the permanently active static fetch line with the existing timed progress component.
- [ ] Pass the selected product name when available.
- [ ] Run frontend tests and production build.

### Task 4: Verification

**Files:**
- Verify: all changed files

- [ ] Run Ruff and the complete backend suite.
- [ ] Run Vitest and the frontend production build.
- [ ] Run the opt-in live Firecrawl test.
- [ ] Execute a live exact-model search and inspect status, duration, sources, and recommendation count.

## Decision Log

- Firecrawl v2 is chosen because its official API supports `includeDomains`, `country`, and an improved search response.
- Budget remains an application hard filter; adding it to the web query reduced recall and produced unrelated results.
- Source-boundary model validation prevents junk rows from polluting cache and makes empty search results observable.
- The existing exact-product check remains in orchestration as a second safety boundary.
