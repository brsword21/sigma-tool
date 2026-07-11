# Generalizacja Picky na rynek używanej elektroniki

## Podsumowanie

- Picky obsługuje cały rynek używanej elektroniki, a kategorię rozpoznaje z wiadomości.
- Interfejs nie sugeruje, że produkt służy wyłącznie do wyszukiwania słuchawek.
- Pytania doprecyzowujące, research i wyjaśnienia używają kategorii rozpoznanej w rozmowie.
- Obecny dwuetapowy przepływ wyboru produktu i rankingu ofert pozostaje bez zmian.
- Słuchawki pozostają poprawną kategorią i scenariuszem demonstracyjnym, ale nie kategorią domyślną.

## Założenia i ograniczenia

- Nie dodajemy sztywnej ontologii wszystkich kategorii elektroniki.
- Model zwraca krótki identyfikator kategorii w `Requirements.category`.
- Zmiana nie zwiększa liczby wywołań modeli ani czasu oczekiwania.
- Nie zmieniamy zasad dostępu do sesji, przechowywania danych ani źródeł ofert.
- Neutralna ilustracja zastępuje symbol słuchawek tam, gdzie brak zdjęcia produktu.

## Projekt

Prompt rozmowy najpierw identyfikuje kategorię i produkt referencyjny, a pytanie formułuje
wprost dla rozpoznanego rodzaju urządzenia. Domyślna kategoria to `electronics`, dzięki czemu
nowa sesja nie przekazuje modelowi błędnego założenia o słuchawkach. Prompty researchu i
wyjaśnień są kategoriowo neutralne oraz wymagają kontroli typowych dla konkretnego produktu.

Frontend zachowuje obecny układ i język wizualny. Nagłówek i przykłady pokazują szeroki zakres,
a uniwersalny znak urządzeń zastępuje ikonę słuchawek. Zdjęcie kandydata ma pierwszeństwo przed
ilustracją zastępczą.

## Decyzje

- Wybrano pełną generalizację zamiast kosmetycznej zmiany tekstu, aby usunąć źródło błędu.
- Wybrano dynamiczną kategorię zamiast zamkniętej listy, aby nie ograniczać rynku.
- Zachowano demo słuchawkowe jako przykładowe dane, ponieważ nie definiuje już zakresu produktu.

