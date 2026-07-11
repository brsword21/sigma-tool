# React Auth and Chat History Design

## Understanding summary

- Picky keeps guest shopping available without an account.
- Signed-in users authenticate with Supabase Magic Link.
- Only signed-in conversations are persisted and visible in account history.
- Guest conversations are not migrated after sign-in.
- FastAPI remains the authority for session ownership and message persistence.
- Supabase RLS and backend ownership checks isolate every user's data.
- The React interface adds account, login, history, empty, loading, and error states.

## Assumptions

- Early-stage scale: thousands of users and hundreds of conversations per account.
- The current unpaginated history endpoint is sufficient for the first release.
- A conversation title is derived from the backend `message_summary`/first user message.
- The browser uses only Supabase's public URL and publishable key.
- Password login, social login, profile editing, chat deletion, and guest-history migration are out of scope.

## Final design

The React app owns the Supabase browser session through a small authentication provider. The API client receives an asynchronous token provider and adds a Bearer header to every request when a session exists. FastAPI validates that token and persists messages for owned sessions; guests continue to use the same endpoints without an Authorization header.

The top bar gains two compact controls: History and Account. Account opens a focused Magic Link dialog when signed out and a small account menu when signed in. History opens a right-side drawer containing the user's conversations. Opening a history item loads its messages into the conversation column; starting a new chat resets the local shopping session.

Visual direction: retain Picky's white technical workspace, blue decision accent, Manrope/Inter typography, and restrained geometry. The signature detail is a vertical blue "memory rail" in the history drawer that connects conversation timestamps, making saved decisions read as a trace rather than a generic list. Motion is limited to the dialog/drawer entrance and is disabled under reduced-motion preferences.

## Security and reliability

- No service-role credential or access token is rendered or logged.
- Invalid supplied credentials return 401 and never silently downgrade to guest mode.
- History endpoints require an authenticated user and enforce ownership.
- Auth failures have actionable Polish copy; failure to load history does not block a new guest chat.
- Email input is constrained in the UI and validated by Supabase.

## Decision log

1. **Supabase Auth in React + FastAPI persistence.** Chosen over direct browser writes and backend cookie sessions because it matches the existing backend and migration with the least duplicated logic.
2. **Guest mode remains first-class.** Chosen to preserve the current zero-friction product flow.
3. **No guest-history migration.** Chosen to avoid ambiguous ownership and hidden data transfer.
4. **Drawer plus modal.** Chosen because history is contextual navigation while login is a focused, interruptive action.
5. **Backend-generated ownership boundary.** Chosen so UI state can never determine access to stored chats.

