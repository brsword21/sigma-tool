# Shopping Agent Backend — Implementation Plan and Roadmap 2.0

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dostarczyć demonstracyjne MVP backendu agenta zakupowego dla używanych słuchawek, które przyjmuje ogólną potrzebę lub produkt referencyjny, znajduje podobne i lepiej dopasowane modele, a następnie osobno ocenia produkt, ofertę i sprzedawcę bez utraty kontekstu rozmowy.

**Architecture:** Modularny monolit FastAPI zapisuje stan, produkt referencyjny, kandydatów i dane ofertowe w Supabase. Kod deterministycznie obsługuje cache, warianty, normalizację, filtry oraz trzy składowe rankingu, a dostawca LLM odpowiada za interpretację języka, identyfikację wzorca, research i krótkie wyjaśnienia. Tani etap odkrywania kandydatów poprzedza pełne pobieranie ofert, a adaptery źródeł pozostają odizolowane wspólnym protokołem.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, Supabase/PostgreSQL, pytest/pytest-asyncio, httpx, OpenAI structured output oraz Firecrawl jako pierwsze źródło danych.

## Status wersji 2.0 — 2026-07-11

- Fazy 0 i 1 są zamknięte.
- Rdzeń deterministyczny oraz mockowy przepływ API powstały w commitach `2399c36` i `756dd27`.
- Oba punkty wejścia dochodzą na mockach do listy kandydatów i trzech konkretnych ofert.
- Do zamknięcia przepływu na mockach brakuje pełnego rerankingu po zmianie preferencji wyrażonej naturalnym językiem, np. „ważniejsza jest gwarancja niż najniższa cena”.
- Integracje OpenAI, Firecrawl i Supabase nie zostały jeszcze wspólnie zweryfikowane w pełnej sesji na żywo.
- Wersja 2.0 zastępuje techniczny podział dawnej fazy 2 podziałem zgodnym z dwunastoma krokami doświadczenia użytkownika.

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

## Zasada realizacji wersji 2.0

- Fazy 0–2 opisują stan historyczny osiągnięty na gałęzi głównej; nie należy ponownie wykonywać zamkniętych zadań.
- Faza 3 jest najbliższym aktywnym zakresem i powinna zostać wykonana przed podłączaniem usług na żywo.
- Integrator pozostaje właścicielem publicznych kontraktów, orkiestracji, API i końcowego scalenia.
- Prace można delegować według obszarów: Supabase i cache, źródła i normalizacja, rozmowa i ranking. Jeden plik ma jednego właściciela w danym momencie.
- Każda równoległa praca powinna powstać na osobnej gałęzi lub w osobnym worktree i zakończyć się małym commitem z wynikiem testów.
- Zmiana publicznego modelu Pydantic, protokołu repozytorium albo kontraktu endpointu wymaga aktualizacji specyfikacji i testów kontraktowych przed scaleniem.

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

## Faza 2 — Pełny przepływ agenta zakupowego na mockach (Integrator + Worker A + Worker B) — W TOKU

**Cel fazy:** przeprowadzić użytkownika od krótkiego opisu potrzeby lub produktu referencyjnego do uzasadnionego rankingu konkretnych ofert. Podział jest zgodny z przebiegiem doświadczenia użytkownika, a nie z wewnętrznymi modułami technicznymi.

**Zasada wykonania:** kroki 2.1–2.6 tworzą tani etap odkrywania produktu. Dopiero wybór kierunku w kroku 2.6 pozwala uruchomić pełne pobieranie i ocenę ofert w krokach 2.7–2.11. Krok 2.12 ponownie wykorzystuje zapisany kontekst i wcześniejszy research.

### 2.1 — Przyjęcie zapytania

**Rezultat:** jedna sesja przyjmuje zarówno opis potrzeby, jak i nazwę produktu referencyjnego z krótką preferencją.

- [x] Obsłużyć wejście od potrzeby, np. „Szukam słuchawek z ANC do 500 zł”.
- [x] Obsłużyć wejście od wzorca, np. „Coś jak AirPods Pro, ale taniej”.
- [x] Zapisać wiadomość i stan rozmowy pod jednym `session_id`.
- [x] Nie wymagać od użytkownika znajomości parametrów technicznych ani wypełniania formularza wag.

### 2.2 — Rozpoznanie intencji

**Rezultat:** agent zamienia krótką wypowiedź na ustrukturyzowane wymagania i, jeśli występuje, identyfikuje produkt referencyjny.

- [x] Rozpoznać kategorię, budżet, wymagane funkcje i preferencje miękkie.
- [x] Rozpoznać markę, model i dostępny wariant produktu referencyjnego.
- [x] Wywnioskować prawdopodobne priorytety bez przedstawiania ich jako potwierdzonych faktów.
- [x] Walidować structured output przez Pydantic i ponawiać niepoprawną odpowiedź najwyżej raz.

### 2.3 — Uzupełnienie brakujących informacji

**Rezultat:** agent pyta tylko o informację, która realnie może zmienić listę kandydatów lub ranking.

- [x] Zadawać najwyżej jedno pytanie naraz.
- [x] Ograniczyć całą sesję do maksymalnie trzech pytań doprecyzowujących.
- [x] Pominąć pytanie, gdy dostępne dane wystarczają do rozpoczęcia szybkiego researchu.
- [x] Zachować wcześniejsze wymagania po każdej odpowiedzi użytkownika.

### 2.4 — Szybki research produktów

**Rezultat:** tani etap researchu znajduje pulę możliwych modeli bez pobierania pełnych danych ofertowych.

- [x] Uruchomić research produktu referencyjnego i alternatyw z limitem maksymalnie 10 kandydatów.
- [x] Ponownie użyć świeżego researchu produktu przez 30 dni.
- [x] Zachować źródło, czas pobrania, poziom pewności i braki danych.
- [x] Nie uruchamiać pełnego wyszukiwania ofert na tym etapie.

### 2.5 — Prezentacja kandydatów

**Rezultat:** użytkownik otrzymuje 4–6 modeli wystarczających do świadomego wyboru kierunku.

- [x] Pokazać nazwę modelu i orientacyjną cenę od pierwszej listy.
- [x] Dla każdego modelu pokazać podobieństwa, różnice, krótkie uzasadnienie i główny kompromis.
- [x] Oznaczyć listę jako etap eksploracji przez `is_final_ranking=false`.
- [x] Nie mieszać kandydatów produktowych z konkretnymi ogłoszeniami.

### 2.6 — Wybór kierunku

**Rezultat:** użytkownik prostym wyborem wskazuje, jak agent ma zawęzić dalsze wyszukiwanie.

- [x] Obsłużyć kierunki `most_similar`, `best_quality`, `lowest_price` i `best_value`.
- [x] Zapisać wybrany model oraz kierunek w istniejącej sesji.
- [x] Nie resetować rozmowy ani zebranego researchu.
- [x] Dopiero po tym kroku utworzyć `search_run` i uruchomić pracę w tle.

### 2.7 — Wyszukanie konkretnych ofert

**Rezultat:** dla wybranego modelu lub kierunku agent znajduje co najmniej trzy konkretne oferty.

- [x] Najpierw sprawdzić świeży cache po twardych filtrach, a następnie podjąć deterministyczną decyzję `rerank` albo `refetch`.
- [x] Pobierać oferty przez adapter `ListingSource`, z osobnym timeoutem i izolacją błędów źródła.
- [x] Zapisywać dane idempotentnie według `(source, external_id)` oraz aktualizować `last_seen_at`.
- [x] Zachować użyteczny cache, gdy zewnętrzne źródło zwróci błąd.

### 2.8 — Normalizacja i weryfikacja danych

**Rezultat:** dane z ogłoszeń mają wspólny format, a niezgodne warianty nie trafiają do rankingu.

- [x] Znormalizować cenę, walutę, stan, lokalizację, dostawę, kolor, wariant i identyfikator.
- [x] Sprawdzić budżet, wymagane funkcje i dokładny wariant jako twarde filtry przed scoringiem.
- [x] Rozróżnić wartość `unknown` od negatywnego sygnału.
- [x] Zachować `source_url`, `retrieved_at`, `confidence` i `data_gaps` dla każdej oferty.

### 2.9 — Ocena w trzech obszarach

**Rezultat:** każda oferta otrzymuje trzy jawne, niezależnie prezentowane oceny.

- [x] Obliczyć `product_match_score` dla dopasowania modelu do potrzeb i produktu referencyjnego.
- [x] Obliczyć `offer_quality_score` na podstawie ceny, stanu, kompletności i logistyki.
- [x] Obliczyć `seller_trust_score` z dostępnych sygnałów sprzedawcy, bez uzupełniania braków domysłem.
- [x] Zachować deterministyczny scoring 30/25/20/10/10/5 i karę ryzyka 0–30 jako audytowalne rozbicie techniczne.

### 2.10 — Przygotowanie rankingu

**Rezultat:** zgodne oferty są ułożone stabilnie według wybranego kierunku, a wynik można wyjaśnić.

- [x] Zastosować twarde filtry przed punktacją.
- [x] Sortować wyniki zgodnie z kierunkiem i deterministycznie rozstrzygać remisy.
- [x] Ograniczyć uzasadnienie do maksymalnie trzech zalet oraz jednego głównego ryzyka lub kompromisu.
- [x] Zwrócić częściowy ranking z cache, jeśli źródło zawiedzie.

### 2.11 — Wskazanie rekomendacji

**Rezultat:** użytkownik otrzymuje krótką listę ofert, wyróżnioną rekomendację i jawne ograniczenia danych.

- [x] Zwrócić co najmniej trzy oferty w kontrolowanym happy pathie.
- [x] Pokazać osobno dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy.
- [x] Dołączyć link, czas pobrania, poziom pewności, braki danych oraz ryzyko.
- [x] Nie przedstawiać niepotwierdzonych informacji o gwarancji, zwrocie, baterii lub oryginalności jako faktów.

### 2.12 — Aktualizacja po zmianie preferencji

**Rezultat:** pojedyncza zmiana priorytetu aktualizuje wynik bez utraty kontekstu i bez niepotrzebnego powtarzania całego procesu.

- [x] Sklasyfikować zmianę jako `rerank`, `refetch` albo `new_product_research`.
- [x] Zachować `session_id`, wybrany produkt, wymagania i wcześniejszy research.
- [x] Dla zmiany kierunku, np. z `lowest_price` na `best_value`, aktualizować preferencje bez resetu sesji.
- [ ] Potwierdzić testem end-to-end, że zdanie „ważniejsza jest gwarancja niż najniższa cena” ponownie przelicza istniejący ranking bez zbędnego pobierania ofert.

**Planowane i istniejące pliki fazy:** `app/conversation/service.py`, `app/product_research/service.py`, `app/orchestration/search.py`, `app/api/sessions.py`, `app/api/runs.py`, `app/sources/firecrawl.py`, `app/listings/normalizer.py`, `app/ranking/engine.py`, `app/repositories/supabase.py`, `app/services/cache_policy.py` oraz odpowiadające im testy w `tests/`.

**Brama:** oba wejścia prowadzą do 4–6 kandydatów, wybór kierunku uruchamia pełne wyszukiwanie, wynik zawiera minimum trzy oferty z trzema osobnymi ocenami, a zmiana preferencji zachowuje kontekst. Do pełnego zamknięcia ścieżki pozostaje test rerankingu po zmianie priorytetu gwarancji.

## Faza 3 — Domknięcie przepływu na mockach (Integrator, 30–45 min)

**Cel:** zakończyć jedyny niepotwierdzony element fazy 2: aktualizację istniejącego rankingu po zmianie miękkiej preferencji wyrażonej naturalnym językiem.

**Rezultat:** po wiadomości „ważniejsza jest gwarancja niż najniższa cena” agent zachowuje sesję, produkt i zebrane oferty, aktualizuje wymagania oraz przelicza ranking bez zbędnego wywołania Firecrawl.

**Planowane pliki:** `app/conversation/service.py`, `app/orchestration/search.py`, `app/api/sessions.py`, `app/api/runs.py`, `tests/api/test_rerank_after_preference_change.py`.

- [ ] Obsłużyć wiadomość użytkownika na etapie `results` bez rozpoczynania nowej sesji.
- [ ] Przetłumaczyć zmianę preferencji na jawne wymagania domenowe, np. priorytet gwarancji lub ceny.
- [ ] Rozróżnić miękki `rerank` od zmiany modelu lub twardego wariantu wymagającej `refetch` albo `new_product_research`.
- [ ] Dla `rerank` wykorzystać zapisane, nadal świeże oferty i nie wywoływać adaptera źródła.
- [ ] Utworzyć nową wersję wyniku lub runu z powiązaniem do poprzedniego, aby historia decyzji była audytowalna.
- [ ] Zwrócić zaktualizowany ranking z krótką informacją, co zmieniło kolejność ofert.
- [ ] Dodać test end-to-end liczący wywołania źródła i potwierdzający zachowanie `session_id`, `selected_product_id` oraz researchu.
- [ ] Uruchomić pełny zestaw testów jednostkowych i API.

**Brama:** scenariusz zmiany priorytetu przechodzi na mockach, ranking faktycznie zmienia kolejność, a licznik wywołań źródła nie rośnie dla czystego `rerank`.

## Faza 4 — Integracje na żywo i zgodność danych (wszyscy, 45–75 min)

**Cel:** zastąpić mocki rzeczywistymi klientami OpenAI, Supabase i Firecrawl bez zmiany kontraktów domenowych.

**Rezultat:** lokalna sesja przechodzi kroki 2.1–2.12 z realnymi usługami, a braki danych są oznaczone jako `unknown` lub `data_gaps`.

### 4A — Supabase

- [ ] Uruchomić migracje na developerskim projekcie Supabase.
- [ ] Wykonać smoke test zapisu sesji, produktu, researchu, ofert, historii ceny, runu i rekomendacji.
- [ ] Potwierdzić idempotencję `(source, external_id)` oraz aktualizację `last_seen_at`.
- [ ] Zweryfikować progi cache 10/5, TTL ofert 24 h i TTL researchu 30 dni na rzeczywistych rekordach.
- [ ] Udokumentować ponowne uruchomienie migracji i czyszczenie wyłącznie danych demonstracyjnych.

### 4B — OpenAI

- [ ] Wykonać realne structured output dla rozpoznania intencji, produktu referencyjnego i kandydatów.
- [ ] Potwierdzić limit trzech pytań oraz maksymalnie jedną próbę naprawczą.
- [ ] Sprawdzić, że model nie tworzy źródeł, których nie zwrócił zatwierdzony mechanizm researchu.
- [ ] Zmierzyć liczbę wywołań, tokeny, koszt i opóźnienie pełnej sesji.
- [ ] Zapisać wersję promptu i nazwę modelu przy wyniku researchu.

### 4C — Firecrawl i pierwsze źródło

- [ ] Wykonać kontrolowane pobranie ofert dla zatwierdzonego wariantu słuchawek.
- [ ] Potwierdzić dostępność pól: wariant, stan, sprzedawca, opinie, gwarancja, zwrot, bateria i oryginalność.
- [ ] Niedostępnych pól nie uzupełniać domysłem; zapisywać `unknown` i `data_gaps`.
- [ ] Potwierdzić timeout, limity, dozwolone domeny i zgodność użycia z regulaminem źródła.
- [ ] Zachować częściowy wynik lub cache po błędzie Firecrawl.

### 4D — Pełna sesja integracyjna

- [ ] Przejść ścieżkę: produkt referencyjny → 4–6 kandydatów z ceną → `best_value` → minimum trzy oferty.
- [ ] Potwierdzić twarde odrzucanie błędnej generacji lub wariantu przed scoringiem.
- [ ] Pokazać osobno `product_match_score`, `offer_quality_score` i `seller_trust_score`.
- [ ] Zmienić preferencję na ważniejszą gwarancję i potwierdzić reranking bez utraty kontekstu.
- [ ] Zapisać logi korelacyjne z `session_id` i `run_id` dla całej ścieżki.

**Brama:** pełna sesja na żywo kończy się bez błędu 500, zwraca minimum trzy aktualne lub jawnie oznaczone jako nieaktualne oferty i nie zawiera zmyślonych faktów.

## Faza 5 — Utwardzenie i próba generalna demo (wszyscy, 30–60 min)

**Cel:** uzyskać powtarzalny pokaz poniżej trzech minut, odporny na typowe awarie usług.

**Rezultat:** jedna komenda uruchamia backend, scenariusz działa dwukrotnie z rzędu, a prowadzący zna wariant awaryjny.

- [ ] Zamrozić dokładny produkt referencyjny i wariant; rekomendacja: jawnie wskazana generacja AirPods Pro.
- [ ] Zamrozić budżet, język polski, walutę PLN oraz cztery kierunki wyszukiwania.
- [ ] Dodać kontrolowane dane demo lub świeży cache jako plan awaryjny, bez przedstawiania ich jako danych pobranych na żywo.
- [ ] Ustawić budżety czasu dla rozmowy, researchu, źródła i całego runu.
- [ ] Pokazać status `pending`, `running`, `partial`, `completed` albo `failed` bez blokowania żądania HTTP.
- [ ] Przećwiczyć awarię OpenAI, Firecrawl i Supabase oraz sprawdzić komunikaty błędów.
- [ ] Wykonać dwie pełne próby z pomiarem czasu i kosztu.
- [ ] Zaktualizować `README.md`: konfiguracja, migracje, start, testy, scenariusz demo i ograniczenia.
- [ ] Zapisać wynik próby: czas, liczba zapytań, liczba ofert, użycie cache i braki danych.

**Brama końcowa MVP:** scenariusz trwa poniżej trzech minut, cena jest widoczna od pierwszej listy, ranking ma trzy osobne oceny, zmiana preferencji nie resetuje sesji, a awaria pojedynczej usługi nie prowadzi do niekontrolowanego błędu 500.

## Faza 6 — Wiarygodność danych i drugi marketplace

**Cel:** ranking korzysta z co najmniej dwóch legalnych i stabilnych źródeł oraz wyjaśnia pochodzenie każdego istotnego sygnału.

- [ ] Dodać drugi adapter, preferencyjnie API eBay lub inne źródło z oficjalnym dostępem.
- [ ] Wprowadzić wspólny model sprzedawcy, opinii, gwarancji, zwrotów i historii sprzedaży.
- [ ] Dodać poziom pewności per pole oraz reguły rozstrzygania sprzecznych danych.
- [ ] Deduplikować tę samą ofertę lub egzemplarz widoczny w wielu źródłach.
- [ ] Monitorować świeżość, skuteczność, koszt i czas odpowiedzi każdego adaptera.
- [ ] Testować adaptery wspólnym zestawem testów kontraktowych.

**Brama:** minimum dwa źródła przechodzą testy kontraktowe, a wynik wskazuje źródło, czas pobrania i pewność każdego kluczowego pola.

## Faza 7 — Inteligentniejsze podobieństwo i jakość produktu

**Cel:** dopasowanie produktu jest liczone na cechach właściwych dla słuchawek, a użytkownik rozumie zyski i kompromisy względem wzorca.

- [ ] Zdefiniować wersjonowaną ontologię: konstrukcja, ANC, kodeki, bateria, mikrofon, ekosystem, komfort i serwisowalność.
- [ ] Rozdzielić twarde podobieństwo funkcjonalne od miękkiego podobieństwa marki i wyglądu.
- [ ] Dodać wiarygodne dane o naprawialności, częściach, baterii i znanych awariach wraz ze źródłami.
- [ ] Uwzględnić jakość i liczbę opinii bez traktowania samej średniej gwiazdek jako dowodu.
- [ ] Kalibrować wagi na ocenach użytkowników, zachowując jawne uzasadnienie.
- [ ] Wersjonować model podobieństwa, aby starsze rekomendacje pozostały audytowalne.

**Brama:** eksperci uznają większość Top 3 zestawu referencyjnego za sensowne alternatywy, a każda ma jasno opisany kompromis.

## Faza 8 — Pamięć, historia cen i proaktywne okazje

**Cel:** system wykorzystuje wcześniejsze dane do szybszych odpowiedzi i lepszej oceny opłacalności.

- [ ] Wersjonować research produktów i ponownie wykorzystywać obliczone podobieństwo.
- [ ] Budować historię ceny oraz dostępności dokładnego wariantu.
- [ ] Wykrywać okazje względem historii cen, a nie tylko bieżącej mediany.
- [ ] Zapamiętywać preferencje wyłącznie za zgodą i z możliwością usunięcia.
- [ ] Dodać zapisane wyszukiwania i powiadomienia o nowych ofertach.
- [ ] Rozróżniać nieaktualny cache od historycznego dowodu cenowego.

**Brama:** cache mierzalnie zmniejsza czas i koszt, a każda „okazja” ma audytowalne uzasadnienie historyczne.

## Faza 9 — Kolejne kategorie i skalowanie produkcyjne

**Cel:** wspólny przepływ obsługuje następne kategorie bez założenia, że wszystkie produkty mają te same cechy i ryzyka.

- [ ] Wydzielić konfigurację cech, twardych filtrów, wariantów i wag per kategoria.
- [ ] Dodać drugą kategorię dopiero po przejściu pełnego zestawu testów kontraktowych.
- [ ] Obsłużyć zdjęcie jako produkt referencyjny i oddzielić podobieństwo wizualne od funkcjonalnego.
- [ ] Dodać konta, zgodę na personalizację i kontrolę prywatności przed pamięcią między sesjami.
- [ ] Zastąpić `BackgroundTasks` trwałą kolejką dopiero po potwierdzeniu potrzeby przez ruch.
- [ ] Dodać obserwowalność, alerty, limity kosztu oraz odzyskiwanie osieroconych runów.

**Brama:** druga kategoria przechodzi przepływ 2.1–2.12, korzystając z własnych kryteriów produktu, wariantu i ryzyka.

## Definition of Done dla MVP 2.0

- [ ] Oba punkty wejścia działają w jednej sesji.
- [ ] Agent zadaje maksymalnie trzy potrzebne pytania.
- [ ] Pierwsza lista zawiera 4–6 modeli, ceny, różnice i kompromisy oraz nie udaje finalnego rankingu.
- [ ] Pełne pobieranie ofert rozpoczyna się dopiero po wyborze kierunku.
- [ ] Co najmniej trzy oferty przechodzą kontrolę wariantu i ranking.
- [ ] Wynik pokazuje osobno dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy.
- [ ] Każdy zewnętrzny fakt ma źródło, czas pobrania i pewność lub jawny brak danych.
- [ ] Zmiana miękkiej preferencji wykonuje rerank bez resetu sesji i bez zbędnego refetchu.
- [ ] Awaria źródła zachowuje cache i prowadzi do wyniku `partial` zamiast błędu 500.
- [ ] Pełna sesja na żywo została dwukrotnie wykonana poniżej trzech minut.
- [ ] `README.md` zawiera komplet komend oraz znane ograniczenia.

## Potwierdzone zależności

- OpenAI `gpt-4o-mini` i oficjalne SDK `openai`.
- Developerski projekt Supabase oraz lokalne sekrety w `.env`.
- Firecrawl jako jedyne źródło ofert w MVP.
- FastAPI `BackgroundTasks` i polling runu w wersji demo.
- Backend na `localhost:8000` oraz CORS dla `localhost:3000` i `localhost:5173`.
- Python `>=3.12,<3.13`, FastAPI, Pydantic 2, httpx, pytest i pytest-asyncio.

## Decyzje wymagające zamrożenia przed fazą 4

- Dokładna generacja i wariant AirPods Pro używane w demo.
- Budżet demonstracyjny oraz minimalny zestaw twardych cech słuchawek.
- Zakres domen dozwolonych w Firecrawl i potwierdzenie zgodności ich użycia.
- Pola sprzedawcy, gwarancji, zwrotu, baterii i oryginalności dostępne w pierwszym źródle.
- Reguła użycia nieaktualnego cache, gdy wszystkie źródła zawiodą.
- Maksymalny koszt oraz limit czasu jednej sesji.

## Aktualne ryzyka

- Naturalnojęzykowa zmiana preferencji nie ma jeszcze potwierdzonego rerankingu end-to-end.
- `BackgroundTasks` nie wznawia pracy po restarcie; osierocony run może pozostać `running`.
- Firecrawl lub strona źródłowa mogą zwrócić niepełny albo zmieniony payload.
- Dane o gwarancji, zwrocie, sprzedawcy, baterii i oryginalności mogą być niedostępne; nie wolno zastępować ich wnioskami LLM.
- Porównanie cen bez dokładnego wariantu prowadzi do błędnej rekomendacji; wariant pozostaje twardym filtrem.
- Jeden wynik 0–100 może ukrywać słabego sprzedawcę; interfejs musi eksponować trzy osobne oceny.
- Realne sekrety i migracje nie zostały jeszcze zweryfikowane razem w pełnym przepływie.
- Testów nie udało się uruchomić w bieżącym środowisku Codex: systemowy Python i `pytest` nie są dostępne, a dołączony runtime nie zawiera `pytest`.
- Scraping marketplace'u może podlegać ograniczeniom technicznym i regulaminowym; właściciel projektu odpowiada za zgodę i limity.
