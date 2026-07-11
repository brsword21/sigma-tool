# Ukrywanie propozycji promptów po rozpoczęciu pisania

## Cel

Na ekranie startowym Picky przykładowe prompty, takie jak „Samsung S25 w dobrym stanie do 2200 zł”, mają natychmiast zniknąć, gdy użytkownik zacznie edytować pole wiadomości. Po usunięciu tekstu nie pojawiają się ponownie w tej samej otwartej sesji aplikacji.

## Projekt

`App` dostanie lokalny stan `examplesDismissed`, początkowo ustawiony na `false`. Pierwsze zdarzenie zmiany pola wiadomości ustawi go na `true`; wartość nie będzie później cofana. Renderowanie listy przykładów będzie wymagało jednocześnie fazy `idle` i `examplesDismissed === false`.

Kliknięcie przykładu nadal tylko wpisuje jego treść do pola. Ponieważ jest to celowa zmiana tekstu prompta, przykłady zostaną po tym kliknięciu ukryte tak samo jak po ręcznym wpisywaniu.

## Zakres i zachowanie brzegowe

- Zmiana dotyczy wyłącznie listy przykładów na ekranie początkowym.
- Wysłanie wiadomości, wybór modelu, obsługa błędów i przebieg wyszukiwania pozostają bez zmian.
- Wyczytanie pola nie przywraca przykładów.
- Ponowne otwarcie lub odświeżenie aplikacji tworzy nową sesję interfejsu i przywraca przykłady.

## Weryfikacja

1. Na początku widoczne są oba przykładowe prompty.
2. Po wpisaniu pierwszego znaku oba natychmiast znikają.
3. Po wyczyszczeniu pola nie wracają.
4. Kliknięcie przykładu wypełnia pole i ukrywa listę.
5. Kompilacja frontendu przechodzi bez błędów typów.
