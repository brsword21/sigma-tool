# Shopping Agent Backend — Execution Phases

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dostarczyć demonstracyjne MVP backendu agenta zakupowego dla używanych słuchawek, od rozmowy i wyboru modelu po ranking ofert oraz zmianę preferencji bez utraty kontekstu.

**Architecture:** Modularny monolit FastAPI zapisuje stan i dane domenowe w Supabase. Kod deterministycznie obsługuje cache, normalizację, filtry i ranking, a dostawca LLM odpowiada wyłącznie za interpretację języka, research i krótkie wyjaśnienia. Adaptery źródeł są izolowane wspólnym protokołem, dzięki czemu awaria źródła nie blokuje danych z cache.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, Supabase/PostgreSQL, pytest/pytest-asyncio, httpx, dostawca LLM z structured output, istniejący scraper OLX, opcjonalnie Firecrawl.

## Global Constraints

- MVP obsługuje jedną kategorię: używane słuchawki.
- Agent zadaje maksymalnie trzy pytania doprecyzowujące i przedstawia 4–6 modeli.
- Cache ofert jest wystarczający przy co najmniej 10 aktywnych ofertach z ostatnich 24 godzin; po twardym filtrowaniu ponowne pobranie następuje poniżej 5 ofert.
- TTL researchu produktu wynosi 30 dni.
- Ranking ma skalę 0–100, jawne składowe 30/25/20/10/10/5 i karę ryzyka 0–30.
- Błąd jednego źródła nie usuwa ani nie blokuje wyników pozostałych źródeł lub cache.
- Odpowiedź LLM jest walidowana przez Pydantic i ponawiana najwyżej raz.
- MVP nie używa Redis, Celery, kont użytkowników, płatności ani automatycznego zakupu.

---

## Zasada podziału między wykonawców

Nazwy wykonawców poniżej są rolami. Przed startem należy potwierdzić rzeczywiste nazwy modeli i ich limity kontekstu.

- **Integrator — GPT na ChatGPT Pro:** właściciel kontraktów, szkieletu, orkiestracji, API, integracji i końcowych merge'y.
- **Worker A — Claude Pro plan 1:** właściciel Supabase, migracji, repozytoriów, cache i idempotencji.
- **Worker B — Claude Pro plan 2:** właściciel źródeł, normalizacji, rankingu i testowych fixture'ów OLX.
- Jedna osoba/model ma wyłączne prawo edycji danego pliku w danej fazie.
- Każdy worker pracuje na osobnej gałęzi/worktree i oddaje mały commit wraz z wynikiem testów.
- Integrator zatwierdza publiczne typy przed rozpoczęciem Fazy 2; późniejsze zmiany kontraktu wymagają jawnej synchronizacji wszystkich gałęzi.

## Faza 0 — Wejścia i decyzje blokujące (właściciel: człowiek + Integrator, 15–25 min)

**Rezultat:** komplet sekretów, przykładowych danych oraz jednoznaczne decyzje eliminujące zgadywanie podczas implementacji.

- [ ] Potwierdzić dostępny model LLM, jego SDK, nazwę modelu, structured output, limity i budżet.
- [ ] Dostarczyć URL projektu Supabase, klucz backendowy i zgodę na wykonanie migracji w środowisku developerskim.
- [ ] Dostarczyć działający kod scrapera OLX wraz z instrukcją uruchomienia i 2–3 zanonimizowanymi odpowiedziami wejście/wyjście.
- [ ] Dostarczyć klucz Firecrawl albo jawnie wyłączyć fallback Firecrawl w MVP.
- [ ] Ustalić, czy endpoint wyboru ma natychmiast zwracać `run_id`, a praca ma być uruchamiana przez `BackgroundTasks` — rekomendacja: tak.
- [ ] Ustalić jedno środowisko demo, publiczny adres backendu i dozwolone originy CORS.
- [ ] Utworzyć trzy worktree/gałęzie i wskazać Integratora jako jedyną osobę scalającą.

**Brama:** nie zaczynać integracji z usługami, dopóki sekrety i próbka OLX nie przejdą prostego smoke testu.

## Faza 1 — Zamrożenie kontraktów i szkielet (Integrator, 25–35 min)

**Rezultat:** aplikacja startuje, `/health` działa lokalnie, a wszystkie równoległe strumienie importują te same typy.

**Planowane pliki:**

- `pyproject.toml` — zależności, lint i pytest.
- `.env.example` — nazwy wymaganych zmiennych bez sekretów.
- `app/main.py`, `app/config.py` — fabryka FastAPI i konfiguracja.
- `app/domain/models.py` — `SearchQuery`, `RawListing`, `NormalizedListing`, wymagania i wyniki rankingu.
- `app/sources/base.py` — `ListingSource`.
- `app/repositories/protocols.py` — interfejsy repozytoriów.
- `app/services/ports.py` — port klienta LLM i zegara.
- `tests/conftest.py`, `tests/test_health.py` — wspólne fixture'y i pierwszy smoke test.

- [ ] Zapisać publiczne modele Pydantic, enumy i sygnatury protokołów.
- [ ] Ustalić format błędów API i statusów `search_runs`: `pending`, `running`, `partial`, `completed`, `failed`.
- [ ] Uruchomić test startu aplikacji i `/health` bez zewnętrznych usług.
- [ ] Opublikować commit bazowy, z którego wystartują oba workery.

**Brama:** workerzy potwierdzają, że nie potrzebują zmian nazw pól ani sygnatur do realizacji swoich zakresów.

## Faza 2 — Równoległy rdzeń deterministyczny (35–50 min)

### 2A — Dane i cache (Worker A)

**Rezultat:** migracje oraz repozytoria zapisują dane idempotentnie i podejmują testowalną decyzję cache/refetch.

**Planowane pliki:** `supabase/migrations/001_initial_schema.sql`, `app/repositories/supabase.py`, `app/services/cache_policy.py`, `tests/repositories/test_listings.py`, `tests/services/test_cache_policy.py`.

- [ ] Utworzyć siedem tabel, indeksy, klucze obce i ograniczenia unikalności zgodnie ze specyfikacją.
- [ ] Zaimplementować upsert ogłoszenia z aktualizacją `last_seen_at` oraz snapshotem ceny/dostępności.
- [ ] Zaimplementować odczyt świeżych aktywnych ofert po twardych filtrach.
- [ ] Zaimplementować decyzję `rerank`/`refetch` z progami 10/5 i TTL 24 h oraz TTL researchu 30 dni.
- [ ] Udowodnić testem, że ponowny zapis `(source, external_id)` nie tworzy duplikatu.

### 2B — Źródła, normalizacja i ranking (Worker B)

**Rezultat:** fixture OLX przechodzi przez adapter i normalizator, a trzy kontrolowane oferty otrzymują stabilną kolejność i rozbicie punktów.

**Planowane pliki:** `app/sources/olx.py`, `app/sources/firecrawl.py`, `app/listings/normalizer.py`, `app/ranking/engine.py`, `app/ranking/risk.py`, `tests/fixtures/olx/`, `tests/sources/test_olx.py`, `tests/ranking/test_engine.py`.

- [ ] Owinąć istniejący scraper kontraktem `ListingSource`; nie przepisywać scrapera w pierwszej iteracji.
- [ ] Znormalizować walutę, cenę, stan, lokalizację, dostawę, kolor i identyfikator z realnego fixture'a.
- [ ] Ograniczyć każde źródło osobnym timeoutem i mapować błąd na kontrolowany rezultat.
- [ ] Zaimplementować twarde filtry przed punktacją oraz dokładne składowe 30/25/20/10/10/5 minus ryzyko 0–30.
- [ ] Ograniczyć dane do uzasadnienia do trzech zalet i jednego ryzyka.

### 2C — Rozmowa i LLM (Integrator)

**Rezultat:** mockowany klient LLM aktualizuje wymagania, pilnuje limitu trzech pytań i zwraca 4–6 modeli w ustrukturyzowanym formacie.

**Planowane pliki:** `app/conversation/service.py`, `app/product_research/service.py`, `app/llm/client.py`, `app/llm/schemas.py`, `tests/conversation/test_service.py`, `tests/product_research/test_service.py`.

- [ ] Oddzielić klasyfikację zmiany (`rerank`, `refetch`, `new_product_research`) od wykonania decyzji.
- [ ] Walidować każde structured output modelem Pydantic i wykonać najwyżej jedną próbę naprawczą.
- [ ] Zapisać prompty jako wersjonowane stałe i nie pozwolić LLM decydować o progach cache ani wyniku rankingu.
- [ ] Zaimplementować mock klienta używany w pełnym teście API.

**Brama:** wszystkie trzy gałęzie przechodzą własne testy bez połączenia z produkcyjnymi usługami.

## Faza 3 — Integracja orkiestracji i API (Integrator, 35–50 min)

**Rezultat:** pełny przepływ API działa na mockach, zapisuje stan runu i zachowuje częściowy wynik po awarii źródła.

**Planowane pliki:** `app/orchestration/search.py`, `app/api/sessions.py`, `app/api/runs.py`, `app/api/products.py`, `app/api/health.py`, `tests/api/test_happy_path.py`, `tests/api/test_partial_failure.py`.

- [ ] Scalić 2A, uruchomić cały zestaw testów, następnie scalić 2B i ponownie uruchomić testy.
- [ ] Równolegle uruchamiać brief oraz sprawdzenie/pobranie ofert przez `asyncio.gather` z izolacją wyjątków.
- [ ] Uruchamiać dłuższy run przez `BackgroundTasks`, od razu zwracając `run_id`.
- [ ] Zapisywać status, sukcesy i błędy źródeł w `search_runs`; nie nadpisywać użytecznego cache.
- [ ] Wystawić siedem endpointów ze specyfikacji i jednolity format odpowiedzi.
- [ ] Przetestować happy path oraz przypadek: jedno źródło pada, wynik drugiego/cache pozostaje dostępny.

**Brama:** kryteria akceptacji przechodzą w całości na mockowanym LLM i źródle.

## Faza 4 — Podłączenie usług i utwardzenie demo (wszyscy, 25–40 min)

**Rezultat:** realna sesja demo kończy się w mniej niż trzy minuty i daje co najmniej trzy oferty z linkami.

- [ ] Worker A uruchamia migracje na developerskim Supabase i wykonuje smoke test repozytoriów.
- [ ] Worker B wykonuje jedno kontrolowane pobranie OLX i potwierdza normalizację realnego payloadu.
- [ ] Integrator wykonuje realne structured output LLM dla rozmowy, researchu i wyjaśnień.
- [ ] Zmierzyć timeout każdego źródła, całkowity czas runu i oznaczenie nieaktualnego cache.
- [ ] Przejść scenariusz: nowa sesja → minimum cztery modele → wybór → minimum trzy oferty → zmiana preferencji → rerank bez utraty kontekstu.
- [ ] Zapisać znane ograniczenia i komendy startowe w `README.md`.

**Brama końcowa:** komplet kryteriów z sekcji 11 specyfikacji, brak błędu 500 przy awarii źródła i cały pokaz poniżej trzech minut.

## Faza 5 — Rezerwa, tylko po spełnieniu MVP

- [ ] Dodać Firecrawl jako fallback, jeśli klucz i domeny są gotowe, a OLX okazał się niestabilny.
- [ ] Dodać drugi adapter wyłącznie wtedy, gdy nie wymaga zmiany domenowych kontraktów.
- [ ] Poprawić obserwowalność i logi korelacyjne przez `session_id` i `run_id`.
- [ ] Nie dodawać Redis/Celery, autoryzacji, płatności ani uczenia rankera w trzygodzinnym oknie.

## Zależności, które musi zapewnić właściciel projektu

### Blokujące przed kodowaniem integracji

- Dokładna nazwa i dostawca modelu LLM, klucz API, dozwolone SDK oraz limit kosztu/rate limit.
- Developerski projekt Supabase: `SUPABASE_URL`, backendowy `SUPABASE_SERVICE_ROLE_KEY`, hasło/connection string dla migracji oraz zgoda na utworzenie tabel.
- Istniejący scraper OLX: repozytorium lub katalog, wersja uruchomieniowa, licencja, sposób uwierzytelnienia/proxy oraz realne, zanonimizowane fixture'y.
- Decyzja, czy Firecrawl wchodzi do MVP; jeśli tak: `FIRECRAWL_API_KEY`, lista dozwolonych stron i oczekiwany limit użycia.
- Środowisko wdrożenia, domena/API URL, lista CORS oraz sposób przekazywania sekretów.

### Decyzje produktowe, które warto zamrozić

- Definicja krytycznych wymagań dla słuchawek i mapa: twarde kontra miękkie preferencje.
- Reguła oceny stanu (`new`, `like_new`, `very_good`, `good`, `fair`, `unknown`) i minimalne sygnały ryzyka.
- Czy „minimum trzy oferty” może pochodzić z nieaktualnego cache, gdy wszystkie źródła zawiodą — rekomendacja: tak, z datą pobrania.
- Język odpowiedzi i waluta demo — rekomendacja: polski i PLN.
- Jedna konkretna ścieżka demo wraz z przykładowym budżetem, modelem oraz zmianą preferencji.

### Zależności programistyczne do zatwierdzenia

- Python `>=3.12,<3.13`.
- `fastapi`, `uvicorn[standard]`, `pydantic>=2`, `pydantic-settings`, `httpx`.
- Oficjalny klient wybranego LLM; tylko jeden dostawca w MVP.
- `supabase` albo bezpośrednio `asyncpg`/PostgREST — rekomendacja dla szybkości MVP: klient `supabase`, migracje SQL wykonywane osobno.
- `pytest`, `pytest-asyncio`, `respx`, `time-machine` lub równoważny wstrzykiwany zegar.
- `ruff` i opcjonalnie `mypy`; nie blokować demo rozbudowaną konfiguracją CI.

## Ryzyka harmonogramu

- „Mniej niż trzy godziny” jest realne tylko przy działającym scraperze, gotowym Supabase i braku zmian kontraktów po Fazie 1.
- Trzy modele pracujące bez osobnych gałęzi/worktree prawdopodobnie stracą czas na konflikty; integrator musi scalać sekwencyjnie.
- `BackgroundTasks` nie gwarantuje wznowienia po restarcie procesu; wystarcza do demo, ale status `running` może pozostać osierocony.
- Research oparty na LLM bez jawnego narzędzia web/retrieval może halucynować źródła; w MVP należy przechowywać tylko źródła faktycznie zwrócone przez zatwierdzony mechanizm researchu.
- Scraping OLX może podlegać ograniczeniom technicznym i regulaminowym; właściciel projektu odpowiada za zgodę, limity i zgodność użycia.
