# znajdź. — prototyp agenta zakupowego

Samodzielny prototyp HTML przygotowany do edycji i uruchomienia w Cursorze.

## Uruchomienie

1. Otwórz cały folder w Cursorze.
2. Otwórz plik `index.html`.
3. Uruchom go przez rozszerzenie **Live Server** (`Open with Live Server`) albo przeciągnij plik do przeglądarki.

Nie trzeba wykonywać `npm install`. Tailwind CSS, Lucide Icons i font są pobierane przez CDN, dlatego podczas uruchamiania potrzebne jest połączenie z internetem.

## Supabase Magic Link

1. Otwórz `config.js` i wpisz URL projektu Supabase oraz publiczny klucz publishable
   (lub starszy klucz `anon`). Nigdy nie wpisuj tutaj klucza `service_role`.
2. Ustaw `apiBaseUrl` na adres backendu FastAPI, domyślnie `http://localhost:8000`.
3. W Supabase Dashboard przejdź do **Authentication → URL Configuration**. Ustaw Site URL
   i dodaj dokładny adres Live Server do Redirect URLs, np. `http://127.0.0.1:5500/**`.
4. Dodaj ten sam origin do `CORS_ORIGINS` backendu, np.
   `http://127.0.0.1:5500,http://localhost:5500`.
5. Zastosuj migrację `supabase/migrations/003_auth_chat_history.sql` i uruchom backend.

Logowanie pozostaje opcjonalne. Rozmowy gościa nie są później przenoszone na konto;
historia zapisuje się od pierwszej wiadomości wysłanej po zalogowaniu.

## Najważniejsze funkcje

- konwersacyjne wyszukiwanie produktów;
- animowana scena z lewitującymi modelami;
- dodawanie pliku graficznego i wklejanie zdjęć ze schowka;
- wybór produktu, tańszy zamiennik, zmiana wariantu i usuwanie;
- menu ustawień agenta;
- opcjonalne logowanie magic linkiem i prywatna historia rozmów;
- responsywny układ desktop/mobile.

## Struktura

- `index.html` — kompletny interfejs, style, logika i osadzone grafiki;
- `design.md` — aktualna specyfikacja UX/UI;
- `README.md` — instrukcja uruchomienia.
