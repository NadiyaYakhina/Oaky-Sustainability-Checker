# Extension Icons

Place your extension icon files here before building:

- `icon16.png`  — 16×16 px (used in the browser toolbar)
- `icon48.png`  — 48×48 px (used in the extensions management page)
- `icon128.png` — 128×128 px (used in the Chrome Web Store)

The build script copies these into `dist/icons/` automatically.
If the files are missing, Chrome will show a default blank icon and log a warning — the extension will still work.
