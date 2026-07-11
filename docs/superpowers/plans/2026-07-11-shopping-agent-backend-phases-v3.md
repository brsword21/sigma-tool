# Shopping Agent Backend — Implementation Plan and Roadmap 3.0

> **Priorytet wymagań:** źródłem prawdy jest `brainstorm.md` oraz wynikający z niego agent do używanej elektroniki. Case „AI Shopping Assistant” jest materiałem uzupełniającym. Uwzględniamy z niego tylko elementy, których brakuje w naszym rozwiązaniu i które nie zmieniają wybranego produktu, kategorii ani głównego przepływu MVP.

**Goal:** Dostarczyć demonstracyjne MVP backendu agenta zakupowego dla używanych słuchawek. Agent przyjmuje potrzebę lub produkt referencyjny, pokazuje 4–6 podobnych modeli, pozwala użytkownikowi skorygować kierunek, a następnie porównuje konkretne oferty i oddzielnie ocenia produkt, ofertę oraz sprzedawcę.

**Architecture:** Modularny monolit FastAPI zapisuje sesję, wymagania, produkt referencyjny, kandydatów, oferty i rekomendacje w Supabase. OpenAI odpowiada za interpretację języka i ustrukturyzowany research. Kod deterministyczny kontroluje warianty, cache, normalizację, koszt końcowy, weryfikację ofert, ranking i audyt. Firecrawl pozostaje pierwszym źródłem realnych ofert, a kontrolowany zestaw danych zapewnia stabilność demo.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, Supabase/PostgreSQL, pytest/pytest-asyncio, httpx, OpenAI structured output oraz Firecrawl.

## 1. Hierarchia zakresu

### Rdzeń z brainstormu — bez zmian

- Jedna kategoria MVP: używane słuchawki.
- Dwa wejścia: opis potrzeby albo produkt referencyjny.
- Produkt referencyjny, np. AirPods Pro, jest skrótem preferencji, nie jedynym dozwolonym modelem.
- Tani research pokazuje 4–6 kandydatów z ceną, podobieństwami, różnicami i kompromisem.
- Użytkownik potwierdza lub poprawia kierunek przed pełnym pobraniem ofert.
- Pełne wyszukiwanie skupia się na wybranym modelu i zwraca co najmniej trzy oferty.
- Ranking rozdziela dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy.
- Braki danych, niepewność i źródła są jawne.
- Zmiana pojedynczej preferencji nie resetuje rozmowy ani wcześniejszego researchu.

### Brakujące elementy zaczerpnięte z case'u

- Porównywanie kosztu końcowego, a nie wyłącznie ceny ogłoszenia.
- Silniejsze rozpoznawanie tego samego produktu i dokładnego wariantu pomiędzy niejednolitymi tytułami.
- Weryfikacja aktualności, dostępności, sprzedawcy, bait listings i pozornych promocji.
- Deterministyczny zestaw ofert i zdarzeń do stabilnego testowania arytmetyki oraz decyzji.
- Audytowalne uzasadnienie: dane wejściowe, źródła, obliczenia, powody odrzucenia i wynik.
- Testy pułapek oraz mierzalna precyzja rekomendacji.
- Ograniczanie zbędnych powiadomień, jeśli po MVP dodamy monitoring okazji.

### Elementy case'u nieuwzględniane w MVP

- Zmiana kategorii demonstracyjnej na sneakersy.
- Skupienie całego produktu na jednym wcześniej znanym modelu.
- Automatyczny zakup i prawdziwe wydawanie pieniędzy.
- Standing mandate, delegowana płatność i integracja PSP.
- Ciągły monitoring wszystkich sklepów jako warunek ukończenia hackathonu.
- Produkcyjny system transgranicznych ceł i podatków dla wielu jurysdykcji.

Te elementy mogą pojawić się w roadmapie, ale nie mogą opóźnić podstawowego przepływu z brainstormu.

## 2. Status obecnej implementacji

- Fazy bazowe, modele domenowe, repozytoria, źródło, normalizacja, ranking i API powstały w commitach wcześniejszych faz.
- Oba punkty wejścia dochodzą na mockach do 4–6 kandydatów i minimum trzech ofert.
- Działa wybór `most_similar`, `best_quality`, `lowest_price` i `best_value`.
- API pokazuje osobno `product_match_score`, `offer_quality_score` oraz `seller_trust_score`.
- Brakuje pełnego rerankingu po zmianie naturalnojęzykowej preferencji na etapie wyników.
- Cena jest obecnie głównie ceną oferty; brakuje pełnego, audytowalnego kosztu końcowego.
- Dokładny wariant jest filtrowany, ale matching wymaga wzmocnienia dla niejednolitych tytułów i brakujących identyfikatorów.
- Brakuje osobnego testowego zestawu bait listings, fake discounts, błędnych wariantów i nieaktualnych ofert.

## 3. Globalne ograniczenia MVP 3.0

- Kategoria: używane słuchawki.
- Referencyjny scenariusz: „coś jak AirPods Pro, ale taniej, z dobrym ANC”.
- Najwyżej trzy pytania doprecyzowujące w sesji.
- Pierwsza lista: 4–6 modeli; nie jest finalnym rankingiem ofert.
- Pełne pobieranie ofert rozpoczyna się dopiero po wyborze kierunku lub modelu.
- Minimum trzy konkretne oferty właściwego wariantu.
- Koszt końcowy obejmuje cenę, dostawę i znane obowiązkowe opłaty. FX, cło i kupony są uwzględniane tylko wtedy, gdy dotyczą źródła i dane są dostępne.
- Nieznanej opłaty nie wolno przyjąć jako zero bez jawnego oznaczenia niepewności.
- Automatyczny zakup, płatności i standing mandate pozostają poza MVP.
- LLM nie decyduje o twardych filtrach, cache, arytmetyce kosztu ani końcowym wyniku punktowym.
- Kontrolowane dane demo są dozwolone i muszą być jawnie odróżnione od ofert pobranych na żywo.

## 4. Główny przepływ użytkownika

### 4.1 — Przyjęcie zapytania

Użytkownik podaje potrzebę albo produkt referencyjny, np. „Chcę słuchawki podobne do AirPods Pro, ale tańsze i z dobrym ANC”.

### 4.2 — Rozpoznanie intencji

Agent rozpoznaje kategorię, budżet, produkt referencyjny, wymagane cechy i prawdopodobne preferencje.

### 4.3 — Minimalne doprecyzowanie

Agent zadaje jedno pytanie tylko wtedy, gdy odpowiedź realnie zmieni listę kandydatów. W całej sesji może zadać najwyżej trzy pytania.

### 4.4 — Tani research kandydatów

Agent analizuje maksymalnie około 10 modeli i wybiera 4–6 sensownych alternatyw. Nie pobiera jeszcze pełnego zestawu ogłoszeń.

### 4.5 — Prezentacja modeli

Każdy kandydat ma orientacyjną cenę, podobieństwa, różnice, uzasadnienie i główny kompromis. Lista jest oznaczona jako etap eksploracji.

### 4.6 — Potwierdzenie lub korekta kierunku

Użytkownik wybiera model albo kierunek: najbardziej podobny, najlepsza jakość, najniższa cena lub najlepszy stosunek ceny do jakości. Może też poprawić wymagania bez resetu sesji.

### 4.7 — Pobranie konkretnych ofert

Backend sprawdza cache, a następnie pobiera oferty wybranego modelu, jeśli dane są niewystarczające lub nieaktualne.

### 4.8 — Exact-product i exact-variant matching

Oferty są normalizowane i klasyfikowane jako `exact_match`, `possible_match` albo `mismatch`. Tylko `exact_match` może trafić do finalnego rankingu; `possible_match` jest jawnie pokazane jako wymagające weryfikacji.

### 4.9 — Obliczenie kosztu końcowego

Backend liczy cenę wraz z dostawą i dostępnymi obowiązkowymi opłatami. Jeśli występują FX, cło lub kupon, zapisuje pełne składowe, kurs, ważność i czas obliczenia.

### 4.10 — Weryfikacja oferty

Backend sprawdza aktualność, dostępność, wariant, sprzedawcę, kompletność opisu, warunki zwrotu i gwarancji oraz dostępne sygnały bait listing lub pozornej promocji.

### 4.11 — Ranking i rekomendacja

Oferty są oceniane osobno przez dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy. Użytkownik otrzymuje minimum trzy wyniki, jedną rekomendację, koszt końcowy, ryzyka, braki danych i źródła.

### 4.12 — Zmiana preferencji

Kolejna wiadomość jest klasyfikowana jako `rerank`, `refetch` albo `new_product_research`. Backend wykorzystuje wcześniejsze dane, jeśli są wystarczające, i nie resetuje sesji.

## Faza 0 — Zamrożone decyzje bazowe ✅

- [x] OpenAI `gpt-4o-mini` i oficjalne SDK.
- [x] Supabase jako trwała pamięć backendu.
- [x] Firecrawl jako pierwsze źródło realnych ofert.
- [x] FastAPI, `BackgroundTasks` i polling `run_id` dla dłuższego wyszukiwania.
- [x] Używane słuchawki jako jedna kategoria MVP.
- [x] Dwa punkty wejścia oraz dwuetapowy research.
- [x] Trzy osobne oceny: produkt, oferta i sprzedawca.

## Faza 1 — Istniejący fundament techniczny ✅

- [x] Konfiguracja i fabryka FastAPI.
- [x] Modele Pydantic i protokoły repozytoriów.
- [x] Sesje, produkty, research, oferty, runy i rekomendacje.
- [x] Adapter `ListingSource` oraz Firecrawl.
- [x] Normalizacja ofert i idempotentny zapis `(source, external_id)`.
- [x] Cache, twarde filtry i ranking deterministyczny.
- [x] Obsługa częściowego wyniku po błędzie źródła.
- [x] Mockowe testy dwóch wejść i minimum trzech ofert.

## Faza 2 — Domknięcie przepływu brainstormu

**Cel:** zakończyć pełny przepływ 4.1–4.12 przed dokładaniem usprawnień z case'u.

**Planowane pliki:** `app/conversation/service.py`, `app/orchestration/search.py`, `app/api/sessions.py`, `app/api/runs.py`, `tests/api/test_rerank_after_preference_change.py`.

- [ ] Obsłużyć wiadomość użytkownika na etapie `results`.
- [ ] Zamienić zmianę preferencji, np. „ważniejsza jest gwarancja”, na jawne wymagania domenowe.
- [ ] Dla `rerank` wykorzystać istniejące świeże oferty bez ponownego wywołania źródła.
- [ ] Dla nowego twardego filtra wykonać `refetch` tylko wtedy, gdy cache nie wystarcza.
- [ ] Zachować `session_id`, wybrany produkt, research i historię zmian.
- [ ] Wyjaśnić użytkownikowi, dlaczego kolejność ofert się zmieniła.
- [ ] Dodać test end-to-end sprawdzający liczbę wywołań źródła i zmianę rankingu.

**Brama:** zmiana miękkiej preferencji zmienia ranking bez resetu sesji i bez zbędnego pobierania ofert.

## Faza 3 — Exact-product matching i koszt końcowy

**Cel:** dodać dwa najważniejsze brakujące elementy z case'u bez zmiany głównego UX.

### 3A — Wzmocnione dopasowanie produktu

**Planowane pliki:** `app/matching/product_identity.py`, `app/listings/normalizer.py`, `app/domain/models.py`, `tests/matching/test_product_identity.py`.

- [ ] Utworzyć kanoniczną tożsamość produktu: marka, model, generacja, typ, kolor i inne cechy wariantu właściwe dla słuchawek.
- [ ] Znormalizować aliasy, interpunkcję, skróty i kolejność wyrazów w tytułach.
- [ ] Używać SKU/MPN/EAN jako silnego dowodu, jeśli jest dostępny.
- [ ] Klasyfikować dopasowanie jako `exact_match`, `possible_match` albo `mismatch`.
- [ ] Nie dopuszczać `possible_match` do automatycznego finalnego rankingu.
- [ ] Zapisać powody i dowody dopasowania.
- [ ] Dodać testy złej generacji, wersji, zestawu, koloru, podobnego modelu i brakującego identyfikatora.

### 3B — Audytowalny koszt końcowy

**Planowane pliki:** `app/pricing/landed_cost.py`, `app/domain/models.py`, `app/ranking/engine.py`, `tests/pricing/test_landed_cost.py`.

- [ ] Dodać `LandedCostBreakdown`: cena, dostawa, obowiązkowe opłaty, FX, cło/podatek, kupon, total i waluta.
- [ ] Dla krajowych ofert w PLN liczyć co najmniej cenę i dostawę.
- [ ] Dla ofert zagranicznych zapisywać kurs, timestamp i regułę zaokrąglenia.
- [ ] Sprawdzać ważność i zakres kuponu przed odjęciem rabatu.
- [ ] Nie traktować nieznanej dostawy lub opłaty jako zera bez dodania `data_gap`.
- [ ] Filtrować budżet po koszcie końcowym, a nie wyłącznie po cenie ogłoszenia.
- [ ] Pokazywać breakdown w API i uzasadnieniu rekomendacji.
- [ ] Dodać testy dokładnie na budżecie, o 0.01 powyżej oraz z nieważnym kuponem.

**Brama:** błędny wariant nie trafia do rankingu, a oferta z niższą ceną bazową może przegrać przez wyższy koszt końcowy.

## Faza 4 — Weryfikacja ofert i kontrolowany zestaw pułapek

**Cel:** nie rekomendować nieaktualnych, zwodniczych ani nieweryfikowalnych ofert.

### 4A — Weryfikacja przed rankingiem

**Planowane pliki:** `app/verification/offers.py`, `app/ranking/risk.py`, `tests/verification/test_offers.py`.

- [ ] Potwierdzić aktualność, dostępność i dokładny wariant oferty.
- [ ] Ocenić kompletność opisu, zdjęć, gwarancji, zwrotu i danych sprzedawcy.
- [ ] Rozróżnić brak danych od negatywnego sygnału.
- [ ] Wykrywać bait listing, gdy atrakcyjna cena dotyczy innego wariantu lub niedostępnego produktu.
- [ ] Nie ufać deklarowanej „starej cenie” bez danych historycznych.
- [ ] Oznaczać promocję jako `verified`, `unverified` albo `suspicious`.
- [ ] Odrzucać ofertę z krytyczną niezgodnością; niekrytyczny brak obniża `confidence`.

### 4B — Deterministyczne dane demo

**Planowane pliki:** `tests/fixtures/deal_validation/`, `app/simulation/offer_events.py`, `tests/simulation/test_offer_events.py`.

- [ ] Przygotować kontrolowane oferty: dobra okazja, zły wariant, bait listing, fake discount, nieaktualna oferta, niewiarygodny sprzedawca i brak kosztu dostawy.
- [ ] Dodać zdarzenia zmiany ceny, dostępności, dostawy i ważności kuponu.
- [ ] Użyć wstrzykiwanego zegara i deterministycznej kolejności zdarzeń.
- [ ] Zapewnić ten sam wynik dla tego samego zestawu danych i preferencji.
- [ ] Jawnie oznaczyć w API, czy wynik pochodzi z danych kontrolowanych, cache czy realnego źródła.

**Brama:** pułapki nie trafiają do Top 3, a dobra oferta zachowuje stabilne uzasadnienie i koszt końcowy.

## Faza 5 — Audyt rekomendacji i mierzalna jakość

**Cel:** każda rekomendacja ma wystarczające dowody, a jakość można zmierzyć przed demo.

**Planowane pliki:** `app/recommendations/audit.py`, `app/evals/runner.py`, `tests/evals/shopping_agent_cases.json`, `tests/evals/test_metrics.py`.

- [ ] Zapisać snapshot wymagań i wersję preferencji użytych do rankingu.
- [ ] Zapisać exact-match evidence, koszt końcowy i źródła pól.
- [ ] Zapisać powody odrzucenia ofert niespełniających twardych warunków.
- [ ] Pokazać maksymalnie trzy zalety, jeden kompromis, ryzyka i `data_gaps`.
- [ ] Zbudować eval set zawierający dobre oferty oraz pułapki z fazy 4.
- [ ] Mierzyć precision Top 3, odsetek błędnych wariantów, bait-rejection rate i dokładność kosztu końcowego.
- [ ] Ustalić twardy gate: zero niewłaściwych wariantów w finalnym rankingu kontrolowanego zestawu.
- [ ] Raportować osobno przypadki, w których system nie miał wystarczających danych.

**Brama:** raport eval potwierdza brak błędnych wariantów i zaakceptowaną precyzję rekomendacji.

## Faza 6 — Integracje na żywo

**Cel:** potwierdzić, że istniejące integracje dostarczają dane wymagane przez rozszerzony model.

### 6A — Supabase

- [ ] Dodać migrację dla identity evidence, landed cost, verification i audytu.
- [ ] Uruchomić migracje w projekcie developerskim.
- [ ] Potwierdzić idempotencję ofert oraz historię cen i dostępności.
- [ ] Wykonać smoke test pełnej sesji i ponownego rankingu.

### 6B — OpenAI

- [ ] Wykonać realne structured output dla obu punktów wejścia.
- [ ] Potwierdzić limit trzech pytań i pojedynczą próbę naprawczą.
- [ ] Nie pozwolić modelowi tworzyć źródeł, kosztów ani wyników punktowych.
- [ ] Zmierzyć tokeny, koszt i opóźnienie sesji.

### 6C — Firecrawl

- [ ] Potwierdzić realną dostępność wariantu, dostawy, sprzedawcy, gwarancji, zwrotu i aktualności.
- [ ] Niedostępne pola oznaczać jako `unknown`, nie uzupełniać ich domysłem.
- [ ] Zweryfikować timeout, limity, regulamin i dozwolone domeny.
- [ ] Zachować użyteczny cache po awarii źródła.

**Brama:** pełna sesja na żywo zwraca minimum trzy oferty albo jawny częściowy wynik bez zmyślonych danych.

## Faza 7 — Próba generalna demo

**Cel:** pokazać pełny przepływ brainstormu wraz z najważniejszymi usprawnieniami z case'u w czasie krótszym niż trzy minuty.

- [ ] Zamrozić dokładny wariant AirPods Pro używany jako wzorzec.
- [ ] Zamrozić budżet i oczekiwane cechy scenariusza.
- [ ] Przejść: prompt → 4–6 modeli → korekta kierunku → minimum trzy oferty.
- [ ] Pokazać ofertę z atrakcyjną ceną bazową, która przegrywa przez dostawę lub inną obowiązkową opłatę.
- [ ] Pokazać odrzucenie błędnego wariantu albo bait listing.
- [ ] Pokazać trzy osobne oceny, koszt końcowy, źródła, ryzyko i braki danych.
- [ ] Zmienić preferencję i wykonać rerank bez utraty kontekstu.
- [ ] Przećwiczyć awarię źródła oraz wynik `partial` z cache.
- [ ] Wykonać dwie pełne próby i zapisać czas, koszt oraz raport eval.
- [ ] Zaktualizować `README.md` i znane ograniczenia.

**Brama końcowa MVP:** oba punkty wejścia działają, cena pojawia się od pierwszej listy, koszt końcowy i wariant są poprawne, Top 3 nie zawiera pułapek, a zmiana preferencji nie resetuje sesji.

## Definition of Done MVP 3.0

- [ ] Obsługiwane są potrzeba użytkownika i produkt referencyjny.
- [ ] Agent zadaje maksymalnie trzy istotne pytania.
- [ ] Pierwsza lista zawiera 4–6 modeli, ceny, różnice i kompromisy.
- [ ] Użytkownik może potwierdzić lub poprawić kierunek przed pełnym wyszukiwaniem.
- [ ] Pełne wyszukiwanie zwraca minimum trzy oferty wybranego modelu.
- [ ] Finalny ranking zawiera wyłącznie potwierdzone warianty.
- [ ] Budżet jest sprawdzany względem znanego kosztu końcowego.
- [ ] Bait listing, podejrzana promocja i nieaktualna oferta są odrzucane lub jawnie oznaczone.
- [ ] Produkt, oferta i sprzedawca mają osobne oceny.
- [ ] Każda rekomendacja zawiera źródła, czas, koszt końcowy, ryzyko i braki danych.
- [ ] Zmiana miękkiej preferencji wykonuje rerank bez resetu i bez zbędnego refetchu.
- [ ] Kontrolowany eval set nie przepuszcza niewłaściwego wariantu do Top 3.
- [ ] Pełna sesja działa na danych kontrolowanych i co najmniej raz na realnych integracjach.
- [ ] Automatyczny zakup i płatności nie są częścią MVP.

## Roadmapa po MVP

### Etap A — Monitoring okazji

- cykliczne odświeżanie zapisanych wyszukiwań;
- historia ceny i wykrywanie rzeczywistych spadków;
- jeden istotny alert zamiast powtarzalnych powiadomień;
- deduplikacja alertów oraz preferencje częstotliwości;
- trwały scheduler zamiast `BackgroundTasks`.

### Etap B — Wiele źródeł i dane transgraniczne

- drugi marketplace lub oficjalne API;
- pełne FX, cło, podatki i kupony dla wspieranych jurysdykcji;
- deduplikacja tej samej oferty pomiędzy źródłami;
- wspólny model sprzedawcy, gwarancji i zwrotów.

### Etap C — Agentic checkout, dopiero po osobnej decyzji produktowej

- checkout intent wymagający potwierdzenia użytkownika;
- jawny, ograniczony i odwoływalny standing mandate;
- hard caps egzekwowane w kodzie;
- eskalowanie przypadków granicznych;
- receipts z pełną matematyką i dowodami;
- shadow mode, threat model, autoryzacja i integracja PSP przed realnym zakupem;
- false-buy rate jako twarda metryka bezpieczeństwa.

### Etap D — Rozszerzenie produktu

- kolejne kategorie elektroniki z własnymi wariantami i kryteriami ryzyka;
- podobieństwo wizualne;
- długoterminowa pamięć preferencji za zgodą;
- personalizacja wag i uczenie rankingu na zachowaniu użytkownika.

## Macierz: elementy case'u w naszym rozwiązaniu

- Same-product problem → faza 3A, jako wzmocnienie kontroli wariantu.
- Landed cost zamiast sticker price → faza 3B.
- Bait listings i fake discounts → faza 4A.
- Mock merchants / deterministic simulator → faza 4B jako stabilne dane demo.
- Receipts + why → faza 5 jako audyt rekomendacji, bez zakupu.
- Proving it works → faza 5 i kontrolowane metryki jakości.
- One alert that matters → roadmapa Etap A.
- Standing consent, hard caps i auto-buy → roadmapa Etap C.
- Strike precision i false-buy rate → po MVP dla monitoringu i agentic checkout; w MVP używamy precision Top 3 i variant-error rate.

## Aktualne ryzyka

- Rozszerzenia z case'u mogą rozmyć główny scenariusz; faza 2 brainstormu ma pierwszeństwo przed fazami 3–5.
- Koszt końcowy może być niepełny, jeśli źródło nie podaje dostawy lub opłat; brak musi obniżać pewność.
- Same-product matching bez identyfikatora może pozostać niejednoznaczny; taki wynik nie powinien wejść do Top 3.
- Historia ceny może być zbyt krótka do potwierdzenia promocji; wtedy promocję oznaczamy jako niezweryfikowaną.
- Firecrawl może nie dostarczać wszystkich sygnałów sprzedawcy, gwarancji i zwrotu.
- Live scraping nie może blokować demo; kontrolowane dane pozostają planem stabilnym.
- `BackgroundTasks` wystarcza do jednorazowego runu, ale nie do przyszłego monitoringu okazji.
