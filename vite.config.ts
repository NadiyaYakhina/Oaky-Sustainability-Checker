import { defineConfig, Plugin } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

// Emits popup.html into the dist/ folder after the bundle is assembled.
// The script tag references popup.js, which is the compiled popup entry point
// (entryFileNames uses [name].js so the filename is always predictable).
function chromeExtensionHtml(): Plugin {
  return {
    name: 'chrome-extension-html',
    generateBundle(_options, bundle) {
      const cssFile = Object.keys(bundle).find(
        (f) => f.endsWith('.css') && !f.startsWith('chunks/')
      )
      const cssLink = cssFile
        ? `\n    <link rel="stylesheet" href="${cssFile}">`
        : ''

      // popup.html (toolbar popup)
      this.emitFile({
        type: 'asset',
        fileName: 'popup.html',
        source: `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Oaky</title>${cssLink}
    <style>
      *, *::before, *::after { box-sizing: border-box; }
      html, body { margin: 0; padding: 0; width: 430px; overflow-x: hidden; background: #f4f4f4; }
      #root { width: 430px; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="popup.js"></script>
  </body>
</html>`,
      })

      // sidebar.html (Chrome side panel)
      this.emitFile({
        type: 'asset',
        fileName: 'sidebar.html',
        source: `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Oaky Sidebar</title>${cssLink}
    <style>
      *, *::before, *::after { box-sizing: border-box; }
      html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #f4f4f4; }
      #root { width: 100%; height: 100%; overflow-y: auto; -webkit-overflow-scrolling: touch; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="sidebar.js"></script>
  </body>
</html>`,
      })
    },
  }
}


function figmaAssetResolver() {
  return {
    name: 'figma-asset-resolver',
    resolveId(id) {
      if (id.startsWith('figma:asset/')) {
        const filename = id.replace('figma:asset/', '')
        return path.resolve(__dirname, 'src/assets', filename)
      }
    },
  }
}

export default defineConfig({
  plugins: [
    figmaAssetResolver(),
    // The React and Tailwind plugins are both required for Make, even if
    // Tailwind is not being actively used – do not remove them
    react(),
    tailwindcss(),
    chromeExtensionHtml(),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory
      '@': path.resolve(__dirname, './src'),
    },
  },

  // File types to support raw imports. Never add .css, .tsx, or .ts files to this.
  assetsInclude: ['**/*.svg', '**/*.csv'],

  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: path.resolve(__dirname, 'src/popup/main.tsx'),
        sidebar: path.resolve(__dirname, 'src/sidebar/main.tsx'),
        background: path.resolve(__dirname, 'src/background/service-worker.ts'),
        content: path.resolve(__dirname, 'src/content/content-script.ts'),
      },
      output: {
        // Predictable filenames — the manifest.json references them by name
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
})
