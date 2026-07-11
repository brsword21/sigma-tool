# Picky Shopping Agent

Backend demonstracyjnego agenta zakupowego dla używanych słuchawek. Przyjmuje potrzebę
albo produkt referencyjny, proponuje 4–6 kierunków, a po wyborze pobiera oferty i osobno
pokazuje dopasowanie produktu, jakość oferty oraz wiarygodność sprzedawcy.

Repozytorium zawiera również frontend React w katalogu `frontend`. Zachowuje on
konwersacyjny charakter Picky, pokazuje kandydatów jako talię decyzji i podłącza pełny
przepływ backendu aż do rankingu konkretnych ofert.

## Uruchomienie

Wymagany jest Python 3.12 oraz lokalny plik `.env` utworzony na podstawie `.env.example`.
Wartości przykładowe zawierające `...` albo `<project-ref>` są celowo odrzucane jako
niegotowa konfiguracja.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check jest dostępny pod `GET http://localhost:8000/health`. Domyślne originy CORS
to `http://localhost:3000` i `http://localhost:5173`.

W drugim terminalu uruchom frontend:

```bash
cd frontend
npm install
cp .env.example .env.local  # jeśli masz lokalny plik przykładowy
npm run dev
```

Aplikacja będzie dostępna pod `http://localhost:5173`. Vite przekazuje żądania `/api`
do backendu na porcie 8000, dlatego frontend nie wymaga osobnego adresu API w kodzie.
Przycisk dodawania zdjęcia jest na razie celowo nieaktywny. Gdy usługi zewnętrzne nie
są dostępne, ekran błędu pozwala jawnie uruchomić oznaczony scenariusz demonstracyjny.

## Baza danych

Przed pierwszym uruchomieniem zastosuj kolejno:

- `supabase/migrations/001_initial_schema.sql`
- `supabase/migrations/002_demo_hardening.sql`
- `supabase/migrations/003_auth_chat_history.sql`
- `supabase/migrations/004_ceneo_new_price_benchmark.sql`

Można wkleić je do SQL Editora developerskiego projektu Supabase albo, dla połączonego
lokalnego projektu Supabase CLI, wykonać `supabase db push`.

## Logowanie Magic Link i historia rozmów

Frontend React obsługuje logowanie magic linkiem przez Supabase Auth. Gość może nadal
używać aplikacji bez konta, ale tylko rozmowy rozpoczęte po zalogowaniu są przypisywane
do użytkownika i dostępne w historii. Rozmowa gościa nie jest przenoszona do konta po
zalogowaniu.

Utwórz `frontend/.env.local` z publicznymi wartościami projektu:

```bash
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
```

W Supabase Dashboard otwórz **Authentication → URL Configuration**, ustaw adres strony
produkcyjnej jako Site URL i dodaj `http://localhost:5173` oraz produkcyjny adres do
Redirect URLs. Magic link nie wróci pod adres, którego nie ma na tej liście.

Backend weryfikuje access token po stronie Supabase i wymaga zastosowania migracji `003`.
Klucz `SUPABASE_SERVICE_ROLE_KEY` pozostaje wyłącznie w `.env` backendu. Przeglądarka używa
osobnego publicznego klucza publishable/anon. Zastosuj migrację
`supabase/migrations/003_auth_chat_history.sql` przed testowaniem historii.

## Testy

```bash
.venv/bin/ruff check app tests scripts
.venv/bin/pytest
```

Testy prawdziwych usług są jawnie opt-in, ponieważ zużywają limity OpenAI i Firecrawl
oraz łączą się z developerskim Supabase:

```bash
RUN_LIVE_TESTS=1 .venv/bin/pytest tests/live/test_phase4_services.py -v -s
.venv/bin/python scripts/phase4_smoke.py
```

Skrypt smoke nie wypisuje kluczy ani pełnych payloadów. Zwraca wyłącznie liczby wyników,
statusy, czas i kontrolowane opisy błędów.

## Faza 5: Deal Watch

Deal Watch działa lokalnie również bez skonfigurowanych usług zewnętrznych. Przyjmuje
mandat `alert_only`, oblicza pełny koszt oferty i zapisuje decyzję `ignore`, `hold` albo
`alert` wraz z rachunkiem oraz powodami.

Utworzenie przykładowego mandatu:

```bash
curl -X POST http://localhost:8000/deal-watch/mandates \
  -H 'content-type: application/json' \
  -d '{
    "product_model": "Apple AirPods Pro",
    "exact_variant": "AirPods Pro 2 USB-C",
    "max_landed_cost": "500.00",
    "currency": "PLN",
    "min_condition": "good",
    "min_seller_rating": "4.5",
    "mode": "alert_only"
  }'
```

Identyfikator `id` z odpowiedzi można przekazać do kontrolowanego scenariusza:

```bash
curl -X POST http://localhost:8000/deal-watch/mandates/<mandate-id>/simulate
curl http://localhost:8000/deal-watch/mandates/<mandate-id>/decisions
```

Symulator zawiera sześć zdarzeń: prawdziwą okazję, zły wariant, pułapkę kosztu
dostawy, brak dostępności, brak oceny sprzedawcy i fałszywą obniżkę. Oczekiwany wynik
to jeden `alert`, jeden `hold` i cztery `ignore`. Można też przekazać 1–10 własnych
zdarzeń do `POST /deal-watch/mandates/<mandate-id>/events`.
Ponowne przesłanie tego samego `event_id` zwraca istniejącą decyzję i nie tworzy
drugiego alertu.

Mandaty i historia są przechowywane wyłącznie w pamięci procesu. Restart je usuwa.
Faza 5 nie wykonuje checkoutu, zakupu ani płatności i nie jest produkcyjnym schedulerem.

## Dane i ograniczenia demo

- Firecrawl obsługuje oferty OLX oraz osobny benchmark najniższej ceny nowego produktu
  na Ceneo; każde wywołanie ma timeout 20 sekund.
- Benchmark Ceneo zawiera dokładnie jedną stronę produktu i nie uczestniczy w rankingu
  ofert używanych. Jest dostępny jako `new_price_benchmark` w `GET /runs/{run_id}`.
- Pełne pobieranie ofert rusza dopiero po wyborze produktu; późniejsza miękka zmiana
  preferencji wykonuje rerank cache bez ponownego pobierania.
- Model i generacja są filtrem twardym przed scoringiem.
- Cache starszy niż 24 godziny może uratować wynik po awarii źródła, ale jest oznaczony
  przez `is_stale=true`, `stale_cache` i pewność nie większą niż `0.4`.
- Opinie sprzedawcy, gwarancja, zwrot, oryginalność i bateria są pokazywane jako
  `unknown`, jeśli payload źródła ich nie zawiera. System ich nie domyśla.
- Research bez dostarczonego źródła ma `unverified_product_research`, pustą listę źródeł
  i obniżoną pewność.
- Błąd OLX albo Ceneo nie powoduje błędu 500 runu: dostępne wyniki drugiego źródła lub
  cache dają status `partial`, a brak ofert używanych kontrolowany status `failed`.
- BackgroundTasks wystarcza do lokalnego demo, ale nie zapewnia trwałości pracy po
  restarcie procesu i nie jest kolejką produkcyjną.
