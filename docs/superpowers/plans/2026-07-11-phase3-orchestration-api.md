# Phase 3 Orchestration and API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dostarczyć pełny przepływ fazy 3 na mockach: rozmowa → eksploracja 4–6 modeli → wybór kierunku → run w tle → co najmniej trzy ocenione oferty, z zachowaniem cache i wyniku częściowego.

**Architecture:** FastAPI deleguje logikę do serwisów wstrzykiwanych przez `app.state`. `SearchOrchestrator` równolegle uruchamia brief produktu i ścieżkę cache/źródła, izoluje błędy, normalizuje i rankuje oferty, a stan zapisuje przez protokoły repozytoriów. Modele Pydantic pozostają jedynym kontraktem pomiędzy API, LLM i domeną.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, asyncio, Supabase/PostgreSQL, pytest/pytest-asyncio.

## Global Constraints

- MVP obsługuje jedną kategorię: używane słuchawki.
- Pierwszy etap zwraca 4–6 modeli i nigdy nie udaje finalnego rankingu ofert.
- Research kandydatów obejmuje maksymalnie 10 kandydatów.
- Długi etap startuje dopiero po wyborze produktu lub kierunku i od razu zwraca `run_id`.
- Awaria źródła nie usuwa cache; wynik z cache otrzymuje status `partial` i jawny błąd źródła.
- Każdy wynik zewnętrzny ujawnia źródło, czas pozyskania, pewność i braki danych.

---

### Task 1: Rozszerzenie kontraktów domenowych i LLM

**Files:**
- Modify: `app/domain/models.py`
- Modify: `app/llm/schemas.py`
- Modify: `app/conversation/service.py`
- Test: `tests/conversation/test_reference_product.py`
- Test: `tests/product_research/test_similarity.py`

**Interfaces:**
- Produces: `SearchDirection`, `ReferenceProduct`, rozszerzone `Requirements`, `ProductSuggestion`, `ConversationResult`.
- Consumes: istniejący `LLMClient.structured_response(...)`.

- [x] Napisać test rozpoznania produktu referencyjnego i powodów podobieństwa.
- [x] Uruchomić test i potwierdzić błąd brakującego kontraktu.
- [x] Dodać pola domenowe i ograniczyć gotową listę do 4–6 spośród maksymalnie 10 kandydatów.
- [x] Uruchomić testy rozmowy i modeli.

### Task 2: Repozytoria sesji, runów, produktów i rekomendacji

**Files:**
- Modify: `app/repositories/protocols.py`
- Modify: `app/repositories/supabase.py`
- Test: `tests/repositories/test_runs.py`

**Interfaces:**
- Produces: repozytoria `SupabaseProductRepository`, `SupabaseSessionRepository`, `SupabaseSearchRunRepository`, `SupabaseProductResearchRepository`, `SupabaseRecommendationRepository`.
- Consumes: siedem tabel z `supabase/migrations/001_initial_schema.sql`.

- [x] Napisać test zapisu statusu częściowego wraz z sukcesami i błędami źródeł.
- [x] Dodać minimalne adaptery CRUD zgodne z protokołami.
- [x] Uruchomić test repozytoriów i sprawdzić idempotencję istniejących ofert.

### Task 3: Orkiestracja briefu, cache, źródeł i rankingu

**Files:**
- Create: `app/orchestration/__init__.py`
- Create: `app/orchestration/search.py`
- Test: `tests/orchestration/test_search.py`

**Interfaces:**
- Produces: `SearchOrchestrator.run(run_id, session_id, product_id, product, requirements)`.
- Consumes: repozytoria, `ProductResearchService`, `ListingSource`, `normalize_listing`, `rank_listings`, `Clock`.

- [x] Napisać test pełnego sukcesu i test awarii źródła z trzema ofertami cache.
- [x] Ustawić run na `running`, uruchomić brief i zbieranie ofert przez `asyncio.gather(..., return_exceptions=True)`.
- [x] Przy sukcesie zapisać nowe oferty, przy awarii zachować cache, następnie zapisać rekomendacje.
- [x] Ustawić `completed`, `partial` albo `failed` na podstawie użytecznego wyniku i błędów.
- [x] Uruchomić testy orkiestratora.

### Task 4: Endpointy FastAPI i zadanie w tle

**Files:**
- Create: `app/api/__init__.py`
- Create: `app/api/dependencies.py`
- Create: `app/api/sessions.py`
- Create: `app/api/runs.py`
- Create: `app/api/products.py`
- Create: `app/api/health.py`
- Modify: `app/main.py`
- Test: `tests/api/test_happy_path.py`
- Test: `tests/api/test_partial_failure.py`

**Interfaces:**
- Produces: `POST /sessions`, `POST /sessions/{id}/messages`, `POST /sessions/{id}/products/{product_id}/select`, `GET /runs/{id}`, `POST /runs/{id}/refresh`, `GET /products/{id}/brief`, `GET /health`.
- Consumes: `ApplicationServices` wstrzyknięte do `create_app(settings, services=...)`.

- [x] Napisać happy path dla wejścia od potrzeby i od „coś jak AirPods Pro, ale taniej”.
- [x] Napisać test zmiany kierunku bez resetu sesji oraz częściowego wyniku po awarii źródła.
- [x] Dodać routery, jednolite błędy 404 i uruchamianie orkiestratora przez `BackgroundTasks`.
- [x] Uruchomić testy API.

### Task 5: Specyfikacja i pełna weryfikacja

**Files:**
- Modify: `docs/superpowers/specs/2026-07-11-shopping-agent-backend-design.md`
- Modify: `docs/superpowers/plans/2026-07-11-shopping-agent-backend-phases.md`

**Interfaces:**
- Consumes: działające kontrakty i endpointy z Tasks 1–4.
- Produces: aktualny opis dwóch wejść, eksploracji, kierunków i trzech ocen.

- [x] Zaktualizować dokumentację i oznaczyć ukończone punkty fazy 3.
- [x] Uruchomić `./.venv/bin/pytest -q` i oczekiwać pełnego PASS.
- [x] Uruchomić `./.venv/bin/ruff check .` i usunąć wszystkie błędy.
- [x] Sprawdzić `git diff --check` oraz potwierdzić, że niezwiązane zmiany użytkownika pozostały nietknięte.
