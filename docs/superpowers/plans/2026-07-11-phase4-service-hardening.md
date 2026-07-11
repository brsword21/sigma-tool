# Phase 4 Service Integration and Demo Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Uruchomić prawdziwe integracje OpenAI, Supabase i Firecrawl, a następnie zapewnić audytowalny scenariusz demo z poprawnym wariantem, jawnymi brakami danych, odpornym cache i czasem poniżej trzech minut.

**Architecture:** `app/bootstrap.py` składa istniejące porty i adaptery wyłącznie z centralnej konfiguracji. Orkiestrator pozostaje właścicielem kolejności pracy, ale otrzymuje pomiar etapów, batchowe wyjaśnienia LLM i twardą walidację modelu/wariantu przed deterministycznym rankingiem. Adapter Firecrawl oraz normalizator wyciągają tylko fakty obecne w payloadzie, a brakujące sygnały są oznaczane jako `unknown`/`data_gaps`.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, OpenAI SDK, Supabase SDK, httpx, pytest/pytest-asyncio.

## Global Constraints

- Jedyną kategorią pozostają używane słuchawki, językiem demo jest polski, a walutą PLN.
- Pełne pobieranie ofert może ruszyć dopiero po wyborze produktu i kierunku.
- Wariant/model jest filtrem twardym przed scoringiem.
- Awaria OpenAI, Firecrawl lub pojedynczego payloadu nie może usuwać użytecznego cache ani kończyć endpointu runu błędem 500.
- Nieznane opinie, sygnały sprzedawcy, gwarancja, zwrot, oryginalność i bateria pozostają jawnie nieznane.
- Każdy run i każde źródło mają mierzalny czas, a cache starszy niż 24 godziny jest oznaczony.
- Structured output jest walidowany przez Pydantic i ponawiany najwyżej raz.

---

### Task 1: Runtime composition of real services

**Files:**
- Create: `app/bootstrap.py`
- Modify: `app/main.py`
- Modify: `app/services/ports.py`
- Test: `tests/test_bootstrap.py`

**Interfaces:**
- Consumes: `Settings`, `OpenAIStructuredClient`, repozytoria Supabase, `OlxFirecrawlSource`.
- Produces: `build_application_services(settings: Settings) -> ApplicationServices` i `SystemClock.now() -> datetime`.

- [ ] **Step 1: Write failing tests for complete and incomplete configuration**

Sprawdź, że komplet kluczy buduje wszystkie usługi przez zamockowane konstruktory, a brak klucza pozostawia API w kontrolowanym stanie `503 services_not_configured`.

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `pytest tests/test_bootstrap.py -v`
Expected: FAIL because `app.bootstrap` does not exist.

- [ ] **Step 3: Implement the composition root**

Utwórz jeden klient Supabase, jeden klient OpenAI, jedno źródło Firecrawl, repozytoria i orkiestrator. Nie czytaj `os.environ` poza `Settings`.

- [ ] **Step 4: Run focused tests**

Run: `pytest tests/test_bootstrap.py tests/test_health.py -v`
Expected: PASS.

### Task 2: Verified fields, exact variant, and safe structured explanations

**Files:**
- Modify: `app/llm/schemas.py`
- Modify: `app/conversation/service.py`
- Modify: `app/product_research/service.py`
- Create: `app/ranking/explanations.py`
- Modify: `app/listings/normalizer.py`
- Modify: `app/ranking/engine.py`
- Modify: `app/orchestration/search.py`
- Modify: `app/api/runs.py`
- Test: `tests/listings/test_normalizer.py`
- Test: `tests/ranking/test_engine.py`
- Test: `tests/ranking/test_explanations.py`
- Test: `tests/api/test_happy_path.py`

**Interfaces:**
- Consumes: `NormalizedListing`, `Requirements`, `LLMClient`.
- Produces: `matches_exact_product(listing, product) -> bool`, `RecommendationExplanationService.explain(...)`, jawne `field_availability` w odpowiedzi API.

- [ ] **Step 1: Write failing data-quality tests**

Dodaj przypadek odrzucenia `AirPods Pro 1. gen` dla wybranego `AirPods Pro 2. gen`, przypadek zachowania zgodnego modelu oraz asercje braków `battery`, `authenticity`, `warranty`, `returns`, `seller_signals`.

- [ ] **Step 2: Implement conservative extraction and hard filtering**

Wartości mogą pochodzić tylko z tytułu, opisu lub atrybutów payloadu. Brak ma wartość prezentacyjną `unknown`; nie jest zastępowany wiedzą modelu.

- [ ] **Step 3: Add one batch structured-output call for explanations**

LLM formułuje maksymalnie trzy zalety i jedno ryzyko wyłącznie z przekazanego rankingu. Błąd wyjaśnień zachowuje deterministyczne fallbacki i oznacza `explanation` w błędach runu.

- [ ] **Step 4: Run focused tests**

Run: `pytest tests/listings tests/ranking tests/api -v`
Expected: PASS.

### Task 3: Source parsing, timing, stale-cache marking, and logs

**Files:**
- Modify: `app/sources/firecrawl.py`
- Create: `app/observability.py`
- Modify: `app/orchestration/search.py`
- Test: `tests/sources/test_firecrawl.py`
- Test: `tests/orchestration/test_observability.py`
- Test: `tests/api/test_partial_failure.py`

**Interfaces:**
- Consumes: Firecrawl v1 search records and the application clock.
- Produces: structured events `search_run_started`, `listing_fetch_started`, `source_finished`, `search_run_finished`; `source_timings_ms`; `stale_cache` data gap.

- [ ] **Step 1: Write failing real-shape payload and observability tests**

Fixture obejmuje cenę obecną wyłącznie w opisie wyniku oraz rekord bez ceny, który ma być pominięty. Log test potwierdza, że `listing_fetch_started` pojawia się dopiero w `run()` wywołanym po selekcji.

- [ ] **Step 2: Harden Firecrawl mapping**

Ekstrahuj cenę i podstawowe pola tylko z treści rekordu, ogranicz wyniki do domeny OLX oraz zachowaj kontrolowany timeout.

- [ ] **Step 3: Add monotonic timing and stale-cache annotation**

Mierz każde źródło i cały run przez `time.perf_counter()`. Przy awarii lub mniej niż pięciu wynikach dołączony cache starszy niż 24 godziny otrzymuje `stale_cache` w `data_gaps` i obniżoną pewność.

- [ ] **Step 4: Run focused tests**

Run: `pytest tests/sources tests/orchestration tests/api/test_partial_failure.py -v`
Expected: PASS.

### Task 4: Controlled live smoke test and operator documentation

**Files:**
- Create: `scripts/phase4_smoke.py`
- Create: `tests/live/test_phase4_services.py`
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-07-11-shopping-agent-backend-phases.md`

**Interfaces:**
- Consumes: lokalny `.env` i publiczne API aplikacji.
- Produces: bezpieczny raport JSON bez sekretów, zawierający status migracji/tabel, liczbę rekordów Firecrawl, wynik walidacji OpenAI, czasy i znane ograniczenia.

- [ ] **Step 1: Implement opt-in live tests**

Testy są pomijane bez `RUN_LIVE_TESTS=1`; nie wypisują kluczy ani pełnych zewnętrznych payloadów.

- [ ] **Step 2: Run local quality gates**

Run: `ruff check app tests scripts && pytest`
Expected: no lint errors and all non-live tests pass.

- [ ] **Step 3: Run repository, Firecrawl, and OpenAI smoke checks**

Run: `RUN_LIVE_TESTS=1 pytest tests/live/test_phase4_services.py -v -s`
Expected: Supabase tables accessible, Firecrawl request controlled, all three OpenAI structured-output schemas valid. A service failure is reported as a named failed check, not a traceback containing secrets.

- [ ] **Step 4: Run the full API demo**

Run: `python scripts/phase4_smoke.py`
Expected: reference-product discovery returns 4–6 candidates; `best_value` returns at least three exact-model listings or a controlled incomplete result; rerank keeps the same session; total duration is under 180 seconds.

- [ ] **Step 5: Document actual evidence and remaining limitations**

README zawiera komendy startowe, live-smoke opt-in, dostępność pól i zachowanie przy awarii. W roadmapie odhacz tylko kryteria potwierdzone testem lub realnym wywołaniem.

## Self-review

- Każde kryterium fazy 4 ma właściciela w jednym z czterech zadań.
- Integracje są składane w jednym miejscu, logika zewnętrzna pozostaje za portami.
- Filtry i scoring pozostają deterministyczne; LLM wyłącznie interpretuje, bada i formułuje wyjaśnienia.
- Testy live są jawnie opt-in i nie blokują zwykłego zestawu testów.
- Nie ma placeholderów ani rozszerzenia zakresu na drugie źródło, kolejkę zadań lub konta.
