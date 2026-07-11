# Picky Remotion Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render a 60-second, 1920×1080 MP4 that demonstrates Picky's complete recommendation workflow with deterministic demo listings.

**Architecture:** Create a standalone Remotion package under `video/` so the application and its existing dependencies remain untouched. A single root composition drives five time-bounded scene components, while shared UI primitives render the Picky window, product cards, offer cards, and animated camera framing from static scene data.

**Tech Stack:** React, TypeScript, Remotion, CSS, Remotion CLI/FFmpeg.

## Global Constraints

- Exact duration: 1800 frames at 30 fps (60 seconds).
- Canvas: 1920×1080, horizontal 16:9.
- Use only deterministic local data; no API calls, assets, audio, narration, external text overlays, or cursor.
- Keep the Picky UI copy in Polish and base sample products/offers on `frontend/src/state/demo.ts`.
- Place the rendered deliverable at `video/out/picky-demo.mp4`.

---

### Task 1: Scaffold the isolated Remotion project

**Files:**
- Create: `video/package.json`
- Create: `video/tsconfig.json`
- Create: `video/remotion.config.ts`
- Create: `video/src/index.ts`
- Create: `video/src/Root.tsx`

**Interfaces:**
- Produces `PickyDemo` composition with `id: 'PickyDemo'`, `fps: 30`, `durationInFrames: 1800`, `width: 1920`, and `height: 1080`.
- Consumed by `npx remotion render src/index.ts PickyDemo out/picky-demo.mp4`.

- [ ] **Step 1: Create the manifest and TypeScript configuration**

```json
{
  "scripts": {
    "start": "remotion studio src/index.ts",
    "render": "remotion render src/index.ts PickyDemo out/picky-demo.mp4",
    "still": "remotion still src/index.ts PickyDemo out/preview.png --frame=1080"
  },
  "dependencies": {
    "@remotion/cli": "latest",
    "@remotion/renderer": "latest",
    "remotion": "latest",
    "react": "latest",
    "react-dom": "latest"
  },
  "devDependencies": {"@types/react": "latest", "typescript": "latest"}
}
```

- [ ] **Step 2: Register the composition**

```tsx
import {Composition} from 'remotion';
import {PickyDemo} from './PickyDemo';

export const RemotionRoot = () => (
  <Composition id="PickyDemo" component={PickyDemo} durationInFrames={1800} fps={30} width={1920} height={1080} />
);
```

- [ ] **Step 3: Install dependencies and list the composition**

Run: `npm install && npx remotion compositions src/index.ts`

Expected: one listed composition named `PickyDemo`, 1920×1080, 30 fps, 1800 frames.

### Task 2: Implement the deterministic application scenes

**Files:**
- Create: `video/src/PickyDemo.tsx`
- Create: `video/src/data.ts`
- Create: `video/src/styles.css`

**Interfaces:**
- Consumes: `PickyDemo` composition props from Task 1.
- Produces: `PickyDemo(): React.ReactElement` and a visual sequence with local scene ranges `0–180`, `180–420`, `420–780`, `780–1440`, and `1440–1800`.

- [ ] **Step 1: Define static candidates and offers**

```ts
export const offers = [
  {title: 'Sony WF-1000XM5, czarne, komplet', price: '479 zł', warranty: '3 miesiące', returns: '14 dni', score: 87},
  {title: 'Sony WF-1000XM5 z etui', price: '419 zł', warranty: 'brak danych', returns: 'brak danych', score: 81},
  {title: 'Sony WF-1000XM5 odnowione', price: '549 zł', warranty: '12 miesięcy', returns: '30 dni', score: 76},
] as const;
```

- [ ] **Step 2: Compose scenes with frame-relative animation**

```tsx
<Sequence from={0} durationInFrames={180}><PromptScene /></Sequence>
<Sequence from={180} durationInFrames={240}><ProductSelectionScene /></Sequence>
<Sequence from={420} durationInFrames={360}><VerificationScene /></Sequence>
<Sequence from={780} durationInFrames={660}><OfferRankingScene /></Sequence>
<Sequence from={1440} durationInFrames={360}><PriorityUpdateScene /></Sequence>
```

Each scene must use `useCurrentFrame()`, `interpolate()` and `spring()` for opacity, translation, scale, typewriter progress, card staging, and the final ranking reorder.

- [ ] **Step 3: Style the UI and camera**

```css
.camera { position: absolute; inset: 0; transform-origin: 50% 50%; }
.app-window { background: #f7f8fa; border-radius: 34px; box-shadow: 0 34px 90px #151c2b2e; overflow: hidden; }
.offer--recommended { border-color: #304dd8; box-shadow: 0 16px 34px #304dd82a; }
```

Use scene-specific camera transforms so frames 6–14 seconds crop to the composer, frames 34–48 seconds crop to the recommended offer's price and evidence fields, and the final three seconds return to a broad ranking view.

- [ ] **Step 4: Build and render a still for visual inspection**

Run: `npx remotion still src/index.ts PickyDemo out/preview.png --frame=1080`

Expected: PNG with an offer-ranking close-up where 479 zł, score 87, warranty and return values are legible.

### Task 3: Render and verify the deliverable

**Files:**
- Create: `video/out/picky-demo.mp4`
- Create: `video/out/preview.png`

**Interfaces:**
- Consumes: `PickyDemo` composition and all scene components.
- Produces: H.264 MP4 at exactly 60 seconds.

- [ ] **Step 1: Run the type check and composition inspection**

Run: `npx tsc --noEmit && npx remotion compositions src/index.ts`

Expected: no TypeScript errors; composition metadata shows 1800 frames at 30 fps and 1920×1080.

- [ ] **Step 2: Render the MP4**

Run: `npx remotion render src/index.ts PickyDemo out/picky-demo.mp4 --codec=h264`

Expected: `out/picky-demo.mp4` exists and the render command exits successfully.

- [ ] **Step 3: Inspect delivery metadata and key frames**

Run: `ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of default=noprint_wrappers=1 out/picky-demo.mp4`

Expected: duration close to `60.000000`, width `1920`, height `1080`, and frame rate `30/1`.

Render stills at frames 0, 300, 600, 1080, 1500 and 1799; inspect them for cropped text, unintentional black frames, and the final 12-month warranty card at rank one.
