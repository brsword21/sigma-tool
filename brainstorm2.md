# Podsumowanie brainstormu produktu

## 1. Cel projektu

Celem jest stworzenie narzędzia, które pomaga użytkownikowi znaleźć **najlepszy produkt podobny do wskazanego wzorca**, ale lepiej dopasowany do jego potrzeb, przede wszystkim pod względem ceny, jakości i wiarygodności oferty.

Przykład:

> "Chcę słuchawki podobne do najnowszych AirPodsów, ale tańsze i niekoniecznie marki Apple."

System powinien samodzielnie:

1. zrozumieć, jaki produkt użytkownik ma na myśli,
2. ustalić najważniejsze cechy produktu referencyjnego,
3. znaleźć podobne produkty,
4. porównać oferty z wielu źródeł,
5. wskazać najlepsze opcje wraz z uzasadnieniem.

---

## 2. Główne założenie UX

Użytkownik nie chce ręcznie wpisywać dużej liczby parametrów. Oczekuje, że system:

- domyśli się intencji na podstawie krótkiego opisu,
- pobierze podstawowe informacje o produkcie referencyjnym,
- pokaże kilka czytelnych opcji,
- umożliwi szybkie doprecyzowanie wyboru.

<u>Najważniejsza zasada: jak najmniej pracy po stronie użytkownika.</u>

System może wykonywać wiele automatycznych kroków w tle, ale dla użytkownika proces powinien wyglądać jak jeden prosty ekran lub jedna spójna rozmowa.

---

## 3. Proponowany przebieg działania

### Krok 1 - wejście użytkownika

Użytkownik podaje produkt referencyjny i ogólne wymaganie.

Przykład:

> "Szukam czegoś podobnego do AirPods Pro, ale taniej."

### Krok 2 - identyfikacja produktu referencyjnego

System pobiera podstawowy opis produktu z internetu, np.:

- typ urządzenia,
- najważniejsze parametry,
- przedział cenowy,
- charakterystyczne funkcje,
- popularne zastosowanie.

Opis może pochodzić ze stron sklepów, producenta, serwisów porównawczych lub innych dostępnych źródeł.

### Krok 3 - szybkie wyszukanie kandydatów

Na początku system wykonuje ograniczoną liczbę zapytań, np. około 10, aby znaleźć pierwszych kandydatów bez dużego kosztu i bez pełnej analizy całego rynku.

### Krok 4 - prezentacja pierwszych propozycji

System pokazuje kilka produktów wraz z:

- zdjęciem lub nazwą,
- ceną,
- krótkim opisem,
- głównymi podobieństwami,
- najważniejszymi różnicami.

<u>Cena powinna być widoczna już przy pierwszej prezentacji produktu.</u>

Nie należy przedstawiać pierwszej propozycji jako ostatecznej odpowiedzi. Interfejs powinien jasno komunikować, że jest to etap rozpoznania potrzeb i wyboru kierunku dalszego wyszukiwania.

### Krok 5 - doprecyzowanie preferencji

Użytkownik wybiera, co jest dla niego najważniejsze, np.:

- jak największe podobieństwo do oryginału,
- niższa cena,
- jakość dźwięku,
- bateria,
- marka,
- gwarancja,
- opinie klientów.

Preferencje powinny być podane jako proste opcje, a nie rozbudowany formularz.

### Krok 6 - pełne porównanie

Po wybraniu kierunku system przeszukuje większą liczbę źródeł i tworzy ranking najlepszych ofert.

---

## 4. Najważniejsze kryteria oceny produktu i oferty

### Kryteria produktu

1. Stopień podobieństwa do produktu referencyjnego.
2. Jakość wykonania.
3. Funkcjonalność.
4. Czas pracy baterii.
5. Stan produktu.
6. Oryginalność produktu i części.
7. Możliwość naprawy i dostępność części.
8. Cena konkretnego wariantu.

### Kryteria sprzedawcy i oferty

1. Zweryfikowane opinie klientów.
2. Wiarygodność sklepu lub sprzedawcy.
3. Liczba sprzedanych produktów.
4. Warunki gwarancji.
5. Możliwość zwrotu.
6. Odpowiedzialność sprzedawcy.
7. Aktualność oferty.
8. Dostępność produktu.
9. Prawidłowe dopasowanie wariantu, np. pamięci, koloru lub generacji.

### Priorytety problemów wskazane podczas rozmowy

1. Niepewność jakości, stanu lub wiarygodności produktu.
2. Bateria, możliwość naprawy i oryginalność części.
3. Konieczność porównania wielu serwisów.
4. Gwarancja, zwrot i odpowiedzialność sprzedawcy.
5. Porównanie cen dokładnie tych samych wariantów.
6. Nieaktualne lub źle posortowane oferty.

---

## 5. Najważniejsze decyzje

<u>1. Demo zostanie początkowo ograniczone do jednego rodzaju produktu.</u>

Najlepiej zacząć od jednego konkretnego przykładu, np. słuchawek, telefonu lub tabletu. Pozwoli to dokładnie dopracować logikę bez budowania od razu uniwersalnej bazy produktów.

<u>2. Nie budujemy własnej kompletnej bazy urządzeń elektronicznych.</u>

Na etapie demo dane mają być pobierane z istniejących stron internetowych i ofert e-commerce.

<u>3. Proces ma wyglądać jak jeden spójny przepływ.</u>

Nie należy dzielić go na niezależne ekrany, które mogą sugerować użytkownikowi, że otrzymał już ostateczny wynik.

<u>4. Cena jest pokazywana od początku.</u>

Produkt bez ceny jest trudny do oceny, a cena silnie wpływa na postrzeganie jakości i atrakcyjności propozycji.

<u>5. Najpierw wykonujemy tani, szybki etap wyszukiwania.</u>

Pełna analiza rynku następuje dopiero po wstępnym rozpoznaniu intencji użytkownika.

<u>6. System powinien automatycznie wnioskować preferencje.</u>

Użytkownik nie powinien być zmuszany do ręcznego definiowania wszystkich parametrów.

<u>7. Opinie klientów i wiarygodność źródeł są kluczowe.</u>

System nie może opierać rekomendacji wyłącznie na specyfikacji technicznej i cenie.

<u>8. Backend demo działa lokalnie i korzysta z zewnętrznych API.</u>

Na obecnym etapie nie jest wymagane wdrażanie pełnej infrastruktury chmurowej.

---

## 6. Decyzje techniczne i ograniczenia

- Brak jednej darmowej, kompletnej bazy danych produktów elektronicznych.
- Dane będą pobierane z wielu stron, które już są analizowane w procesie wyszukiwania ofert.
- Dostępność bezpłatnych API jest ograniczona.
- eBay został wskazany jako jedno z niewielu źródeł umożliwiających bezpłatny dostęp do danych, ale integracja może być czasochłonna.
- Należy kontrolować liczbę zapytań i zużycie tokenów.
- Na pierwszym etapie wystarczy niewielka liczba kandydatów.
- Pełne przeszukiwanie wielu źródeł powinno odbywać się dopiero po doprecyzowaniu intencji.

---

## 7. Proponowany prompt systemowy dla demo

```text
Jesteś asystentem zakupowym. Twoim zadaniem jest znaleźć produkty podobne do produktu wskazanego przez użytkownika, ale lepiej dopasowane do jego potrzeb.

1. Zidentyfikuj produkt referencyjny.
2. Ustal jego najważniejsze cechy, typową cenę oraz główne zastosowanie.
3. Wywnioskuj z wypowiedzi użytkownika jego najbardziej prawdopodobne priorytety.
4. Znajdź kilka podobnych produktów z różnych źródeł.
5. Dla każdego produktu podaj:
   - cenę,
   - stopień podobieństwa do produktu referencyjnego,
   - najważniejsze zalety i różnice,
   - jakość i wiarygodność opinii,
   - gwarancję i możliwość zwrotu,
   - wiarygodność sprzedawcy,
   - ewentualne ryzyka.
6. Nie przedstawiaj pierwszego znalezionego produktu jako ostatecznego wyboru.
7. Pokaż użytkownikowi kilka czytelnych opcji i pozwól mu wybrać kierunek:
   - najbardziej podobny,
   - najlepsza jakość,
   - najniższa cena,
   - najlepszy stosunek ceny do jakości.
8. Po wyborze wykonaj dokładniejsze porównanie ofert.
9. Korzystaj wyłącznie z aktualnych danych i podawaj źródła.
10. Jeżeli dane są niepewne lub sprzeczne, zaznacz to wprost.
```

---

## 8. Agenda dalszych prac

### Priorytet 1 - przygotowanie demo

1. Wybrać jeden typ produktu do demonstracji.
2. Wybrać jeden produkt referencyjny, np. AirPods Pro.
3. Przygotować około 10 przykładowych produktów lub ofert.
4. Zdefiniować format danych wejściowych i wyjściowych.
5. Przygotować podstawowy prompt.
6. Zbudować prosty ekran prezentujący propozycje i ceny.

### Priorytet 2 - logika rankingu

1. Zdefiniować sposób obliczania podobieństwa.
2. Ustalić wagi kryteriów.
3. Oddzielić ocenę produktu od oceny oferty i sprzedawcy.
4. Dodać wykrywanie dokładnych wariantów produktu.
5. Dodać ocenę ryzyka i niepewności danych.

### Priorytet 3 - źródła danych

1. Sprawdzić integrację z eBay.
2. Wybrać dodatkowe sklepy lub porównywarki.
3. Określić, które dane można pobierać bezpośrednio ze stron.
4. Zweryfikować regulaminy i ograniczenia techniczne.
5. Zbudować mechanizm ujednolicania danych z wielu źródeł.

### Priorytet 4 - prezentacja

1. Przygotować prosty scenariusz użytkownika.
2. Pokazać, że rozwiązanie może później działać dla innych kategorii elektroniki.
3. Nie deklarować pełnej uniwersalności, jeżeli demo obsługuje tylko jeden typ produktu.
4. Pokazać ograniczenie kosztu dzięki wyszukiwaniu dwuetapowemu.
5. Podkreślić ograniczenie liczby działań wymaganych od użytkownika.

---

## 9. Otwarte pytania

1. Jaki produkt zostanie wykorzystany w finalnym demo?
2. Czy pierwsze propozycje mają służyć wyłącznie doprecyzowaniu potrzeb, czy mają już być częścią rankingu?
3. Jak dokładnie obliczać stopień podobieństwa?
4. Jakie źródła danych są możliwe do wdrożenia w dostępnym czasie?
5. Jak odróżniać opinie zweryfikowane od niewiarygodnych?
6. Jak często aktualizować ceny i dostępność?
7. Czy system ma pozwalać użytkownikowi ręcznie zmieniać wagi kryteriów?
8. Jak prezentować brak pewności co do stanu, oryginalności lub jakości produktu?

---

## 10. Minimalny zakres MVP

MVP powinno:

- obsługiwać jeden typ produktu,
- przyjmować nazwę produktu referencyjnego i krótką preferencję,
- pobierać podstawowy opis produktu,
- znaleźć kilka podobnych produktów,
- pokazać ceny i podstawowe różnice,
- ocenić podobieństwo, jakość oferty i wiarygodność sprzedawcy,
- umożliwić użytkownikowi wybranie preferowanego kierunku,
- przygotować finalny ranking z uzasadnieniem i źródłami.

<u>Najważniejszy efekt demo: użytkownik podaje krótki opis, a system sam prowadzi go do kilku wiarygodnych i dobrze porównanych ofert.</u>
