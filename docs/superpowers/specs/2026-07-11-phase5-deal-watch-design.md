# Phase 5 — Deal Watch / Mandate Design

## Understanding summary

- Faza 5 ma pokazać, że Sigma potrafi cierpliwie obserwować rynek i wydać jedną
  audytowalną decyzję, zamiast tylko sortować bieżące ogłoszenia.
- Funkcja pozostaje częścią demonstracyjnego backendu dla używanych słuchawek.
- Użytkownik definiuje dokładny wariant, limit kosztu końcowego, minimalny stan i
  minimalną ocenę sprzedawcy.
- System oblicza koszt końcowy z ceny, dostawy, opłat, kosztu FX i ważnego kuponu.
- Decyzja ma jedną z wartości `ignore`, `hold` albo `alert`; faza nie wykonuje zakupu.
- Demo działa deterministycznie i nie zależy od OpenAI, Firecrawl ani Supabase.
- Istniejący przepływ wyszukiwania i ranking ofert pozostają bez zmian.

## Assumptions and non-functional requirements

- Językiem API pozostają stabilne angielskie identyfikatory, a walutą scenariusza PLN.
- Dane są przechowywane wyłącznie w pamięci procesu; restart usuwa mandaty i historię.
- Jedna paczka zawiera maksymalnie 10 zdarzeń, a pola tekstowe mają twarde limity.
- Wszystkie kwoty są nieujemnymi wartościami `Decimal` z dokładnością do grosza.
- Nie są przetwarzane dane osobowe, sekrety, tokeny ani dane płatnicze.
- Moduł jest przeznaczony do lokalnego demo, nie do ciągłego monitoringu produkcyjnego.

## Considered approaches

1. **Isolated Deal Watch / Mandate module — selected.** Najlepsza zgodność z case'em,
   małe ryzyko integracyjne i w pełni deterministyczne demo.
2. **Second marketplace adapter.** Większy zasięg, ale zależność od zewnętrznego API,
   nowe reguły deduplikacji i słabsza odporność demonstracji.
3. **Only caching and observability improvements.** Niskie ryzyko, lecz brak widocznej
   nowej wartości dla użytkownika i jury.

## Architecture

`app/deal_watch/models.py` definiuje walidowane kontrakty mandatu, zdarzenia rynkowego,
rachunku kosztu i decyzji. `costs.py` wykonuje wyłącznie arytmetykę, a `policy.py`
wykonuje wyłącznie reguły biznesowe. `repository.py` przechowuje mandaty i historię
w pamięci, natomiast `service.py` koordynuje zapis i ewaluację. `scenarios.py` dostarcza
kontrolowany zestaw sześciu pułapek. Router FastAPI tylko waliduje transport, wywołuje
usługę i mapuje brak mandatu na 404.

Przepływ: utworzenie mandatu → przyjęcie realnych zdarzeń albo uruchomienie scenariusza
demo → obliczenie kosztu końcowego → sprawdzenie twardych warunków → `ignore` dla
jednoznacznej porażki, `hold` dla brakującego krytycznego dowodu, `alert` dla pełnego
dopasowania → zapis pełnego rachunku i powodów → odczyt historii.

## Error handling and edge cases

- Zły wariant, brak stocku, zbyt słaby stan, zbyt słaby sprzedawca, fałszywa obniżka
  lub przekroczenie budżetu dają `ignore` z konkretnymi kodami powodów.
- Brak wymaganej oceny sprzedawcy daje `hold`, nie pozytywny alert.
- Nieważny kupon jest widoczny w rachunku, ale nie obniża kosztu.
- Koszt po kuponie nie może spaść poniżej zera.
- Nieznany mandat zwraca kontrolowane 404 bez ujawniania szczegółów wewnętrznych.
- Powtórzony `event_id` jest idempotentny i nie emituje kolejnego alertu.

## Testing strategy

Testy jednostkowe obejmują arytmetykę, każdy typ decyzji i brak fałszywego alertu.
Test API obejmuje utworzenie mandatu, symulację sześciu zdarzeń, historię, 404 oraz
odrzucenie zbyt dużego payloadu. Pełny `pytest` i `ruff` pozostają bramą ukończenia.

## Decision log

- Wybrano `alert_only`; alternatywy `checkout_ready` i `auto_buy` odłożono, ponieważ
  wymagałyby autoryzacji, trwałej zgody i integracji płatniczej.
- Wybrano pamięć procesu zamiast nowej migracji, aby faza była niezależna od usług live.
- Wybrano jawne składniki landed cost zamiast jednej dostarczonej kwoty, aby decyzja
  była audytowalna.
- Wybrano `hold` dla brakujących krytycznych danych zamiast optymistycznego `alert`.
- Symulator jest jawnie oznaczony jako demo i nie podszywa się pod prawdziwe źródło.
