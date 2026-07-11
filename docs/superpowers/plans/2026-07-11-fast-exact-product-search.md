# Fast Exact Product Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Return concrete listings faster when the user explicitly asks for offers for one exact product model.

**Architecture:** Add a conservative, deterministic fast-path before the conversational LLM call. It extracts only explicit `offers/listings for <brand> <model>` commands with a model identifier, creates/selects that product, and starts the existing search orchestrator. Keep deterministic ranking explanations in the critical path and stop awaiting optional LLM prose.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, pytest, React, TypeScript, Vitest

## Global Constraints

- Do not change the Supabase schema.
- Preserve the existing discovery flow for needs, comparisons, and ambiguous product requests.
- Require an explicit offer/listing search phrase and a model containing a digit before bypassing the LLM.
- Preserve deterministic ranking, risk scoring, source links, and partial-failure behavior.
- Do not overwrite unrelated local frontend changes.

---

### Task 1: Detect an explicit exact-product search

**Files:**
- Modify: `app/conversation/service.py`
- Test: `tests/conversation/test_service.py`

**Interfaces:**
- Produces: `infer_direct_product_search(message: str) -> ReferenceProduct | None`

- [ ] Add failing parameterized tests for explicit Sony, Samsung, and Apple listing requests and ambiguous/comparison messages.
- [ ] Run `.venv/bin/pytest tests/conversation/test_service.py -q` and verify failure.
- [ ] Implement conservative normalization and extraction without calling the LLM.
- [ ] Re-run the focused tests and verify success.

### Task 2: Start the search immediately

**Files:**
- Modify: `app/api/sessions.py`
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/state/useShoppingSession.ts`
- Test: `tests/api/test_happy_path.py`

**Interfaces:**
- Consumes: `infer_direct_product_search`
- Produces: message response with `run_id`, `status=pending`, `direct_search=true`, and no candidates.

- [ ] Add an API test asserting that an explicit listing request makes zero conversation-LLM calls and returns ranked offers.
- [ ] Run the focused API test and verify failure.
- [ ] Create/upsert the exact product, update the session, create the run, and schedule the existing orchestrator.
- [ ] Add `direct_search` to the frontend response type and show accurate search-progress copy.
- [ ] Re-run focused backend and frontend tests.

### Task 3: Remove optional LLM prose from the critical path

**Files:**
- Modify: `app/bootstrap.py`
- Test: `tests/api/test_happy_path.py`

**Interfaces:**
- The orchestrator continues using its existing deterministic `item.explanation` fallback.

- [ ] Add an assertion that production service construction does not attach an explanation LLM to the orchestrator.
- [ ] Configure production orchestration with `explanations=None` while retaining the standalone explanation service and live contract test.
- [ ] Verify ranked recommendations still contain explanations.

### Task 4: Regression and quality verification

**Files:**
- Verify: all changed files

- [ ] Run `.venv/bin/ruff check app tests scripts`.
- [ ] Run `.venv/bin/pytest`.
- [ ] Run `npm test -- --run` in `frontend`.
- [ ] Run `npm run build` in `frontend`.
- [ ] Review `git diff` and confirm unrelated user changes remain intact.

## Decision Log

- Use a conservative deterministic command parser instead of another LLM call because latency reduction is the primary goal.
- Preserve the normal candidate flow unless the user explicitly asks for listings/offers for a model containing a numeric identifier.
- Use existing deterministic explanations in initial results; optional LLM wording is not worth blocking the ranking.
- Keep Firecrawl, Ceneo, and product research parallel because measurements show they are not the dominant serial bottleneck.
