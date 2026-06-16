# Plan: Oaky — Chrome Extension

## Context
Oaky is a sustainability checker Chrome extension. When the user is browsing a clothing item, the popup shows a sustainability report (Oaky character + scores). The design has 7 screens from Figma, already imported into `src/imports/`. The project is currently a Figma Make workspace; we need to layer in Chrome extension infrastructure alongside the existing Vite+React setup without breaking the Figma Make entrypoint.

---

## Chrome Extension Architecture

### Manifest V3 structure
```
/workspaces/default/code/
├── manifest.json              ← NEW: Chrome extension manifest (MV3)
├── popup.html                 ← NEW: popup entry point HTML
├── src/
│   ├── popup/
│   │   └── main.tsx           ← NEW: React root for the popup
│   ├── background/
│   │   └── service-worker.ts  ← NEW: background service worker
│   ├── content/
│   │   └── content-script.ts  ← NEW: injected into shopping pages
│   ├── app/
│   │   └── App.tsx            ← MODIFIED: main UI component
│   └── imports/               ← READ-ONLY: Figma designs
└── vite.config.ts             ← MODIFIED: multi-entry build for extension
```

### Role of each piece

| File | Role |
|---|---|
| `manifest.json` | Declares permissions, popup, content scripts, service worker |
| `popup.html` | Minimal HTML shell that mounts the React app |
| `src/popup/main.tsx` | `ReactDOM.createRoot` → `<App />` |
| `src/background/service-worker.ts` | Listens for messages from popup; calls sustainability backend (placeholder for now); returns `ReportData` |
| `src/content/content-script.ts` | Extracts product info from the active tab (brand, product name, URL); sends to background |
| `src/app/App.tsx` | All 7 screens, screen state machine, color logic, character selection |

---

## Backend integration contract

All data slots are **placeholders** — easy to swap for real API responses later.

```ts
// The shape the popup expects back from the background worker
interface ReportData {
  overallScore: number;        // 1–10
  brandReputation: number;     // 1–10
  materialComposition: number; // 1–10
  numberOfWears: number;       // 0–1000+
}

// Sent from popup → background to trigger a lookup
interface LookupRequest {
  type: 'LOOKUP';
  productUrl: string;
  productName?: string;
  brandName?: string;
}
```

Placeholder response (hardcoded in service worker until real backend exists):
```ts
const PLACEHOLDER_REPORT: ReportData = {
  overallScore: 5,
  brandReputation: 6,
  materialComposition: 3,
  numberOfWears: 50,
};
```

---

## Color + character logic (in App.tsx)

### Per-metric color bands
```ts
function scoreColor(metric: keyof ReportData, value: number): 'red' | 'yellow' | 'green' {
  if (metric === 'overallScore') {
    if (value <= 3) return 'red';
    if (value <= 6) return 'yellow';
    return 'green';
  }
  if (metric === 'numberOfWears') return value <= 40 ? 'red' : 'green';
  // brandReputation, materialComposition
  return value <= 5 ? 'red' : 'green';
}
```

### Oaky character variant
Count red vs green across all 4 metrics. Yellow counts as neither.
- Majority red → **Sad Oaky** (`ReportSadOaky`)
- Majority green → **Happy Oaky** (`ReportHappyOaky`)
- Tie or majority yellow → **Mediocre Oaky** (`ReportMediocreOaky`)

### Stat card colors
- `red` → `#dba2b2`
- `yellow` → `#ebddc2` (card) with `#f0b100` progress bar fill
- `green` → `#7db493`

### Overall score progress bar
Fill width = `(overallScore / 10) * 100%` of track.

---

## Screen flow

```
IntroScreen
  → [Start button] → LoadingAfterStartButton (2s auto-advance)
    → fetches ReportData from background worker
    → [result] → Report screen (Happy/Mediocre/Sad, dynamic colors)
      → [Close/X button] → SurveyAfterAttemptToClose
        → [radio selected] → SurveyChosenIfFirstTwoThenPlusOneStar
          → [Close] → IntroScreen (restart)
```

---

## Vite config changes

Add a second build entry alongside the existing Figma Make app. The extension build outputs to `dist/`:

```ts
// vite.config.ts additions
build: {
  outDir: 'dist',
  rollupOptions: {
    input: {
      popup: 'popup.html',
      background: 'src/background/service-worker.ts',
      content: 'src/content/content-script.ts',
    },
    output: {
      entryFileNames: '[name].js',  // no hash — manifest references fixed names
    },
  },
}
```

Add `"build:ext": "vite build"` to package.json scripts.

---

## manifest.json (MV3)

```json
{
  "manifest_version": 3,
  "name": "Oaky — Sustainability Checker",
  "version": "1.0.0",
  "description": "Check the sustainability of clothes while you shop.",
  "permissions": ["activeTab", "scripting", "storage"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": { "48": "icon48.png" }
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "run_at": "document_idle"
  }]
}
```

---

## Popup dimensions
Chrome popups are capped at 800×600px. The Figma artboard is 3430px wide. Scale factor: `430 / 3430 ≈ 0.1254`. Each screen is wrapped in a container that:
1. Sets the inner canvas to `3430px` wide
2. Applies `transform: scale(0.1254); transform-origin: top left`
3. Outer container is `width: 430px; overflow: hidden` with `height` set to match the post-scale content height

The popup body will be `430px × 932px` (approximate height of visible screen content after scaling).

---

## Files to create/modify

1. `manifest.json` — extension manifest
2. `popup.html` — HTML shell with `<script type="module" src="/src/popup/main.tsx">`
3. `src/popup/main.tsx` — React root mount
4. `src/background/service-worker.ts` — message listener + placeholder data
5. `src/content/content-script.ts` — page scraper (placeholder: posts current URL)
6. `src/app/App.tsx` — full 7-screen app with dynamic colors + character logic
7. `src/styles/fonts.css` — Google Fonts import for Instrument Serif
8. `vite.config.ts` — multi-entry extension build
9. `package.json` — add `build:ext` script

---

## How to load in Chrome (verification)

1. Run `pnpm build:ext` → produces `dist/`
2. Open Chrome → `chrome://extensions` → enable Developer Mode
3. Click "Load unpacked" → select the `dist/` folder
4. Pin the Oaky extension → click it on any shopping page
5. Verify: Intro screen loads → Start → Loading → Report renders with placeholder scores → Close → Survey → select option → chosen state shows
