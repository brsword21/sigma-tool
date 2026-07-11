# Goal: agent zakupowy do używanej elektroniki

## 1. Cel produktu

W ciągu 6 godzin budujemy działający prototyp agenta zakupowego, który pomaga osobie nieznającej się na elektronice:

1. ustalić, jaki konkretny model produktu najlepiej odpowiada jej potrzebom;
2. znaleźć pasujące oferty używane tego modelu;
3. porównać oferty i wskazać najlepszy zakup wraz z krótkim uzasadnieniem.

Produkt ma skrócić drogę od ogólnej potrzeby — np. „szukam dobrych słuchawek do 500 zł” — do pewnej, uzasadnionej decyzji zakupowej.

## 2. Problem użytkownika

Rynek używanej elektroniki jest rozproszony. Użytkownik musi osobno:

- zrozumieć, jakie modele spełniają jego wymagania;
- czytać recenzje, fora i porównania;
- przeglądać wiele serwisów ogłoszeniowych;
- oceniać cenę, stan, wiarygodność i opłacalność ofert;
- rozpoznawać, czy tańszy zamiennik nie spełnia potrzeb równie dobrze.

Osoba bez wiedzy technicznej często nie zna właściwych parametrów ani nazw modeli. Istnieją porównywarki nowej elektroniki, ale brakuje jednego wygodnego narzędzia prowadzącego przez wybór produktu i zakup z rynku wtórnego.

## 3. Użytkownik docelowy

Osoba, która:

- chce kupić elektronikę możliwie tanio;
- dopuszcza zakup rzeczy używanej;
- nie śledzi rynku i nie zna wszystkich modeli;
- potrafi opisać potrzebę, budżet i preferencje prostym językiem;
- oczekuje kilku trafnych propozycji zamiast setek wyników;
- chce, aby narzędzie pomogło jej podjąć decyzję, a nie tylko pokazało linki.

Przykład: użytkowniczka szuka bezprzewodowych słuchawek do 500 zł, zależy jej na wygodzie, ANC i niebieskim kolorze, ale nie zna konkretnych modeli.

## 4. Obietnica wartości

**Opisz, czego potrzebujesz. Agent wybierze właściwy model, znajdzie używane oferty i pokaże, którą warto kupić.**

Wyróżnikiem produktu jest połączenie dwóch dziś rozdzielonych zadań:

- researchu produktowego: „co mam kupić?”;
- wyszukiwania ofert: „gdzie i którą sztukę kupić?”.

## 5. Główny przebieg użytkownika

### Faza 1: wybór modelu

1. Użytkownik opisuje potrzebę własnymi słowami.
2. Agent aktywnie dopytuje tylko o informacje istotne dla decyzji, np. budżet, zastosowanie i najważniejsze cechy.
3. Agent przedstawia krótką listę 4–6 modeli z:
   - nazwą i zdjęciem, jeśli jest dostępne;
   - orientacyjną ceną;
   - najważniejszymi cechami;
   - krótkim „dlaczego pasuje”;
   - najważniejszym kompromisem.
4. Użytkownik wybiera jeden model lub prosi o zmianę pojedynczego wymagania.
5. Kontekst rozmowy zostaje zachowany — nie trzeba zaczynać od zera.

### Faza 2: wybór oferty

1. Po wskazaniu modelu agent uruchamia wyszukiwanie ofert używanych.
2. Zbiera ograniczoną liczbę aktualnych ofert z dostępnego źródła lub źródeł.
3. Normalizuje podstawowe dane: cena, stan, wariant, lokalizacja/dostawa, opis i link.
4. Ocenia oferty pod kątem zgodności z potrzebą i opłacalności.
5. Pokazuje 3–5 najlepszych wyników oraz rekomenduje jedną ofertę z uzasadnieniem.

## 6. Zakres MVP na hackathon

### Must have

- interfejs rozmowy z zachowaniem kontekstu;
- obsługa jednej kategorii demonstracyjnej, najlepiej słuchawek;
- przyjęcie potrzeby i zadanie pytań doprecyzowujących;
- rekomendacja kilku konkretnych modeli;
- wybór modelu przez użytkownika;
- pobranie lub wykorzystanie przygotowanego zestawu ofert używanych;
- ranking ofert według ceny, zgodności i jakości;
- wskazanie najlepszej oferty z czytelnym uzasadnieniem;
- klikalny link do źródła oferty;
- pełny, stabilny scenariusz demonstracyjny od potrzeby do decyzji.

### Should have, jeśli zostanie czas

- porównanie ceny używanej z ceną nowego produktu;
- możliwość zmiany jednego parametru bez resetowania rozmowy;
- wyszukiwanie podobnego, tańszego zamiennika;
- sygnały ryzyka w ofercie, np. brak ważnych informacji lub podejrzanie niska cena;
- zapis wyników researchu, aby nie wykonywać ponownie tej samej pracy.

### Poza zakresem MVP

- pełne pokrycie wszystkich kategorii elektroniki;
- niezawodne skrapowanie wielu platform w czasie rzeczywistym;
- zakupy lub płatności wewnątrz aplikacji;
- długoterminowe uczenie się preferencji wszystkich użytkowników;
- zaawansowany system kont, profili i powiadomień;
- perfekcyjne wykrywanie oszustw;
- rozbudowany silnik matematyczny, jeżeli prosty scoring wystarczy do demo.

## 7. Logika rekomendacji

Na etapie wyboru modelu ranking powinien uwzględniać:

- zgodność z budżetem;
- zgodność z zastosowaniem;
- wymagane cechy;
- preferencje miękkie, np. kolor, wygląd lub marka;
- dostępność na rynku wtórnym;
- jakość i wiarygodność modelu wynikającą z researchu.

Na etapie wyboru oferty ranking powinien uwzględniać:

- cenę względem typowej ceny rynkowej;
- deklarowany stan;
- kompletność opisu;
- zgodność wariantu z wymaganiami;
- dostawę lub lokalizację;
- widoczne czynniki ryzyka.

Na hackathon wystarczy przejrzysty scoring ważony. Użytkownik powinien widzieć ludzkie uzasadnienie, nie sam wynik liczbowy.

## 8. Założenia techniczne MVP

- model językowy prowadzi rozmowę, porządkuje wymagania i generuje uzasadnienia;
- dane ofert pochodzą z jednego działającego źródła albo kontrolowanego zestawu demonstracyjnego;
- warstwa pobierania danych jest oddzielona od logiki rekomendacji, aby później łatwo dodać kolejne serwisy;
- aplikacja przechowuje stan sesji i wybrane preferencje;
- kosztowne, głębokie analizy uruchamiane są dopiero po zawężeniu wyboru;
- wcześniejsze wyniki mogą być buforowane, ale cache nie może blokować ukończenia głównego scenariusza.

## 9. Kryteria ukończenia

MVP jest gotowe, gdy podczas demo można bez ręcznego omijania błędów:

1. wpisać ogólną potrzebę zakupową;
2. odpowiedzieć na pytania agenta;
3. otrzymać co najmniej 4 sensowne modele z uzasadnieniem;
4. wybrać model;
5. otrzymać co najmniej 3 konkretne oferty używane;
6. zobaczyć rekomendowaną ofertę i powód wyboru;
7. przejść linkiem do ogłoszenia;
8. zmienić jedno wymaganie bez utraty całego kontekstu.

## 10. Metryki sukcesu prototypu

- użytkownik dochodzi od pierwszego promptu do rekomendacji w mniej niż 3 minuty;
- liczba niezbędnych pytań doprecyzowujących nie przekracza 3;
- każda rekomendacja zawiera jasne „dlaczego tak” oraz kompromis;
- cały happy path działa powtarzalnie podczas prezentacji;
- jury rozumie różnicę między produktem a zwykłą porównywarką cen po jednym zdaniu.

## 11. Scenariusz demo

> Szukam używanych słuchawek bezprzewodowych do 500 zł. Będę ich używać w komunikacji miejskiej i podczas pracy. Zależy mi na ANC, wygodzie i niebieskim kolorze.

Agent dopytuje o konstrukcję lub priorytet, proponuje kilka modeli, użytkownik wybiera jeden, a system pokazuje najlepsze używane oferty i rekomenduje zakup. Następnie użytkownik mówi: „te są za drogie, znajdź podobne tańsze”, demonstrując zachowanie kontekstu i możliwość znalezienia zamiennika.

## 12. Najważniejsza decyzja produktowa

Najpierw dowozimy jeden kompletny i efektowny przepływ dla jednej kategorii. Szerokość katalogu, liczba źródeł i zaawansowanie algorytmu są mniej ważne niż wiarygodna demonstracja, że agent potrafi przeprowadzić użytkownika od niejasnej potrzeby do konkretnej oferty.
