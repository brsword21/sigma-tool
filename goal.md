# Goal v3: agent zakupowy do używanej elektroniki

## 0. Priorytet wymagań

Podstawą produktu jest `brainstorm.md`: agent do używanych słuchawek, który zaczyna od potrzeby lub produktu referencyjnego i już w pierwszej odpowiedzi pokazuje trzy najlepsze propozycje produktów. Pierwsza propozycja jest aktualnie najlepsza, a pogłębiony research działa w tle i ulepsza wynik po potwierdzeniu lub korekcie cech.

Z case'u „AI Shopping Assistant” przyjmujemy wyłącznie brakujące elementy zgodne z tym kierunkiem:

- dokładniejsze rozpoznawanie tego samego produktu i wariantu;
- koszt końcowy zamiast samej ceny ogłoszenia;
- wykrywanie bait listings, pozornych promocji i nieaktualnych ofert;
- deterministyczny zestaw pułapek oraz mierzalne testy jakości;
- audytowalne źródła, obliczenia i powody decyzji.

Po ustaleniu dokładnego produktu agent uruchamia ciągły monitoring ofert. Najlepsza zweryfikowana oferta generuje alert w interfejsie i przygotowany checkout. Symulowany automatyczny zakup jest dozwolony wyłącznie wtedy, gdy użytkownik jawnie zatwierdził jego warunki; w przeciwnym razie oferta jest eskalowana do użytkownika.

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
- Pierwsza odpowiedź zawiera dokładnie trzy propozycje produktów, a najlepsza jest pokazana jako pierwsza.
- Orientacyjna cena, najważniejsze cechy, różnice i kompromisy są widoczne od razu.
- Pogłębiony research działa w tle i może aktualizować propozycje bez osobnego, sztucznego przejścia między etapami.
- Po pierwszej iteracji czat prosi o potwierdzenie albo korektę odczytanych cech.
- W finalnych ofertach cena oznacza znany koszt końcowy; brakujące opłaty są jawnie oznaczone.
- Po zatwierdzeniu produktu agent monitoruje oferty, a nowe zdarzenia są dostępne jako JSON do odpytywania przez interfejs.
- Jedna okazja generuje jeden istotny alert, nie serię powtarzalnych komunikatów.
- Wyraźne komunikowanie źródeł, braków danych i niepewności.

## 6. Główny przebieg użytkownika

### Jedna progresywna sesja

1. Użytkownik opisuje potrzebę, produkt referencyjny i opcjonalnie warunki przyszłego automatycznego zakupu.
2. Agent identyfikuje produkt, jego charakterystyczne cechy, budżet i priorytety.
3. Pierwszy research korzysta z realnego źródła i od razu zwraca trzy propozycje produktów z orientacyjną ceną, cechami, różnicami i kompromisem. Najlepsza propozycja jest pierwsza.
4. Ta sama operacja zwraca `run_id`; pogłębiony research działa w tle i może doprecyzować ceny, cechy oraz kolejność.
5. Czat prosi użytkownika o potwierdzenie odczytanych cech albo ich korektę. Nie wymaga osobnego wyboru kierunku, jeśli pierwsza propozycja jest zaakceptowana.
6. Po ustaleniu dokładnego produktu agent uruchamia hunt monitorujący konkretne oferty.
7. Każdy cykl normalizuje tożsamość produktu i wariant, liczy koszt końcowy oraz sprawdza aktualność, stock, sprzedawcę, zwrot, gwarancję i sygnały ryzyka.
8. Monitoring początkowo korzysta z realnie pobranych ofert, a dalsze zdarzenia demo są deterministyczne i odtwarzalne.
9. Nowa najlepsza zweryfikowana oferta tworzy jeden alert oraz przygotowany checkout.
10. Bez jawnego mandatu alert ma stan `awaiting_user`; użytkownik zatwierdza symulowany zakup.
11. Przy jawnie zatwierdzonych warunkach automatycznego zakupu agent może wykonać symulację w tle, ale wyłącznie w ramach hard capów i wcześniejszych priorytetów.
12. Niepewna albo najlepsza oferta poza mandatem jest eskalowana do użytkownika w interfejsie.
13. Każda decyzja, alert, checkout i symulowany zakup otrzymują receipt z pełnym uzasadnieniem oraz obliczeniami.

## 7. Zakres MVP na hackathon

### Must have

- interfejs rozmowy z zachowaniem kontekstu;
- obsługa jednej kategorii demonstracyjnej — słuchawek;
- dwa wejścia: potrzeba użytkownika oraz nazwa produktu referencyjnego;
- identyfikacja produktu referencyjnego i jego najważniejszych cech;
- automatyczne wnioskowanie preferencji oraz maksymalnie trzy pytania;
- dokładnie trzy pierwsze propozycje produktów z orientacyjną ceną, podobieństwami, różnicami i kompromisem;
- najlepsza aktualna propozycja pokazana jako pierwsza;
- `run_id` i pogłębiony research działający w tle bez blokowania pierwszej odpowiedzi;
- potwierdzenie lub korekta cech produktu po pierwszej iteracji;
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
- ciągły hunt uruchamiany po zatwierdzeniu dokładnego produktu;
- realne pobranie początkowe i deterministyczne kolejne zdarzenia w scenariuszu demo;
- endpoint JSON do odpytywania o nowe alerty i zmianę stanu huntu;
- dokładnie jeden alert dla tej samej okazji i wersji warunków;
- przygotowany, symulowany checkout;
- jawnie zatwierdzony standing mandate z hard capami, priorytetami i możliwością odwołania;
- symulowany zakup w tle wyłącznie w ramach aktywnego mandatu;
- eskalacja najlepszej oferty do użytkownika, jeśli nie podlega automatycznemu zakupowi;
- receipt dla alertu, checkoutu i symulowanego zakupu;
- stabilny scenariusz od krótkiego promptu do decyzji.

### Should have, jeśli zostanie czas

- porównanie ceny używanej z nowym produktem;
- opinie, gwarancja i zwrot pozyskane z realnego źródła;
- zmiana kierunku rankingu bez ponownego pobierania danych;
- porównanie więcej niż jednego modelu w pełnym etapie;
- zapis researchu i ofert do ponownego użycia;
- adapter powiadomień e-mail wykorzystujący ten sam kontrakt co alert w interfejsie;
- produkcyjny scheduler zamiast kontrolowanych ticków demo;
- drugi adapter źródła, np. eBay, jeśli nie opóźni demo.

### Poza zakresem MVP

- pełne pokrycie wszystkich kategorii elektroniki;
- własna kompletna baza urządzeń;
- niezawodne skrapowanie wielu platform w czasie rzeczywistym;
- ręczne ustawianie rozbudowanych wag każdego kryterium;
- rzeczywiste obciążenie karty lub konta;
- integracja produkcyjnego PSP;
- rzeczywisty zakup na zewnętrznym marketplace;
- produkcyjnie niezawodne monitorowanie wszystkich sklepów;
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
- pierwsza odpowiedź zwraca trzy aktualnie najlepsze produkty, a kosztowniejszy research kontynuuje pracę w tle pod tym samym `run_id`;
- wyniki mogą być buforowane, ale cache nie może blokować ukończenia głównego scenariusza;
- po potwierdzeniu produktu powstaje trwały hunt z kontrolowanymi tickami monitoringu;
- początkowy snapshot ofert pochodzi z realnego źródła, a kolejne zdarzenia demo są deterministyczne;
- alerty są przechowywane jako JSON i udostępniane przez polling; wysyłka używa interfejsu providerów, aby później dodać e-mail;
- standing mandate jest osobnym, wersjonowanym i odwoływalnym obiektem, a nie polem wywnioskowanym przez LLM;
- symulowany zakup działa jako idempotentna funkcja w tle i ponownie sprawdza hard capy bezpośrednio przed wykonaniem;
- brak jawnego mandatu zawsze prowadzi do alertu i stanu oczekującego na decyzję użytkownika;
- backend demo działa lokalnie i korzysta z zewnętrznych API bez wymagania pełnej infrastruktury chmurowej;
- gdy dane są niepełne lub sprzeczne, API zwraca poziom pewności lub listę braków;
- rekomendacja przechowuje snapshot wymagań, dowody dopasowania wariantu, rozbicie kosztu końcowego i powody odrzucenia ofert.

## 10. Kryteria ukończenia

MVP jest gotowe, gdy podczas demo można bez ręcznego omijania błędów:

1. wpisać „coś jak AirPods Pro, ale taniej” albo ogólną potrzebę;
2. otrzymać maksymalnie trzy trafne pytania doprecyzowujące;
3. natychmiast zobaczyć trzy sensowne modele z orientacyjną ceną, podobieństwami i kompromisami oraz wskazaniem aktualnie najlepszego;
4. otrzymać `run_id`, a następnie zobaczyć doprecyzowany wynik pogłębionego researchu;
5. potwierdzić albo poprawić cechy bez rozpoczynania osobnego przepływu;
6. uruchomić monitoring zatwierdzonego produktu;
7. otrzymać co najmniej trzy konkretne oferty właściwego wariantu;
8. zobaczyć znany koszt końcowy i jego składowe zamiast samej ceny ogłoszenia;
9. zobaczyć odrzucenie co najmniej jednej oferty z niewłaściwym wariantem, nieaktualnością albo sygnałem bait listing;
10. zobaczyć oddzielną ocenę produktu, oferty i sprzedawcy w zakresie dostępnych danych;
11. otrzymać jeden alert JSON z przygotowanym checkoutem dla najlepszej oferty;
12. bez mandatu zatwierdzić symulowany zakup ręcznie, a z mandatem zobaczyć jego wykonanie w tle;
13. zobaczyć receipt, źródła, obliczenia, ryzyka i użyte warunki mandatu;
14. zmienić priorytet lub odwołać mandat bez utraty kontekstu.

## 11. Metryki sukcesu prototypu

- użytkownik dochodzi od pierwszego promptu do rekomendacji w mniej niż 3 minuty;
- liczba niezbędnych pytań nie przekracza 3;
- pierwsza odpowiedź zawiera dokładnie trzy propozycje, orientacyjną cenę i co najmniej jedną różnicę względem wzorca;
- aktualnie najlepszy produkt jest dostępny przed zakończeniem pogłębionego researchu;
- każda finalna rekomendacja zawiera „dlaczego tak”, kompromis, ryzyko i źródło;
- niewłaściwy lub niepotwierdzony wariant nie trafia do Top 3;
- budżet jest sprawdzany względem znanego kosztu końcowego;
- kontrolowany bait listing nie trafia do Top 3;
- obliczenia kosztu końcowego przechodzą testy graniczne dokładnie na budżecie i o 0,01 powyżej;
- system jawnie oznacza brak danych zamiast tworzyć niepotwierdzone fakty;
- raport testowy pokazuje precision Top 3, variant-error rate i bait-rejection rate;
- ta sama okazja generuje dokładnie jeden alert;
- żaden symulowany zakup nie przekracza hard capu ani nie odbywa się bez jawnego, aktywnego mandatu;
- wszystkie przypadki bez mandatu są eskalowane do użytkownika;
- false-buy rate kontrolowanego scenariusza wynosi zero;
- cały happy path działa powtarzalnie podczas prezentacji;
- jury rozumie po jednym zdaniu różnicę względem chatbota i porównywarki cen.

## 12. Scenariusz demo

> Chcę słuchawki podobne do AirPods Pro, z dobrym ANC, ale tańsze i niekoniecznie Apple.

Agent identyfikuje wzorzec i natychmiast pokazuje trzy propozycje z orientacyjnymi cenami, ustawiając aktualnie najlepszą jako pierwszą. W tle kontynuuje pogłębiony research. Czat prosi o potwierdzenie odczytanych cech; użytkownik doprecyzowuje, że gwarancja jest ważniejsza niż najniższa cena. Wynik aktualizuje się bez resetu. Po zatwierdzeniu produktu agent tworzy hunt. Początkowe oferty pochodzą z realnego źródła, a kolejne zdarzenia demo są deterministyczne. Agent odrzuca zły wariant i ofertę przekraczającą budżet po doliczeniu dostawy. Najlepsza zweryfikowana oferta tworzy jeden alert JSON i checkout. Bez mandatu użytkownik zatwierdza symulowany zakup; przy wcześniej jawnie zatwierdzonych warunkach symulacja wykonuje się w tle. Receipt pokazuje pełny koszt, źródła, powód decyzji i użyte priorytety.

## 13. Najważniejsza decyzja produktowa

Dowozimy jeden kompletny, progresywny przepływ dla słuchawek: trzy natychmiastowe propozycje, pogłębiony research w tle, potwierdzenie cech, monitoring wybranego produktu, jeden alert, przygotowany checkout i bezpieczny symulowany zakup. Rzeczywiste płatności i produkcyjny zakup pozostają poza MVP.
