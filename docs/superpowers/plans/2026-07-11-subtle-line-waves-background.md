# Subtle LineWaves Background Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render a quiet, white animated line-wave background behind the complete Picky interface.

**Architecture:** A focused `LineWaves` React component owns the OGL canvas lifecycle and exposes only visual configuration. `App` mounts it once, while a dedicated stylesheet fixes the visual layer behind all interactive content and provides the static fallback for reduced motion or unavailable WebGL.

**Tech Stack:** React, TypeScript, OGL, CSS, Vite.

## Global Constraints

- Render one fixed, non-interactive background across the complete viewport.
- Use white waves with low brightness and low speed; do not enable mouse interaction.
- Keep existing interface panels readable above the background.
- Hide the canvas under `prefers-reduced-motion: reduce` while retaining a static light background.
- Preserve normal operation when WebGL is unavailable.

---

### Task 1: Add the background renderer and visual layer

**Files:**

- Create: `frontend/src/components/LineWaves.tsx`
- Create: `frontend/src/styles/line-waves.css`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles/components.css`
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/package.json`

**Interfaces:**

- Consumes: OGL `Renderer`, `Program`, `Mesh`, and `Triangle`.
- Produces: `LineWaves({ speed, brightness, enableMouseInteraction })`, a decorative component with no user-facing controls.

- [ ] **Step 1: Add the OGL dependency**

Run `npm install ogl` from `frontend/`. Expect `frontend/package.json` and `frontend/package-lock.json` to contain `ogl`.

- [ ] **Step 2: Create the renderer component**

Create `frontend/src/components/LineWaves.tsx` with the supplied fullscreen vertex and fragment shader. Its public contract is:

```tsx
export function LineWaves({
  speed = 0.12,
  brightness = 0.055,
  enableMouseInteraction = false,
}: {
  speed?: number
  brightness?: number
  enableMouseInteraction?: boolean
}) {
  return <div className="line-waves" aria-hidden="true" />
}
```

Initialise `Renderer({ alpha: true, premultipliedAlpha: false })`, update `uTime` through `requestAnimationFrame`, synchronise `uResolution` on resize, and release the frame, listeners, canvas, and WebGL context on cleanup. Use `#ffffff` for all shader colours, `innerLineCount=30`, `outerLineCount=34`, `warpIntensity=0.8`, `rotation=-45`, and `edgeFadeWidth=0`. Catch renderer creation errors and leave the element empty so the CSS fallback stays visible.

- [ ] **Step 3: Layer the visual safely**

Create `frontend/src/styles/line-waves.css` with these rules:

```css
.line-waves { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; background: radial-gradient(circle at 20% 5%, #f8fbff 0, transparent 42%), linear-gradient(135deg, #f5f8fe, #ffffff 58%, #f4f7fc); }
.line-waves canvas { width: 100%; height: 100%; display: block; opacity: .72; }
.app { position: relative; isolation: isolate; background: transparent; }
.app > :not(.line-waves) { position: relative; z-index: 1; }
.conversation, .decision { background: rgba(255, 255, 255, .78); backdrop-filter: blur(18px); }
@media (prefers-reduced-motion: reduce) { .line-waves canvas { display: none; } }
```

Import this stylesheet after `components.css` in `frontend/src/main.tsx`. Change `.decision` in `frontend/src/styles/components.css` from an opaque surface to `rgba(245, 247, 251, .78)`.

- [ ] **Step 4: Mount the component exactly once**

In `frontend/src/App.tsx`, add `import { LineWaves } from './components/LineWaves'`. Place `<LineWaves />` immediately inside the root app `<div>`, before the header.

- [ ] **Step 5: Verify compilation and behaviour**

Run `npm run build` from `frontend/`. Expect TypeScript checks and Vite production build to pass. Inspect desktop and mobile widths: waves cover the viewport; links and controls remain clickable; modal and drawer overlays stay above the waves; reduced motion shows only static background.

- [ ] **Step 6: Commit**

Run `git add frontend/package.json frontend/package-lock.json frontend/src/App.tsx frontend/src/main.tsx frontend/src/components/LineWaves.tsx frontend/src/styles/components.css frontend/src/styles/line-waves.css` followed by `git commit -m "feat: add subtle animated background"`.
