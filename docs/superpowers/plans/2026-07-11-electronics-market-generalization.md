# Electronics Market Generalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Usunąć założenie, że Picky obsługuje wyłącznie słuchawki, i poprawnie obsłużyć dowolną kategorię używanej elektroniki.

**Architecture:** Zachować obecny przepływ, ale zmienić neutralny stan początkowy modelu i instrukcje LLM. Frontend zachowuje układ, używa neutralnego copy i uniwersalnej ilustracji produktu.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, pytest, React, TypeScript, Vite, Vitest.

## Global Constraints

- Bez nowych zależności i dodatkowych wywołań LLM.
- Bez zmian w autoryzacji, źródłach ofert i algorytmie rankingu.
- Słuchawki nadal muszą działać jako jedna z kategorii.

---

### Task 1: Regresja kategorii w rozmowie

**Files:**
- Modify: `tests/conversation/test_service.py`
- Modify: `app/conversation/service.py`
- Modify: `app/domain/models.py`

**Interfaces:**
- Consumes: `ConversationService.handle_message(message, current)`
- Produces: neutralny `Requirements.category` i prompt wymagający kategorii właściwej dla wiadomości

- [x] Dodać test sprawdzający neutralną kategorię domyślną i treść promptu dla Samsung S25.
- [x] Uruchomić test i potwierdzić regresję.
- [x] Uogólnić prompt i wartość domyślną kategorii.
- [x] Uruchomić testy rozmowy.

### Task 2: Neutralny research i ranking

**Files:**
- Modify: `app/product_research/service.py`
- Modify: `app/ranking/explanations.py`
- Modify: `app/ranking/engine.py`

**Interfaces:**
- Consumes: produkt z dynamiczną kategorią i brief produktu
- Produces: kategoriowo neutralny research i opis rekomendacji

- [x] Zastąpić instrukcje dotyczące słuchawek instrukcjami właściwymi dla dowolnej elektroniki.
- [x] Zastąpić deterministyczne sformułowanie „tych słuchawek” sformułowaniem „tego urządzenia”.
- [x] Uruchomić testy researchu i rankingu.

### Task 3: Neutralny interfejs

**Files:**
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: istniejący `Candidate`, w tym opcjonalne `image_url`
- Produces: neutralny ekran startowy i fallback wizualny dla dowolnej elektroniki

- [x] Zmienić przykłady, nagłówek i etykietę baterii/zasilania.
- [x] Zastąpić `HeadphoneMark` uniwersalnym `ElectronicsMark`.
- [x] Wyświetlać `candidate.image_url` przed fallbackiem.
- [x] Uruchomić testy i build frontendu.

### Task 4: Weryfikacja całości

**Files:**
- Verify: `tests/`
- Verify: `frontend/`

**Interfaces:**
- Consumes: zmiany z Tasks 1–3
- Produces: potwierdzenie braku regresji

- [x] Uruchomić pełny zestaw testów backendu.
- [x] Uruchomić testy frontendu.
- [x] Zbudować frontend produkcyjnie.
- [x] Przeszukać aktywny kod pod kątem pozostałych założeń o słuchawkach.
