# Sigma — Unique Value Proposition

## Najkrótsza wersja

**Sigma to ekspert zakupowy AI do używanej elektroniki. Pomaga wybrać właściwy produkt,
sprawdza konkretną ofertę i pokazuje, czego jeszcze trzeba dowiedzieć się od sprzedawcy,
zanim kupujący wyda pieniądze.**

Nie jest tylko wyszukiwarką ani porównywarką cen. Jej główną wartością jest wstępne
due diligence zakupu: uporządkowany raport o dopasowaniu produktu, jakości oferty,
wiarygodności sprzedawcy, ryzykach, brakujących danych i cenie na tle rynku.

## Historia, od której zaczynamy

Kiedy kupujemy używany samochód, często zabieramy ze sobą osobę, która zna się na
samochodach, albo płacimy ekspertowi za oględziny. Taka osoba wie, o co zapytać, co
sprawdzić i kiedy pozornie dobra cena powinna wzbudzić podejrzenia.

Przy zakupie używanego telefonu, słuchawek, aparatu czy laptopa większość ludzi nie ma
takiego wsparcia. Kupujący zna swoje potrzeby, ale nie zawsze potrafi przełożyć je na
model, wariant i kryteria oceny oferty. Sprzedający zna produkt i jego historię, ale
kupujący widzi tylko fragment informacji z ogłoszenia. W efekcie łatwo kupić niewłaściwy
wariant, przepłacić albo przeoczyć istotne ryzyko.

**Sigma ma być takim kompetentnym znajomym, którego zabierasz ze sobą na zakup używanej
elektroniki.**

## Problem: asymetria informacji

Na rynku wtórnym obie strony wiedzą coś, czego nie wie druga:

- kupujący zna swój budżet, potrzeby i preferencje, których sprzedający nie zna;
- sprzedający zna stan, pochodzenie i historię produktu, których kupujący nie zna;
- samo ogłoszenie rzadko wystarcza, aby ocenić właściwy wariant, uczciwość ceny,
  kompletność zestawu, stan baterii, gwarancję, możliwość zwrotu i ryzyko transakcji;
- osoba bez wiedzy technicznej często nie wie nawet, jakie pytania powinna zadać.

Sigma zmniejsza tę asymetrię. Najpierw rozumie potrzeby kupującego, następnie zbiera i
porządkuje dostępne dowody o produkcie, ofercie i sprzedawcy, a na końcu wskazuje braki,
które trzeba wyjaśnić przed decyzją.

## Propozycja wartości

### Dla kupującego

Sigma:

1. tłumaczy krótką potrzebę lub produkt referencyjny na konkretne kryteria zakupu;
2. proponuje kilka trafnych modeli zamiast setek przypadkowych wyników;
3. pilnuje dokładnej generacji i wariantu produktu;
4. porównuje cenę, stan, kompletność, dostawę i dostępne sygnały o sprzedawcy;
5. oddziela dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy;
6. pokazuje ryzyka, kompromisy, źródła, czas pozyskania i dane, których brakuje;
7. podpowiada, co sprawdzić lub o co zapytać sprzedawcę przed zakupem;
8. rekomenduje decyzję, ale nie udaje pewności, gdy dowody są niewystarczające.

Rezultat: mniej ręcznego researchu, mniej nietrafionych zakupów i większa pewność, że
niska cena nie przesłoniła kosztu, złego wariantu albo ryzyka.

### Dla sprzedającego — kierunek rozwoju

Docelowo Sigma może obsługiwać również drugą stronę rynku. Na podstawie tych samych
kryteriów jakości może wskazać sprzedającemu:

- jakich informacji i zdjęć brakuje w ogłoszeniu;
- które deklaracje zwiększają wiarygodność i jak je udokumentować;
- jakie pytania prawdopodobnie zada kupujący;
- czy cena jest uzasadniona na tle porównywalnych ofert i ceny nowego produktu;
- co poprawić poza samym obniżeniem ceny, aby zwiększyć szansę sprzedaży;
- które elementy opisu obniżają zaufanie lub pozostawiają niepotrzebną niepewność.

To zmienia Sigmę z jednostronnego asystenta zakupowego w pośrednika informacji, który
pomaga kupującemu podjąć bezpieczniejszą decyzję, a rzetelnemu sprzedającemu lepiej
udowodnić jakość oferty. Ten zakres jest wizją produktu, a nie gotową funkcją MVP.

## Co wyróżnia Sigmę

Porównywarka odpowiada: **„Gdzie jest najtaniej?”**  
Chatbot odpowiada: **„Jaki model może Ci pasować?”**  
Sigma odpowiada: **„Co warto kupić, dlaczego właśnie tę ofertę, jakie są dowody i czego
jeszcze nie wiemy?”**

Przewaga powstaje z połączenia trzech zadań w jednym procesie:

- doradztwa produktowego — jaki model rzeczywiście odpowiada potrzebie;
- analizy rynku — która konkretna oferta ma sens cenowy i dotyczy właściwego wariantu;
- wstępnego due diligence — jakie są sygnały jakości, wiarygodności i ryzyka oraz czego
  nie da się potwierdzić na podstawie dostępnych danych.

## Raport due diligence

Głównym artefaktem Sigmy powinien być krótki, zrozumiały raport przedzakupowy zawierający:

1. **werdykt** — warto rozważyć, wstrzymać decyzję albo odrzucić;
2. **dopasowanie produktu** — zgodność z potrzebą, budżetem i wymaganymi funkcjami;
3. **jakość oferty** — cena, dokładny wariant, stan, kompletność i warunki transakcji;
4. **wiarygodność sprzedawcy** — wyłącznie na podstawie dostępnych, wskazanych sygnałów;
5. **cena w kontekście** — porównanie z podobnymi ofertami i benchmarkiem nowego produktu;
6. **ryzyka i czerwone flagi** — na przykład podejrzanie niska cena, zły wariant lub
   niespójny opis;
7. **braki dowodowe** — informacje nieznane, których system nie powinien zgadywać;
8. **następny krok** — pytania do sprzedawcy i elementy do sprawdzenia przed płatnością.

Raport jest wsparciem decyzji, nie gwarancją stanu produktu, autentyczności ani uczciwości
sprzedawcy. „Nie wiadomo” jest prawidłowym i wartościowym wynikiem analizy.

## Aktualny stan produktu

### Gotowe w repozytorium

- kompletny demonstracyjny przepływ dla używanych słuchawek: od potrzeby lub produktu
  referencyjnego, przez wybór modelu, do rankingu konkretnych ofert;
- konwersacyjny frontend React połączony z API oraz jawny fallback na dane demonstracyjne;
- backend FastAPI z sesjami, interpretacją preferencji, wyborem produktu i asynchronicznym
  runem wyszukiwania;
- 4–6 kierunków produktowych z cenami, podobieństwami, różnicami i kompromisami;
- integracje OpenAI, Firecrawl/OLX, Supabase oraz benchmark ceny nowego produktu z Ceneo;
- normalizacja ofert, twarda kontrola wariantu, ranking i sygnały ryzyka;
- osobne oceny dopasowania produktu, jakości oferty i wiarygodności sprzedawcy;
- jawne oznaczanie nieznanych danych, źródeł, czasu pobrania, confidence i starego cache;
- zmiana miękkiej preferencji i ponowny ranking bez ponownego pobierania ofert;
- opcjonalne logowanie magic linkiem i historia rozmów w starszym prototypie statycznym;
- Deal Watch w trybie `alert_only`: pełny koszt, decyzje `ignore`/`hold`/`alert` oraz
  idempotencja zdarzeń w kontrolowanym scenariuszu;
- lokalna brama backendu: **66 testów zaliczonych, 3 testy live pominięte**, a `ruff`
  przechodzi bez błędów (stan zweryfikowany 11 lipca 2026).

### W toku lub wymagające potwierdzenia

- pełne testy live prawdziwych usług wymagają poprawnych kluczy i developerskiego
  Supabase; ich sukces nie jest jeszcze potwierdzony przez domyślny zestaw testów;
- frontend ma testy i konfigurację buildu, ale w bieżącym środowisku nie zainstalowano
  zależności `node_modules`, dlatego test i build nie zostały lokalnie potwierdzone;
- aktualna integracja UI koncentruje się na głównym flow demo; logowanie i historia nie są
  jeszcze włączone do nowego frontendu React;
- ocena sprzedawcy wykorzystuje tylko dane dostępne w źródle. Nie jest pełną weryfikacją
  tożsamości sprzedawcy ani gwarancją braku oszustwa;
- pytania do sprzedawcy i pełny, osobny raport due diligence powinny zostać wyeksponowane
  jako pierwszoplanowy rezultat interfejsu, a nie tylko elementy rankingu;
- Deal Watch działa w pamięci procesu i nie ma jeszcze trwałego schedulera ani kanału
  powiadomień.

### Kolejne kroki wynikające z UVP

1. Zmienić język interfejsu z „rankingu ofert” na „raport przedzakupowy”.
2. Dodać generowaną checklistę pytań i dowodów wymaganych od sprzedawcy dla danej kategorii.
3. Rozróżnić sygnał, informację zweryfikowaną i deklarację sprzedawcy.
4. Dodać analizę jakości ogłoszenia dla sprzedającego wraz z konkretnymi rekomendacjami.
5. Rozbudować źródła, deduplikację, historię cen i trwałe monitorowanie ofert.
6. Dopiero po zbudowaniu warstwy dowodowej rozwijać pośrednictwo obu stron lub automatyzację
   transakcji.

## Proponowany przekaz

### Jedno zdanie

**Sigma to ekspert AI, który przed zakupem używanej elektroniki sprawdza produkt, ofertę
i sprzedawcę oraz mówi, co wiadomo, czego nie wiadomo i o co zapytać.**

### Wersja prezentacyjna

> Kupując używany samochód, zabierasz ze sobą kogoś, kto się na nim zna. Przy używanej
> elektronice zwykle takiego wsparcia nie masz. Sigma jest ekspertem AI, który rozumie,
> czego potrzebujesz, porównuje właściwe warianty i wykonuje wstępne due diligence
> konkretnej oferty. Nie pokazuje tylko najniższej ceny — pokazuje dowody, ryzyka, braki
> danych i pytania, które należy zadać sprzedawcy przed zakupem.

### Hasła robocze

- **Nie kupuj kota w worku. Zabierz Sigmę na zakupy.**
- **Twój ekspert od używanej elektroniki.**
- **Od „podoba mi się” do „wiem, co kupuję”.**
- **Nie tylko najlepsza cena. Lepsza decyzja.**

