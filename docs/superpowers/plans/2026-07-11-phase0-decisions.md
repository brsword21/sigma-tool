# Faza 0 — Zapis decyzji blokujących

Data: 2026-07-11  
Status: **ZAMKNIĘTA**

---

## Decyzje

| # | Punkt z checklisty | Decyzja |
|---|---|---|
| 1 | Model LLM | **OpenAI `gpt-4o-mini`** — SDK `openai` (Python), structured output via `response_format={"type":"json_schema"}`, rate limit: Tier 1 domyślnie |
| 2 | Supabase | Projekt do założenia przez właściciela na supabase.com; wymagane: `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`. Zgoda na wykonanie migracji w środowisku dev. |
| 3 | Scraper OLX | **Brak gotowego scrapera.** Firecrawl jest **jedynym i głównym źródłem** ogłoszeń w MVP. Adapter `OlxFirecrawlSource` implementuje `ListingSource` i używa Firecrawl do scrapowania OLX. |
| 4 | Firecrawl | **Wchodzi do MVP** jako source primary. Klucz `FIRECRAWL_API_KEY` dostarcza właściciel. |
| 5 | BackgroundTasks | **Tak** — `POST /sessions/{id}/products/{pid}/select` zwraca `run_id` natychmiast; praca idzie w `FastAPI BackgroundTasks`; frontend polluje `GET /runs/{run_id}`. |
| 6 | Środowisko demo | **Lokalnie** — backend `localhost:8000`, CORS: `http://localhost:3000`, `http://localhost:5173`. |
| 7 | Worktree/gałęzie | **Utworzone:** `feat/integrator`, `feat/worker-a`, `feat/worker-b`. Integrator = jedyna osoba scalająca do `main`. |

---

## Konsekwencje dla zakresów Fazy 2

### Worker B (2B) — korekta zakresu

Oryginalny plan zakładał owinięcie istniejącego scrapera OLX.  
**Nowy zakres:** napisać `app/sources/firecrawl.py` implementujący `ListingSource` jako primary source (nie fallback).  
Fixture'y testowe tworzymy ręcznie lub przez nagranie realnej odpowiedzi Firecrawl.

### Worker A (2A) — bez zmian

Migracje, repozytoria, cache — zakres niezmieniowy.

### Integrator — bez zmian

Kontrakty, rozmowa, LLM, orkiestracja — zakres niezmieniony.

---

## Brakujące sekrety (właściciel dostarcza przed Fazą 2)

- [ ] `OPENAI_API_KEY` — klucz OpenAI
- [ ] `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` — po założeniu projektu Supabase
- [ ] `FIRECRAWL_API_KEY` — klucz Firecrawl

Docelowo umieszczone w pliku `.env` (na podstawie `.env.example`, `.env` w `.gitignore`).

---

## Jak założyć projekt Supabase (5 minut)

1. Wejdź na [supabase.com](https://supabase.com) → **New project**.
2. Wybierz region (np. `eu-central-1` Frankfurt dla niskiego ping z PL).
3. Po utworzeniu: **Settings → API** → skopiuj `Project URL` i `service_role` (secret key).
4. Wklej do `.env`:
   ```
   SUPABASE_URL=https://<ref>.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   ```
5. Migracje SQL uruchomimy w Fazie 2A przez `supabase db push` lub ręczne wykonanie pliku SQL w SQL Editor.

---

## Brama wejścia do Fazy 1

Faza 1 może wystartować natychmiast — nie wymaga żywych sekretów.  
Faza 2 (integracja) startuje dopiero gdy:
- `.env` ma wszystkie trzy klucze,
- smoke test `python -c "import openai, supabase, firecrawl"` przechodzi.
