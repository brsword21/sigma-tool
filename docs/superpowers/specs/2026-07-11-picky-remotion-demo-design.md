# Picky — minutowe demo Remotion

## Cel

Stworzyć kontrolowane, poziome demo Picky pokazujące pełny proces wyboru używanej elektroniki. Film ma trwać dokładnie 60 sekund, mieć rozdzielczość 1920×1080 i działać bez usług live.

## Odbiorca i przekaz

Materiał ma szybko wyjaśniać, że Picky nie tylko wyszukuje ogłoszenia: najpierw zawęża produkt, potem porównuje konkretne oferty, a na końcu aktualizuje rekomendację, gdy zmienia się priorytet kupującego. Nie ma lektora ani dodatkowych plansz narracyjnych; znaczenie niesie istniejący tekst interfejsu i ruch.

## Przebieg (60 s)

| Czas | Ujęcie | Akcja |
| --- | --- | --- |
| 0–6 s | Szeroki start | Interfejs Picky pojawia się z łagodnym najazdem kamery. |
| 6–14 s | Close-up kompozytora | Wpisywane jest zapytanie o słuchawki podobne do AirPods Pro, z dobrym ANC i niższą ceną. |
| 14–26 s | Widok modeli | Pojawiają się cztery propozycje; kamera prowadzi wzrok do Sony WF-1000XM5 i przycisku sprawdzania ofert. |
| 26–34 s | Weryfikacja | Krótkie, rytmiczne przejście przez stan sprawdzania modelu, źródeł i wariantów. |
| 34–48 s | Ranking ogłoszeń | Wyniki ofert pojawiają się kaskadowo. Dynamiczne zbliżenia pokazują cenę, stan, gwarancję, zwroty oraz trzy składowe wyniku. |
| 48–57 s | Zmiana potrzeby | W kompozytorze pojawia się priorytet gwarancji; karta z 12-miesięczną gwarancją przesuwa się na pierwszą pozycję. |
| 57–60 s | Finał | Kamera oddala się na zaktualizowany ranking i spokojnie wygasza ujęcie. |

## Materiał i mechanika

- Remotion renderuje repliki kluczowych stanów interfejsu, oparte na stylistyce obecnego frontendu Picky.
- Dane są deterministyczne: cztery kandydatury i trzy przykładowe ogłoszenia Sony WF-1000XM5 z obecnego trybu demonstracyjnego.
- Kamera to animowane kadrowanie sceny, a nie nagrany ekran. Dzięki temu typografia pozostaje ostra w close-upach.
- Przejścia korzystają z interpolowanej pozycji, skali i krycia; kliknięcia podkreślają krótkie rozbłyski oraz lokalne przesunięcia elementów.
- Bez kursora, dźwięku, zewnętrznych materiałów i połączeń sieciowych.

## Kompozycja i komponenty

Główna kompozycja `PickyDemo` ma 30 fps, 1800 klatek i wymiar 1920×1080. Dzieli film na pięć izolowanych scen: `PromptScene`, `ProductSelectionScene`, `VerificationScene`, `OfferRankingScene` oraz `PriorityUpdateScene`. Wspólne elementy, takie jak ramka aplikacji, karta ogłoszenia, wskaźnik wyniku i ruch kamery, pozostają osobnymi komponentami. Każda scena przyjmuje wyłącznie czas lokalny i statyczne dane demo.

## Błędy i weryfikacja

Nie występują błędy usług, ponieważ film nie wywołuje API. Implementacja ma dać się uruchomić lokalnym podglądem oraz wyrenderować do MP4. Weryfikacja obejmie kontrolę czasu trwania, rozdzielczości, build TypeScript i oględziny klatek z początku, każdego przejścia oraz końca filmu.
