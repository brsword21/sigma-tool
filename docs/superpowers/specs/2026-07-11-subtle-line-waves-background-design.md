# Subtelne animowane tło LineWaves

## Cel

Dodać do całej aplikacji Picky spokojną, białą animację fal jako tło dekoracyjne. Efekt ma być widoczny, ale nie może konkurować z treścią ani zmniejszać czytelności interfejsu.

## Zakres

- Nowy komponent React `LineWaves` wykorzystuje dostarczony shader WebGL i bibliotekę OGL.
- Komponent jest renderowany raz na poziomie korzenia aplikacji jako nieruchoma warstwa tła obejmująca cały viewport.
- Warstwa tła nie reaguje na kursor i nie przechwytuje interakcji użytkownika.
- Wszystkie istniejące panele pozostają na jasnych, lekko nieprzezroczystych powierzchniach nad animacją.
- Przy ustawieniu systemowym `prefers-reduced-motion: reduce` tło nie jest animowane.

## Wygląd i parametry

- Kolory wszystkich fal: biały (`#ffffff`).
- Prędkość i jasność są niższe niż w dostarczonym przykładzie, aby efekt był dyskretny.
- Tło bazowe pozostaje chłodne i bardzo jasne; falom towarzyszy delikatny gradient, który pozwala je dostrzec mimo białego koloru.
- Zawartość aplikacji otrzymuje wyższy kontekst nakładania, bez zmian w działaniu formularzy, menu i okien modalnych.

## Struktura

1. `frontend/src/components/LineWaves.tsx` zawiera komponent, shadery i bezpieczne sprzątanie zasobów WebGL.
2. `frontend/src/styles/line-waves.css` definiuje pozycjonowanie tła, powierzchnie aplikacji oraz regułę ograniczenia ruchu.
3. `frontend/src/App.tsx` montuje komponent tła jako pierwszy element aplikacji.
4. `frontend/package.json` zawiera zależność `ogl`.

## Zachowanie awaryjne i dostępność

- Brak WebGL nie blokuje interfejsu: widoczny pozostaje statyczny jasny gradient.
- Warstwa ma `aria-hidden` i `pointer-events: none`.
- Przy ograniczeniu ruchu kanwa jest ukrywana; użytkownik nadal widzi statyczne tło.

## Weryfikacja

- Kompilacja TypeScript i produkcyjny build frontendu kończą się powodzeniem.
- Ręczny podgląd potwierdza zasięg pełnego viewportu, brak blokowania kliknięć oraz dobrą czytelność na widokach rozmowy, wyników i modali.
