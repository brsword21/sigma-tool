# Raport zgodności projektu Sigma Shopping Agent z case'em Solidgate

**Data analizy:** 11 lipca 2026  
**Źródła:** `solidgate-case.pdf` (7 slajdów), bieżący kod i dokumentacja projektu  
**Zakres:** zgodność pomysłu, przepływu użytkownika, architektury i demonstracji z sugestiami organizatorów hackathonu

## 1. Wniosek wykonawczy

Projekt jest **dobrze dopasowany do rdzenia case'u**: scoutowania ofert, rozpoznawania właściwego wariantu i odrzucania pozornych okazji. Obecnie wymaga przede wszystkim doprecyzowania sposobu pokazania tej wartości w demo.

Sigma pomaga wybrać produkt i konkretne używane oferty, ocenia wariant, jakość ogłoszenia, ryzyko i sprzedawcę. To jest prawidłowa interpretacja narzuconego przez organizatorów zadania: agent ma scoutować okazje i podejmować uzasadnioną decyzję, nie być zwykłą listą wyników. Case dodatkowo akcentuje **monitorowanie**, **pełny koszt zakupu**, **jedno istotne powiadomienie** i audyt uzasadnienia. Przygotowanie checkoutu lub zakup są wizją końcową, a nie warunkiem prezentacji - slajd 7 wprost wskazuje, że integracja PSP nie jest wymagana.

Najkrócej:

> Sigma jest już agentem scoutującym oferty; warto domknąć demonstrację „deal hunter loop” przez pokazanie, dlaczego konkretna oferta jest lub nie jest okazją.

Ocena ogólna na podstawie obecnego repozytorium: **dobra zgodność z wymaganym rdzeniem, około 75% zakresu hackathonowego**. To nie jest miara jakości kodu. Kod jest w dobrym stanie lokalnym; wynik opisuje pokrycie funkcji i narracji wskazanych w prezentacji.

Najlepszą równoległą ścieżką rozwoju jest **wąski tryb Deal Watch / Mandate**, oparty na deterministycznym symulatorze zmian cen. Nie zmienia on celu produktu; uwidacznia narzucone przez case scoutowanie okazji bez ryzyka live scrapingu.

## 2. Co organizatorzy rzeczywiście premiują

Prezentacja nie opisuje zwykłej porównywarki ani jednorazowego chatbota zakupowego. Jej rdzeniem jest:

1. **Brief w naturalnym języku** - produkt, wariant, limit ceny i warunki.
2. **Długotrwałe przejęcie zadania** - agent monitoruje sklepy i reaguje dopiero na właściwy moment.
3. **Dopasowanie tego samego produktu** mimo niejednolitych tytułów, SKU i mylących ofert.
4. **Landed cost zamiast ceny z etykiety** - cena, dostawa, waluta, opłaty/cła i kupony.
5. **Odróżnienie prawdziwej okazji od przynęty** - dostępność, sprzedawca, fałszywa obniżka, zawyżona cena „przed”.
6. **Jedno powiadomienie, które ma znaczenie**, zamiast zalewu alertów.
7. **Mandat i granice autonomii** - twardy limit, warunki, standing consent, eskalacja przypadku granicznego.
8. **Checkout przygotowany albo zakup wykonany** w ramach mandatu.
9. **Audytowalność** - rachunek, źródła, powód decyzji i historia override'ów.
10. **Dowód działania na kontrolowanym zbiorze** zawierającym pułapki cenowe i ofertowe.

Szczególnie ważna jest sugestia ze slajdu 6: **„mock the merchants, real the math”**. Organizatorzy wprost wskazują, że live scraping jest zakładnikiem demo, a wartością projektu mają być ocena i matematyka kosztu końcowego.

## 3. Macierz zgodności

| Element case'u | Stan w Sigma | Ocena | Dowód / komentarz |
|---|---|---:|---|
| Brief w naturalnym języku | Działa dla potrzeby i produktu referencyjnego; do 3 pytań | **mocne** | `ConversationService`, `Requirements`, dwa happy pathy API |
| Wąski, czytelny zakres | Jedna kategoria: używane słuchawki | **mocne** | zgodne z zasadą „scope ruthlessly” |
| Rozpoznanie właściwego produktu i wariantu | Wariant jest twardym filtrem przed scoringiem | **mocne** | `matches_exact_product`, test odrzucenia AirPods Pro 1 gen dla 2 gen |
| Ocena jakości i ryzyka oferty | Cena, stan, kompletność, logistyka, sprzedawca, braki danych | **mocne** | deterministyczny ranking i osobne składowe produktu/oferty/sprzedawcy |
| Źródła i niepewność | URL, czas pobrania, confidence, data gaps, stale cache | **mocne** | API prezentuje pochodzenie i pola `unknown` |
| Odporność demo | Cache, częściowy wynik przy awarii źródła, timeouty i logi | **mocne** | test partial failure i obserwowalność fazy 4 |
| Monitoring w czasie | Są snapshoty ceny i cache, ale brak cyklicznego watchera | **słabe** | `listing_snapshots` to fundament, nie aktywna pętla monitorowania |
| Wiele sklepów / granic | Jedno źródło OLX przez Firecrawl | **brak** | brak porównania sklepów, krajów i walut w jednym runie |
| Pełny koszt zakupu | Cena i bool dostawy; brak kosztu dostawy, FX, ceł i kuponów | **brak** | budżet filtruje cenę ogłoszenia, nie landed cost |
| Historia ceny i prawdziwy discount | Snapshoty istnieją, ale ranking nie używa historii | **częściowe** | podejrzanie niska cena jest liczona względem bieżącej mediany |
| Bait listing / real stock | Częściowe heurystyki ryzyka, brak jawnej weryfikacji stocku | **częściowe** | wykrywane są m.in. krótki opis, brak zdjęć i sygnały usterki |
| Jedno znaczące powiadomienie | Brak modelu alertu i polityki powiadomień | **brak** | wynik jest zwracany na żądanie przez polling |
| Mandat zakupowy | Brak standing consent, hard caps i reguł eskalacji | **brak** | `Requirements` opisuje preferencje, ale nie uprawnienia do wydania pieniędzy |
| Checkout / zakup | Świadomie poza zakresem MVP | **nie wymagane** | case wskazuje to jako endgame; slajd 7 nie wymaga integracji PSP |
| Receipt + why | Wyjaśnienie rankingu i logi istnieją; brak rekordu decyzji zakupowej | **częściowe** | jest „dlaczego polecam”, nie ma „dlaczego agent uderzył / wstrzymał się” |
| Eval set z pułapkami | Są testy jednostkowe i happy path; brak zestawu case-specific | **częściowe** | brak macierzy bait, fake discount, FX trap, stock trap i false-buy rate |
| Deterministyczne demo merchantów | Projekt stawia na realny Firecrawl | **rozbieżność** | jest to przeciwne bezpośredniej sugestii organizatorów ze slajdu 6 |

## 4. Co już jest bardzo dobrym fundamentem

### 4.1. Agent rozumie intencję, zamiast wymagać filtrów

To odpowiada wejściu „one plain-language message”. Użytkownik może zacząć od potrzeby albo produktu referencyjnego, a system sam buduje wymagania. Jest to mocniejszy UX niż formularz zapisanej wyszukiwarki.

### 4.2. Wariant jest filtrem, nie sugestią

Case wskazuje „same-product problem” jako jeden z najtrudniejszych elementów. Projekt już rozumie, że generacja lub wersja nie może być miękką cechą rankingu. Test dokładnej generacji AirPods jest dobrym materiałem do narracji demo.

### 4.3. Decyzja jest deterministyczna i audytowalna

LLM interpretuje dane i formułuje wyjaśnienia, natomiast filtry, ranking, cache i ryzyko kontroluje kod. To dobrze odpowiada oczekiwaniu, że agent ma móc udowodnić, dlaczego podjął decyzję.

### 4.4. System nie udaje wiedzy

Jawne `unknown`, `data_gaps`, `confidence`, źródło i czas pobrania dobrze wspierają zaufanie. Przy używanej elektronice jest to szczególnie cenne, bo bateria, oryginalność i stan często nie są weryfikowalne.

### 4.5. Jest zalążek cierpliwego agenta

Tabela `listing_snapshots`, cache, `first_seen_at`/`last_seen_at` i ponowny ranking tworzą dobrą bazę pod historię ceny i monitoring. Brakuje wykonawczej pętli i polityki strike, ale nie trzeba zaczynać od zera.

## 5. Najważniejsze rozbieżności

### 5.1. Należy wyeksponować, że rekomendacja jest scoutowaniem okazji

Obecna obietnica - „pomogę wybrać najlepszą używaną ofertę” - mieści się w case'ie. W demo trzeba jednak pokazać, że ranking nie jest zwykłym sortowaniem ogłoszeń: agent ma samodzielnie wykrywać, dlaczego dana oferta spełnia brief, a inna mimo niskiej ceny nie jest okazją. Wykorzystajcie do tego istniejące twarde dopasowanie wariantu, scoring ryzyka i jawne braki danych.

### 5.2. Cena oferty nie jest kosztem końcowym

Model przechowuje `price`, `currency` i informację, czy dostawa istnieje, ale nie ma kwot dla:

- dostawy,
- przeliczenia waluty i kursu,
- opłat/cła/podatków,
- kuponu i jego ważności,
- całkowitego kosztu dostarczonego do użytkownika.

W efekcie filtr budżetu może zaakceptować ofertę, która po doliczeniu kosztów przekracza limit. To centralna pułapka opisana przez organizatorów.

### 5.3. Granice autonomii są szansą na wyróżnienie, nie blokadą zgodności

Preferencje zakupowe nie są mandatem płatniczym. Case oczekuje rozróżnienia:

- „powiadom mnie”,
- „przygotuj checkout”,
- „kup automatycznie, ale wyłącznie w twardych warunkach”,
- „eskaluj przypadek graniczny”.

Projekt nie ma modelu zgody, limitu autonomii, odwołania mandatu ani rekordu decyzji `held / alerted / struck`. Nie blokuje to scoutowania ofert w MVP, ale nawet prosty tryb `alert_only` oraz decyzja `hold / alert` dobrze pokazałyby kluczową ideę case'u: agent działa w zdefiniowanych granicach.

### 5.4. Demo zależy od live scrapingu

Faza 4 utwardza Firecrawl i OLX. To rozsądne dla realnego produktu, lecz warto mieć obok niego kontrolowany scenariusz demonstracyjny. Organizatorzy wprost sugerują zasymulowanie merchantów, aby pokazać prawdziwą matematykę i judgment bez ryzyka niestabilnych stron. Nie jest to argument za porzuceniem scoutowania realnych ofert, tylko za uniezależnieniem kluczowego pokazu od zewnętrznych stron.

### 5.5. Brakuje dowodu fałszywie pozytywnych decyzji

Testy wykazują stabilność rankingu i odporność techniczną. Nie mierzą jednak najważniejszego ryzyka agenta wydającego pieniądze: **false-buy rate**. System powinien udowodnić, że nie „kupuje” oferty z fałszywą obniżką, niedostępnym stanem, niewłaściwym wariantem albo kosztem końcowym ponad limit.

## 6. Rekomendowana równoległa ścieżka: Deal Watch / Mandate

Nie przebudowywać obecnego flow. Dodać obok niego mały pionowy scenariusz, który wykorzystuje istniejący research, normalizację, exact-match i ranking, aby wyraźnie pokazać scoutowanie okazji narzucone w case'ie.

### Zakres weekendowy

1. **Mandat z naturalnego języka**
   - produkt i dokładny wariant,
   - maksymalny koszt końcowy,
   - wymagany stan i sprzedawca,
   - tryb: `alert_only`, `checkout_ready` albo symulowane `auto_buy`,
   - reguła graniczna: kiedy eskalować.

2. **Deterministyczny symulator rynku**
   - 6-10 zdarzeń cenowych z 2-3 fikcyjnych merchantów,
   - prawidłowa okazja,
   - fałszywa obniżka,
   - niewłaściwy wariant,
   - niski sticker price z wysoką dostawą/FX,
   - brak stocku lub niespełniony warunek sprzedawcy.

3. **Jawny landed-cost engine**
   - `item_price + shipping + duties/tax + FX cost - valid coupon`,
   - wszystkie składniki widoczne w wyniku,
   - twarde porównanie całkowitego kosztu z mandatem.

4. **Polityka decyzji**
   - `IGNORE` - warunki nie są spełnione,
   - `HOLD` - przypadek niepewny lub graniczny,
   - `ALERT` - dobra oferta wymagająca decyzji człowieka,
   - `STRIKE_SIMULATED` - wszystkie warunki mandatu spełnione.

5. **Receipt / decision log**
   - stan rynku i źródło,
   - pełny rachunek,
   - reguły, które przeszły i nie przeszły,
   - powód alertu, strike'u albo wstrzymania,
   - informacja, że zakup jest symulowany.

6. **Jedno powiadomienie**
   - tylko przy zmianie decyzji na `ALERT` lub `STRIKE_SIMULATED`,
   - deduplikacja kolejnych zdarzeń tej samej oferty,
   - brak integracji z zewnętrznym kanałem wymaganej do demo; wystarczy zdarzenie w UI/API.

### Czego nie dodawać przed demo

- realnej płatności ani integracji PSP,
- Celery/Redis i produkcyjnego schedulera,
- kolejnej kategorii,
- wielu niestabilnych scraperów,
- rozbudowanych kont i autoryzacji,
- uczenia maszynowego do scoringu,
- automatycznego zakupu bez wyraźnego oznaczenia symulacji.

## 7. Proponowany scenariusz demo zgodny z case'em

### Krok 1 - brief

> „Chcę AirPods Pro 2. gen w bardzo dobrym stanie, do 500 zł z dostawą. Tylko sprzedawca z wiarygodnymi opiniami. Jeśli koszt końcowy jest do 480 zł, kup w symulacji; między 480 a 500 zł zapytaj mnie.”

### Krok 2 - agent czeka

UI pokazuje aktywny mandat, twarde limity i brak potrzeby dalszej pracy użytkownika.

### Krok 3 - symulowane zdarzenia

- Oferta A: 449 zł + 69 zł dostawy - odrzucona, bo landed cost to 518 zł.
- Oferta B: 470 zł z dostawą, ale AirPods Pro 1. gen - odrzucona przez exact-match.
- Oferta C: „przecena z 700 zł”, ale historia pokazuje stałe 490 zł - brak fałszywego świętowania.
- Oferta D: 459 zł z dostawą, właściwy wariant i sprzedawca - `STRIKE_SIMULATED`.

### Krok 4 - dowód

System pokazuje jeden alert/strike oraz receipt: pełny rachunek, wariant, dane sprzedawcy, reguły mandatu, źródła i powód decyzji. To bezpośrednio demonstruje hasło „agentic commerce, on a leash”.

## 8. Priorytety

### P0 - konieczne dla zgodności narracji

1. Zmienić demo z jednorazowego wyszukania na aktywny mandat i sekwencję zdarzeń.
2. Dodać pełny koszt końcowy i pokazać jego składniki.
3. Dodać jawne decyzje `hold / alert / simulated strike`.
4. Przygotować case-specific eval set z pułapkami.
5. Pokazać receipt oraz powód podjęcia lub odmowy działania.

### P1 - wzmacnia efekt

1. Wykorzystać historię snapshotów do wykrycia fałszywej promocji.
2. Dodać deduplikację alertów.
3. Pozwolić użytkownikowi odwołać lub zmienić mandat.
4. Pokazać przypadek graniczny wymagający akceptacji człowieka.

### P2 - po hackathonie

1. Produkcyjny scheduler i kanały powiadomień.
2. Kolejne legalne źródła oraz realne dane o kosztach dostawy i FX.
3. Checkout API i delegowane płatności po analizie bezpieczeństwa i zgodności.
4. Konta, trwała zgoda i pełny rejestr audytowy.

## 9. Kryteria gotowości do prezentacji

Demo można uznać za zgodne z sugestiami organizatorów, jeśli:

- jeden brief tworzy aktywny, odwoływalny mandat;
- agent przetwarza serię zdarzeń bez kolejnych działań użytkownika;
- każda oferta ma policzony pełny koszt końcowy;
- niewłaściwy wariant i co najmniej trzy rodzaje pułapek są poprawnie odrzucane;
- emitowany jest najwyżej jeden istotny alert dla tej samej okazji;
- strike następuje wyłącznie w twardych granicach mandatu;
- przypadek graniczny jest eskalowany, a nie automatycznie akceptowany;
- każda decyzja ma audytowalny receipt i czytelne „dlaczego”;
- testy mierzą zarówno trafne strike'i, jak i false-buy rate;
- live scraping nie jest warunkiem powodzenia prezentacji.

## 10. Stan techniczny podczas analizy

- Lokalnie zebrano **33 testy**: **30 przeszło**, **3 testy live pominięto** zgodnie z mechanizmem opt-in.
- Kontrola stylu i błędów statycznych (`ruff`) przeszła bez uwag.
- Testy potwierdzają oba wejścia rozmowy, zachowanie kontekstu, twardy filtr wariantu, częściowy wynik po awarii źródła i wykorzystanie cache.
- Nie uruchamiano zewnętrznych testów OpenAI, Supabase ani Firecrawl, dlatego raport nie potwierdza jeszcze końcowej bramy fazy 4 ani czasu realnego demo poniżej trzech minut.
- Analiza dotyczyła bieżącego, niezacommitowanego stanu repozytorium, w którym prace fazy 4 są aktywne.

## 11. Ostateczna rekomendacja

Nie porzucać obecnego agenta do używanej elektroniki. Jego rozpoznawanie potrzeb, exact-match, ryzyko, niepewność i deterministyczny ranking są wartościowym rdzeniem.

Na hackathon należy opowiedzieć go jako:

> **Agent scoutujący oferty, któremu określasz produkt i limit. Odrzuca pozorne okazje, a gdy znajdzie właściwą ofertę, jasno pokazuje rzeczywisty koszt, ryzyko i powód rekomendacji.**

Największy przyrost zgodności da nie kolejny marketplace, lecz **kontrolowana pętla monitoring - landed cost - decyzja - uzasadnienie**.
