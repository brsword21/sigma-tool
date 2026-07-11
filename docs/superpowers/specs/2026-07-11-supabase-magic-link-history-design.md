# Supabase Magic Link and Chat History Design

## Understanding summary

- Logowanie jest opcjonalne; użytkownik-gość może nadal korzystać z aplikacji.
- Supabase Auth wysyła jednorazowy magic link na podany adres e-mail.
- Tylko rozmowy rozpoczęte po zalogowaniu są przypisywane do konta i dostępne później.
- Backend FastAPI weryfikuje token Supabase, ale brak tokenu pozostaje poprawnym trybem gościa.
- Historia zalogowanego użytkownika jest izolowana po `user_id` w API i przez RLS w bazie.
- Zakres nie obejmuje haseł, logowania społecznościowego, panelu administratora ani migracji rozmów gościa.

## Assumptions

- Aplikacja używa istniejącego projektu Supabase i hostowanej usługi Auth.
- Publiczny klient używa URL projektu oraz klucza publishable/anon; `service_role` pozostaje na serwerze.
- Skala demonstracyjna to maksymalnie kilkuset użytkowników i typowy ruch aplikacji hackathonowej.
- Niedostępność Auth nie blokuje trybu gościa.
- Magic link korzysta z limitów i czasu ważności skonfigurowanych w Supabase.
- Adres lokalny i produkcyjny strony zostaną dodane do listy dozwolonych redirectów Auth.

## Architecture

Frontend korzysta z `supabase-js` do wysłania magic linku, odtworzenia sesji po powrocie
i wylogowania. Dostęp do Auth jest konfigurowany w osobnym, lokalnym pliku
`prototype/znajdz/config.js`, aby repozytorium nie zawierało danych środowiskowych.

FastAPI przyjmuje opcjonalny nagłówek Bearer. Brak nagłówka oznacza gościa, a błędny lub
wygasły token zwraca `401`. Zweryfikowane `user_id` jest przekazywane do repozytorium sesji.
Sesje zalogowane mają właściciela; anonimowe zachowują `user_id = null`. Wiadomości są
zapisywane w osobnej tabeli z rolą `user` albo `assistant`.

Backend używa klucza `service_role`, który omija RLS, dlatego każda operacja historii
dodatkowo filtruje po zweryfikowanym `user_id`. RLS pozostaje drugą warstwą ochrony dla
ewentualnego bezpośredniego użycia Data API.

## Data flow

1. Użytkownik wpisuje e-mail i frontend wywołuje `signInWithOtp` z dozwolonym redirectem.
2. Po kliknięciu linku Supabase odtwarza sesję w przeglądarce.
3. Frontend dołącza access token do żądań tworzenia sesji i wysyłania wiadomości.
4. FastAPI waliduje token w Supabase Auth i zapisuje `user_id` przy nowej sesji.
5. Wiadomość użytkownika oraz tekstowa odpowiedź agenta są zapisywane w kolejności.
6. Widok historii pobiera wyłącznie sesje należące do bieżącego użytkownika.

## Error handling and edge cases

- Niepoprawny e-mail jest odrzucany po stronie formularza i Supabase.
- Ponowne kliknięcie zużytego lub wygasłego linku pokazuje kontrolowany komunikat.
- Niepoprawny token nie przełącza żądania cicho w tryb gościa.
- Użytkownik nie może czytać ani modyfikować sesji przypisanej do innego konta.
- Sesje gościa nie pojawiają się w historii po późniejszym zalogowaniu.
- Brak konfiguracji Supabase ukrywa funkcje konta, ale pozostawia działający prototyp.

## Testing strategy

- Testy zależności Auth: brak tokenu, poprawny token, błędny schemat i nieważny token.
- Testy API: sesja gościa, sesja zalogowana, zapis wiadomości i izolacja właścicieli.
- Testy repozytorium: filtry `user_id`, kolejność historii i payload wiadomości.
- Kontrola statyczna UI oraz ręczny smoke test formularza, powrotu z linku i wylogowania.

## Decision log

1. Wybrano Supabase Auth zamiast Cloudflare Access, ponieważ projekt już korzysta z Supabase
   i potrzebuje tożsamości powiązanej z rekordami aplikacji.
2. Wybrano zapis dopiero od momentu logowania zamiast kont anonimowych lub importu danych
   lokalnych, aby ograniczyć złożoność i ryzyko błędnego przypisania historii.
3. Logowanie pozostaje opcjonalne, ponieważ użytkownik chce zachować dostępny tryb gościa.
4. Autoryzacja jest egzekwowana w API i RLS, ponieważ serwerowy klucz omija polityki RLS.
5. Konfiguracja klienta jest zewnętrzna wobec HTML, aby nie wpisywać wartości środowiskowych
   bezpośrednio w prototyp.

