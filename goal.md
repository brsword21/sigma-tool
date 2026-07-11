# Goal v3: agent zakupowy do używanej elektroniki

## 0. Priorytet wymagań

Podstawą produktu jest `brainstorm.md`: dwuetapowy agent zakupowy do używanych słuchawek, który zaczyna od potrzeby lub produktu referencyjnego, pomaga wybrać model, a następnie porównuje konkretne oferty.

Z case'u „AI Shopping Assistant” przyjmujemy wyłącznie brakujące elementy zgodne z tym kierunkiem:

- dokładniejsze rozpoznawanie tego samego produktu i wariantu;
- koszt końcowy zamiast samej ceny ogłoszenia;
- wykrywanie bait listings, pozornych promocji i nieaktualnych ofert;
- deterministyczny zestaw pułapek oraz mierzalne testy jakości;
- audytowalne źródła, obliczenia i powody decyzji.

Monitoring okazji, standing mandate, delegowana płatność i automatyczny zakup nie należą do MVP. Mogą być rozważone dopiero po ukończeniu podstawowego przepływu.

## 1. Cel produktu

W ciągu 6 godzin budujemy działający prototyp agenta zakupowego, który pomaga osobie nieznającej się na elektronice przejść od krótkiej potrzeby lub znanego produktu referencyjnego do konkretnej, uzasadnionej i możliwie bezpiecznej decyzji zakupowej na rynku wtórnym.

Agent powinien:

1. zrozumieć potrzebę albo zidentyfikować wskazany produkt referencyjny;
2. znaleźć produkty podobne, tańsze lub lepiej dopasowane do priorytetów użytkownika;
3. potwierdzić tożsamość i dokładny wariant produktu mimo niejednolitych tytułów ofert;
4. oddzielnie ocenić dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy;
5. porównać koszt końcowy, a nie tylko cenę ogłoszenia;
6. odrzucić nieaktualne, zwodnicze lub nieweryfikowalne oferty;
7. wskazać najlepszy zakup wraz ze źródłami, obliczeniami, kompromisami i poziomem niepewności.

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
- rozpoznawać ten sam produkt mimo skrótów, aliasów i brakujących identyfikatorów;
- doliczać dostawę oraz dostępne obowiązkowe opłaty do ceny ogłoszenia;
- oceniać stan, oryginalność, baterię, możliwość naprawy i kompletność oferty;
- sprawdzać opinie, gwarancję, zwrot i wiarygodność sprzedawcy;
- rozpoznawać nieaktualne, źle opisane lub podejrzane oferty;
- nie dać się zwieść bait listingom ani pozornym promocjom dotyczącym innego wariantu.

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

**Powiedz, czego potrzebujesz albo co Ci się podoba. Agent znajdzie podobne, lepiej dopasowane produkty i wskaże używaną ofertę, którą warto rozważyć — po sprawdzeniu wariantu, kosztu końcowego i dostępnych sygnałów ryzyka.**

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
- Możliwość potwierdzenia albo poprawienia kierunku przed pełnym pobieraniem ofert.
- W finalnych ofertach cena oznacza znany koszt końcowy; brakujące opłaty są jawnie oznaczone.
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
3. Normalizuje cenę, stan, tożsamość produktu, wariant, lokalizację, dostawę, gwarancję, zwrot, sprzedawcę, opis, link i czas aktualizacji — o ile dane są dostępne.
4. Klasyfikuje dopasowanie jako `exact_match`, `possible_match` albo `mismatch`; tylko potwierdzony wariant może wejść do finalnego rankingu.
5. Oblicza znany koszt końcowy: cenę, dostawę i obowiązkowe opłaty, a przy ofertach zagranicznych także dostępne FX, cło/podatki i ważny kupon.
6. Sprawdza aktualność, dostępność oraz dostępne sygnały bait listing, pozornej promocji i niewiarygodnego sprzedawcy.
7. Odrzuca oferty niespełniające twardych wymagań, dotyczące niewłaściwego wariantu albo zawierające krytyczną sprzeczność.
8. Oddzielnie ocenia produkt, ofertę i wiarygodność sprzedawcy.
9. Pokazuje krótki ranking 3–5 najlepszych ofert z jedną wyróżnioną rekomendacją; dla każdej wskazuje koszt końcowy, zalety, kompromisy, ryzyka, źródła i braki danych.

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
- kontrola tożsamości produktu i dokładnego wariantu, również przy niejednolitych tytułach;
- klasyfikacja `exact_match`, `possible_match` i `mismatch`;
- obliczenie znanego kosztu końcowego z ceną, dostawą i dostępnymi obowiązkowymi opłatami;
- wykrywanie nieaktualnej oferty, bait listing i podejrzanej promocji w zakresie danych dostępnych w MVP;
- oddzielne składowe oceny produktu, oferty i sprzedawcy w zakresie dostępnych danych;
- sygnały ryzyka oraz jawne oznaczenie danych nieznanych;
- co najmniej trzy oferty z linkami, źródłami i czasem pozyskania;
- rekomendacja jednej opcji z czytelnym uzasadnieniem;
- kontrolowany zestaw ofert zawierający poprawne wyniki i pułapki;
- mierzalny test, w którym niewłaściwy wariant nie trafia do Top 3;
- stabilny scenariusz od krótkiego promptu do decyzji.

### Should have, jeśli zostanie czas

- porównanie ceny używanej z nowym produktem;
- opinie, gwarancja i zwrot pozyskane z realnego źródła;
- zmiana kierunku rankingu bez ponownego pobierania danych;
- porównanie więcej niż jednego modelu w pełnym etapie;
- zapis researchu i ofert do ponownego użycia;
- historia ceny wystarczająca do odróżnienia realnej obniżki od niepotwierdzonej „starej ceny”;
- zapisane wyszukiwanie i jedno istotne powiadomienie o okazji;
- drugi adapter źródła, np. eBay, jeśli nie opóźni demo.

### Poza zakresem MVP

- pełne pokrycie wszystkich kategorii elektroniki;
- własna kompletna baza urządzeń;
- niezawodne skrapowanie wielu platform w czasie rzeczywistym;
- ręczne ustawianie rozbudowanych wag każdego kryterium;
- zakupy lub płatności w aplikacji;
- standing mandate, delegowana płatność i automatyczny zakup;
- ciągłe monitorowanie wszystkich sklepów jako wymaganie ukończenia MVP;
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

- koszt końcowy względem budżetu i typowej ceny właściwego wariantu;
- cena bazowa, dostawa oraz dostępne obowiązkowe opłaty;
- FX, cło/podatki i ważność kuponu, jeżeli dotyczą oferty i dane są dostępne;
- deklarowany stan i kompletność informacji;
- oryginalność produktu lub części, jeśli można ją zweryfikować;
- zgodność wariantu, np. generacji, koloru lub wersji;
- gwarancja, zwrot, dostawa i lokalizacja;
- aktualność oraz dostępność;
- sygnały bait listing i pozornej promocji;
- sygnały ryzyka i dane nieznane.

### Ocena sprzedawcy lub źródła

- zweryfikowane opinie i ich liczba;
- historia lub liczba sprzedaży;
- warunki reklamacji i odpowiedzialność sprzedawcy;
- wiarygodność źródła i spójność informacji.

Na hackathon wystarczy przejrzysty scoring ważony. Użytkownik powinien widzieć trzy składowe oraz ludzkie uzasadnienie, nie jedną pozornie precyzyjną liczbę. Brak danych nie może być automatycznie traktowany jako pozytywny sygnał.

Twarda zgodność produktu i wariantu jest sprawdzana przed scoringiem. `possible_match` nie może być automatycznie traktowane jak potwierdzona oferta. Budżet jest sprawdzany względem znanego kosztu końcowego; brak niezbędnej składowej kosztu obniża pewność i musi być pokazany użytkownikowi.

## 9. Założenia techniczne MVP

- model językowy interpretuje intencję, identyfikuje wzorzec, porządkuje wymagania i generuje wyjaśnienia;
- kod aplikacji kontroluje źródła, cache, twarde filtry, warianty, arytmetykę kosztu końcowego, weryfikację i scoring;
- LLM nie może samodzielnie potwierdzić wariantu, wymyślić opłaty ani wykonywać arytmetyki decydującej o budżecie;
- wszystkie fakty produktowe i ofertowe przechowują źródło oraz czas pozyskania;
- dane ofert pochodzą z jednego działającego źródła albo kontrolowanego zestawu demonstracyjnego;
- kontrolowany zestaw demonstracyjny zawiera również błędny wariant, bait listing, podejrzaną promocję, nieaktualną ofertę i brak kosztu dostawy;
- warstwa źródeł jest oddzielona od logiki rekomendacji;
- aplikacja przechowuje etap sesji, produkt referencyjny, wybrany kierunek i preferencje;
- pierwszy etap używa małej liczby kandydatów, a kosztowna analiza rusza dopiero po zawężeniu;
- wyniki mogą być buforowane, ale cache nie może blokować ukończenia głównego scenariusza;
- backend demo działa lokalnie i korzysta z zewnętrznych API bez wymagania pełnej infrastruktury chmurowej;
- gdy dane są niepełne lub sprzeczne, API zwraca poziom pewności lub listę braków;
- rekomendacja przechowuje snapshot wymagań, dowody dopasowania wariantu, rozbicie kosztu końcowego i powody odrzucenia ofert.

## 10. Kryteria ukończenia

MVP jest gotowe, gdy podczas demo można bez ręcznego omijania błędów:

1. wpisać „coś jak AirPods Pro, ale taniej” albo ogólną potrzebę;
2. otrzymać maksymalnie trzy trafne pytania doprecyzowujące;
3. zobaczyć co najmniej cztery sensowne modele z ceną, podobieństwami i kompromisami;
4. wybrać model lub kierunek rekomendacji;
5. otrzymać co najmniej trzy konkretne oferty właściwego wariantu;
6. zobaczyć znany koszt końcowy i jego składowe zamiast samej ceny ogłoszenia;
7. zobaczyć odrzucenie co najmniej jednej oferty z niewłaściwym wariantem, nieaktualnością albo sygnałem bait listing;
8. zobaczyć oddzielną ocenę produktu, oferty i sprzedawcy w zakresie dostępnych danych;
9. zobaczyć rekomendację, źródła, czas pozyskania, ryzyka i braki danych;
10. przejść linkiem do oferty;
11. zmienić jeden priorytet bez utraty całego kontekstu i bez zbędnego ponownego pobrania danych.

## 11. Metryki sukcesu prototypu

- użytkownik dochodzi od pierwszego promptu do rekomendacji w mniej niż 3 minuty;
- liczba niezbędnych pytań nie przekracza 3;
- pierwsza lista zawiera cenę i co najmniej jedną różnicę względem wzorca;
- każda finalna rekomendacja zawiera „dlaczego tak”, kompromis, ryzyko i źródło;
- niewłaściwy lub niepotwierdzony wariant nie trafia do Top 3;
- budżet jest sprawdzany względem znanego kosztu końcowego;
- kontrolowany bait listing nie trafia do Top 3;
- obliczenia kosztu końcowego przechodzą testy graniczne dokładnie na budżecie i o 0,01 powyżej;
- system jawnie oznacza brak danych zamiast tworzyć niepotwierdzone fakty;
- raport testowy pokazuje precision Top 3, variant-error rate i bait-rejection rate;
- cały happy path działa powtarzalnie podczas prezentacji;
- jury rozumie po jednym zdaniu różnicę względem chatbota i porównywarki cen.

## 12. Scenariusz demo

> Chcę słuchawki podobne do AirPods Pro, z dobrym ANC, ale tańsze i niekoniecznie Apple.

Agent identyfikuje wzorzec, pokazuje 4–6 alternatyw z cenami, podobieństwami i różnicami. Użytkownik wybiera „najlepszy stosunek ceny do jakości”. System wyszukuje konkretne używane oferty, potwierdza warianty i oblicza znany koszt końcowy. Oferta z atrakcyjną ceną bazową zostaje odrzucona, ponieważ dotyczy złej generacji albo po doliczeniu dostawy przekracza budżet. Finalny wynik pokazuje oddzielnie dopasowanie produktu, jakość oferty oraz wiarygodność sprzedawcy. Następnie użytkownik mówi: „ważniejsza jest gwarancja niż najniższa cena”, a ranking aktualizuje się bez utraty kontekstu i bez zbędnego pobierania ofert.

## 13. Najważniejsza decyzja produktowa

Najpierw dowozimy jeden kompletny przepływ dla słuchawek i jednego rozpoznawalnego produktu referencyjnego. Wiarygodna demonstracja przejścia od „coś jak ten produkt, ale lepiej dla mnie” do zweryfikowanej oferty właściwego wariantu i z poprawnym kosztem końcowym jest ważniejsza niż szerokość katalogu, liczba źródeł, monitoring cen oraz automatyczny zakup.
