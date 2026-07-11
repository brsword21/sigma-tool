# Burza mózgów przed hackathonem — scalone ustalenia

## Kontekst

Zespół szuka produktu możliwego do pokazania podczas hackathonu. Pierwszy brainstorm wskazał używaną elektronikę i dwuetapowy agentowy proces zakupowy. Drugi doprecyzował główny przypadek użycia: użytkownik może wskazać produkt referencyjny i poprosić o podobną, tańszą lub lepiej dopasowaną alternatywę. Poniższy dokument scala oba spotkania i rozdziela decyzje MVP od późniejszej roadmapy.

## Key takeaways z brainstormu 2

1. **Produkt referencyjny staje się ważnym punktem wejścia.** Użytkownik może napisać „coś jak AirPods Pro, ale taniej”, zamiast znać parametry techniczne.
2. **Minimalny wysiłek użytkownika jest nadrzędną zasadą UX.** System sam identyfikuje wzorzec, wnioskuje priorytety i pyta tylko o brakujące informacje, które realnie zmieniają wynik.
3. **Cena musi być widoczna od pierwszej listy kandydatów.** Wstępne propozycje służą wyborowi kierunku, ale powinny być ocenialne ekonomicznie.
4. **Wyszukiwanie pozostaje dwuetapowe.** Najpierw ograniczony, tani research kandydatów, a po doprecyzowaniu preferencji pełniejsze porównanie produktów i konkretnych ofert.
5. **Ranking należy rozdzielić na trzy warstwy:** dopasowanie produktu, jakość konkretnej oferty oraz wiarygodność sprzedawcy lub źródła.
6. **Specyfikacja i cena nie wystarczą.** Rekomendacja powinna uwzględniać m.in. opinie, gwarancję, zwrot, stan, baterię, oryginalność części, naprawialność, aktualność i dokładny wariant.
7. **Nie budujemy kompletnej bazy elektroniki na potrzeby demo.** Korzystamy z danych pozyskanych z istniejących źródeł i kontrolujemy liczbę zapytań oraz koszt modeli.
8. **Demo pozostaje wąskie.** Jedna kategoria i jeden mocny scenariusz mają pierwszeństwo przed wieloma kategoriami, źródłami i pełną uniwersalnością.
9. **Niepewność jest częścią wyniku.** Brak danych, sprzeczne informacje lub nieweryfikowalne deklaracje muszą być jawnie komunikowane, a nie maskowane pewnym językiem.

## 1. Problem i wybrany rynek

Punktem wyjścia był rosnący rynek rzeczy używanych i presja na oszczędzanie. Moda została odrzucona jako pierwsza kategoria dla agenta, ponieważ wybór jest silnie wizualny, subiektywny i oparty na przyjemności przeglądania katalogu.

Elektronika jest lepszym punktem wejścia, ponieważ:

- użytkownicy często nie znają modeli ani znaczenia parametrów;
- potrzeby można opisać przez budżet, zastosowanie i oczekiwane cechy;
- decyzja wymaga researchu, który użytkownik chętnie deleguje;
- rynek wtórny jest rozproszony i bardziej ryzykowny niż zakup nowego produktu;
- istniejące porównywarki koncentrują się głównie na nowych produktach.

Roboczą kategorią pozostaje używana elektronika użytkowa, a rekomendowaną kategorią demonstracyjną są słuchawki.

## 2. Dwa równorzędne punkty wejścia

Użytkownik może rozpocząć rozmowę na dwa sposoby:

1. **Od potrzeby:** „Szukam wygodnych słuchawek z ANC do 500 zł”.
2. **Od produktu referencyjnego:** „Chcę coś podobnego do AirPods Pro, ale taniej i niekoniecznie Apple”.

Obie ścieżki prowadzą do tego samego rezultatu: krótkiej listy produktów dopasowanych do potrzeb, a następnie rankingu konkretnych ofert. Produkt referencyjny jest skrótem opisującym oczekiwany poziom jakości, funkcje, wygląd lub doświadczenie, a nie sztywnym wymaganiem marki.

## 3. Docelowy przepływ użytkownika

### Etap 1: rozpoznanie intencji

- Agent rozpoznaje potrzebę albo identyfikuje produkt referencyjny.
- Pobiera lub odczytuje jego podstawowe cechy, typową cenę, zastosowanie i charakterystyczne funkcje.
- Automatycznie wnioskuje prawdopodobne priorytety użytkownika.
- Zadaje najwyżej jedno pytanie naraz i tylko wtedy, gdy odpowiedź istotnie zmieni rekomendację.

### Etap 2: szybkie wyszukanie kandydatów

- System wykonuje ograniczoną liczbę zapytań, docelowo około 10 dla demo.
- Pokazuje 4–6 kandydatów z nazwą lub zdjęciem, orientacyjną ceną, podobieństwami, różnicami, uzasadnieniem i głównym kompromisem.
- Lista jest wyraźnie oznaczona jako etap wyboru kierunku, a nie ostateczna rekomendacja.
- Cena jest pokazywana od początku.

### Etap 3: szybkie doprecyzowanie

Użytkownik wybiera kierunek za pomocą prostych opcji, np.:

- najbardziej podobny;
- najlepsza jakość;
- najniższa cena;
- najlepszy stosunek ceny do jakości;
- priorytet baterii, ANC, marki, gwarancji lub opinii.

Zmiana pojedynczej preferencji nie resetuje rozmowy ani wcześniejszego researchu.

### Etap 4: pełne porównanie

Po wyborze kierunku system dokładniej analizuje wybrane modele i konkretne oferty. Normalizuje dane, odrzuca niezgodne warianty, ocenia ryzyko i zwraca krótki ranking wraz ze źródłami oraz informacją o niepewności.

## 4. Zasady UX

- Jak najmniej pracy po stronie użytkownika.
- Jedna spójna rozmowa lub jeden ciągły ekran, bez fałszywego poczucia zakończenia po pierwszej liście.
- Zachowanie kontekstu i możliwość korekty jednej cechy.
- Proste wybory zamiast rozbudowanego formularza wag.
- Aktywny agent, ale maksymalnie trzy pytania doprecyzowujące w całej sesji.
- Krótkie listy i czytelne kompromisy zamiast setek wyników.
- Wyraźne oddzielenie faktów, wniosków i informacji niepewnych.

## 5. Model oceny

### Dopasowanie produktu

- podobieństwo do produktu referencyjnego;
- zgodność z zastosowaniem i wymaganymi funkcjami;
- jakość wykonania i funkcjonalność;
- bateria;
- marka, wygląd i inne preferencje miękkie;
- naprawialność oraz dostępność części;
- dostępność na rynku wtórnym;
- cena właściwego wariantu.

### Jakość oferty

- cena względem rynku;
- deklarowany i możliwy do potwierdzenia stan;
- kompletność opisu i zdjęć;
- oryginalność produktu i części;
- dokładność wariantu, np. generacji, koloru lub pamięci;
- gwarancja i możliwość zwrotu;
- aktualność i dostępność;
- dostawa lub lokalizacja;
- jawne sygnały ryzyka i braki danych.

### Wiarygodność sprzedawcy lub źródła

- zweryfikowane opinie i ich liczba;
- historia lub liczba sprzedaży;
- wiarygodność sklepu albo sprzedawcy;
- odpowiedzialność sprzedawcy i warunki reklamacji;
- spójność informacji pomiędzy źródłami.

W MVP wystarczy jawny scoring ważony. Ocena produktu nie może być mieszana w jedną nieczytelną liczbę z oceną ogłoszenia i sprzedawcy; interfejs powinien pokazać trzy składowe oraz ludzkie uzasadnienie.

## 6. Dane i źródła

Nie istnieje jedna kompletna, darmowa baza urządzeń i ofert. Demo nie będzie takiej bazy budować. Dane produktowe i ofertowe mają pochodzić z istniejących stron, producentów, sklepów, porównywarek lub marketplace'ów.

Ustalenia:

- pierwszy przepływ może działać na jednym stabilnym źródle lub kontrolowanym zestawie danych;
- eBay jest kandydatem do późniejszej integracji ze względu na dostęp do API, ale nie może blokować demo;
- każde nowe źródło wymaga weryfikacji regulaminu, stabilności i zakresu danych;
- dane z wielu źródeł muszą być normalizowane do wspólnego modelu;
- wyniki researchu i pobrane oferty można buforować w Supabase;
- pełne przeszukiwanie uruchamia się dopiero po wyborze kierunku;
- system przechowuje źródło, czas pobrania i poziom pewności danych.

## 7. Pozycjonowanie produktu

Produkt nie jest kolejną porównywarką cen ani zwykłym chatbotem. Łączy:

- zrozumienie nieprecyzyjnej potrzeby;
- użycie znanego produktu jako wzorca;
- znalezienie podobnej, tańszej lub lepiej dopasowanej alternatywy;
- wybór modelu i konkretnej sztuki na rynku wtórnym;
- ocenę produktu, oferty i sprzedawcy;
- aktywną rozmowę z pamięcią kontekstu;
- uzasadnienie rekomendacji i komunikowanie ryzyka.

Najbardziej zapamiętywalny komunikat dla jury: **„Powiedz, co Ci się podoba, a agent znajdzie podobną, tańszą i bezpieczniejszą opcję na rynku wtórnym.”**

## 8. Decyzje produktowe

1. Demo obsługuje jedną kategorię — słuchawki.
2. Wiodącym produktem referencyjnym są AirPods Pro lub równoważny, łatwo rozpoznawalny model.
3. Obsługujemy wejście od potrzeby i od produktu referencyjnego.
4. Przepływ pozostaje dwuetapowy: tani research kandydatów, potem pełna analiza ofert.
5. Pierwsza lista pokazuje ceny i nie jest przedstawiana jako wynik ostateczny.
6. Agent automatycznie wnioskuje preferencje i ogranicza liczbę pytań.
7. Ranking rozdziela dopasowanie produktu, ofertę i sprzedawcę.
8. Opinie, gwarancja, zwrot, dokładny wariant oraz niepewność danych są istotnymi sygnałami.
9. Backend demo działa lokalnie i korzysta z zewnętrznych API lub kontrolowanych danych.
10. Kompletna baza urządzeń, wiele kategorii i zaawansowany model rankingu nie są wymagane do demo.

## 9. Minimalny zakres MVP

MVP powinno:

- przyjąć nazwę produktu referencyjnego lub opis potrzeby;
- rozpoznać kategorię, wzorzec i krótką preferencję;
- pobrać podstawowy opis produktu referencyjnego wraz ze źródłami;
- wywnioskować priorytety i zadać tylko konieczne pytanie;
- znaleźć 4–6 podobnych produktów;
- od początku pokazać orientacyjną cenę, podobieństwa i różnice;
- pozwolić użytkownikowi wybrać kierunek dalszego wyszukiwania;
- znaleźć co najmniej trzy konkretne oferty dla wybranego kierunku;
- sprawdzić dokładny wariant;
- oddzielnie ocenić produkt, ofertę i wiarygodność sprzedawcy na podstawie dostępnych danych;
- pokazać ryzyka, niepewność, źródła i rekomendację z uzasadnieniem;
- zachować kontekst po zmianie jednej preferencji.

## 10. Pomysły po MVP

- porównanie wielu marketplace'ów i sklepów;
- dedykowany adapter eBay;
- podobieństwo wizualne na podstawie zdjęcia;
- trwała baza wiedzy i ponowne użycie wcześniejszych researchów;
- historia cen oraz wykrywanie okazji;
- personalizowane wagi i długoterminowa pamięć preferencji;
- wiele kategorii elektroniki;
- zaawansowane wykrywanie fałszywek i oszustw;
- uczenie rankingu na zachowaniu użytkowników;
- powiadomienia o nowych ofertach.

## 11. Otwarte pytania i ryzyka

- Czy finalnym wzorcem demo będą AirPods Pro i który dokładnie wariant?
- Czy pierwsze propozycje są wyłącznie etapem eksploracji, czy także wejściem do rankingu produktu?
- Jak zdefiniować podobieństwo dla słuchawek i które cechy są twarde?
- Jakie dane o opiniach, gwarancji, zwrotach i historii sprzedawcy faktycznie udostępni pierwsze źródło?
- Jak rozróżniać brak danych od negatywnego sygnału?
- Jak potwierdzać oryginalność, stan baterii i części bez fizycznej inspekcji?
- Jak często odświeżać ceny oraz dostępność?
- Czy ręczna zmiana wag jest potrzebna, czy wystarczą proste kierunki wyboru?
- Czy wybrane źródła pozwalają legalnie i stabilnie pobierać dane?
- Jak zagwarantować aktualne źródła i uniknąć halucynowanych faktów?

## 12. Rekomendowany scenariusz demo

> Chcę słuchawki podobne do AirPods Pro, przede wszystkim z dobrym ANC, ale tańsze i niekoniecznie Apple.

Agent identyfikuje produkt referencyjny, pokazuje 4–6 alternatyw z orientacyjną ceną, podobieństwami i kompromisami. Użytkownik wybiera „najlepszy stosunek ceny do jakości”. System pobiera konkretne oferty, oddzielnie pokazuje dopasowanie modelu, jakość oferty i wiarygodność sprzedawcy, rekomenduje jedną opcję oraz zaznacza braki danych. Następnie użytkownik mówi: „ważniejsza jest gwarancja niż najniższa cena”, a ranking aktualizuje się bez resetowania rozmowy.

Najważniejszy efekt demo: krótka wiadomość użytkownika uruchamia zrozumiały proces prowadzący do kilku wiarygodnych i dobrze porównanych ofert, bez ręcznego definiowania wielu parametrów.
