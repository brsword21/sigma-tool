# Plan fixów — uspójnienie kodu, goal.md i opisu core'a

> Audyt z 2026-07-11: porównanie opisu core'a działania produktu, `goal.md` oraz faktycznego kodu (stan: 21 testów przechodzi, Fazy 0–2 zamknięte, kod Fazy 3 w praktyce istnieje).

## Zdiagnozowane zjazdy

| # | Zjazd | Gdzie | Waga |
|---|-------|-------|------|
| Z1 | Pierwsza lista 4–6 kandydatów pochodzi wyłącznie z wiedzy LLM (gpt-4o-mini), bez wyszukiwania online; ceny `estimated_used_price_pln` to szacunki modelu | `app/conversation/service.py` | wysoka |
| Z2 | Brief produktowy jest generowany równolegle, ale jego treść nie zasila rankingu — `SearchOrchestrator.run` ignoruje `brief_result` poza błędami; ranking to generyczny keyword-match, nie „istotne dla tego urządzenia parametry" | `app/orchestration/search.py:65-81`, `app/ranking/engine.py` | wysoka |
| Z3 | Uzasadnienia pozycji w top 10 są generyczne (3 mocne strony ze scoringu), a nie „dlaczego jest na tej pozycji" względem parametrów urządzenia | `app/ranking/engine.py:88-98` | średnia |
| Z4 | Rozjazd liczbowy: opis core'a mówi „top 10 z uzasadnieniem", `goal.md` §6 mówi „3–5 wyników + rekomendacja jednej oferty", kod robi top 10 bez wyróżnionej rekomendacji | `goal.md` §6/§10, `app/orchestration/search.py:81` | średnia |
| Z5 | „Wiadomość leci do pamięci czatu" — sesja nadpisuje `message_summary` ostatnią wiadomością; nie ma historii rozmowy (kontekst trzyma się tylko przez `Requirements`) | `app/api/sessions.py:57-64` | niska |
| Z6 | Opis core'a: „porównanie specyfikacji technicznych" — kandydaci mają `key_features`/`differences`, ale bez wspólnej osi porównania spec-vs-spec | `app/llm/schemas.py` | niska |
| Z7 | Plan faz nieaktualny: checkboxy Fazy 3 puste mimo istniejących plików i przechodzących testów (`test_happy_path.py`, `test_partial_failure.py`, `test_reference_product.py`); plan wymienia `app/sources/olx.py` i `tests/fixtures/olx/`, których nie ma (decyzja Fazy 0: Firecrawl-only) | `docs/superpowers/plans/2026-07-11-shopping-agent-backend-phases.md` | dokumentacyjna |

## Co jest zgodne (nie ruszać)

- Pętla doprecyzowania: kolejny prompt aktualizuje wymagania bez resetu sesji, limit 3 pytań egzekwowany w kodzie.
- Dwa równoległe procesy po wyborze: `asyncio.gather(brief, scraping)` z izolacją wyjątków.
- Brief zawiera dokładnie to, co opis core'a: charakterystykę, `key_parameters`, `second_hand_checks`, `known_risks` + źródła.
- Cache 10/5, TTL 24 h ofert i 30 dni researchu, idempotentny upsert.
- Trzy składowe oceny (produkt/oferta/sprzedawca), `confidence` i `data_gaps` w wynikach.
- Link do ogłoszenia dostępny w rekomendacjach (`get_for_run` robi join `listings(*)`).

## P1 — fixy funkcjonalne (przed Fazą 4)

- [x] **F1 (Z2): brief zasila ranking.** `SearchOrchestrator.run` przekazuje wynik briefu do `rank_listings(listings, requirements, brief)`. `key_parameters` briefu stają się dodatkowymi terminami dopasowania w komponencie wymagań (blend `0.7*user + 0.3*brief_coverage`, cap 25 zachowany), `known_risks` zasilają uzasadnienie. Gdy brief padnie lub nie ma parametrów, ranking działa identycznie jak przed zmianą (degradacja, nie blokada). Weryfikacja: kolejność `generic → device-fit` odwraca się na `device-fit → generic` po podaniu briefu.
- [x] **F2 (Z3): uzasadnienie pozycji odnosi się do urządzenia.** `_build_explanation` w `engine.py` buduje `explanation` z 1–2 mocnych stron + „spełnia kluczowe dla tych słuchawek parametry: …" + „na co uważać: …" z briefu. Szablon deterministyczny, bez dodatkowego wywołania LLM. Gdy brak briefu → `explanation=None`, orchestrator używa dotychczasowego fallbacku.
- [x] **F3 (Z4): Top 5 + 1 wyróżniona + 15 dalszych.** `TOP_RESULTS=5`, `TOTAL_RESULTS=20`. Każda rekomendacja ma `tier` (`top`/`secondary`) i `recommended` (tylko rank 1). Decyzja produktowa: Top 5 z jedną wyróżnioną rekomendacją oraz do 15 słabszych propozycji.
- [ ] **F4 (Z1, wariant minimalny na MVP):** jawnie oznaczyć pochodzenie cen pierwszej listy — pole `price_basis: "llm_estimate"` w odpowiedzi `/messages` i komunikat, że pierwsza lista jest eksploracyjna (goal.md §5 tego wymaga). Nie udawać researchu online, którego nie ma.
- [ ] **F5 (Z5): historia rozmowy.** Zamienić nadpisywanie `message_summary` na dopisywanie do listy wiadomości w sesji (kolumna/JSON już w Supabase albo nowa kolumna `messages`). Tani fix, realizuje „wiadomość leci do pamięci czatu".

## P2 — uspójnienie dokumentów

- [x] **D1: goal.md §6** — zaktualizowane do: „Top 5 z jedną wyróżnioną rekomendacją + do 15 dalszych; uzasadnienie pozycji z parametrów briefu". §10.5 (min. 3 oferty) pozostaje spójne.
- [ ] **D2: plan faz** — odhaczyć faktycznie wykonane punkty Fazy 3, usunąć/oznaczyć jako nieaktualne odwołania do `app/sources/olx.py` i `tests/fixtures/olx/`, dopisać zamrożoną decyzję: „kandydaci Fazy 1 pochodzą z wiedzy LLM (MVP), grounding online przeniesiony do rezerwy/Fazy 6".
- [ ] **D3: opis core'a do repo** — wkleić opis core'a działania (prompt → porównanie → doprecyzowanie → 2 procesy → ranking top 10 → przejście do oferty) jako sekcję w `goal.md` albo osobny `docs/core-flow.md`, żeby przestał żyć tylko w głowie/wiadomościach.

## P3 — jeśli zostanie czas (nie blokuje demo)

- [ ] **F6 (Z1, wariant pełny):** tani grounding pierwszej listy — jedno wyszukiwanie Firecrawl per kandydat (albo tylko dla cen) z zapisem `source_url` i `retrieved_at`; dopiero to realizuje „wyszukiwanie produktów online" z opisu core'a.
- [ ] **F7 (Z6):** wspólna oś porównania specyfikacji — poprosić LLM o ten sam zestaw 4–5 cech dla wszystkich kandydatów (`spec_axes`), żeby frontend mógł pokazać tabelę porównawczą.

## Kolejność wykonania

1. F1 + F2 (jeden PR — orchestrator + engine + testy `test_engine.py`, `test_happy_path.py`),
2. F3 (mały PR — orchestrator + kontrakt odpowiedzi runu),
3. F4 + F5 (mały PR — API sesji),
4. D1–D3 (dokumenty, bez kodu),
5. F6/F7 tylko po zamknięciu bramy Fazy 4.
