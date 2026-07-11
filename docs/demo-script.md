# Picky — scenariusz prezentacji

## Przygotowanie

1. Uruchom backend na `http://127.0.0.1:8000`.
2. Uruchom frontend na `http://127.0.0.1:5173`.
3. Otwórz czystą kartę przeglądarki i sprawdź `GET /health`.
4. Nie uruchamiaj testów live podczas prezentacji.

## Główny przebieg — cel poniżej 3 minut

1. Wpisz: „Chcę słuchawki podobne do AirPods Pro, z dobrym ANC, ale tańsze i niekoniecznie Apple.”
2. Zwróć uwagę, że pierwsza lista jest eksploracją 4–6 modeli i od razu pokazuje ceny oraz kompromisy.
3. Wybierz kierunek „Najlepsza wartość” i model Sony WF-1000XM5 lub pierwszą trafną propozycję live.
4. Przy rekomendowanej ofercie pokaż osobno: dopasowanie produktu, jakość oferty i wiarygodność sprzedawcy.
5. Pokaż dokładny wariant, źródło, czas pobrania, ryzyka i jawnie oznaczone braki danych.
6. Otwórz „Zobacz ofertę” w nowej karcie.
7. W tej samej rozmowie wpisz: „Ważniejsza jest gwarancja niż najniższa cena”.
8. Pokaż, że ranking zmienia się bez resetu rozmowy i bez ponownego pełnego researchu.

## Kontrolowany fallback

Jeśli usługi live nie odpowiedzą, na ekranie błędu wybierz „Uruchom dane demonstracyjne”. Banner musi przez cały czas informować, że dane są przygotowane. Następnie wpisz zmianę priorytetu dotyczącą gwarancji — oferta z roczną gwarancją powinna znaleźć się na pierwszym miejscu.

## Zapasowy dowód techniczny

Deal Watch działa bez usług zewnętrznych. Symulacja sześciu zdarzeń powinna dać dokładnie jeden `alert`, jeden `hold` i cztery `ignore`, pokazując pełny koszt, zły wariant, brak dostępności i fałszywą obniżkę.
