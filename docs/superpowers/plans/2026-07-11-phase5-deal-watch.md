# Phase 5 Deal Watch / Mandate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dodać deterministyczny tryb Deal Watch, który oblicza koszt końcowy i zapisuje audytowalną decyzję `ignore`, `hold` lub `alert` dla zdarzeń rynkowych.

**Architecture:** Nowy moduł `app/deal_watch` izoluje modele, arytmetykę, politykę, pamięciowe repozytorium i usługę. Cienki router FastAPI udostępnia funkcję również wtedy, gdy zewnętrzne usługi MVP nie są skonfigurowane.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, Decimal, pytest.

## Global Constraints

- Jedyną kategorią pozostają używane słuchawki, a scenariusz demo używa PLN.
- Faza 5 nie wykonuje checkoutu, zakupu ani płatności.
- Wszystkie decyzje i składniki kosztu są deterministyczne i audytowalne.
- Jedna paczka API zawiera 1–10 zdarzeń, a wszystkie dane wejściowe waliduje Pydantic.
- Moduł nie wymaga OpenAI, Firecrawl, Supabase, Redis ani Celery.

---

### Task 1: Domain contracts and landed-cost engine

**Files:**
- Create: `app/deal_watch/__init__.py`
- Create: `app/deal_watch/models.py`
- Create: `app/deal_watch/costs.py`
- Test: `tests/deal_watch/test_costs.py`

**Interfaces:**
- Produces: `DealMandate`, `MarketEvent`, `CostBreakdown`, `DealDecision`, `calculate_landed_cost(event) -> CostBreakdown`.

- [x] **Step 1: Write failing arithmetic and validation tests**

Test sumowania ceny, dostawy, opłat i FX, odjęcia tylko ważnego kuponu, zaokrąglenia do `0.01` oraz odrzucenia wartości ujemnych.

- [x] **Step 2: Run focused tests and confirm failure**

Run: `.venv/bin/pytest tests/deal_watch/test_costs.py -v`
Expected: FAIL because `app.deal_watch` does not exist.

- [x] **Step 3: Implement strict Pydantic contracts and pure cost calculation**

Modele używają `Decimal`, `Field(ge=0)`, ograniczeń długości oraz `extra="forbid"`.
`calculate_landed_cost` oblicza `max(0, item + shipping + duties + fx - applied_coupon)`
i kwantyzuje każdą wartość do `Decimal("0.01")`.

- [x] **Step 4: Run focused tests**

Run: `.venv/bin/pytest tests/deal_watch/test_costs.py -v`
Expected: PASS.

### Task 2: Deterministic decision policy

**Files:**
- Create: `app/deal_watch/policy.py`
- Test: `tests/deal_watch/test_policy.py`

**Interfaces:**
- Consumes: `DealMandate`, `MarketEvent`, `CostBreakdown`.
- Produces: `evaluate_event(mandate, event, evaluated_at) -> DealDecision`.

- [x] **Step 1: Write failing tests for alert, hold, and ignore**

Przypadki obejmują poprawny alert, zły wariant, brak stocku, przekroczony landed cost,
zbyt słaby stan, słabego sprzedawcę, brak wymaganej oceny i fałszywą obniżkę.

- [x] **Step 2: Run focused tests and confirm failure**

Run: `.venv/bin/pytest tests/deal_watch/test_policy.py -v`
Expected: FAIL because `evaluate_event` does not exist.

- [x] **Step 3: Implement ordered hard-failure and uncertainty rules**

Reguły budują stabilne kody `variant_mismatch`, `out_of_stock`, `budget_exceeded`,
`condition_below_minimum`, `seller_rating_below_minimum`, `fake_discount` i
`seller_rating_unknown`. Dowolna porażka daje `ignore`, brak dowodu daje `hold`, a
pełne spełnienie warunków daje `alert`.

- [x] **Step 4: Run focused tests**

Run: `.venv/bin/pytest tests/deal_watch/test_policy.py -v`
Expected: PASS.

### Task 3: Repository, service, and deterministic demo scenario

**Files:**
- Create: `app/deal_watch/repository.py`
- Create: `app/deal_watch/service.py`
- Create: `app/deal_watch/scenarios.py`
- Test: `tests/deal_watch/test_service.py`

**Interfaces:**
- Produces: `InMemoryDealWatchRepository`, `DealWatchService.create_mandate`,
  `DealWatchService.evaluate`, `DealWatchService.history`, `demo_market_events()`.

- [x] **Step 1: Write failing service and scenario tests**

Test zapis mandatu, ewaluację paczki, kolejność historii, brak mandatu i scenariusz
sześciu zdarzeń zawierający dokładnie jeden `alert` oraz co najmniej jeden `hold`.

- [x] **Step 2: Run focused tests and confirm failure**

Run: `.venv/bin/pytest tests/deal_watch/test_service.py -v`
Expected: FAIL because service modules do not exist.

- [x] **Step 3: Implement async in-memory repository and coordinating service**

Repozytorium chroni mutacje `asyncio.Lock`, zwraca kopie list i nie zawiera reguł
biznesowych. Usługa nadaje UUID, wywołuje politykę i zapisuje decyzje.

- [x] **Step 4: Implement six explicit demo events**

Zdarzenia: dobra okazja, zły wariant, wysoka dostawa, brak stocku, nieznana ocena
sprzedawcy i fałszywa obniżka.

- [x] **Step 5: Run focused tests**

Run: `.venv/bin/pytest tests/deal_watch/test_service.py -v`
Expected: PASS.

### Task 4: Thin API endpoints and application wiring

**Files:**
- Create: `app/api/deal_watch.py`
- Modify: `app/api/__init__.py`
- Modify: `app/main.py`
- Test: `tests/api/test_deal_watch.py`

**Interfaces:**
- Produces: `POST /deal-watch/mandates`, `POST /deal-watch/mandates/{id}/events`,
  `POST /deal-watch/mandates/{id}/simulate`, `GET /deal-watch/mandates/{id}/decisions`.

- [x] **Step 1: Write failing API happy-path and validation tests**

Test pełnego scenariusza, 404, dodatkowych pól, pustej paczki i więcej niż 10 zdarzeń.

- [x] **Step 2: Run focused tests and confirm failure**

Run: `.venv/bin/pytest tests/api/test_deal_watch.py -v`
Expected: FAIL with 404 because the router is not registered.

- [x] **Step 3: Implement dependency and thin route handlers**

Każdy handler jedynie pobiera usługę z `app.state`, wywołuje jedną metodę i mapuje
`MandateNotFoundError` na bezpieczne 404. Logika oceny pozostaje w usłudze/polityce.

- [x] **Step 4: Wire one service instance per FastAPI application**

`create_app` zawsze ustawia `app.state.deal_watch`, niezależnie od konfiguracji usług
zewnętrznych, i rejestruje router.

- [x] **Step 5: Run focused API tests**

Run: `.venv/bin/pytest tests/api/test_deal_watch.py -v`
Expected: PASS.

### Task 5: Documentation and complete quality gate

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-07-11-shopping-agent-backend-phases.md`

**Interfaces:**
- Produces: operator instructions and a checked Phase 5 roadmap.

- [x] **Step 1: Document endpoint flow and demo limitations**

README pokazuje utworzenie mandatu, uruchomienie symulacji i odczyt decyzji oraz mówi
wprost, że dane są pamięciowe i nie dochodzi do zakupu.

- [x] **Step 2: Update Phase 5 checklist with verified deliverables**

Zastąp rezerwową listę zaakceptowanym Deal Watch i odhacz wyłącznie funkcje pokryte
testami.

- [x] **Step 3: Run all checks**

Run: `.venv/bin/ruff check app tests scripts`
Expected: `All checks passed!`

Run: `.venv/bin/pytest`
Expected: all non-live tests pass; live tests remain skipped unless explicitly enabled.

## Self-review

- Projekt fazy 5 jest pokryty przez pięć zadań bez zmian istniejącego rankingu.
- Modele i nazwy `DealMandate`, `MarketEvent`, `CostBreakdown`, `DealDecision` są spójne.
- Plan nie zawiera późniejszych zobowiązań ani zależności od usług zewnętrznych.
- Walidacja wejścia, limity payloadu i bezpieczne 404 są częścią testów API.
