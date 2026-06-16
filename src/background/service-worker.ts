// Background service worker for Oaky extension.
// Currently returns placeholder data — replace PLACEHOLDER_REPORT with a real API call.

export interface ReportData {
  overallScore: number;        // 1–10
  brandReputation: number;     // 1–10
  materialComposition: number; // 1–10
  numberOfWears: number;       // 0–1000+
}

export interface LookupRequest {
  type: "LOOKUP";
  productUrl: string;
  productName?: string;
  brandName?: string;
}

export interface LookupResponse {
  type: "LOOKUP_RESULT";
  data: ReportData;
  error?: string;
}

// PLACEHOLDER — replace with real sustainability API call
const PLACEHOLDER_REPORT: ReportData = {
  overallScore: 5,
  brandReputation: 6,
  materialComposition: 3,
  numberOfWears: 50,
};

async function fetchSustainabilityReport(request: LookupRequest): Promise<ReportData> {
  // TODO: Replace this with a real API call to your sustainability backend:
  //
  // const response = await fetch("https://your-api.example.com/report", {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({
  //     url: request.productUrl,
  //     productName: request.productName,
  //     brandName: request.brandName,
  //   }),
  // });
  // return response.json();

  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1500));
  return PLACEHOLDER_REPORT;
}

chrome.runtime.onMessage.addListener((message: LookupRequest, _sender, sendResponse) => {
  if (message.type === "LOOKUP") {
    fetchSustainabilityReport(message)
      .then((data) => sendResponse({ type: "LOOKUP_RESULT", data } as LookupResponse))
      .catch((err) => sendResponse({ type: "LOOKUP_RESULT", data: PLACEHOLDER_REPORT, error: String(err) } as LookupResponse));
    return true; // keep channel open for async response
  }
});

// The integrated side panel is provided via the `side_panel` manifest key
// and served from `sidebar.html`. No window-creation code is required.

function openFallbackWindow() {
  return chrome.windows
    .create({
      url: chrome.runtime.getURL('sidebar.html'),
      type: 'popup',
      width: 420,
      height: 800,
    })
    .then(() => {
      try {
        if (chrome.notifications && typeof chrome.notifications.create === 'function') {
          chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Oaky',
            message: 'Side panel could not be opened — opened fallback window.',
          } as any)
        } else {
          console.log('Side panel could not be opened — opened fallback window.')
        }
      } catch (e) {
        console.log('Fallback notification could not be shown.')
      }
    })
    .catch((err) => {
      console.error('Fallback window could not be opened.', err)
    })
}

// Programmatically open the side panel when the toolbar action is clicked.
// chrome.sidePanel.open() requires a tabId or windowId, and it only works from
// a user gesture such as chrome.action.onClicked.
chrome.action.onClicked.addListener((tab) => {
  const sp = (chrome as any).sidePanel

  const openSidePanel = () => {
    if (!sp || typeof sp.open !== 'function') {
      return Promise.reject(new Error('chrome.sidePanel.open is unavailable'))
    }

    const options = tab.id ? { tabId: tab.id } : { windowId: tab.windowId }
    return sp.open(options)
  }

  openSidePanel().catch((err) => {
    console.warn('Could not open the side panel; opening fallback window.', err)
    openFallbackWindow()
  })
})
