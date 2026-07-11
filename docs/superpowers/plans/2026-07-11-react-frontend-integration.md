# Picky React Frontend Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a React/Vite frontend that preserves the Picky prototype interactions and completes the real FastAPI shopping flow from conversation to merchant offer.

**Architecture:** A standalone TypeScript frontend owns presentation state and calls FastAPI through a Vite `/api` proxy. A typed API module isolates transport while focused React components render conversation, product selection, search progress, and ranked offers.

**Tech Stack:** React 19, TypeScript 5, Vite 7, Vitest, Testing Library, CSS.

## Global Constraints

- Root `DESIGN.md` is authoritative for color, typography, layout, motion, accessibility, and copy.
- Preserve the general demonstration logic from `prototype/znajdz`.
- Do not implement image upload, authentication, history, payments, or checkout.
- Merchant actions open the backend-provided offer URL.
- The primary target is a reliable localhost demo.

---

### Task 1: Frontend foundation and typed API

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/types.ts`
- Test: `frontend/src/api/client.test.ts`

**Interfaces:**
- Produces: `createSession()`, `sendMessage(sessionId, message)`, `selectProduct(sessionId, productId, direction)`, `getRun(runId)`, and `refreshRun(runId)`.

- [ ] Create the Vite/React/TypeScript package and proxy `/api` to `http://localhost:8000` after stripping the `/api` prefix.
- [ ] Define API response types matching `app/api/sessions.py` and `app/api/runs.py`.
- [ ] Implement a fetch wrapper that parses backend error details and throws a typed `ApiError`.
- [ ] Test successful JSON parsing and useful error messages with mocked `fetch`.
- [ ] Run `npm test -- --run`; expect all API tests to pass.

### Task 2: State machine and real backend flow

**Files:**
- Create: `frontend/src/state/useShoppingSession.ts`
- Create: `frontend/src/state/demo.ts`
- Create: `frontend/src/state/presentation.ts`
- Test: `frontend/src/state/presentation.test.ts`

**Interfaces:**
- Consumes: API functions from Task 1.
- Produces: `ShoppingSessionViewModel` with phase, messages, candidates, selected product, recommendations, progress, error, and actions.

- [ ] Implement lazy session creation on the first submitted message.
- [ ] Handle clarifying questions without leaving conversation mode.
- [ ] Map candidates into the product stage and submit selection direction to the backend.
- [ ] Poll runs every 1.5 seconds until `completed`, `partial`, or `failed`, with an overall demo timeout.
- [ ] Preserve the user's message when a request fails and expose retry actions.
- [ ] Add an explicitly labeled demo dataset used only after the user chooses demo mode.
- [ ] Test money, status, score, and missing-data presentation helpers.

### Task 3: Picky interface and preserved demo interactions

**Files:**
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/components/Header.tsx`
- Create: `frontend/src/components/Conversation.tsx`
- Create: `frontend/src/components/Composer.tsx`
- Create: `frontend/src/components/ProductStage.tsx`
- Create: `frontend/src/components/ProductCard.tsx`
- Create: `frontend/src/components/SearchProgress.tsx`
- Create: `frontend/src/components/OfferRanking.tsx`
- Create: `frontend/src/components/HeadphoneVisual.tsx`

**Interfaces:**
- Consumes: `ShoppingSessionViewModel` from Task 2.
- Produces: keyboard-accessible UI for every application phase.

- [ ] Build the sparse conversation-first opening screen with example prompts.
- [ ] Build the candidate stage with one dominant product and visible neighboring cards.
- [ ] Preserve select, cheaper alternative, next variant, and remove behaviors without pretending they are backend mutations.
- [ ] Disable image attachment with explanatory tooltip text.
- [ ] Build named searching states with an `aria-live` announcement.
- [ ] Build a ranked offer list with three separate scores, risks, data gaps, source time, and safe merchant links.
- [ ] Add header integration hooks for the separately implemented history and account features.

### Task 4: Visual system, accessibility, and responsiveness

**Files:**
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/styles/global.css`
- Create: `frontend/src/styles/components.css`

**Interfaces:**
- Consumes: semantic class names from Task 3.
- Produces: the complete responsive Picky visual system.

- [ ] Encode the exact root `DESIGN.md` color, spacing, radius, shadow, and typography tokens.
- [ ] Implement a desktop conversation/stage composition and a single-column mobile flow.
- [ ] Keep blue limited to intent, selection, and the primary next action.
- [ ] Add visible focus rings, minimum 44px targets, semantic status styles, and 200% text resilience.
- [ ] Implement the conversation-to-focus transition and disable spatial motion for `prefers-reduced-motion`.
- [ ] Verify layouts at 375px, 768px, and 1440px widths.

### Task 5: Documentation and verification

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: completed frontend and existing backend.
- Produces: reproducible local startup and verification instructions.

- [ ] Document backend and frontend startup commands and the localhost URLs.
- [ ] Ignore frontend dependencies, build output, and coverage.
- [ ] Run `npm test -- --run`; expect all frontend tests to pass.
- [ ] Run `npm run build`; expect TypeScript and Vite production build success.
- [ ] Run `.venv/bin/ruff check app tests scripts`; expect no lint failures.
- [ ] Run `.venv/bin/pytest`; expect the existing backend suite to pass.
- [ ] Complete a browser smoke test for the start, question, candidate, searching, result, partial, and error states.
