# Shopping Agent Backend — Implementation Plan and Roadmap 3.1

> **Źródło prawdy:** `brainstorm.md`, decyzje produktowe w `goal.md` oraz uzgodnienia z 2026-07-11. Case „AI Shopping Assistant” rozszerza nasz agentowy przepływ o monitoring, alert, checkout i bezpieczną symulację zakupu, ale nie zmienia kategorii demonstracyjnej ani wejścia od potrzeby lub produktu referencyjnego.

**Goal:** Zbudować progresywnego agenta do używanych słuchawek. Pierwszy prompt od razu zwraca trzy propozycje produktów z orientacyjnymi cenami i wskazuje aktualnie najlepszą. Pogłębiony research pracuje w tle i aktualizuje wynik po potwierdzeniu lub korekcie cech. Po ustaleniu dokładnego produktu agent monitoruje oferty, wykrywa najlepszą zweryfikowaną okazję, tworzy jeden alert i checkout, a przy jawnie zatwierdzonym mandacie wykonuje bezpieczny symulowany zakup.

**Architecture:** Modularny monolit FastAPI używa jednego progresywnego `research_run` zamiast dwóch osobnych etapów wyszukiwania. Krótki research z realnego źródła zwraca Top 3 oraz `run_id`; `BackgroundTasks` pogłębia wynik. Potwierdzenie cech blokuje `ProductIdentity` i tworzy trwały `hunt`. Początkowy snapshot huntu pochodzi z realnego źródła, a kolejne zdarzenia demo są deterministyczne. Supabase przechowuje sesje, runy, briefy, produkty, obserwacje, mandaty, alerty, checkouty, symulowane zakupy i receipts.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, Supabase/PostgreSQL, pytest/pytest-asyncio, httpx, OpenAI structured output i Firecrawl. MVP nie wykonuje prawdziwych płatności ani realnego zakupu na marketplace.

## 1. Zamrożone decyzje produktowe

1. Pierwsza odpowiedź zawiera dokładnie trzy propozycje produktów, a aktualnie najlepsza jest pierwsza.
2. Propozycje mają orientacyjną cenę, kluczowe cechy, różnice, kompromis i poziom pewności.
3. Nie ma osobnego przejścia „lista kandydatów → pełny research”. Jeden run zwraca wynik progresywnie.
4. Krótka część researchu korzysta z realnego źródła i zwraca wynik możliwie szybko; pogłębiona analiza działa w tle.
5. Po pierwszej iteracji użytkownik potwierdza albo poprawia odczytane cechy. Akceptacja aktualnego lidera nie wymaga dodatkowego wyboru produktu.
6. Po ustaleniu dokładnego produktu automatycznie powstaje ciągły hunt ofert.
7. Początkowe oferty huntu są realne; kolejne zdarzenia w demo są deterministyczne.
8. Alert jest zapisywany jako JSON i pobierany przez polling interfejsu. Warstwa providerów ma umożliwiać późniejsze dodanie e-maila.
9. Najlepsza zweryfikowana oferta jest eskalowana do użytkownika, jeśli nie istnieje pasujący jawny mandat automatycznego zakupu.
10. Warunki auto-buy podaje użytkownik i zatwierdza osobno. LLM nie może wywnioskować zgody na wydanie pieniędzy.
11. Zakup i checkout są w MVP symulowane.
12. Mandat używa wcześniej zdefiniowanych priorytetów, twardych wymagań, dokładnego wariantu i maksymalnego kosztu końcowego.

## 2. Docelowy przepływ

### 2.1 — Prompt i szybki wynik

- Użytkownik opisuje potrzebę albo produkt referencyjny.
- Backend interpretuje wymagania i uruchamia `research_run`.
- W kontrolowanym budżecie czasu pobiera realne dane i zwraca Top 3 z liderem.
- Odpowiedź zawiera `run_id`, `research_status=deepening` i wersję wyniku.

### 2.2 — Pogłębienie w tle

- `BackgroundTasks` rozszerza research o dokładniejsze cechy, ceny, warianty, źródła i ryzyka.
- `GET /runs/{run_id}` zwraca najnowszą wersję Top 3.
- Nowy wynik zastępuje poprzedni tylko wtedy, gdy ma nowszą wersję i wystarczające dowody.

### 2.3 — Potwierdzenie cech

- Czat pokazuje odczytane cechy lidera i prosi o potwierdzenie lub korektę.
- Korekta aktualizuje wymagania i inteligentnie ponownie wykorzystuje dotychczasowe dane.
- Czysta zmiana priorytetu wykonuje rerank; brakujące dane uruchamiają refetch; zmiana produktu uruchamia nowy research.

### 2.4 — Zablokowanie produktu

- Po akceptacji powstaje kanoniczny `ProductIdentity`.
- Tożsamość obejmuje markę, model, generację i właściwe dla słuchawek cechy wariantu.
- `possible_match` nie może zostać automatycznie zablokowane jako dokładny produkt.

### 2.5 — Monitoring

- Backend tworzy hunt dla zablokowanego produktu i zapisuje priorytety użytkownika.
- Pierwszy snapshot ofert pochodzi z Firecrawl lub innego realnego adaptera.
- Kolejne ticki demo odtwarzają deterministyczne zmiany ceny, dostawy, stocku, kuponu i dostępności.
- Każdy tick ponownie wykonuje matching, landed cost, verification oraz ranking.

### 2.6 — Najlepsza oferta i eskalacja

- Oferta musi być exact match, mieścić się w hard capach i przejść weryfikację.
- Nowa najlepsza oferta tworzy jeden alert dla danej wersji briefu i okazji.
- Bez mandatu alert ma status `awaiting_user` i jest eskalacją do użytkownika.
- Z mandatem oferta przechodzi do symulowanego zakupu, jeżeli wszystkie warunki są jednoznacznie spełnione.

### 2.7 — Checkout, zakup i receipt

- Alert zawiera przygotowany `checkout_intent`.
- Użytkownik może zatwierdzić symulowany zakup jednym wywołaniem.
- Aktywny mandat pozwala wykonać ten sam zakup jako idempotentną funkcję w tle.
- Receipt zapisuje dane produktu, ofertę, koszt końcowy, sprzedawcę, warunki mandatu, dowody i powód decyzji.

## 3. Elementy istniejącego backendu do wykorzystania

### Gotowa baza

- FastAPI, konfiguracja, `/health` i format błędów;
- sesje, produkty, runy i statusy `pending`, `running`, `partial`, `completed`, `failed`;
- OpenAI structured output z walidacją Pydantic;
- protokoły repozytoriów i implementacje Supabase;
- `ListingSource`, Firecrawl, normalizacja ofert i idempotentny upsert;
- cache, twarde filtry, izolacja błędów i ranking;
- oddzielne oceny produktu, oferty i sprzedawcy;
- `BackgroundTasks` i polling runu.

### Kontrakty wymagające zmiany

- kandydaci 4–6 → dokładnie trzy progresywne propozycje;
- osobny endpoint wyboru produktu → potwierdzenie cech i automatyczne zablokowanie lidera;
- jednorazowy search run → research run z wersjonowanymi wynikami oraz późniejszy hunt;
- cena oferty → `LandedCostBreakdown`;
- proste dopasowanie wariantu → `exact_match`/`possible_match`/`mismatch` z dowodami;
- rekomendacja → alert, checkout intent, purchase simulation i receipt;
- brak zgody zakupowej → wersjonowany i odwoływalny `StandingMandate`.

## Faza 0 — Aktualizacja kontraktów i migracja ze starego przepływu

**Cel:** usunąć założenie dwóch osobnych etapów bez utraty działających komponentów.

**Planowane pliki:** `app/domain/models.py`, `app/llm/schemas.py`, `app/api/sessions.py`, `app/api/runs.py`, `docs/superpowers/specs/2026-07-11-shopping-agent-backend-design.md`.

- [ ] Zmienić kontrakt discovery na dokładnie trzy `ProductProposal`.
- [ ] Dodać `proposal_rank`, `is_current_best`, `estimated_price_range`, `result_version` i `research_status`.
- [ ] Dodać `InferredFeature` z wartością, pewnością i statusem potwierdzenia.
- [ ] Zastąpić obowiązkowy wybór produktu akcją `confirm_features`/`correct_features`.
- [ ] Pozostawić endpoint wyboru jako kompatybilność przejściową, ale nie używać go w nowym happy pathie.
- [ ] Dodać migrację sesji ze starego `PRODUCT_SELECTION` do progresywnego `RESEARCHING`/`CONFIRMING`.
- [ ] Zaktualizować testy kontraktowe API i specyfikację.

**Brama:** stary kod nie zwraca 4–6 kandydatów w nowym kontrakcie, a trzy propozycje mają stabilną kolejność i wersję.

## Faza 1 — Natychmiastowy Top 3 i pogłębiony research w tle

**Cel:** pierwszy prompt zwraca użyteczny wynik bez czekania na pełny research.

**Planowane pliki:** `app/product_research/progressive.py`, `app/orchestration/research.py`, `app/api/sessions.py`, `app/api/runs.py`, `tests/api/test_progressive_research.py`.

- [ ] Uruchomić krótki research realnego źródła w kontrolowanym budżecie czasu.
- [ ] Zwrócić trzy propozycje, aktualnego lidera i `run_id`.
- [ ] Jeśli realne źródło nie odpowie w budżecie, zwrócić jawnie oznaczony świeży cache zamiast fikcyjnej ceny.
- [ ] Kontynuować pogłębiony research przez `BackgroundTasks`.
- [ ] Wersjonować wyniki i aktualizować Top 3 atomowo.
- [ ] Zachować źródło, czas i pewność każdej ceny oraz cechy.
- [ ] Nie pogarszać potwierdzonego wyniku na podstawie słabszych dowodów.
- [ ] Dodać test, że pierwsza odpowiedź jest dostępna przed zakończeniem zadania w tle.
- [ ] Dodać test zmiany lidera po pojawieniu się lepszych danych.

**Brama:** API od razu zwraca Top 3, a polling później pokazuje doprecyzowaną wersję bez resetu sesji.

## Faza 2 — Potwierdzanie cech i inteligentna korekta

**Cel:** użytkownik sprawdza, czy agent zrozumiał produkt, zamiast ręcznie przechodzić do drugiego etapu.

**Planowane pliki:** `app/conversation/service.py`, `app/conversation/feature_confirmation.py`, `app/api/sessions.py`, `tests/api/test_feature_confirmation.py`.

- [ ] Po pierwszej iteracji zwrócić najważniejsze wywnioskowane cechy lidera do potwierdzenia.
- [ ] Pozwolić potwierdzić komplet cech jednym komunikatem.
- [ ] Pozwolić poprawić jedną lub kilka cech bez utraty researchu.
- [ ] Klasyfikować zmianę jako `rerank`, `refetch` albo `new_product_research`.
- [ ] Po korekcie aktualizować Top 3 i wskazanie lidera.
- [ ] Po akceptacji stworzyć kanoniczny `ProductIdentity` i automatycznie uruchomić hunt.
- [ ] Nie aktywować mandatu zakupowego na podstawie samego potwierdzenia cech.
- [ ] Dodać test: „gwarancja ważniejsza niż cena” zmienia lidera bez zbędnego refetchu.

**Brama:** zatwierdzenie cech tworzy hunt, a korekta zachowuje sesję, źródła i użyteczny cache.

## Faza 3 — Product identity, koszt końcowy i weryfikacja

**Cel:** monitoring działa wyłącznie na dokładnym produkcie i porównuje rzeczywisty znany koszt.

### 3A — Same-product matching

- [ ] Utworzyć kanoniczną tożsamość: marka, model, generacja, konstrukcja, kolor i inne cechy wariantu.
- [ ] Normalizować aliasy, skróty, kolejność słów i identyfikatory SKU/MPN/EAN.
- [ ] Klasyfikować oferty jako `exact_match`, `possible_match` albo `mismatch`.
- [ ] Zapisywać dowody i powody dopasowania.
- [ ] Blokować zakup i Top 3 ofert dla `possible_match` oraz `mismatch`.

### 3B — Landed cost

- [ ] Dodać breakdown: cena, dostawa, obowiązkowe opłaty, FX, cło/podatek, kupon, total i waluta.
- [ ] Nie traktować nieznanej opłaty jako zera bez `data_gap`.
- [ ] Sprawdzać budżet i mandat względem kosztu końcowego.
- [ ] Zapisywać kurs, timestamp, ważność kuponu i regułę zaokrąglenia.

### 3C — Verification

- [ ] Potwierdzać aktualność, stock, sprzedawcę, gwarancję, zwrot i kompletność danych.
- [ ] Wykrywać bait listing, pozorną promocję i krytyczną sprzeczność wariantu.
- [ ] Ponownie weryfikować ofertę bezpośrednio przed checkoutem i zakupem.
- [ ] Brak krytycznego dowodu kierować do eskalacji, nie do auto-buy.

**Brama:** błędny wariant i oferta przekraczająca hard cap po doliczeniu dostawy nie mogą wygrać ani zostać kupione.

## Faza 4 — Hunt i kontrolowany monitoring

**Cel:** po ustaleniu produktu backend stale ocenia nowe i zmienione oferty.

**Planowane pliki:** `app/hunts/service.py`, `app/hunts/orchestrator.py`, `app/simulation/offer_events.py`, `app/api/hunts.py`, `tests/hunts/test_monitoring.py`.

- [ ] Dodać stany huntu: `active`, `paused`, `alerted`, `awaiting_user`, `purchased`, `cancelled`.
- [ ] Zapisać `ProductIdentity`, priorytety, twarde wymagania i wersję briefu.
- [ ] Pobrać pierwszy snapshot ofert przez realny adapter.
- [ ] Zbudować deterministyczne eventy: price, delivery, stock, coupon, availability i seller signal.
- [ ] Dodać jawny endpoint `POST /hunts/{id}/ticks` dla demo.
- [ ] Po każdym ticku wykonać matching, landed cost, verification i ranking.
- [ ] Zapisywać checkpoint, aby retry nie przetwarzało eventu drugi raz.
- [ ] Pozwolić pause, resume i cancel.
- [ ] Zmiana priorytetów tworzy nową wersję briefu i ponownie ocenia istniejące obserwacje.

**Brama:** realny snapshot uruchamia hunt, a ten sam deterministyczny scenariusz zawsze prowadzi do tej samej najlepszej oferty.

## Faza 5 — Alert JSON, polling i eskalacja

**Cel:** interfejs otrzymuje jedno zdarzenie wymagające decyzji, a system jest gotowy na przyszły kanał e-mail.

**Planowane pliki:** `app/alerts/service.py`, `app/alerts/providers.py`, `app/api/alerts.py`, `tests/alerts/test_deduplication.py`.

- [ ] Dodać model `AlertEvent` z typem, hunt, ofertą, kosztem, reason codes i statusem.
- [ ] Deduplikować alert po hunt, brief version, offer i rodzaju okazji.
- [ ] Udostępnić `GET /hunts/{id}/alerts?after=<cursor>`.
- [ ] Zwracać cursor, `has_more` i timestamp do ciągłego pollingu.
- [ ] Oznaczać alert jako `awaiting_user`, `accepted`, `dismissed`, `expired` albo `auto_purchased`.
- [ ] Utworzyć protokół `NotificationProvider`; MVP implementuje `InAppJsonProvider`.
- [ ] Zaprojektować payload bez zależności od UI, aby później dodać `EmailProvider`.
- [ ] Traktować znalezienie najlepszej zweryfikowanej oferty bez mandatu jako eskalację.
- [ ] Unieważnić alert po zmianie ceny, stocku albo briefu.

**Brama:** jedna okazja daje jeden alert JSON, polling nie zwraca duplikatów, a payload można przekazać innemu providerowi.

## Faza 6 — Standing mandate, checkout i symulowany zakup

**Cel:** zakup może wykonać się w tle tylko na podstawie jawnej, ograniczonej zgody.

**Planowane pliki:** `app/mandates/models.py`, `app/mandates/policy.py`, `app/checkout/service.py`, `app/purchases/service.py`, `tests/mandates/test_purchase_policy.py`.

- [ ] Dodać wersjonowany `StandingMandate` z jawnym `confirmed_at` i możliwością odwołania.
- [ ] Zapisać exact product, wariant, maksymalny landed cost, wymagany stan i twarde priorytety.
- [ ] Użyć istniejących priorytetów produktu, oferty i sprzedawcy jako policy input.
- [ ] Rozdzielić preferencje rankingowe od twardych warunków zakupu.
- [ ] Nigdy nie tworzyć aktywnego mandatu wyłącznie z interpretacji LLM.
- [ ] Dodać `checkout_intent` do każdej zaakceptowanej najlepszej oferty.
- [ ] Bez mandatu wymagać `POST /checkout-intents/{id}/confirm`.
- [ ] Z aktywnym mandatem uruchomić idempotentny purchase job przez `BackgroundTasks`.
- [ ] Bezpośrednio przed zakupem ponownie sprawdzić ofertę, stock, koszt i mandat.
- [ ] Przypadek niejednoznaczny lub niespełniający mandatu eskalować do alertu `awaiting_user`.
- [ ] Zapisać symulowany wynik zakupu; nigdy nie obciążać prawdziwej metody płatności.

**Brama:** nie istnieje ścieżka zakupu bez jawnego mandatu lub ręcznego potwierdzenia; hard cap jest nieprzekraczalny.

## Faza 7 — Receipts i audyt

**Cel:** każda rekomendacja, eskalacja i symulowany zakup są odtwarzalne.

- [ ] Receipt zawiera snapshot briefu, wersję mandatu i exact-match evidence.
- [ ] Pokazać cenę, dostawę, opłaty, FX, kupon i landed total.
- [ ] Zapisać sprzedawcę, stock, gwarancję, zwrot i sygnały ryzyka.
- [ ] Zapisać odrzucone oferty i powody odrzucenia liderów pozornych.
- [ ] Zapisać decyzję `alert`, `escalate`, `manual_purchase` albo `auto_purchase`.
- [ ] Dodać endpoint `GET /receipts/{id}`.
- [ ] Dodać możliwość override'u użytkownika, tworzącą nową wersję briefu zamiast zmiany starego receiptu.

**Brama:** wynik policy engine da się odtworzyć wyłącznie z receiptu i wersjonowanych danych.

## Faza 8 — Eval set i bezpieczeństwo

**Cel:** pułapki nie prowadzą do alertu ani zakupu, a metryki są mierzalne.

- [ ] Przygotować exact match, wrong variant, bait listing, fake discount, expired coupon, missing delivery, no stock, seller risk i revoked mandate.
- [ ] Mierzyć precision Top 3, variant-error rate, bait-rejection rate i landed-cost accuracy.
- [ ] Mierzyć alert deduplication rate, escalation accuracy i false-buy rate.
- [ ] Ustalić gate `false_buy_rate = 0` dla deterministycznego scenariusza.
- [ ] Sprawdzić retry alertu, checkoutu i purchase jobu.
- [ ] Potwierdzić, że odwołanie mandatu przed jobem blokuje zakup.

**Brama:** zero false buys, zero złych wariantów w Top 3 i dokładnie jeden alert dla właściwej okazji.

## Faza 9 — Integracje i próba generalna

**Cel:** pokazać pełną ścieżkę od promptu do alertu oraz obu wariantów symulowanego zakupu.

- [ ] Uruchomić migracje Supabase dla wersji wyników, huntów, alertów, mandatów, checkoutów, zakupów i receiptów.
- [ ] Wykonać realny szybki research OpenAI + Firecrawl.
- [ ] Potwierdzić realne pola: cena, wariant, dostawa, stock, sprzedawca, gwarancja i zwrot.
- [ ] Braki oznaczać jako `unknown`; nie uzupełniać ich domysłem.
- [ ] Przejść ścieżkę: prompt → natychmiastowe Top 3 → deepening → potwierdzenie cech → hunt.
- [ ] Odtworzyć deterministyczny price event i otrzymać jeden alert JSON.
- [ ] Bez mandatu eskalować najlepszą ofertę i wykonać ręcznie potwierdzony symulowany zakup.
- [ ] W drugiej próbie aktywować mandat i wykonać purchase job w tle.
- [ ] Pokazać receipt i raport eval z `false_buy_rate = 0`.
- [ ] Zmierzyć czas pierwszej odpowiedzi, czas pogłębienia, polling, koszt API i czas całego demo.
- [ ] Zaktualizować `README.md`, komendy startowe i znane ograniczenia.

**Brama końcowa:** pierwsza odpowiedź daje Top 3 i lidera, wynik pogłębia się bez resetu, hunt generuje jeden alert, a oba warianty symulowanego zakupu przestrzegają hard capów.

## Minimalne endpointy v3.1

- `POST /sessions` — tworzy sesję.
- `POST /sessions/{id}/messages` — zwraca Top 3, lidera i `run_id`.
- `GET /runs/{run_id}` — zwraca wersjonowany progresywny wynik.
- `POST /sessions/{id}/features/confirm` — potwierdza cechy i tworzy hunt.
- `PATCH /sessions/{id}/features` — poprawia cechy i aktualizuje research.
- `GET /hunts/{id}` — zwraca stan huntu i najlepszą ofertę.
- `POST /hunts/{id}/ticks` — wykonuje deterministyczny cykl demo.
- `PATCH /hunts/{id}` — pause, resume lub cancel.
- `GET /hunts/{id}/alerts?after=<cursor>` — pollinguje nowe alerty JSON.
- `POST /hunts/{id}/mandates` — tworzy mandat po jawnym potwierdzeniu.
- `DELETE /hunts/{id}/mandates/{mandate_id}` — odwołuje mandat.
- `POST /checkout-intents/{id}/confirm` — potwierdza symulowany zakup ręczny.
- `GET /purchases/{id}` — zwraca status purchase jobu.
- `GET /receipts/{id}` — zwraca audyt decyzji i zakupu.

## Definition of Done v3.1

- [ ] Pierwszy prompt zwraca dokładnie trzy propozycje i aktualnego lidera.
- [ ] Każda propozycja ma orientacyjną cenę, źródło, czas i pewność.
- [ ] Pogłębiony research działa w tle pod tym samym `run_id`.
- [ ] Czat prosi o potwierdzenie lub korektę cech po pierwszej iteracji.
- [ ] Potwierdzenie dokładnego produktu automatycznie tworzy hunt.
- [ ] Pierwszy snapshot huntu pochodzi z realnego źródła.
- [ ] Deterministyczne zdarzenie może zmienić najlepszą ofertę.
- [ ] Exact match, landed cost i verification poprzedzają alert oraz zakup.
- [ ] Jedna okazja generuje dokładnie jeden alert JSON.
- [ ] Polling cursor nie zwraca duplikatów.
- [ ] Bez mandatu najlepsza oferta jest eskalowana do użytkownika.
- [ ] Mandat jest jawny, wersjonowany, odwoływalny i oparty na wcześniejszych priorytetach.
- [ ] Checkout oraz zakup są symulowane.
- [ ] Purchase job może działać w tle i ponownie sprawdza hard capy.
- [ ] Niepewność, zmiana ceny lub brak stocku blokują auto-buy.
- [ ] Każda decyzja ma receipt z pełną matematyką i dowodami.
- [ ] False-buy rate deterministycznego scenariusza wynosi zero.

## Świadomie poza zakresem

- prawdziwe obciążenie karty lub konta;
- integracja produkcyjnego PSP;
- rzeczywisty zakup na zewnętrznym marketplace;
- niezawodny scheduler produkcyjny i monitoring wszystkich sklepów 24/7;
- wysyłka e-mail — kontrakt jest gotowy, ale MVP używa JSON w interfejsie;
- wiele kategorii i własna kompletna baza produktów;
- perfekcyjne wykrywanie podróbek i oszustw.

## Najważniejsze ryzyka

- „Natychmiastowy” wynik z realnego źródła wymaga twardego budżetu czasu i jawnego fallbacku do cache.
- Aktualizacja lidera w tle może dezorientować UI; wynik musi być wersjonowany i wyjaśniać zmianę.
- Potwierdzenie cech nie może zostać pomylone ze zgodą na zakup.
- Mandat musi rozdzielać preferencje rankingowe od nieprzekraczalnych warunków zakupu.
- `BackgroundTasks` nie jest trwałą kolejką; wystarcza do demo, ale purchase job może zginąć po restarcie.
- Polling alertów wymaga cursorów i idempotencji, inaczej UI pokaże duplikaty.
- Realne źródło może nie udostępniać stocku, gwarancji albo pełnego kosztu; brak krytycznego pola blokuje auto-buy.
- Symulowany zakup musi być wyraźnie oznaczony, aby jury nie uznało go za prawdziwą transakcję.
