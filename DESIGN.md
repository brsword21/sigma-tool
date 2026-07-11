# Picky — UI Design Direction

## 1. Cel dokumentu

Ten dokument opisuje wizualny charakter, typografię, hierarchię interfejsu i zasady
projektowania aplikacji Picky. Jest wspólnym punktem odniesienia dla designu oraz
implementacji frontendu.

Picky pomaga wybrać używaną elektronikę: od krótkiego opisu potrzeby, przez odkrywanie
pasujących modeli, aż po ocenę konkretnych ofert i sprzedawców. Interfejs łączy dwa
znane modele interakcji:

- **ChatGPT:** spokojna rozmowa, mało elementów na ekranie, ciągłość kontekstu;
- **Tinder:** jedna decyzja naraz, duże karty i szybkie porównywanie propozycji.

Nie kopiujemy wyglądu żadnego z tych produktów. Łączymy ich sposób prowadzenia
użytkownika w niezależny język wizualny Picky.

## 2. Charakter produktu

Picky ma sprawiać wrażenie:

- **czystej** — każdy element ma jedno zadanie;
- **spokojnej** — aplikacja redukuje stres związany z kosztowną decyzją;
- **inteligentnej** — podpowiada następny krok, nie epatując technologią;
- **selektywnej** — pokazuje kilka mocnych propozycji zamiast katalogu wyników;
- **wiarygodnej** — odróżnia fakty, interpretacje, ryzyka i brak danych;
- **dynamicznej** — wybór kart daje poczucie postępu, ale nie przypomina gry.

Docelowe odczucie można streścić jako **„spokojna pewność przy szybkim wyborze”**.
Minimalizm nie oznacza sterylności: charakter budują duże zdjęcia produktów, precyzyjna
typografia, zdecydowany niebieski i płynna zmiana trybu z rozmowy na wybór.

## 3. Główna idea doświadczenia

### Conversation first

Rozmowa jest domyślną osią aplikacji. Użytkownik zaczyna od naturalnego zdania, a Picky
odpowiada krótko i pokazuje tylko informacje potrzebne do następnej decyzji.

Po zrozumieniu potrzeby interfejs płynnie przechodzi do **focus mode**: centralnej talii
kart z propozycjami. Chat nie znika — zwija się do krótkiego podsumowania preferencji,
które można rozwinąć lub skorygować.

Po wyborze kierunku talia zmienia się w uporządkowany ranking konkretnych ofert.
Użytkownik przez cały czas pozostaje w jednej historii, bez wrażenia przechodzenia do
osobnej porównywarki.

```text
Rozmowa → Podsumowanie potrzeb → Karty produktów → Ranking ofert → Decyzja
   ↑                                                        |
   └──────────── korekta preferencji bez resetu ────────────┘
```

Szczegółowa mechanika gestów akceptowania i odrzucania będzie zdefiniowana w osobnym
dokumencie. Ten system powinien traktować ją jako warstwę interakcji nad kartami, a nie
podstawę całej estetyki.

## 4. Zasady wizualne

### 4.1. Monochromatyczna baza, niebieska intencja

Biel i czerń tworzą spokojną, premium bazę. Niebieski pojawia się wyłącznie tam, gdzie
oznacza intencję, wybór, aktywny stan albo rekomendowany następny krok. Nie używamy go
dekoracyjnie na dużych powierzchniach.

### 4.2. Jeden dominujący obiekt

W każdym stanie ekranu istnieje jeden wizualny punkt ciężkości:

- w rozmowie — ostatnia odpowiedź i pole wpisywania;
- w eksploracji — aktywna karta produktu;
- w rankingu — rekomendowana oferta;
- w szczegółach — decyzja i jej uzasadnienie.

### 4.3. Warstwy zamiast ramek

Hierarchię budują odstępy, delikatne zmiany tła i subtelny cień. Obramowania są cienkie
i funkcjonalne. Unikamy siatki jednakowych „dashboardowych” kafelków.

### 4.4. Dane bez fałszywej precyzji

Ocena produktu, jakości oferty i wiarygodności sprzedawcy pozostaje rozdzielona.
Uzasadnienie w prostym języku jest ważniejsze niż jedna duża liczba. Brak danych nie
może wyglądać jak wynik neutralny lub pozytywny.

## 5. Paleta kolorów

| Token | Wartość | Zastosowanie |
|---|---:|---|
| `canvas` | `#FFFFFF` | Główne tło |
| `surface` | `#F7F8FA` | Powierzchnie drugiego planu |
| `ink` | `#101114` | Główny tekst i mocne elementy |
| `muted` | `#686C75` | Tekst pomocniczy i metadane |
| `line` | `#E5E7EB` | Delikatne separatory i obramowania |
| `blue` | `#1769FF` | Główna akcja, wybór, aktywny stan |
| `blue-soft` | `#EAF1FF` | Tło wybranego elementu lub informacji |
| `danger` | `#D92D20` | Potwierdzone ryzyko lub błąd |
| `warning` | `#B54708` | Niepewność i brak krytycznych danych |
| `success` | `#16794B` | Potwierdzony pozytywny sygnał |

Niebieski jest kolorem decyzji, nie oceną jakości. Zielony, bursztynowy i czerwony są
kolorami semantycznymi i powinny zajmować małą część ekranu. Informacja nigdy nie może
być przekazywana wyłącznie kolorem — zawsze towarzyszy jej tekst lub ikona.

## 6. Typografia

### Rodziny

- **Inter** — tekst interfejsu, odpowiedzi, przyciski i formularze;
- **Manrope** — nazwy produktów, ceny oraz najważniejsze nagłówki;
- systemowy `ui-monospace` — wyłącznie techniczne identyfikatory, jeśli będą potrzebne.

Manrope wnosi lekko technologiczny, zdecydowany charakter, a Inter utrzymuje wysoką
czytelność rozmowy. Jeśli fonty sieciowe nie są dostępne, fallback to
`system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.

### Skala

| Rola | Rozmiar / interlinia | Waga |
|---|---:|---:|
| Hero | `48 / 52 px` | 650 |
| H1 | `36 / 42 px` | 650 |
| H2 | `28 / 34 px` | 650 |
| H3 / nazwa produktu | `22 / 28 px` | 650 |
| Duża cena | `30 / 34 px` | 700 |
| Body | `16 / 24 px` | 400 |
| Body strong | `16 / 24 px` | 600 |
| Small | `14 / 20 px` | 400–600 |
| Caption | `12 / 16 px` | 500 |

Na urządzeniach mobilnych Hero zmniejsza się do `36 / 40 px`, H1 do `30 / 36 px`, a
pozostałe role zachowują rozmiary. Tekst główny nigdy nie schodzi poniżej 16 px.
Używamy sentence case. Unikamy wersalików poza krótkimi etykietami statusu.

## 7. Rytm, geometria i głębia

- Bazowa jednostka odstępów: **4 px**.
- Najczęstsze odstępy: `8`, `12`, `16`, `24`, `32`, `48`, `64` px.
- Maksymalna szerokość rozmowy: **760 px**.
- Maksymalna szerokość widoku wyników: **1200 px**.
- Minimalny boczny padding: **20 px mobile**, **32 px tablet**, **48 px desktop**.
- Promień pól i małych kontrolek: **12 px**.
- Promień kart: **24 px**.
- Przyciski główne mają wysokość **48 px**, elementy dotykowe minimum **44 × 44 px**.

Cień aktywnej karty:

```css
box-shadow: 0 24px 64px rgba(16, 17, 20, 0.12),
            0 2px 8px rgba(16, 17, 20, 0.06);
```

Cienie nie mogą tworzyć efektu unoszących się wszędzie kafelków. W jednym widoku
wyraźny cień powinien mieć najwyżej jeden, najważniejszy element.

## 8. Architektura ekranów

### 8.1. Start i rozmowa

Ekran startowy jest niemal pusty: krótka obietnica, dwa przykłady zapytań i duże pole
wpisywania. Nie pokazujemy od razu filtrów, kategorii ani panelu parametrów.

```text
┌──────────────────────────────────────────────┐
│ Picky                                    ••• │
│                                              │
│   Znajdź elektronikę, którą warto kupić.     │
│   [ Coś jak AirPods Pro, ale taniej…     ↑ ] │
│                                              │
│   „Laptop do montażu do 3000 zł”             │
│   „Używany aparat na początek”                │
└──────────────────────────────────────────────┘
```

Wiadomości nie są zamykane w ciężkich dymkach. Wypowiedź użytkownika może mieć lekkie
niebieskie tło, natomiast odpowiedź Picky leży bezpośrednio na białym płótnie. Awatar
asystenta jest opcjonalny; nazwa i rytm treści wystarczają do rozpoznania autora.

### 8.2. Focus mode — wybór produktu

Na środku znajduje się jedna duża karta. Krawędzie maksymalnie dwóch kolejnych kart
mogą być widoczne z tyłu, aby zasugerować talię bez wizualnego bałaganu. Nad kartą
pokazujemy liczbę propozycji i krótkie podsumowanie potrzeb. Pod kartą znajdują się
jawnie podpisane akcje dostępne także bez gestów.

Zdjęcie zajmuje około 55% wysokości karty. Poniżej widoczne są nazwa, orientacyjna cena,
jednozdaniowe „dlaczego pasuje”, 2–3 najważniejsze cechy i jeden kompromis. Reszta
informacji jest dostępna po rozwinięciu, nie na froncie karty.

### 8.3. Ranking ofert

Po wyborze produktu układ staje się bardziej analityczny. Pierwsza oferta jest
wyróżniona rozmiarem i etykietą „Najlepszy wybór”, ale nie samym kolorem. Kolejne
oferty tworzą spokojną pionową listę, nie kolejną talię.

Każda oferta pokazuje:

- cenę całkowitą i źródło;
- dokładny wariant i deklarowany stan;
- dopasowanie produktu, jakość oferty oraz sprzedawcę jako trzy osobne wiersze;
- najważniejszy argument za i kompromis;
- ryzyka oraz brakujące dane;
- czas ostatniej aktualizacji;
- jednoznaczną akcję „Zobacz ofertę”.

### 8.4. Szczegóły decyzji

Widok wyjaśnia rekomendację w kolejności: **werdykt → powody → kompromisy → dowody →
następny krok**. Źródła są dostępne blisko twierdzeń, których dotyczą. Nie chowamy
ryzyka wyłącznie w tooltipach.

## 9. Typologia komponentów

### Komponenty nawigacyjne

- górny pasek z nazwą Picky, historią i menu;
- zwijane podsumowanie aktywnych preferencji;
- wskaźnik etapu oparty na nazwach, nie abstrakcyjnych numerach.

### Komponenty konwersacyjne

- wiadomość użytkownika;
- odpowiedź Picky;
- composer z autosize, akcją wysłania i stanem pracy;
- szybkie odpowiedzi w formie tekstowych chipsów;
- blok źródeł i poziomu pewności.

### Komponenty wyboru

- karta produktu;
- stos kart;
- jawne przyciski decyzji;
- chip preferencji;
- pasek postępu talii;
- cofnięcie ostatniej decyzji, jeśli dopuszcza je specyfikacja gestów.

### Komponenty oceny i zaufania

- trzyczęściowe podsumowanie: produkt / oferta / sprzedawca;
- znacznik `Potwierdzone`, `Niepewne`, `Brak danych`;
- alert ryzyka z konkretnym powodem;
- lista kompromisów;
- źródło z datą aktualizacji;
- wyjaśnienie „Dlaczego ta rekomendacja?”.

### Komponenty systemowe

- loading skeleton odpowiadający finalnemu układowi;
- pusty stan z jedną następną akcją;
- komunikat częściowego wyniku;
- błąd z informacją, co użytkownik może zrobić;
- toast tylko dla krótkiego potwierdzenia wykonanej akcji.

## 10. Przyciski i kontrolki

- **Primary:** niebieskie tło, biały tekst; jedna główna akcja w danym obszarze.
- **Secondary:** białe tło, ciemny tekst, subtelna ramka.
- **Tertiary:** tekst lub ikona bez stałego tła.
- **Destructive:** czerwony wyłącznie dla trwałego usunięcia lub rzeczywistego ryzyka.

Zwykłe pominięcie produktu nie jest akcją destrukcyjną i nie powinno automatycznie być
czerwone. Każda akcja oparta na ikonie otrzymuje etykietę dostępną dla czytnika oraz
tooltip na urządzeniach ze wskaźnikiem.

## 11. Ruch i mikrointerakcje

Najważniejszym momentem ruchu jest przejście z rozmowy do focus mode. Podsumowanie
potrzeb przesuwa się ku górze, a pierwsza karta pojawia się z lekkim ruchem i zmianą
skali. Całość trwa `280–360 ms` i używa łagodnego easing bez sprężynowania.

- hover i focus: `120–160 ms`;
- zmiana układu: `220–300 ms`;
- wejście karty: do `360 ms`;
- skeleton: spokojny shimmer lub puls bez migotania;
- żadnych animacji uruchamianych wyłącznie dla dekoracji.

Przy `prefers-reduced-motion: reduce` przesunięcia i obrót są wyłączone, a zmiany
odbywają się przez krótkie przenikanie lub natychmiastowo. Gest zawsze ma dostępny
równoważny przycisk.

## 12. Responsywność

Projekt powstaje mobile first.

- **Mobile, 320–767 px:** jedna kolumna, karta niemal na całą szerokość, composer
  przyklejony do dolnej krawędzi z uwzględnieniem safe area.
- **Tablet, 768–1023 px:** szersza karta i opcjonalny panel szczegółów wysuwany z boku.
- **Desktop, od 1024 px:** rozmowa pozostaje centralna; focus mode może pokazać obok
  karty wąski panel „Dlaczego pasuje”, a ranking wykorzystuje pełną szerokość treści.

Desktop nie powinien wyglądać jak panel administracyjny. Dodatkowa przestrzeń służy
czytelności, porównaniu i źródłom, nie zwiększaniu liczby jednoczesnych kontrolek.

## 13. Dostępność

- kontrast zgodny co najmniej z WCAG 2.2 AA;
- widoczny focus ring: `0 0 0 3px rgba(23, 105, 255, 0.28)`;
- pełna obsługa klawiatury i logiczna kolejność fokusu;
- gesty nie są jedynym sposobem wykonania akcji;
- poprawne nagłówki, landmarki i komunikaty `aria-live` dla postępu researchu;
- zdjęcia produktów mają opis funkcjonalny lub pusty `alt`, jeśli są dekoracyjne;
- statusy i wyniki używają tekstu oraz ikony, nie tylko barwy;
- minimalny obszar dotykowy wynosi 44 × 44 px;
- powiększenie tekstu do 200% nie blokuje głównego przepływu.

## 14. Język interfejsu

Picky mówi prosto, konkretnie i spokojnie. Używa aktywnych czasowników i krótkich zdań.
Nie udaje człowieka ani nie przypisuje sobie emocji.

Preferowane:

- „Znalazłem 5 modeli, które mieszczą się w budżecie.”
- „Brakuje informacji o stanie baterii.”
- „Wybierz kierunek, a sprawdzę konkretne oferty.”
- „Ta oferta jest tańsza, ale sprzedawca ma mało opinii.”

Unikamy:

- „Oto idealny produkt dla Ciebie!”;
- „AI przeanalizowało tysiące parametrów”;
- niejasnych przycisków typu „Dalej”, jeśli można napisać „Porównaj oferty”;
- technicznych nazw etapów backendu.

## 15. Stany szczególne

### Ładowanie

Interfejs nazywa wykonywane zadanie: „Sprawdzam dokładne warianty”, „Porównuję cenę ze
średnią rynkową”. Nie pokazuje fałszywie precyzyjnego procentu, jeśli go nie zna.
Podczas każdej operacji agenta globalny status zmienia się z „Agent gotowy” na „Agent
działa”. W rozmowie oczekiwanie na odpowiedź sygnalizuje spinner w kolejnym wierszu
Picky. Oba wskaźniki korzystają z jednego stanu pracy i znikają po odpowiedzi lub
błędzie.

### Brak danych

Stan `Brak danych` jest osobną, neutralną etykietą z wyjaśnieniem wpływu na decyzję.
Nie jest pokazywany jako zero ani wyszarzona pozytywna ocena.

### Wynik częściowy

Użytkownik widzi dostępne propozycje oraz jasny komunikat, czego nie udało się sprawdzić.
Główna ścieżka pozostaje dostępna, jeśli decyzja nadal może być podjęta bezpiecznie.

### Błąd

Komunikat opisuje problem i możliwy następny krok, np. „Nie udało się odświeżyć ofert.
Pokazujemy wyniki z 10 lipca. Spróbuj ponownie”.

## 16. Wymagania niefunkcjonalne

- Główna treść powinna być użyteczna w ciągu około 2,5 s na typowym połączeniu mobilnym.
- Obrazy używają responsywnych formatów i lazy loading poza aktywną kartą.
- Przesuwanie i animacje powinny utrzymywać 60 fps na współczesnych telefonach.
- UI nie przechowuje sekretów ani danych płatniczych; linki zewnętrzne są oznaczone.
- Historia i preferencje użytkownika wymagają jasnych zasad przechowywania i usuwania.
- Komponenty muszą obsługiwać dowolną kategorię elektroniki oraz dłuższe nazwy modeli.
- System tokenów pozostaje mały i współdzielony, aby mógł być utrzymywany przez mały
  zespół bez osobnej biblioteki design systemu na etapie MVP.

## 17. Czego nie robimy

- nie tworzymy marketplace'u z gęstą siatką dziesiątek produktów;
- nie kopiujemy gradientów, ikonografii ani brandingu Tindera lub ChatGPT;
- nie stosujemy glassmorphismu, neonów ani dekoracyjnych gradientów AI;
- nie zamieniamy wyboru drogiego produktu w grę;
- nie ukrywamy ryzyka za atrakcyjnym wynikiem liczbowym;
- nie wymagamy gestu do wykonania kluczowej akcji;
- nie używamy niebieskiego na każdym interaktywnym elemencie.

## 18. Kryteria spójności

Przed zaakceptowaniem nowego ekranu należy sprawdzić:

1. Czy istnieje jeden oczywisty następny krok?
2. Czy użytkownik rozumie, czy ogląda model, ofertę czy sprzedawcę?
3. Czy ryzyko i brak danych są widoczne bez otwierania tooltipu?
4. Czy ekran nadal działa bez gestów i animacji?
5. Czy niebieski wskazuje intencję lub aktywny stan?
6. Czy usunięcie jednego elementu uprości ekran bez utraty znaczenia?
7. Czy układ działa dla telefonu i długich nazw dowolnej elektroniki?

## 19. Założenia i ryzyka

### Założenia

- Picky będzie obsługiwać wszystkie kategorie używanej elektroniki, mimo że pierwsze
  demo może koncentrować się na słuchawkach.
- Interfejs jest budowany mobile first i pozostaje użyteczny na desktopie.
- Użytkownik może zmienić preferencję bez utraty całej rozmowy.
- Szczegółowa semantyka gestów kart powstaje w osobnym dokumencie.
- Na etapie MVP design system jest utrzymywany bez dedykowanego zespołu.

### Ryzyka

- zbyt zabawowa mechanika może osłabić wiarygodność decyzji zakupowej;
- zbyt wiele metryk może zmienić aplikację w ciężki dashboard;
- niepełne dane źródłowe mogą wyglądać jak pewna rekomendacja;
- zdjęcia o różnej jakości mogą zaburzyć spójność kart;
- długie nazwy modeli i wariantów mogą przeciążać mobilny layout.

Odpowiedzią na te ryzyka są: spokojna baza wizualna, jedna decyzja naraz, jawna
niepewność, stałe proporcje mediów i testy komponentów na skrajnie długich treściach.

## 20. Decision log

| Decyzja | Rozważane alternatywy | Uzasadnienie |
|---|---|---|
| Conversation-first | Card-first, split view | Najlepiej zachowuje zaufanie i kontekst, a karty pojawiają się w momencie, gdy faktycznie pomagają. |
| Biało-czarna baza z niebieskim | Wielokolorowy marketplace, dark-first | Czytelność, spokój i wyraźne wskazanie intencji bez wizualnego szumu. |
| Inter + Manrope | Jeden font systemowy, bardziej ekspresyjny display | Czytelna rozmowa z subtelnym charakterem w nazwach i cenach. |
| Jedna aktywna karta | Siatka produktów | Mniejszy wysiłek poznawczy i zgodność z szybkim wyborem kierunku. |
| Lista dla ofert finalnych | Talia na każdym etapie | Konkretne oferty wymagają porównania dowodów, ryzyk i kosztów, nie tylko szybkiej reakcji. |
| Trzy oddzielne oceny | Jeden zbiorczy score | Zapobiega ukrywaniu słabej oferty lub sprzedawcy za dobrym dopasowaniem produktu. |
| Semantyczna czerwień | Czerwone odrzucenie | Odrzucenie preferencji nie jest błędem ani zagrożeniem. |
| Gesty jako dodatkowa warstwa | Interfejs tylko gestowy | Dostępność, obsługa klawiatury i większa kontrola użytkownika. |
| Jeden stan aktywności agenta | Osobne flagi dla czatu i researchu | Zapewnia spójny status w nagłówku i rozmowie niezależnie od rodzaju wykonywanej operacji. |

## 21. Element rozpoznawczy

Charakterystycznym elementem Picky jest **płynna przemiana rozmowy w talię decyzji**.
Ostatnia odpowiedź nie kończy się listą linków: kondensuje się do krótkiego briefu nad
kartą, dzięki czemu użytkownik widzi bezpośredni związek między tym, co powiedział, a
tym, co otrzymał. To połączenie kontekstu rozmowy z wyborem jednej rzeczy naraz powinno
być najbardziej zapamiętywalnym momentem produktu.
