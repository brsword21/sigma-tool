# znajdź. — kierunek UX/UI

## Idea

Interfejs nie wygląda jak panel e-commerce ani komunikator. Jest pustą przestrzenią roboczą, w której jedno zapytanie uruchamia wizualnego agenta zakupowego. Tekst służy tylko do wydania polecenia i potwierdzenia wyniku. Produkty są pokazywane przede wszystkim jako obiekty, nie rekordy w katalogu.

## Zasada redukcji

Na ekranie początkowym pozostają tylko:

- nazwa `znajdź.`;
- menu `•••`;
- duże pole zapytania z możliwością dodania lub wklejenia zdjęcia;
- pusta scena produktowa oznaczona pojedynczym punktem.

Nie ma nagłówków sekcji, filtrów, onboardingowych akapitów, sugestii zapytań, statusu online, licznika koszyka ani stałego podsumowania.

## Układ

Desktop dzieli ekran dokładnie na dwie części:

- lewa połowa jest rozmową sprowadzoną do krótkich zdań i wyników w formie trzech lekkich wierszy;
- prawa połowa jest dużą, organiczną sceną, na której lewitują wygenerowane, bezmarkowe modele produktów.

Na telefonie rozmowa i scena układają się pionowo. Po zakończeniu wyszukiwania widok płynnie przesuwa się do modeli.

## Scena produktowa

- Tło jest neutralne, ciepłe i prawie monochromatyczne.
- Podczas wyszukiwania trzy modele pojawiają się kolejno i poruszają szybciej, jak elementy analizowane przez agenta.
- Po zakończeniu wybrany model rośnie i przechodzi na pierwszy plan; pozostałe pozostają w tle.
- Kliknięcie w wynik tekstowy albo model zmienia aktywny produkt.
- Jedyny opis na scenie to nazwa kategorii, dwie cechy, cena i trzy ikonowe akcje.
- Modele nie mają nazw marek, logotypów, tekstów ani mocnych kolorów.

## Pole zapytania

- Jedyny dominujący komponent po lewej stronie.
- `Enter` wysyła, `Shift + Enter` tworzy nowy wiersz.
- Spinacz otwiera wybór obrazu.
- Obraz można wkleić bezpośrednio ze schowka.
- Miniatura pozwala usunąć zdjęcie przed wysłaniem.
- Można wysłać sam obraz bez tekstu.

## Menu agenta

Menu pod trzema kropkami zawiera wyłącznie:

- włącznik automatycznych zamian;
- priorytet: balans, cena albo jakość;
- reset rozmowy.

Ustawienia nie konkurują z głównym zadaniem i są zamknięte domyślnie.

## Wyniki i działania

Po znalezieniu produktów pojawiają się trzy krótkie wiersze: numer, ogólna nazwa produktu i cena. Bez badge’y, ocen dopasowania i list cech. Wybrany produkt można:

- zamienić na tańszy;
- przełączyć na inny wariant;
- usunąć.

Działania są ikonowe, mają opisy dostępności oraz podpowiedzi systemowe.

## Charakter wizualny

- Typografia: Manrope, zwarta i lekko techniczna.
- Kolory: biel, ciepły papier `#f4f2ed`, niemal czarny `#161616`.
- Akcent `#c7ff4a` występuje tylko w zaznaczeniu tekstu, nie jako dekoracja interfejsu.
- Obramowania mają niską przezroczystość, a cień występuje tylko pod polem rozmowy i menu.
- Asymetryczny obrys sceny i ruch produktów nadają interfejsowi własny charakter.

## Stany

1. **Początek:** pusta scena i aktywne pole rozmowy.
2. **Załącznik:** miniatura obrazu wewnątrz pola.
3. **Szukanie:** trzy modele lewitują, a jedyny status zmienia się między „szukam”, „porównuję” i „układam”.
4. **Wynik:** trzy wiersze po lewej, aktywny model po prawej.
5. **Modyfikacja:** cena, wariant lub liczba wyników zmienia się bez przeładowania widoku.

## Dostępność

- Semantyczne formularze i przyciski.
- `aria-live` dla wyników i komunikatów.
- Opisy przycisków ikonowych.
- Widoczne obramowanie fokusu.
- Obsługa klawiatury i ograniczonego ruchu przez `prefers-reduced-motion`.
- Maksymalny rozmiar wklejanego obrazu: 8 MB.
