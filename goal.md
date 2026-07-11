# Goal: agent zakupowy do używanej elektroniki

## 1. Cel produktu

W ciągu 6 godzin budujemy działający prototyp agenta zakupowego, który pomaga osobie nieznającej się na elektronice przejść od krótkiej potrzeby lub znanego produktu referencyjnego do konkretnej, uzasadnionej i możliwie bezpiecznej decyzji zakupowej na rynku wtórnym.

Agent powinien:

1. zrozumieć potrzebę albo zidentyfikować wskazany produkt referencyjny;
2. znaleźć produkty podobne, tańsze lub lepiej dopasowane do priorytetów użytkownika;
3. porównać właściwe warianty oraz konkretne oferty;
4. oddzielnie ocenić dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy;
5. wskazać najlepszy zakup wraz ze źródłami, kompromisami i poziomem niepewności.

Przykładowe wejścia:

> Szukam dobrych słuchawek z ANC do 500 zł.

> Chcę coś podobnego do AirPods Pro, ale taniej i niekoniecznie Apple.

## 2. Problem użytkownika

Rynek używanej elektroniki jest rozproszony, niejednorodny i trudny do oceny. Użytkownik musi osobno:

- zrozumieć, jakie modele spełniają jego potrzeby;
- przełożyć znany produkt na cechy, których naprawdę szuka;
- czytać recenzje, fora i porównania;
- porównywać ceny dokładnie tych samych wariantów;
- przeglądać wiele serwisów ogłoszeniowych i sklepów;
- oceniać stan, oryginalność, baterię, możliwość naprawy i kompletność oferty;
- sprawdzać opinie, gwarancję, zwrot i wiarygodność sprzedawcy;
- rozpoznawać nieaktualne, źle opisane lub podejrzane oferty.

Osoba bez wiedzy technicznej często nie zna parametrów ani nazw alternatywnych modeli. Produkt ma zdjąć z niej ciężar ręcznego researchu, nie ukrywając przy tym braków i niepewności danych.

## 3. Użytkownik docelowy

Osoba, która:

- chce kupić elektronikę możliwie tanio i dopuszcza rynek wtórny;
- zna ogólną potrzebę albo produkt, który jej się podoba;
- nie śledzi rynku i nie potrafi samodzielnie porównać wszystkich wariantów;
- oczekuje kilku trafnych propozycji zamiast setek wyników;
- chce ograniczyć ryzyko złego stanu, niewłaściwego wariantu lub niewiarygodnego sprzedawcy;
- chce podjąć decyzję, a nie tylko otrzymać listę linków.

## 4. Obietnica wartości

**Powiedz, czego potrzebujesz albo co Ci się podoba. Agent znajdzie podobne, lepiej dopasowane produkty i wskaże używaną ofertę, którą warto rozważyć.**

Wyróżnikiem jest połączenie trzech rozdzielonych dziś zadań:

- researchu produktowego: „co spełni moje potrzeby?”;
- wyszukiwania alternatyw: „co jest podobne, ale tańsze lub lepsze dla mnie?”;
- oceny zakupu: „który wariant, oferta i sprzedawca są najbardziej wiarygodni?”.

## 5. Zasady doświadczenia użytkownika

- Jak najmniej pracy po stronie użytkownika.
- Jedna spójna rozmowa z zachowaniem kontekstu.
- Automatyczne wnioskowanie preferencji z krótkiej wypowiedzi.
- Maksymalnie trzy pytania doprecyzowujące w sesji.
- Cena widoczna już przy pierwszych propozycjach.
- Proste kierunki wyboru zamiast rozbudowanego formularza wag.
- Jasne oznaczenie, że pierwsza lista służy eksploracji, a nie jest ostatecznym rankingiem.
- Wyraźne komunikowanie źródeł, braków danych i niepewności.

## 6. Główny przebieg użytkownika

### Faza 1: rozpoznanie i wybór kierunku

1. Użytkownik opisuje potrzebę albo wskazuje produkt referencyjny i krótkie oczekiwanie.
2. Agent identyfikuje produkt, jego charakterystyczne cechy, typową cenę i zastosowanie.
3. Agent wnioskuje priorytety i pyta tylko o krytyczny brak.
4. Wykonuje ograniczony, tani research i przedstawia 4–6 modeli z:
   - nazwą i zdjęciem, jeśli jest dostępne;
   - orientacyjną ceną;
   - stopniem oraz powodami podobieństwa;
   - najważniejszymi różnicami;
   - krótkim „dlaczego pasuje”;
   - głównym kompromisem.
5. Użytkownik wybiera model albo kierunek: najbardziej podobny, najlepsza jakość, najniższa cena lub najlepszy stosunek ceny do jakości.
6. Kontekst rozmowy zostaje zachowany przy zmianie pojedynczej preferencji.

### Faza 2: pełne porównanie ofert

1. Agent uruchamia dokładniejszy research wybranych produktów i wyszukiwanie ofert.
2. Zbiera ograniczoną liczbę aktualnych ofert z dostępnego źródła lub źródeł.
3. Normalizuje cenę, stan, wariant, lokalizację lub dostawę, gwarancję, zwrot, sprzedawcę, opis, link i czas aktualizacji — o ile dane są dostępne.
4. Odrzuca oferty niespełniające twardych wymagań lub dotyczące niewłaściwego wariantu.
5. Oddzielnie ocenia produkt, ofertę i wiarygodność sprzedawcy.
6. Pokazuje ranking ofert: 5 najlepszych (Top 5) z jedną wyróżnioną rekomendacją oraz do 15 dalszych, słabszych propozycji; dla każdej wskazuje zalety, kompromisy, ryzyka i braki danych. Uzasadnienie pozycji odnosi się do parametrów istotnych dla danego urządzenia, pochodzących z briefu produktowego.

## 7. Zakres MVP na hackathon

### Must have

- interfejs rozmowy z zachowaniem kontekstu;
- obsługa jednej kategorii demonstracyjnej — słuchawek;
- dwa wejścia: potrzeba użytkownika oraz nazwa produktu referencyjnego;
- identyfikacja produktu referencyjnego i jego najważniejszych cech;
- automatyczne wnioskowanie preferencji oraz maksymalnie trzy pytania;
- 4–6 kandydatów z ceną, podobieństwami, różnicami i kompromisem;
- wybór produktu lub prostego kierunku dalszego wyszukiwania;
- pobranie albo użycie przygotowanego zestawu ofert;
- kontrola dokładnego wariantu;
- oddzielne składowe oceny produktu, oferty i sprzedawcy w zakresie dostępnych danych;
- sygnały ryzyka oraz jawne oznaczenie danych nieznanych;
- co najmniej trzy oferty z linkami, źródłami i czasem pozyskania;
- rekomendacja jednej opcji z czytelnym uzasadnieniem;
- stabilny scenariusz od krótkiego promptu do decyzji.

### Should have, jeśli zostanie czas

- porównanie ceny używanej z nowym produktem;
- opinie, gwarancja i zwrot pozyskane z realnego źródła;
- zmiana kierunku rankingu bez ponownego pobierania danych;
- porównanie więcej niż jednego modelu w pełnym etapie;
- zapis researchu i ofert do ponownego użycia;
- drugi adapter źródła, np. eBay, jeśli nie opóźni demo.

### Poza zakresem MVP

- pełne pokrycie wszystkich kategorii elektroniki;
- własna kompletna baza urządzeń;
- niezawodne skrapowanie wielu platform w czasie rzeczywistym;
- ręczne ustawianie rozbudowanych wag każdego kryterium;
- zakupy lub płatności w aplikacji;
- długoterminowe uczenie preferencji wszystkich użytkowników;
- perfekcyjne wykrywanie oszustw, fałszywek lub stanu baterii;
- podobieństwo wizualne na podstawie zdjęcia;
- zaawansowany model uczenia maszynowego, jeśli jawny scoring wystarczy.

## 8. Logika rekomendacji

### Ocena produktu

- podobieństwo do produktu referencyjnego;
- zgodność z budżetem, zastosowaniem i wymaganymi funkcjami;
- jakość, funkcjonalność i bateria;
- preferencje miękkie, np. marka, kolor lub wygląd;
- naprawialność i dostępność części;
- dostępność na rynku wtórnym;
- jakość oraz wiarygodność opinii.

### Ocena oferty

- cena względem typowej ceny właściwego wariantu;
- deklarowany stan i kompletność informacji;
- oryginalność produktu lub części, jeśli można ją zweryfikować;
- zgodność wariantu, np. generacji, koloru lub wersji;
- gwarancja, zwrot, dostawa i lokalizacja;
- aktualność oraz dostępność;
- sygnały ryzyka i dane nieznane.

### Ocena sprzedawcy lub źródła

- zweryfikowane opinie i ich liczba;
- historia lub liczba sprzedaży;
- warunki reklamacji i odpowiedzialność sprzedawcy;
- wiarygodność źródła i spójność informacji.

Na hackathon wystarczy przejrzysty scoring ważony. Użytkownik powinien widzieć trzy składowe oraz ludzkie uzasadnienie, nie jedną pozornie precyzyjną liczbę. Brak danych nie może być automatycznie traktowany jako pozytywny sygnał.

## 9. Założenia techniczne MVP

- model językowy interpretuje intencję, identyfikuje wzorzec, porządkuje wymagania i generuje wyjaśnienia;
- kod aplikacji kontroluje źródła, cache, twarde filtry, warianty i scoring;
- wszystkie fakty produktowe i ofertowe przechowują źródło oraz czas pozyskania;
- dane ofert pochodzą z jednego działającego źródła albo kontrolowanego zestawu demonstracyjnego;
- warstwa źródeł jest oddzielona od logiki rekomendacji;
- aplikacja przechowuje etap sesji, produkt referencyjny, wybrany kierunek i preferencje;
- pierwszy etap używa małej liczby kandydatów, a kosztowna analiza rusza dopiero po zawężeniu;
- wyniki mogą być buforowane, ale cache nie może blokować ukończenia głównego scenariusza;
- backend demo działa lokalnie i korzysta z zewnętrznych API bez wymagania pełnej infrastruktury chmurowej;
- gdy dane są niepełne lub sprzeczne, API zwraca poziom pewności lub listę braków.

## 10. Kryteria ukończenia

MVP jest gotowe, gdy podczas demo można bez ręcznego omijania błędów:

1. wpisać „coś jak AirPods Pro, ale taniej” albo ogólną potrzebę;
2. otrzymać maksymalnie trzy trafne pytania doprecyzowujące;
3. zobaczyć co najmniej cztery sensowne modele z ceną, podobieństwami i kompromisami;
4. wybrać model lub kierunek rekomendacji;
5. otrzymać co najmniej trzy konkretne oferty właściwego wariantu;
6. zobaczyć oddzielną ocenę produktu, oferty i sprzedawcy w zakresie dostępnych danych;
7. zobaczyć rekomendację, źródła, czas pozyskania, ryzyka i braki danych;
8. przejść linkiem do oferty;
9. zmienić jeden priorytet bez utraty całego kontekstu.

## 11. Metryki sukcesu prototypu

- użytkownik dochodzi od pierwszego promptu do rekomendacji w mniej niż 3 minuty;
- liczba niezbędnych pytań nie przekracza 3;
- pierwsza lista zawiera cenę i co najmniej jedną różnicę względem wzorca;
- każda finalna rekomendacja zawiera „dlaczego tak”, kompromis, ryzyko i źródło;
- niewłaściwy wariant nie trafia do finalnego rankingu;
- system jawnie oznacza brak danych zamiast tworzyć niepotwierdzone fakty;
- cały happy path działa powtarzalnie podczas prezentacji;
- jury rozumie po jednym zdaniu różnicę względem chatbota i porównywarki cen.

## 12. Scenariusz demo

> Chcę słuchawki podobne do AirPods Pro, z dobrym ANC, ale tańsze i niekoniecznie Apple.

Agent identyfikuje wzorzec, pokazuje 4–6 alternatyw z cenami, podobieństwami i różnicami. Użytkownik wybiera „najlepszy stosunek ceny do jakości”. System wyszukuje konkretne używane oferty, sprawdza warianty i pokazuje oddzielnie dopasowanie produktu, jakość oferty oraz wiarygodność sprzedawcy. Następnie użytkownik mówi: „ważniejsza jest gwarancja niż najniższa cena”, a ranking aktualizuje się bez utraty kontekstu.

## 13. Najważniejsza decyzja produktowa

Najpierw dowozimy jeden kompletny przepływ dla słuchawek i jednego rozpoznawalnego produktu referencyjnego. Wiarygodna demonstracja przejścia od „coś jak ten produkt, ale lepiej dla mnie” do konkretnej oferty jest ważniejsza niż szerokość katalogu, liczba źródeł i złożoność algorytmu.
