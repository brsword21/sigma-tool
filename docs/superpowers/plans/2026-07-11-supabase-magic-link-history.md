# Supabase Magic Link and Chat History Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with a test-first checkpoint after each backend unit.

**Goal:** Add optional Supabase magic-link login and persist chat history only for signed-in users.

**Architecture:** The browser owns the Supabase Auth session and sends its access token to FastAPI. FastAPI validates optional Bearer tokens, assigns authenticated sessions to a user, persists messages, and filters history by the verified owner.

**Tech Stack:** Python 3.12, FastAPI, Supabase Python client, PostgreSQL RLS, vanilla JavaScript, Supabase JS v2, Tailwind CDN, pytest.

## Global Constraints

- Guest usage must remain available without authentication.
- Guest conversations are not migrated after sign-in.
- The service-role key must never be exposed to the browser.
- Invalid supplied credentials return `401`; they never fall back to guest mode.
- Do not modify or discard unrelated working-tree changes.
- Do not create commits without an explicit user request.

---

### Task 1: Database ownership and messages

**Files:**
- Create: `supabase/migrations/003_auth_chat_history.sql`
- Test: `tests/repositories/test_session_history.py`

**Interfaces:**
- Sessions gain nullable `user_id uuid references auth.users(id)`.
- Messages expose `id`, `session_id`, `role`, `content`, and `created_at`.
- RLS owner predicate is `(select auth.uid()) = user_id` or the owning session's `user_id`.

- [ ] Add the nullable owner column, indexes, message table, grants, RLS, and owner policies.
- [ ] Add repository tests proving create/list/filter behavior and chronological message ordering.
- [ ] Run `pytest tests/repositories/test_session_history.py -v` and confirm it passes.

### Task 2: Optional authentication boundary

**Files:**
- Create: `app/auth/models.py`
- Create: `app/auth/service.py`
- Modify: `app/config.py`
- Modify: `app/api/dependencies.py`
- Modify: `app/bootstrap.py`
- Test: `tests/api/test_auth.py`

**Interfaces:**
- `AuthenticatedUser(id: UUID, email: str | None)` represents verified identity.
- `AuthVerifier.verify(access_token: str) -> AuthenticatedUser | None` validates with Supabase.
- `get_optional_user(request, services) -> AuthenticatedUser | None` treats a missing header as guest and rejects malformed/invalid supplied credentials.

- [ ] Write dependency tests for missing, valid, malformed, and invalid Bearer credentials.
- [ ] Implement the verifier and optional dependency using centralized settings.
- [ ] Run `pytest tests/api/test_auth.py -v` and confirm it passes.

### Task 3: Owned sessions and persisted messages

**Files:**
- Modify: `app/repositories/protocols.py`
- Modify: `app/repositories/supabase.py`
- Modify: `app/api/dependencies.py`
- Modify: `app/api/sessions.py`
- Modify: `tests/api/helpers.py`
- Create: `tests/api/test_chat_history.py`

**Interfaces:**
- `SessionRepository.create(user_id: UUID | None = None) -> UUID`.
- `SessionRepository.list_for_user(user_id: UUID) -> list[dict]`.
- `MessageRepository.add(session_id, role, content) -> UUID`.
- `MessageRepository.list_for_session(session_id) -> list[dict]`.
- `GET /sessions/history` requires login and returns owned sessions.
- `GET /sessions/{session_id}/history` requires the session owner.

- [ ] Write API tests for guest compatibility, authenticated persistence, history ordering, and cross-user denial.
- [ ] Implement repositories and route ownership checks.
- [ ] Save the user message and a concise assistant transcript entry during the existing conversation flow.
- [ ] Run `pytest tests/api/test_chat_history.py tests/api/test_happy_path.py -v` and confirm it passes.

### Task 4: Magic-link and history interface

**Files:**
- Modify: `prototype/znajdz/index.html`
- Create: `prototype/znajdz/config.example.js`
- Modify: `prototype/znajdz/README.md`

**Interfaces:**
- `window.SIGMA_CONFIG` provides `supabaseUrl`, `supabasePublishableKey`, and `apiBaseUrl`.
- The auth modal uses `signInWithOtp({ email, options: { emailRedirectTo } })`.
- Authenticated requests use `Authorization: Bearer <access_token>`.

- [ ] Add a precise account row in the existing settings menu and a modal matching the paper/ink/acid visual language.
- [ ] Add accessible pending, success, error, signed-in, history, empty, and signed-out states.
- [ ] Persist new authenticated prototype messages and render the owned history list.
- [ ] Add setup instructions for `config.js`, Supabase Site URL, and allowed redirect URLs.

### Task 5: Verification and documentation

**Files:**
- Modify: `.env.example`
- Modify: `README.md`

- [ ] Document backend Auth configuration and migration order without exposing secrets.
- [ ] Run `ruff check app tests scripts`.
- [ ] Run the complete `pytest` suite.
- [ ] Run `git diff --check` and inspect only files in this feature's scope.
- [ ] Perform a final security review for token leakage, owner filters, RLS, error details, and browser configuration.

