# Burza mózgów przed hackathonem — przebieg i ustalenia

## Kontekst spotkania

Zespół szukał pomysłu na produkt możliwy do zbudowania podczas hackathonu. Rozmowa była prowadzona najpierw w trybie swobodnego generowania pomysłów, a dopiero później miała przejść do oceny realności i implementacji. Ze względu na ograniczony czas zespół przyjął, że warto szybko wybrać obiecujący kierunek, rozpocząć budowę uniwersalnego szkieletu i równolegle zweryfikować założenia rynkowe.

## 1. Punkt wyjścia: rynek rzeczy używanych

Rozmowa zaczęła się od obserwacji, że konsumenci coraz częściej odchodzą od potrzeby posiadania nowych rzeczy na rzecz korzystania z rzeczy używanych. Jako przykłady pojawiły się Vinted, odzież vintage oraz ogólna presja na oszczędzanie.

Rozważano, czy dane z platform ogłoszeniowych da się pobierać automatycznie. Pojawiły się obawy o dostępność API i blokowanie skrapowania, znane m.in. z innych platform. Ustalono jednak, że na etapie generowania pomysłów nie należy odrzucać kierunku tylko z powodu niezweryfikowanych ograniczeń technicznych. Jedna z osób deklarowała wcześniejsze testy wskazujące, że pobieranie danych może być możliwe.

## 2. Moda kontra elektronika

Początkowo jako naturalny rynek rzeczy używanych rozważano modę. Zespół uznał jednak, że moda jest trudniejszym punktem wejścia dla agenta rekomendacyjnego:

- wybór jest silnie wizualny i subiektywny;
- użytkownicy lubią samodzielnie przeglądać dużą liczbę rzeczy;
- styl, kolor i indywidualny gust trudno sprowadzić do krótkiego zestawu parametrów;
- sam wynik wygenerowany na podstawie promptu może być mniej satysfakcjonujący niż przeglądanie katalogu.

Elektronika została oceniona jako lepsza kategoria startowa, ponieważ:

- wiele osób nie zna aktualnych modeli i parametrów;
- użytkownicy chętnie korzystają z recenzji i poradników;
- potrzeby da się opisać przez budżet, zastosowanie i cechy;
- część decyzji użytkownik chętnie deleguje ekspertowi lub agentowi;
- rynek wtórny jest rozproszony, podczas gdy dla nowych produktów istnieją już porównywarki, np. Ceneo.

Wniosek: głównym kierunkiem została używana elektronika użytkowa.

## 3. Odkrycie dwóch osobnych problemów

W toku rozmowy zespół zauważył, że użytkownik może przyjść w dwóch różnych sytuacjach:

1. nie wie, jaki produkt lub model powinien kupić;
2. zna konkretny model i chce znaleźć najlepszą ofertę.

Zamiast łączyć wszystko w jedno kosztowne wyszukiwanie, zaproponowano dwie następujące po sobie fazy.

### Faza 1: research i wybór modelu

Użytkownik opisuje potrzebę, np. „szukam słuchawek”. Agent zbiera podstawowe wymagania i pokazuje kilka modeli mieszczących się w budżecie. Na tym etapie informacje mają być wystarczające do wstępnej selekcji, ale nie przesadnie szczegółowe.

W rozmowie pojawiła się także propozycja pokazania nawet kilkunastu lub kilkudziesięciu podobnych produktów, z których użytkownik wybierze kilka do dalszej analizy. Ostateczny kierunek MVP powinien jednak ograniczać listę, aby interfejs i koszty analizy pozostały pod kontrolą.

### Faza 2: głęboka analiza i wyszukiwanie ofert

Dopiero po wyborze modelu system wykonuje dokładniejszy research, pobiera konkretne ogłoszenia i analizuje cenę, stan, dostawę oraz inne szczegóły ważne dla użytkownika. Dzięki temu agent nie zużywa czasu i zasobów na szczegółową analizę wielu produktów, które zaraz zostaną odrzucone.

To rozdzielenie zostało uznane za jedną z najważniejszych decyzji produktowych.

## 4. Forma interakcji: aktywny agent z pamięcią kontekstu

Rozważano dwa interfejsy:

- niezależne bloki „prompt → odpowiedź”, resetowane po każdym zapytaniu;
- ciągłą rozmowę, w której system pamięta wcześniejsze wymagania.

Zespół skłonił się ku rozmowie z pamięcią. Użytkownik powinien móc doprecyzować pojedynczą cechę — np. „jednak chcę niebieskie” — bez ponownego wpisywania całego zapytania i generowania całego raportu od zera.

Agent nie powinien być bierny. Ma zadawać pytania, gdy brakuje informacji potrzebnych do dobrej rekomendacji. Jednocześnie liczba pytań musi być mała, aby rozmowa nie stała się przeszkodą.

## 5. Pomysł na zamienniki i produkty podobne

Zwrócono uwagę, że użytkownicy często nie szukają konkretnego produktu, lecz czegoś podobnego i tańszego. Przykładem były produkty wybierane również ze względu na wygląd lub konkretny detal wzorniczy.

Powstał pomysł funkcji, w której użytkownik wskazuje produkt i prosi o:

- tańszy odpowiednik;
- podobny wygląd;
- zachowanie konkretnych cech;
- lepsze dopasowanie do wcześniejszych wymagań.

Funkcja została oceniona jako potencjalny „game changer”, ale w kontekście hackathonu jest rozszerzeniem głównego przepływu, a nie warunkiem działania MVP.

## 6. Pamięć wyników i ograniczenie kosztów

Pojawiła się propozycja zapisywania wykonanych researchów i pobranych danych, aby kolejne zapytania nie wymagały ponownego skrapowania i analizy tych samych produktów. Jako potencjalne miejsce przechowywania wskazano Supabase.

Argumenty za:

- przechowywanie danych jest tanie;
- ponowne pobieranie i parsowanie może być wolniejsze oraz droższe;
- baza może z czasem zwiększać jakość i szybkość odpowiedzi.

Jednocześnie zespół zauważył, że nie jest to potrzebne w pierwszej wersji backendu. Priorytetem powinien pozostać kompletny przepływ użytkownika.

## 7. Ranking ofert

Po pobraniu ofert system ma wybrać najlepszą według zmiennych podanych przez użytkownika. W rozmowie padł pomysł wykorzystania bardziej zaawansowanego modelu lub „korelacji nieliniowej”, częściowo na bazie rozwiązania z wcześniejszego projektu.

Nie ustalono konkretnego algorytmu. Istotą pomysłu jest jednak wielokryterialna ocena ofert, a nie sortowanie wyłącznie po cenie. Dla prototypu prosty, jawny scoring może dać lepszy stosunek efektu do czasu niż skomplikowany model.

## 8. Wyróżnienie na tle rynku

Zespół podkreślił, że produkt nie powinien być kolejną porównywarką nowych produktów. Ten problem jest już dobrze obsługiwany przez istniejące serwisy agregujące sklepy.

Przewaga ma wynikać z:

- skupienia na elektronice używanej;
- połączenia rekomendacji modelu z wyszukiwaniem konkretnej sztuki;
- aktywnej rozmowy doprecyzowującej potrzeby;
- oceny ofert według wielu kryteriów;
- możliwości znalezienia podobnego, tańszego produktu.

Padła też sugestia, że bardziej niszowy i jednoznaczny przypadek użycia może być łatwiejszy do zapamiętania przez jury niż bardzo szeroka aplikacja zakupowa.

## 9. Podejście do walidacji

Ustalono, że dwie osoby wykonają szybki research rynku elektroniki używanej, aby sprawdzić założenia na realnych danych. Research ma odpowiedzieć przede wszystkim na pytania:

- czy problem jest wystarczająco wyraźny;
- jakie rozwiązania już istnieją;
- gdzie jest największa luka;
- która wąska kategoria nadaje się najlepiej do demonstracji;
- z jakich źródeł można realnie pozyskać oferty.

Research nie miał być długą analizą. Jego rolą było potwierdzenie lub zanegowanie kierunku, gdy część techniczna równolegle buduje uniwersalny szkielet aplikacji. Jeżeli dane wykażą brak sensu pomysłu, zespół pozostawił sobie możliwość szybkiego pivotu.

## 10. Podział pracy zarysowany na spotkaniu

- Kuba i druga osoba: szybki research rynku oraz wybór najtrafniejszej niszy w elektronice używanej.
- Mikołaj i Rem: przygotowanie repozytorium, ogólnego szkieletu oraz elementów technicznych możliwych do wykorzystania niezależnie od ostatecznego wariantu.
- Równolegle: rozpoczęcie pracy nad silnikiem dla elektroniki, aby nie czekać bezczynnie na wyniki researchu.

Nazwy i dokładne zakresy nie zostały w transkrypcie w pełni doprecyzowane.

## 11. Decyzje podjęte

1. Roboczą kategorią jest używana elektronika użytkowa.
2. Produkt łączy dobór modelu z wyszukiwaniem konkretnej oferty.
3. Proces zostaje podzielony na dwie fazy: lekki research, potem głęboka analiza wybranego produktu.
4. Interfejs ma formę rozmowy zachowującej kontekst.
5. Agent ma aktywnie zadawać pytania doprecyzowujące.
6. Budowa szkieletu zaczyna się od razu, równolegle z szybkim researchem rynku.
7. Kierunek może zostać zmieniony, jeżeli research szybko wykaże brak sensownej niszy lub brak dostępu do danych.

## 12. Pomysły odłożone na później

- podobne, ale tańsze zamienniki;
- dopasowanie produktów na podstawie wyglądu lub zdjęcia;
- uczenie się na wcześniejszych researchach;
- trwała baza wiedzy w Supabase;
- wiele kategorii produktowych;
- agregowanie wielu platform;
- zaawansowany nieliniowy model rankingu;
- uwzględnianie nowych ofert jako punktu odniesienia cenowego.

## 13. Otwarte pytania i ryzyka

- Czy wybrane serwisy pozwolą legalnie i stabilnie pobierać dane?
- Które źródło ofert da się zintegrować w czasie hackathonu?
- Czy istnieje już bezpośredni konkurent agregujący używaną elektronikę?
- Jaka jedna podkategoria będzie najlepsza do demo?
- Jak oceniać wiarygodność i stan oferty na podstawie niepełnego opisu?
- Jak dużo danych agent powinien pokazywać w fazie pierwszej?
- Czy dane mają być aktualne w czasie rzeczywistym, czy do demo wystarczy kontrolowany zestaw?
- Jak ograniczyć koszt i czas odpowiedzi modelu?
- Jak pokazać przewagę nad zwykłym chatbotem i porównywarką cen?

## 14. Rekomendacja wynikająca z rozmowy

Zespół powinien potraktować słuchawki jako pierwszą kategorię demonstracyjną i zbudować jeden kompletny scenariusz. Integracja z jednym źródłem oraz prosty scoring wystarczą, jeśli użytkownik rzeczywiście przejdzie od ogólnej potrzeby do konkretnej, uzasadnionej oferty. Funkcje efektowne, ale ryzykowne — podobieństwo wizualne, trwała pamięć czy wiele platform — należy wdrażać dopiero po ustabilizowaniu głównego przepływu.
