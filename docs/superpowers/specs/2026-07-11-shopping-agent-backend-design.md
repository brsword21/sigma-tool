# Projekt backendu agenta zakupowego do używanej elektroniki

## 1. Cel i ograniczenia

Celem jest zbudowanie w mniej niż trzy godziny stabilnego backendowego MVP dla jednej kategorii demonstracyjnej: używanych słuchawek. Dwie osoby mają dostarczyć kompletny przepływ od opisu potrzeby, przez rekomendację modeli, po ranking konkretnych ofert i przekierowanie do portalu.

MVP działa jako modularny monolit FastAPI z Supabase jako trwałą pamięcią produktów, researchu, ogłoszeń, historii cen i sesji. Istniejący scraper OLX oraz Firecrawl są podłączane przez ten sam kontrakt co przyszłe źródła, np. Allegro przez MCP. Awaria jednego źródła nie może blokować prezentacji danych zapisanych wcześniej.

## 2. Zakres MVP

### W zakresie

- rozmowa z zachowaniem wymagań użytkownika;
- maksymalnie trzy pytania doprecyzowujące;
- porównanie 4–6 modeli słuchawek;
- wybór modelu i uruchomienie dwóch równoległych procesów: briefu zakupowego oraz pobierania ofert;
- trwały zapis produktów, researchu i ogłoszeń w Supabase;
- obsługa OLX przez istniejący scraper lub Firecrawl;
- wspólny kontrakt pozwalający później dodać Allegro i inne portale;
- jawny, ważony ranking ofert;
- Top 10 z uzasadnieniami oraz wyróżniona najlepsza oferta;
- ponowny ranking istniejących danych po zmianie preferencji;
- ponowne pobieranie tylko wtedy, gdy baza nie wystarcza albo dane są nieaktualne.

### Poza zakresem pierwszych trzech godzin

- niezawodne pokrycie wielu kategorii i portali;
- kolejka Redis/Celery i osobne workery;
- konta użytkowników i rozbudowana autoryzacja;
- automatyczny zakup lub płatności;
- zaawansowane wykrywanie oszustw;
- uczenie modelu rankingowego;
- pełna deduplikacja tej samej oferty wystawionej na różnych portalach.

## 3. Architektura

Backend jest jednym procesem FastAPI podzielonym na moduły o odrębnych odpowiedzialnościach:

1. `conversation` — przechowuje etap rozmowy, wydobywa wymagania i rozpoznaje zmianę preferencji;
2. `product_research` — wyszukuje modele, zapisuje specyfikacje i tworzy brief second-hand;
3. `sources` — adaptery OLX, Firecrawl i przyszłych portali;
4. `listings` — normalizuje, deduplikuje i zapisuje ogłoszenia;
5. `ranking` — filtruje, punktuje i uzasadnia kolejność;
6. `repositories` — jedyna warstwa komunikująca się z Supabase;
7. `orchestration` — steruje pełnym przepływem i równoległymi operacjami.

LLM odpowiada za interpretację języka, uporządkowanie wymagań, research i sformułowanie wyjaśnień. Kod aplikacji podejmuje decyzje o cache, wywołaniu źródeł, filtrach i punktacji. Dzięki temu wynik jest powtarzalny i łatwy do demonstracji.

## 4. Przepływ danych

1. Klient wysyła wiadomość wraz z `session_id`.
2. Backend łączy wiadomość z zapisanym stanem i aktualizuje ustrukturyzowane wymagania.
3. Jeżeli brakuje krytycznej informacji, agent zadaje jedno pytanie. W przeciwnym razie zwraca 4–6 modeli.
4. Po wyborze modelu orkiestrator równolegle:
   - odczytuje lub generuje brief produktu;
   - sprawdza liczbę i świeżość ofert w Supabase.
5. Jeśli baza zawiera wystarczające dane, ranking korzysta z cache. W przeciwnym razie backend pobiera oferty z dostępnych adapterów i zapisuje je przez `upsert`.
6. Ranking wylicza wynik każdej oferty, a LLM formułuje krótkie uzasadnienia Top 10 na podstawie punktów składowych.
7. Kolejny prompt jest klasyfikowany jako:
   - `rerank` — istniejące dane zawierają wymaganą cechę;
   - `refetch` — danych jest za mało, są stare albo nowy filtr nie był pozyskiwany;
   - `new_product_research` — użytkownik zmienia kategorię lub oczekuje innego modelu.

## 5. Kontrakt źródła ofert

Każde źródło implementuje logicznie ten sam interfejs:

```python
class ListingSource(Protocol):
    source_name: str

    async def search(self, query: SearchQuery) -> list[RawListing]: ...
    async def get_details(self, external_id: str) -> RawListing | None: ...
```

`SearchQuery` zawiera model produktu, budżet, warianty, lokalizację i limit wyników. Adapter przekształca odpowiedź portalu do `RawListing`, a centralny normalizator tworzy `NormalizedListing`. Firecrawl jest narzędziem używanym wewnątrz adaptera, a nie osobnym elementem domeny.

Pierwsza implementacja produkcyjna korzysta z działającego kodu OLX. Adapter Firecrawl może obsłużyć OLX jako plan awaryjny oraz inne publicznie dostępne strony. Allegro/MCP jest kolejnym adapterem i nie jest wymagane do ukończenia trzygodzinnego MVP.

## 6. Model Supabase

### `products`

- `id` UUID;
- `category`, `brand`, `model`, `canonical_name`;
- `specifications` JSONB;
- `created_at`, `updated_at`.

Unikalność: znormalizowane `(brand, model)`.

### `product_research`

- `id`, `product_id`;
- `summary`, `key_parameters`, `second_hand_checks`, `known_risks`;
- `sources` JSONB;
- `research_version`, `refreshed_at`.

### `listings`

- `id`, `product_id`;
- `source`, `external_id`, `url`, `title`;
- `price`, `currency`, `condition`, `color`, `location`, `delivery`;
- `description`, `attributes` JSONB, `raw_payload` JSONB;
- `first_seen_at`, `last_seen_at`, `active`.

Unikalność: `(source, external_id)`. Każde pobranie wykonuje `upsert` i aktualizuje `last_seen_at`.

### `listing_snapshots`

- `id`, `listing_id`, `price`, `active`, `observed_at`.

Tabela tworzy historię cen i dostępności potrzebną do przyszłego szacowania typowej wartości rynkowej.

### `sessions`

- `id`, `stage`, `requirements` JSONB, `selected_product_id`;
- `message_summary`, `created_at`, `updated_at`.

### `search_runs`

- `id`, `session_id`, `product_id`, `query` JSONB;
- `sources_requested`, `sources_succeeded`, `status`, `error_summary`;
- `started_at`, `finished_at`.

### `recommendations`

- `id`, `search_run_id`, `listing_id`, `rank`, `score`;
- `score_breakdown` JSONB, `explanation`, `created_at`.

## 7. Cache i decyzja o ponownym scrapowaniu

Dane z bazy są wystarczające, gdy dla wybranego produktu istnieje co najmniej 10 aktywnych ofert pasujących do twardych filtrów, a ich `last_seen_at` mieści się w początkowym TTL 24 godzin. W demo próg można obniżyć do 5, gdy portal zwróci mało wyników.

Zmiana miękka, np. preferowany niebieski kolor, modyfikuje wagi i kolejność. Zmiana twarda, np. maksymalna cena lub wymagany wariant, najpierw filtruje cache. Scraper uruchamia się tylko wtedy, gdy po filtrowaniu pozostało mniej niż 5 ofert albo dane przekroczyły TTL.

Research produktu ma osobny TTL 30 dni. Zapisane dane są rozwijane wersjami zamiast generowane od zera przy każdej sesji.

## 8. Ranking

Początkowy wynik oferty ma skalę 0–100:

- 30 punktów — cena względem mediany aktywnych ofert danego modelu;
- 25 punktów — zgodność z wymaganymi cechami i wariantem;
- 20 punktów — deklarowany stan;
- 10 punktów — kompletność opisu i zdjęć;
- 10 punktów — dostawa lub lokalizacja;
- 5 punktów — zgodność z miękkimi preferencjami, np. kolorem;
- kary od 0 do 30 punktów — sygnały ryzyka.

Wagi są jawne i mogą być modyfikowane przez wymagania użytkownika. Twarde wymagania mogą wykluczać ofertę zamiast jedynie obniżać wynik. Uzasadnienie odwołuje się do maksymalnie trzech najważniejszych zalet i jednego ryzyka lub kompromisu.

## 9. API MVP

- `POST /sessions` — tworzy sesję;
- `POST /sessions/{id}/messages` — aktualizuje wymagania i zwraca pytanie, modele albo wynik;
- `POST /sessions/{id}/products/{product_id}/select` — wybiera model i uruchamia brief oraz wyszukiwanie;
- `GET /runs/{run_id}` — zwraca status i częściowe lub końcowe wyniki;
- `POST /runs/{run_id}/refresh` — wymusza odświeżenie ofert;
- `GET /products/{product_id}/brief` — zwraca zapisany brief;
- `GET /health` — sprawdza backend i połączenie z Supabase.

Dla MVP długie zadanie może być wykonane przez `asyncio.gather` i FastAPI `BackgroundTasks`. Stan zadania jest zapisany w `search_runs`, aby frontend mógł odpytywać o wynik. Brak zewnętrznej kolejki jest świadomym ograniczeniem prototypu.

## 10. Obsługa błędów

- błąd pojedynczego portalu zapisuje się w `search_runs`, ale nie kasuje wyników innych źródeł;
- jeżeli wszystkie źródła zawiodą, backend zwraca nieaktualne dane z wyraźnym oznaczeniem czasu pobrania;
- jeżeli nie ma cache, zwraca status kontrolowany i możliwość ponowienia zamiast błędu serwera;
- niepoprawna odpowiedź LLM jest walidowana przez modele Pydantic i ponawiana najwyżej raz;
- każdy timeout źródła jest ograniczony, aby całe żądanie demo nie wisiało;
- zapis ogłoszeń jest idempotentny dzięki `upsert`.

## 11. Testy i kryteria akceptacji

Minimalne testy obejmują:

- normalizację przykładowej oferty OLX;
- idempotentny zapis i brak duplikatów;
- ranking trzech kontrolowanych ofert;
- klasyfikację `rerank` kontra `refetch`;
- happy path API z zamockowanym LLM i źródłem ofert;
- zachowanie częściowego wyniku po awarii jednego źródła.

Backend jest gotowy do demo, gdy użytkownik w jednej sesji otrzyma co najmniej cztery modele, wybierze jeden, dostanie minimum trzy konkretne oferty z linkami, zobaczy rekomendację z uzasadnieniem oraz zmieni jedną preferencję bez utraty kontekstu. Całość ma zająć mniej niż trzy minuty.

## 12. Granice dalszego rozwoju

Po MVP adaptery źródeł można przenieść do workerów, nie zmieniając API domenowego. Rosnąca baza Supabase umożliwi liczenie median cen z historii, wykrywanie okazji, ograniczanie kosztu LLM i rezygnację z powtarzanego scrapowania. Kolejne kategorie wymagają własnych definicji parametrów i wag, ale korzystają z tego samego przepływu, repozytoriów i kontraktów źródeł.
