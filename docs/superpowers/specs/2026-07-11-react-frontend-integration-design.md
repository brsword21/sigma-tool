# Picky React Frontend Integration Design

## Understanding summary

- Build a React frontend from the interaction and layout ideas in `prototype/znajdz`.
- Treat the root `DESIGN.md` as the authoritative visual and UX specification.
- Preserve the prototype's product stage, selection, cheaper-alternative, variant, and remove interactions.
- Connect the real FastAPI flow: create session, send messages, select a candidate, poll a run, and present ranked offers.
- Leave authentication and usage history as integration boundaries because they are being implemented separately.
- End the purchase journey by opening the merchant URL; no payments or checkout are in scope.
- Keep the attachment affordance visible but disabled; image upload is explicitly deferred.

## Assumptions and non-functional requirements

- The frontend is a Vite + React + TypeScript application in `frontend/`.
- Vite proxies `/api` to `http://localhost:8000`; the backend continues to run separately.
- Local demo reliability matters more than production deployment configuration.
- Search may take tens of seconds, so the UI polls without showing invented percentages.
- Demo fallback data is explicit and never silently replaces a failed live request.
- No secrets, payment data, or persistent personal data are stored in the browser.
- The UI meets the responsive, keyboard, reduced-motion, and WCAG 2.2 AA goals in `DESIGN.md`.

## Approaches considered

1. Serve the existing static prototype from FastAPI. Lowest effort, but poor long-term component boundaries.
2. Keep the existing prototype on a separate static server. Preserves code but makes state and API integration brittle.
3. Build a separate React/Vite application. Chosen because it preserves the demo concept while creating maintainable state, component, and API boundaries.

## Final design

The application uses a conversation-first shell. The opening state is deliberately sparse. Once the backend returns candidates, the last request condenses into a preference summary while a single dominant product card appears on the stage. Selecting a model starts the real offer run. The stage then gives way to a ranked, evidence-oriented offer view with product fit, offer quality, and seller confidence shown separately.

The frontend state machine is `idle → conversing → selecting → searching → results`, with recoverable `error` and explicit `demo` annotations. API access is isolated in a typed client. Polling stops on `completed`, `partial`, or `failed`, and is cancellable when a new run begins or the component unmounts.

The visual system follows `DESIGN.md`: white canvas, quiet gray surfaces, `#101114` ink, and `#1769FF` only for intent and active state. Inter is used for interface text and Manrope for product names, prices, and major headings. The memorable gesture is the transition from a conversation to one focused product decision. Motion is restrained and removed when requested by the operating system.

Authentication and history appear only as stable header hooks. Image attachment remains visible but disabled with a clear explanation. Merchant links open in a new tab with safe relationship attributes.

## Error and edge-case behavior

- Session creation and message failures keep the user's draft and offer a retry.
- A clarifying backend question remains in conversation mode.
- Empty candidates produce a directed empty state rather than a blank stage.
- Search polling reports named tasks and times out with a retry action.
- Partial runs show available recommendations plus the backend's missing-source information.
- Failed runs do not fabricate merchant offers; the user can retry or intentionally enter the labeled demo scenario.
- Missing product images use a code-native headphone illustration, not a misleading product photograph.

## Testing strategy

- Type-check and production-build the React app.
- Unit-test API URL handling and key presentation helpers.
- Run the existing Python test suite to ensure backend behavior is unchanged.
- Exercise the full mocked localhost journey in a browser at desktop and mobile widths.
- Verify keyboard focus, reduced motion, loading, partial, empty, and error states.

## Decision log

| Decision | Alternatives | Reason |
|---|---|---|
| React + Vite + TypeScript | Static HTML, server-rendered frontend | Maintains demo velocity with clearer state and API contracts. |
| Separate dev servers with a Vite proxy | Hard-coded backend URL, FastAPI static hosting | Keeps backend unchanged and avoids browser CORS complexity. |
| Root `DESIGN.md` is authoritative | Preserve prototype palette and name | Explicit user direction and consistent Picky product identity. |
| Preserve stage interactions | Replace prototype with a conventional results page | The stage is the prototype's strongest demo behavior. |
| Explicit demo fallback | Silent fallback | Maintains trust and avoids presenting synthetic data as live. |
| Defer image upload | Add a speculative endpoint | The user explicitly requested no image upload yet. |
