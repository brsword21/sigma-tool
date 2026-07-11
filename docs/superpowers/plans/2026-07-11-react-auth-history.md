# React Auth and Chat History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Supabase Magic Link authentication and private chat-history navigation to the React Picky frontend.

**Architecture:** A React auth provider owns the Supabase browser session and supplies access tokens to the existing API client. FastAPI remains responsible for session ownership and message persistence; UI components only request authenticated history and render it.

**Tech Stack:** React, TypeScript, Vite, Supabase JS v2, Vitest, FastAPI, PostgreSQL RLS.

## Global Constraints

- Guest usage remains available and guest conversations are not migrated.
- Never expose `SUPABASE_SERVICE_ROLE_KEY` to the browser.
- Invalid Bearer credentials must not fall back to guest mode.
- Preserve unrelated working-tree changes and do not commit without explicit permission.
- Keep the interface responsive, keyboard accessible, and reduced-motion aware.

---

### Task 1: Auth client and API contract

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/auth/supabase.ts`
- Create: `frontend/src/auth/AuthProvider.tsx`
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/api/client.ts`
- Test: `frontend/src/api/client.test.ts`

**Interfaces:**
- Produces: `setAccessTokenProvider(provider: () => Promise<string | null>): void`.
- Produces: `useAuth(): { status, user, signInWithMagicLink, signOut }`.
- Produces: `listHistory()` and `getSessionHistory(sessionId)`.

- [ ] Add Supabase JS v2 and environment validation without embedding credentials.
- [ ] Write API-client tests proving Bearer attachment and guest omission.
- [ ] Implement the token provider and typed history endpoints.
- [ ] Run `npm test -- --run` and confirm the API tests pass.

### Task 2: Account and history interface

**Files:**
- Create: `frontend/src/components/AuthModal.tsx`
- Create: `frontend/src/components/AccountControls.tsx`
- Create: `frontend/src/components/HistoryDrawer.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles/components.css`
- Modify: `frontend/src/styles/global.css`

**Interfaces:**
- Consumes: `useAuth`, `listHistory`, `getSessionHistory`.
- Produces: accessible modal and drawer with loading, empty, success, and failure states.

- [ ] Build the Magic Link form with email validation and precise pending/success/error copy.
- [ ] Build account controls and a private history drawer with the memory-rail signature.
- [ ] Integrate controls into the existing top bar without disturbing shopping results.
- [ ] Verify keyboard focus, labels, mobile layout, and reduced motion.

### Task 3: Restore and reset chat state

**Files:**
- Modify: `frontend/src/state/useShoppingSession.ts`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `SessionHistoryResponse`.
- Produces: `restoreHistory(history)` and `reset()` on `useShoppingSession`.

- [ ] Add deterministic restoration of saved messages and current session ID.
- [ ] Reset the active session when starting a new chat or changing account identity.
- [ ] Keep restored history read/write capable for follow-up messages.
- [ ] Confirm guest chats remain local-only.

### Task 4: Configuration, verification, and security review

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `frontend/src/vite-env.d.ts`

**Interfaces:**
- Documents: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`.

- [ ] Document frontend environment values, Site URL, redirect URL, and migration order.
- [ ] Run `npm test -- --run` and `npm run build` in `frontend`.
- [ ] Run targeted backend auth/history tests and the complete Python test suite.
- [ ] Run `git diff --check` and inspect the feature diff for tokens, owner leaks, and unrelated edits.

