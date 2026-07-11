# Sigma Shopping Agent

Backend demonstracyjnego agenta zakupowego dla używanych słuchawek. Przyjmuje potrzebę
albo produkt referencyjny, proponuje 4–6 kierunków, a po wyborze pobiera oferty i osobno
pokazuje dopasowanie produktu, jakość oferty oraz wiarygodność sprzedawcy.

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

## Baza danych

Przed pierwszym uruchomieniem zastosuj kolejno:

- `supabase/migrations/001_initial_schema.sql`
- `supabase/migrations/002_demo_hardening.sql`

Można wkleić je do SQL Editora developerskiego projektu Supabase albo, dla połączonego
lokalnego projektu Supabase CLI, wykonać `supabase db push`.

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

## Dane i ograniczenia demo

- Firecrawl jest jedynym źródłem ofert i ma osobny timeout 20 sekund.
- Pełne pobieranie ofert rusza dopiero po wyborze produktu; późniejsza miękka zmiana
  preferencji wykonuje rerank cache bez ponownego pobierania.
- Model i generacja są filtrem twardym przed scoringiem.
- Cache starszy niż 24 godziny może uratować wynik po awarii źródła, ale jest oznaczony
  przez `is_stale=true`, `stale_cache` i pewność nie większą niż `0.4`.
- Opinie sprzedawcy, gwarancja, zwrot, oryginalność i bateria są pokazywane jako
  `unknown`, jeśli payload źródła ich nie zawiera. System ich nie domyśla.
- Research bez dostarczonego źródła ma `unverified_product_research`, pustą listę źródeł
  i obniżoną pewność.
- Błąd Firecrawl nie powoduje błędu 500 runu: dostępny cache daje status `partial`, a brak
  danych kontrolowany status `failed`.
- BackgroundTasks wystarcza do lokalnego demo, ale nie zapewnia trwałości pracy po
  restarcie procesu i nie jest kolejką produkcyjną.
