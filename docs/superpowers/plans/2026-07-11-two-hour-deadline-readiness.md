# Picky — plan gotowości demo na ostatnie 2 godziny

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Doprowadzić istniejący backend i rozpoczęty frontend do jednego powtarzalnego, widocznego w przeglądarce scenariusza z `goal.md`: od krótkiej potrzeby do co najmniej trzech ofert, rekomendacji i zmiany priorytetu bez utraty kontekstu.

**Architecture:** Nie zmieniamy sprawdzonego backendu ani modelu danych. Domykamy cienką aplikację React nad istniejącymi endpointami sesji i runów, z jawnym stanem częściowego błędu oraz kontrolowanym trybem demonstracyjnym uruchamianym wyłącznie decyzją prezentera. Ostatnie 30 minut jest zamrożone na weryfikację i próbę prezentacji, nie na nowe funkcje.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Supabase, OpenAI, Firecrawl, React, TypeScript, Vite, Vitest, CSS.

## Global Constraints

- `goal.md` jest źródłem prawdy dla zakresu produktu i kryteriów ukończenia.
- Obsługiwana kategoria demonstracyjna to wyłącznie słuchawki.
- Pytania doprecyzowujące nie mogą przekroczyć trzech w jednej sesji.
- Pierwsza lista zawiera 4–6 modeli; finalny widok zawiera co najmniej trzy konkretne oferty.
- Dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy pozostają trzema osobnymi ocenami.
- Brak danych jest pokazywany jako brak danych, nigdy jako sygnał pozytywny.
- Nie dodajemy płatności, kolejnej kategorii, nowego marketplace’u, produkcyjnego schedulera ani nowego systemu uwierzytelniania.
- Po T-30 nie wprowadzamy zmian funkcjonalnych; poprawiamy tylko błędy blokujące scenariusz demo.

---

## 1. Zweryfikowany stan wyjściowy

### Dowody techniczne

- `.venv/bin/ruff check app tests scripts`: wynik pozytywny.
- `.venv/bin/pytest`: **66 testów przeszło, 3 testy live pominięto**, jedno ostrzeżenie deprecacyjne z biblioteki testowej.
- Usługi zewnętrzne są skonfigurowane lokalnie, ale bieżąca analiza nie zużywała limitów OpenAI/Firecrawl i nie zapisywała do developerskiego Supabase.
- `npm run build` w `frontend/` nie przechodzi: zależności nie są zainstalowane (`tsc: command not found`). Nawet po instalacji kompilację blokują brakujące `frontend/src/App.tsx` oraz trzy importowane arkusze stylów.
- Katalog `frontend/` i jego plan/specyfikacja są nieśledzone przez Git, więc można je łatwo utracić lub pominąć przy przekazaniu projektu.

### Pokrycie wymagań `goal.md`

| Wymaganie | Stan | Dowód / luka |
|---|---|---|
| Jedna rozmowa z kontekstem | Częściowe | Backend zapisuje wymagania i wybrany produkt w sesji; brak działającego interfejsu React. |
| Jedna kategoria: słuchawki | Gotowe | Prompt, modele domenowe i testy są zawężone do słuchawek. |
| Wejście przez potrzebę lub produkt referencyjny | Gotowe | Oba wejścia przechodzą test API `test_both_entry_points_reach_three_ranked_offers`. |
| Identyfikacja produktu referencyjnego | Gotowe | `ReferenceProduct`, walidacja odpowiedzi LLM i testy rozmowy. |
| Automatyczne preferencje, maks. 3 pytania | Gotowe w backendzie | Limit jest w modelu i `ConversationService`; testowane jest zatrzymanie czwartego pytania. |
| 4–6 kandydatów z ceną i kompromisem | Gotowe w backendzie | Schemat i serwis wymagają 4–6; happy path zwraca cztery. UI nie renderuje ich jeszcze. |
| Wybór modelu lub kierunku | Gotowe w API | Endpoint wyboru obsługuje cztery kierunki rankingu. |
| Oferty z działającego źródła lub zestawu demo | Częściowe | Jest OLX/Firecrawl, cache i deterministyczny Deal Watch; brak kontrolowanego fallbacku głównego flow w interfejsie. |
| Kontrola dokładnego wariantu | Gotowe | `matches_exact_product` działa przed scoringiem; test odrzuca złą generację. |
| Osobna ocena produktu/oferty/sprzedawcy | Gotowe w backendzie | Trzy wartości trafiają do `score_breakdown`; brak ich prezentacji w UI. |
| Ryzyka, źródła, czas i nieznane pola | Gotowe w backendzie | API zwraca `source_url`, `retrieved_at`, `confidence`, `data_gaps`, `field_availability`. |
| Co najmniej 3 oferty i jedna rekomendacja | Gotowe w testowanym backendzie | Happy path zwraca trzy oferty i flagę `recommended`. |
| Zmiana priorytetu bez utraty kontekstu | Gotowe w backendzie | Follow-up wykonuje rerank cache bez ponownego pobierania. Brak sterowania w UI. |
| Stabilny scenariusz poniżej 3 minut | Niezweryfikowane end-to-end | Testy deterministyczne przechodzą, lecz nie ma działającego frontendu ani zmierzonego dry-runu live. |

### Decyzja zakresowa

Backend głównego flow jest wystarczająco kompletny na demo. W ostatnich dwóch godzinach największy zwrot daje **dokończenie pionowego przekroju frontendu i próba generalna**, nie rozbudowa Deal Watch, autoryzacji, historii lub scoringu.

---

## 2. Harmonogram T-120 → T-0

| Okno | Rezultat | Brama wyjścia |
|---|---|---|
| T-120–T-110 | Zabezpieczony punkt startowy i zależności frontendu | `npm test -- --run` uruchamia istniejące testy klienta. |
| T-110–T-80 | Działający stan aplikacji i polling | Hook przechodzi przez `idle → selecting → searching → results`; follow-up zachowuje sesję. |
| T-80–T-45 | Minimalny, czytelny interfejs całego flow | W przeglądarce można wysłać prompt, wybrać model i otworzyć ofertę. |
| T-45–T-30 | Stany awarii i jawny fallback demo | `partial`, `failed`, timeout i dane demo nie powodują pustego ekranu ani udawania danych live. |
| T-30–T-15 | Automatyczne bramy jakości | Build frontendu oraz testy backendu są zielone. |
| T-15–T-5 | Próba generalna z pomiarem czasu | Pełny scenariusz trwa <3 min i ma zapisane kroki prezentera. |
| T-5–T-0 | Bufor i zamrożenie | Tylko restart usług lub poprawa błędu blokującego; żadnych nowych funkcji. |

---

### Task 1: Zabezpieczyć fundament frontendu (T-120–T-110)

**Files:**
- Modify: `.gitignore`
- Verify: `frontend/package.json`
- Verify: `frontend/src/api/client.ts`
- Test: `frontend/src/api/client.test.ts`

**Interfaces:**
- Consumes: istniejące endpointy `/sessions`, `/sessions/{id}/messages`, `/sessions/{id}/products/{product_id}/select`, `/runs/{id}`.
- Produces: powtarzalne środowisko instalacji oraz zielony test transportu HTTP.

- [ ] **Step 1:** Dodać do `.gitignore` dokładnie:

```gitignore
frontend/node_modules/
frontend/dist/
frontend/coverage/
```

- [ ] **Step 2:** Zainstalować zależności w `frontend/` i zachować wygenerowany lockfile w repozytorium.

```bash
cd frontend
npm install
npm test -- --run
```

Expected: dwa testy `frontend/src/api/client.test.ts` przechodzą.

- [ ] **Step 3:** Sprawdzić, że proxy nadal usuwa prefiks `/api` przed przekazaniem żądania do `http://localhost:8000`.

```bash
cd frontend
npm run build
```

Expected at this point: błąd dotyczy wyłącznie brakującego UI (`App` lub style), nie klienta API ani konfiguracji TypeScript.

### Task 2: Dodać minimalną maszynę stanów i polling (T-110–T-80)

**Files:**
- Create: `frontend/src/state/useShoppingSession.ts`
- Create: `frontend/src/state/presentation.ts`
- Create: `frontend/src/state/demo.ts`
- Test: `frontend/src/state/presentation.test.ts`

**Interfaces:**
- Consumes: funkcje z `frontend/src/api/client.ts`.
- Produces: `useShoppingSession()` z polami `phase`, `messages`, `candidates`, `recommendations`, `error` oraz akcjami `submit`, `select`, `retry`, `useDemo`.

- [ ] **Step 1:** Zdefiniować fazy bez dodatkowych stanów produktu:

```ts
export type ShoppingPhase =
  | 'idle'
  | 'conversing'
  | 'selecting'
  | 'searching'
  | 'results'
  | 'error'
```

- [ ] **Step 2:** Przy pierwszym `submit` utworzyć sesję, a następnie wysłać wiadomość. Gdy odpowiedź ma `question`, pozostać w `conversing`; gdy ma kandydatów, przejść do `selecting`.

- [ ] **Step 3:** Po `select(candidate, direction)` zapisać wybrany produkt, wywołać `selectProduct`, a następnie odpytywać `getRun` co 1500 ms. Zatrzymać polling dla `completed`, `partial` i `failed` oraz po 45 sekundach.

- [ ] **Step 4:** Follow-up wysłany w fazie wyników ma użyć tego samego `sessionId`. Jeżeli backend zwróci `run_id`, polling uruchamia się ponownie bez czyszczenia wcześniejszych wiadomości.

- [ ] **Step 5:** W `presentation.ts` dodać deterministyczne formatowanie ceny, daty, statusu pola i trzech ocen. Nie przeliczać ani nie wymyślać wartości brakujących.

```ts
export const fieldLabel = (value: unknown) =>
  value === null || value === undefined || value === 'unknown'
    ? 'Brak danych'
    : String(value)
```

- [ ] **Step 6:** `demo.ts` ma zawierać cztery modele i trzy oferty odpowiadające strukturze typów API. Każda syntetyczna oferta ma `source: 'demo'`, URL w domenie `example.com`, stały czas oraz widoczne `data_gaps`; tryb włącza się wyłącznie przyciskiem „Uruchom dane demonstracyjne”.

- [ ] **Step 7:** Przetestować formatowanie PLN, `Brak danych`, rozpoznanie stanu terminalnego i limit czasu.

```bash
cd frontend
npm test -- --run
```

Expected: test klienta API i testy prezentacji przechodzą.

### Task 3: Zbudować jeden kompletny ekran demo (T-80–T-45)

**Files:**
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/styles/global.css`
- Create: `frontend/src/styles/components.css`
- Modify: `frontend/src/main.tsx`

**Interfaces:**
- Consumes: `useShoppingSession()`.
- Produces: dostępny klawiaturą flow od promptu do linku sprzedawcy.

- [ ] **Step 1:** W `App.tsx` wyrenderować jeden semantyczny układ: nagłówek Picky, historię rozmowy, composer, fazę wyboru produktu, stan wyszukiwania i ranking ofert. Nie tworzyć teraz osobnego systemu routingu ani biblioteki komponentów.

- [ ] **Step 2:** Composer ma zachować tekst po błędzie, blokować wielokrotne wysłanie w trakcie żądania i umożliwiać wysłanie klawiszem Enter. Załącznik obrazu pozostaje widoczny, ale `disabled` z tekstem „Zdjęcia dodamy po demo”.

- [ ] **Step 3:** Każda karta modelu pokazuje nazwę, cenę orientacyjną, `why_it_fits`, maksymalnie trzy cechy, różnice oraz `tradeoff`. Udostępnić cztery jawne kierunki wyboru zgodne z `SearchDirection`.

- [ ] **Step 4:** Ranking pokazuje na pierwszym ekranie co najmniej trzy oferty. Dla każdej wyrenderować:

```text
cena i źródło
dokładny wariant i stan
dopasowanie produktu / jakość oferty / sprzedawca
uzasadnienie
ryzyka i braki danych
czas pobrania
Zobacz ofertę
```

- [ ] **Step 5:** Link sprzedawcy otwiera się jako `target="_blank"` z `rel="noreferrer noopener"`. Nie renderować przycisku, jeśli URL nie istnieje.

- [ ] **Step 6:** Po wynikach utrzymać composer aktywny, aby wiadomość „ważniejsza jest gwarancja niż najniższa cena” uruchamiała rerank tej samej sesji.

- [ ] **Step 7:** W CSS użyć tokenów z `DESIGN.md`: białe płótno, `#101114` dla tekstu i `#1769FF` wyłącznie dla intencji/akcji. Zapewnić widoczny focus, cele dotykowe min. 44 px i jedną kolumnę poniżej 768 px.

```bash
cd frontend
npm run build
```

Expected: TypeScript i produkcyjny build Vite kończą się kodem 0.

### Task 4: Domknąć odporność demo (T-45–T-30)

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/state/useShoppingSession.ts`
- Modify: `frontend/src/styles/components.css`

**Interfaces:**
- Consumes: statusy `partial`, `failed` i `error_summary` z backendu.
- Produces: czytelny następny krok przy każdej awarii.

- [ ] **Step 1:** Dla `partial` pokazać dostępne rekomendacje i komunikat „Część źródeł jest chwilowo niedostępna”; nie ukrywać `error_summary`.
- [ ] **Step 2:** Dla `failed`, timeoutu i błędu sieciowego pozostawić prompt oraz pokazać dwie akcje: „Spróbuj ponownie” i „Uruchom dane demonstracyjne”.
- [ ] **Step 3:** Oznaczyć cały fallback stałym bannerem „Tryb demonstracyjny — dane przygotowane”, a każdą ofertę źródłem `demo`. Nie przełączać na fallback automatycznie.
- [ ] **Step 4:** Dodać `aria-live="polite"` dla stanu wyszukiwania i komunikatów błędu. Dla `prefers-reduced-motion: reduce` wyłączyć transformacje i animacje przejścia.
- [ ] **Step 5:** Nie integrować teraz osobnego interfejsu Deal Watch. Jego endpointy pozostają zapasowym, deterministycznym dowodem logiki landed cost i odrzucania pułapek podczas pytań technicznych jury.

### Task 5: Wykonać bramy jakości i próbę generalną (T-30–T-5)

**Files:**
- Modify: `README.md`
- Create: `docs/demo-script.md`

**Interfaces:**
- Produces: powtarzalne uruchomienie i scenariusz prezentera.

- [ ] **Step 1:** Uruchomić pełny zestaw automatycznych bram:

```bash
cd frontend
npm test -- --run
npm run build
cd ..
.venv/bin/ruff check app tests scripts
.venv/bin/pytest
```

Expected: frontend test/build przechodzą; backend ma 66 testów zaliczonych i 3 live pominięte.

- [ ] **Step 2:** Uruchomić backend i frontend w dwóch terminalach:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

- [ ] **Step 3:** W `docs/demo-script.md` zapisać dokładny scenariusz:

```text
1. „Chcę słuchawki podobne do AirPods Pro, z dobrym ANC, ale tańsze i niekoniecznie Apple.”
2. Wskaż „najlepszy stosunek ceny do jakości”.
3. Pokaż trzy oddzielne oceny, ryzyko, brak danych, źródło i czas przy rekomendowanej ofercie.
4. Otwórz link oferty w nowej karcie.
5. Napisz „ważniejsza jest gwarancja niż najniższa cena”.
6. Pokaż zmianę rankingu bez resetu rozmowy i bez ponownego pobrania źródła.
```

- [ ] **Step 4:** Zmierzyć cały scenariusz. Brama: mniej niż 3 minuty od wysłania pierwszej wiadomości do wyrenderowania rekomendacji; co najmniej trzy oferty; brak błędu w konsoli; link działa.
- [ ] **Step 5:** Powtórzyć scenariusz w trybie kontrolowanym. Brama: przełączenie wymaga jawnego kliknięcia, banner demo jest widoczny, a przebieg kończy się tym samym układem wyników.
- [ ] **Step 6:** Sprawdzić szerokość 375 px oraz obsługę samą klawiaturą: composer → wybór modelu → kierunek → oferta.
- [ ] **Step 7:** Uzupełnić `README.md` o dwa polecenia uruchomienia, adresy `8000`/`5173`, konfigurację proxy i jawny sposób uruchomienia fallbacku.

### Task 6: Zamrożenie przed prezentacją (T-5–T-0)

**Files:**
- No code changes unless the verified demo path is blocked.

- [ ] Zrestartować oba procesy i otworzyć czystą kartę przeglądarki.
- [ ] Pozostawić gotowy prompt demo w schowku.
- [ ] Potwierdzić `GET /health` oraz ekran startowy na `http://127.0.0.1:5173`.
- [ ] Nie uruchamiać migracji, nie zmieniać modeli LLM, promptów, scoringu, zależności ani konfiguracji Supabase/Firecrawl.

---

## 3. Kolejność cięć, jeśli czas się kurczy

1. Zachować: działający prompt → 4 modele → wybór → 3 oferty → trzy oceny → link → follow-up.
2. Zachować: czytelny błąd, ręczne ponowienie i jawny fallback demo.
3. Uprościć: animacje, talia kart, zdjęcia modeli, rozwijane szczegóły.
4. Odłożyć: historia i logowanie w nowym React UI, interfejs Deal Watch, porównanie dodatkowych modeli, rozbudowane testy wizualne.
5. Nie ciąć: źródeł/czasu, ryzyk, braków danych, dokładnego wariantu ani oddzielenia trzech ocen — to rdzeń obietnicy `goal.md`.

## 4. Definicja gotowości na deadline

Projekt jest gotowy wyłącznie wtedy, gdy w czystej sesji przeglądarki można bez ręcznego omijania błędów:

- przejść oba typy wejścia do 4–6 modeli;
- wybrać model i kierunek;
- zobaczyć minimum trzy oferty z linkiem, źródłem i czasem;
- zobaczyć rekomendację, kompromis, ryzyko, braki danych i trzy osobne oceny;
- zmienić priorytet w tej samej rozmowie;
- ukończyć przebieg w mniej niż 3 minuty;
- powtórzyć ten sam przebieg na jawnie oznaczonych danych demonstracyjnych po awarii usług live.
