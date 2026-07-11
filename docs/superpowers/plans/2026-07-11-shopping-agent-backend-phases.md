# Shopping Agent Backend — Implementation Plan and Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dostarczyć demonstracyjne MVP backendu agenta zakupowego dla używanych słuchawek, które przyjmuje ogólną potrzebę lub produkt referencyjny, znajduje podobne i lepiej dopasowane modele, a następnie osobno ocenia produkt, ofertę i sprzedawcę bez utraty kontekstu rozmowy.

**Architecture:** Modularny monolit FastAPI zapisuje stan, produkt referencyjny, kandydatów i dane ofertowe w Supabase. Kod deterministycznie obsługuje cache, warianty, normalizację, filtry oraz trzy składowe rankingu, a dostawca LLM odpowiada za interpretację języka, identyfikację wzorca, research i krótkie wyjaśnienia. Tani etap odkrywania kandydatów poprzedza pełne pobieranie ofert, a adaptery źródeł pozostają odizolowane wspólnym protokołem.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, Supabase/PostgreSQL, pytest/pytest-asyncio, httpx, OpenAI structured output oraz Firecrawl jako pierwsze źródło danych.

## Global Constraints

- MVP obsługuje jedną kategorię: używane słuchawki.
- Agent przyjmuje dwa wejścia: opis potrzeby albo nazwę produktu referencyjnego wraz z krótką preferencją.
- Agent zadaje maksymalnie trzy pytania doprecyzowujące i przedstawia 4–6 modeli z orientacyjną ceną, podobieństwami, różnicami i kompromisem.
- Pierwsza lista służy wyborowi kierunku i nie może być przedstawiana jako ostateczny ranking ofert.
- Wyszukiwanie jest dwuetapowe: ograniczony research kandydatów, następnie pełne porównanie po wyborze kierunku.
- Finalny wynik rozdziela ocenę dopasowania produktu, jakości oferty oraz wiarygodności sprzedawcy; brak danych pozostaje jawnie oznaczony.
- Każdy fakt zewnętrzny przechowuje źródło i czas pozyskania; niepewnych danych nie wolno przedstawiać jako potwierdzonych.
- Dokładny wariant produktu jest twardym filtrem przed rankingiem.
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

## Faza 0 — Wejścia i decyzje blokujące (właściciel: człowiek + Integrator, 15–25 min) ✅ ZAMKNIĘTA

**Rezultat:** komplet sekretów, przykładowych danych oraz jednoznaczne decyzje eliminujące zgadywanie podczas implementacji. Szczegóły: `docs/superpowers/plans/2026-07-11-phase0-decisions.md`.

- [x] Potwierdzić dostępny model LLM, jego SDK, nazwę modelu, structured output, limity i budżet. → **OpenAI gpt-4o-mini, SDK openai**
- [x] Dostarczyć URL projektu Supabase, klucz backendowy i zgodę na wykonanie migracji w środowisku developerskim. → **projekt dev gotowy, klucze w lokalnym `.env`, zgoda na migracje: tak**
- [x] Dostarczyć działający kod scrapera OLX wraz z instrukcją uruchomienia i 2–3 zanonimizowanymi odpowiedziami wejście/wyjście. → **brak scrapera; Firecrawl jako jedyne źródło (nie fallback)**
- [x] Dostarczyć klucz Firecrawl albo jawnie wyłączyć fallback Firecrawl w MVP. → **Firecrawl w MVP jako primary source, klucz w lokalnym `.env`**
- [x] Ustalić, czy endpoint wyboru ma natychmiast zwracać `run_id`, a praca ma być uruchamiana przez `BackgroundTasks` — rekomendacja: tak. → **tak, BackgroundTasks + polling**
- [x] Ustalić jedno środowisko demo, publiczny adres backendu i dozwolone originy CORS. → **lokalnie localhost:8000, CORS: localhost:3000, localhost:5173**
- [x] Utworzyć trzy worktree/gałęzie i wskazać Integratora jako jedyną osobę scalającą. → **feat/integrator, feat/worker-a, feat/worker-b — utworzone**

**Brama:** ✅ spełniona — decyzje zamrożone, sekrety lokalnie, gałęzie gotowe. Integracja z usługami (Faza 2+) dopiero po smoke teście SDK w środowisku z Fazy 1.

## Faza 1 — Zamrożenie kontraktów i szkielet (Integrator, 25–35 min) ✅ ZAKOŃCZONA

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

- [x] Zapisać publiczne modele Pydantic, enumy i sygnatury protokołów.
- [x] Ustalić format błędów API i statusów `search_runs`: `pending`, `running`, `partial`, `completed`, `failed`.
- [x] Uruchomić test startu aplikacji i `/health` bez zewnętrznych usług.
- [x] Przygotować commit bazowy, z którego wystartują oba workery.

**Brama:** workerzy potwierdzają, że nie potrzebują zmian nazw pól ani sygnatur do realizacji swoich zakresów.

## Faza 2 — Równoległy rdzeń deterministyczny (35–50 min) ✅ ZAKOŃCZONA

### 2A — Dane i cache (Worker A)

**Rezultat:** migracje oraz repozytoria zapisują dane idempotentnie i podejmują testowalną decyzję cache/refetch.

**Planowane pliki:** `supabase/migrations/001_initial_schema.sql`, `app/repositories/supabase.py`, `app/services/cache_policy.py`, `tests/repositories/test_listings.py`, `tests/services/test_cache_policy.py`.

- [x] Utworzyć siedem tabel, indeksy, klucze obce i ograniczenia unikalności zgodnie ze specyfikacją.
- [x] Zaimplementować upsert ogłoszenia z aktualizacją `last_seen_at` oraz snapshotem ceny/dostępności.
- [x] Zaimplementować odczyt świeżych aktywnych ofert po twardych filtrach.
- [x] Zaimplementować decyzję `rerank`/`refetch` z progami 10/5 i TTL 24 h oraz TTL researchu 30 dni.
- [x] Udowodnić testem, że ponowny zapis `(source, external_id)` nie tworzy duplikatu.

### 2B — Źródła, normalizacja i ranking (Worker B)

**Rezultat:** fixture OLX przechodzi przez adapter i normalizator, a trzy kontrolowane oferty otrzymują stabilną kolejność i rozbicie punktów.

**Planowane pliki:** `app/sources/olx.py`, `app/sources/firecrawl.py`, `app/listings/normalizer.py`, `app/ranking/engine.py`, `app/ranking/risk.py`, `tests/fixtures/olx/`, `tests/sources/test_olx.py`, `tests/ranking/test_engine.py`.

- [x] Owinąć Firecrawl dla OLX kontraktem `ListingSource` zgodnie z decyzją Fazy 0.
- [x] Znormalizować walutę, cenę, stan, lokalizację, dostawę, kolor i identyfikator z fixture'a Firecrawl.
- [x] Ograniczyć źródło osobnym timeoutem i mapować błąd na kontrolowany rezultat.
- [x] Zaimplementować twarde filtry przed punktacją oraz dokładne składowe 30/25/20/10/10/5 minus ryzyko 0–30.
- [x] Ograniczyć dane do uzasadnienia do trzech zalet i jednego ryzyka.

### 2C — Rozmowa i LLM (Integrator)

**Rezultat:** mockowany klient LLM aktualizuje wymagania, pilnuje limitu trzech pytań i zwraca 4–6 modeli w ustrukturyzowanym formacie.

**Planowane pliki:** `app/conversation/service.py`, `app/product_research/service.py`, `app/llm/client.py`, `app/llm/schemas.py`, `tests/conversation/test_service.py`, `tests/product_research/test_service.py`.

- [x] Oddzielić klasyfikację zmiany (`rerank`, `refetch`, `new_product_research`) od wykonania decyzji.
- [x] Walidować każde structured output modelem Pydantic i wykonać najwyżej jedną próbę naprawczą.
- [x] Zapisać prompty jako wersjonowane stałe i nie pozwolić LLM decydować o progach cache ani wyniku rankingu.
- [x] Zaimplementować mock klienta używany w testach usług (pełny test API należy do Fazy 3).

**Brama:** ✅ spełniona — 16 testów przechodzi bez połączenia z produkcyjnymi usługami.

## Faza 3 — Rozszerzenie kontraktów, orkiestracja i API (Integrator, 50–70 min)

**Rezultat:** pełny przepływ od potrzeby lub produktu referencyjnego do rankingu ofert działa na mockach, zapisuje stan runu i zachowuje częściowy wynik po awarii źródła.

**Planowane pliki:** `docs/superpowers/specs/2026-07-11-shopping-agent-backend-design.md`, `app/domain/models.py`, `app/llm/schemas.py`, `app/conversation/service.py`, `app/product_research/service.py`, `app/orchestration/search.py`, `app/api/sessions.py`, `app/api/runs.py`, `app/api/products.py`, `app/api/health.py`, `tests/conversation/test_reference_product.py`, `tests/product_research/test_similarity.py`, `tests/api/test_happy_path.py`, `tests/api/test_partial_failure.py`.

- [x] Scalić 2A, uruchomić cały zestaw testów, następnie scalić 2B i ponownie uruchomić testy.
- [x] Zaktualizować specyfikację backendu o dwa wejścia, produkt referencyjny, etap eksploracji i trzy osobne składowe oceny.
- [x] Rozszerzyć modele domenowe o `reference_product`, `search_direction`, `similarity_reasons`, `differences`, `estimated_price`, `exact_variant`, `seller_signals`, `warranty`, `returns`, `data_gaps`, `confidence` i metadane źródła.
- [x] Rozszerzyć structured output rozmowy tak, aby rozpoznawał produkt referencyjny, wnioskował priorytety i nie zadawał pytania, jeśli krótka wypowiedź wystarcza do pierwszego researchu.
- [x] Zaimplementować tani etap odkrywania maksymalnie 10 kandydatów i zwracać 4–6 propozycji z ceną, podobieństwami, różnicami oraz kompromisem.
- [x] Dodać wybór kierunku: `most_similar`, `best_quality`, `lowest_price`, `best_value`; wybór aktualizuje preferencje bez resetowania sesji.
- [x] Równolegle uruchamiać brief oraz sprawdzenie lub pobranie ofert przez `asyncio.gather` z izolacją wyjątków dopiero po wyborze modelu lub kierunku.
- [x] Uruchamiać dłuższy run przez `BackgroundTasks`, od razu zwracając `run_id`.
- [x] Zapisywać status, sukcesy i błędy źródeł w `search_runs`; nie nadpisywać użytecznego cache.
- [x] Wystawić endpointy ze specyfikacji i jednolity format odpowiedzi zawierający `source_url`, `retrieved_at`, `confidence` oraz `data_gaps`.
- [x] Przetestować dwa happy pathy: wejście od potrzeby i wejście „coś jak AirPods Pro, ale taniej”.
- [x] Przetestować zachowanie kontekstu po zmianie kierunku oraz przypadek, w którym źródło pada, lecz cache pozostaje dostępny.

**Brama:** oba punkty wejścia przechodzą na mockach do co najmniej trzech ofert, cena jest widoczna od pierwszej listy, a niepewne dane pozostają oznaczone.

## Faza 4 — Podłączenie usług i utwardzenie demo (wszyscy, 25–40 min)

**Rezultat:** realna sesja demo od produktu referencyjnego kończy się w mniej niż trzy minuty i daje co najmniej trzy oferty z linkami, wariantami oraz dostępnymi sygnałami ryzyka.

- [ ] Worker A uruchamia migracje na developerskim Supabase i wykonuje smoke test repozytoriów.
- [ ] Worker B wykonuje jedno kontrolowane pobranie OLX i potwierdza normalizację realnego payloadu.
- [ ] Integrator wykonuje realne structured output LLM dla rozmowy, researchu i wyjaśnień.
- [ ] Potwierdzić, które pola dotyczące opinii, sprzedawcy, gwarancji, zwrotu, oryginalności i baterii są realnie dostępne; niedostępne pola oznaczać jako `unknown`, nie uzupełniać ich przez domysł. → **normalizator i API oznaczają braki; potwierdzenie live payloadu czeka na prawidłowy klucz Firecrawl**
- [x] Zweryfikować dokładny wariant każdej finalnej oferty i odrzucać niezgodną generację lub wersję przed scoringiem.
- [x] Zmierzyć timeout każdego źródła, całkowity czas runu i oznaczenie nieaktualnego cache.
- [ ] Przejść scenariusz: „jak AirPods Pro, ale taniej” → minimum cztery modele z ceną → `best_value` → minimum trzy oferty → „ważniejsza jest gwarancja” → rerank bez utraty kontekstu.
- [x] Pokazać osobno wynik produktu, oferty i sprzedawcy oraz co najmniej jedno jawne ograniczenie lub brak danych.
- [x] Udowodnić w logach, że pełne pobieranie ofert uruchamia się dopiero po zawężeniu kierunku.
- [x] Zapisać znane ograniczenia i komendy startowe w `README.md`.

**Brama końcowa:** komplet kryteriów z `goal.md`, brak błędu 500 przy awarii źródła, brak zmyślonych faktów oraz cały pokaz poniżej trzech minut.

## Faza 5 — Deal Watch / Mandate ✅ ZAKOŃCZONA

**Rezultat:** deterministyczny scenariusz pokazuje, że agent odrzuca pozorne okazje,
oblicza pełny koszt i emituje pojedynczy audytowalny alert wyłącznie po spełnieniu
twardych warunków mandatu. Projekt i plan: `docs/superpowers/specs/2026-07-11-phase5-deal-watch-design.md`
oraz `docs/superpowers/plans/2026-07-11-phase5-deal-watch.md`.

- [x] Dodać mandat `alert_only` z dokładnym wariantem, maksymalnym kosztem końcowym,
  minimalnym stanem i minimalną oceną sprzedawcy.
- [x] Obliczać jawny landed cost: cena + dostawa + opłaty + koszt FX − ważny kupon.
- [x] Zaimplementować decyzje `ignore`, `hold` i `alert` z kodami powodów oraz pełnym
  rachunkiem kosztu.
- [x] Dodać sześć deterministycznych zdarzeń: prawdziwa okazja, zły wariant, pułapka
  dostawy, brak stocku, brak oceny sprzedawcy i fałszywa obniżka.
- [x] Udostępnić osobne endpointy utworzenia mandatu, oceny zdarzeń, symulacji i historii.
- [x] Ograniczyć paczkę wejściową do 1–10 unikalnych zdarzeń i odrzucać dodatkowe pola.
- [x] Zapewnić idempotencję `event_id`, aby ponowienie żądania nie tworzyło drugiego alertu.
- [x] Udowodnić testami wynik scenariusza: 1 `alert`, 1 `hold`, 4 `ignore`.
- [x] Zachować izolację od OpenAI, Firecrawl i Supabase oraz nie dodawać zakupu,
  płatności, Redis ani Celery.

## Roadmapa po hackathonie

### Faza 6 — Wiarygodność danych i drugi marketplace

**Cel:** ranking korzysta z co najmniej dwóch źródeł i potrafi wyjaśnić pochodzenie oraz świeżość każdego istotnego sygnału.

- [ ] Dodać produkcyjny adapter eBay lub innego źródła z legalnym i stabilnym dostępem.
- [ ] Wprowadzić wspólny model sprzedawcy, opinii, gwarancji, zwrotów i historii sprzedaży.
- [ ] Dodać reguły rozstrzygania sprzecznych danych oraz poziom pewności per pole.
- [ ] Deduplikować tę samą ofertę lub ten sam egzemplarz widoczny w wielu źródłach.
- [ ] Monitorować świeżość, skuteczność i koszt każdego adaptera.

**Brama:** co najmniej dwa źródła przechodzą test kontraktowy, a UI potrafi wskazać źródło, czas i pewność danych.

### Faza 7 — Inteligentniejsze podobieństwo i jakość produktu

**Cel:** podobieństwo jest obliczane na poziomie cech właściwych dla kategorii, a użytkownik rozumie, co zyskuje i traci względem wzorca.

- [ ] Zdefiniować wersjonowaną ontologię cech słuchawek: konstrukcja, ANC, kodeki, bateria, mikrofon, ekosystem, komfort, serwisowalność.
- [ ] Rozdzielić twarde podobieństwo funkcjonalne od miękkiego podobieństwa marki i wyglądu.
- [ ] Włączyć jakość i wiarygodność opinii bez traktowania liczby gwiazdek jako samodzielnego dowodu.
- [ ] Dodać dane o naprawialności, dostępności części, baterii i znanych awariach wraz ze źródłami.
- [ ] Skalibrować wagi na podstawie testów użytkowników, pozostawiając jawne uzasadnienie wyniku.

**Brama:** dla zestawu referencyjnego eksperci oceniają większość Top 3 jako sensowne alternatywy, a system wskazuje kluczowy kompromis każdej z nich.

### Faza 8 — Pamięć, historia cen i proaktywne okazje

**Cel:** system wykorzystuje wcześniejsze dane do szybszych odpowiedzi i lepszej oceny opłacalności.

- [ ] Wersjonować research produktów i podobieństwa zamiast generować je od zera.
- [ ] Budować historię ceny i dostępności właściwego wariantu.
- [ ] Wykrywać okazje względem historycznej ceny, a nie tylko mediany bieżących ogłoszeń.
- [ ] Zapamiętywać preferencje użytkownika za zgodą i z możliwością ich usunięcia.
- [ ] Dodać powiadomienia o nowych ofertach spełniających zapisane kryteria.

**Brama:** cache obniża koszt i czas bez pogorszenia świeżości, a „okazja” ma audytowalne uzasadnienie historyczne.

### Faza 9 — Rozszerzenie kategorii i interakcja wizualna

**Cel:** wspólny przepływ działa dla kolejnych kategorii bez udawania, że wszystkie mają te same kryteria.

- [ ] Wydzielić konfigurację cech, filtrów i wag per kategoria.
- [ ] Dodać drugą kategorię dopiero po przejściu pełnego zestawu testów kontraktowych.
- [ ] Obsłużyć zdjęcie jako produkt referencyjny i oddzielić podobieństwo wizualne od funkcjonalnego.
- [ ] Dodać konta, zgodę na personalizację i kontrolę prywatności przed trwałą pamięcią między sesjami.
- [ ] Ocenić potrzebę kolejki zadań i workerów na podstawie realnego ruchu, nie założeń.

**Brama:** nowa kategoria przechodzi ten sam happy path, ale korzysta z własnych kryteriów produktu, wariantu i ryzyka.

## Zależności, które musi zapewnić właściciel projektu

### Blokujące przed kodowaniem integracji

- Dokładna nazwa i dostawca modelu LLM, klucz API, dozwolone SDK oraz limit kosztu/rate limit.
- Developerski projekt Supabase: `SUPABASE_URL`, backendowy `SUPABASE_SERVICE_ROLE_KEY`, hasło/connection string dla migracji oraz zgoda na utworzenie tabel.
- Firecrawl jako pierwsze źródło: `FIRECRAWL_API_KEY`, lista dozwolonych stron, oczekiwany limit użycia oraz realne, zanonimizowane fixture'y odpowiedzi.
- Potwierdzenie, że wykorzystanie wybranych domen i pobieranych pól jest zgodne z ich regulaminami oraz warunkami demo.
- Środowisko wdrożenia, domena/API URL, lista CORS oraz sposób przekazywania sekretów.

### Decyzje produktowe, które warto zamrozić

- Jeden dokładny produkt referencyjny i wariant do demo — rekomendacja: AirPods Pro z jawnym wskazaniem generacji.
- Definicja czterech kierunków: najbardziej podobny, najlepsza jakość, najniższa cena i najlepszy stosunek ceny do jakości.
- Definicja krytycznych wymagań dla słuchawek i mapa: twarde kontra miękkie preferencje.
- Minimalny zestaw cech używany do oceny podobieństwa produktu.
- Reguła dokładnego dopasowania wariantu oraz sposób prezentowania `unknown`.
- Reguła oceny stanu (`new`, `like_new`, `very_good`, `good`, `fair`, `unknown`) i minimalne sygnały ryzyka.
- Dane o sprzedawcy, opiniach, gwarancji i zwrocie, które realnie udostępnia pierwsze źródło.
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

- Nowe wymagania zmieniają kontrakty zamrożone w Fazie 1; rozszerzenia należy wykonać centralnie przed budową orkiestracji, inaczej powstaną niespójne modele API i bazy.
- „Mniej niż trzy godziny” jest realne tylko przy gotowym Firecrawl, Supabase i ograniczeniu danych sprzedawcy do pól faktycznie dostępnych w pierwszym źródle.
- Trzy modele pracujące bez osobnych gałęzi/worktree prawdopodobnie stracą czas na konflikty; integrator musi scalać sekwencyjnie.
- `BackgroundTasks` nie gwarantuje wznowienia po restarcie procesu; wystarcza do demo, ale status `running` może pozostać osierocony.
- Research oparty na LLM bez jawnego narzędzia web/retrieval może halucynować źródła; w MVP należy przechowywać tylko źródła faktycznie zwrócone przez zatwierdzony mechanizm researchu.
- Opinie, gwarancja, zwrot, oryginalność części i stan baterii mogą nie być dostępne w źródle; brak danych musi obniżać pewność, ale nie może być fałszywie uzupełniany.
- Porównywanie cen bez dokładnego wariantu prowadzi do błędnych rekomendacji; wariant jest filtrem, nie miękką preferencją.
- Dodanie wielu źródeł przed ustabilizowaniem happy path zwiększa ryzyko niespójności, duplikatów i przekroczenia czasu demo.
- Scraping OLX może podlegać ograniczeniom technicznym i regulaminowym; właściciel projektu odpowiada za zgodę, limity i zgodność użycia.
