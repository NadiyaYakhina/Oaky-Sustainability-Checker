// Content script — injected into every page the user visits.
// Extracts product context and stores it for the popup to retrieve.

interface PageContext {
  url: string;
  productName?: string;
  brandName?: string;
}

function extractPageContext(): PageContext {
  const url = window.location.href;

  // TODO: Add site-specific selectors for the shopping platforms you target.
  // Generic heuristics for now:
  const titleEl =
    document.querySelector('[itemprop="name"]') ||
    document.querySelector("h1") ||
    null;

  const brandEl =
    document.querySelector('[itemprop="brand"]') ||
    document.querySelector('[class*="brand"]') ||
    null;

  return {
    url,
    productName: titleEl?.textContent?.trim() ?? undefined,
    brandName: brandEl?.textContent?.trim() ?? undefined,
  };
}

// Store context in session storage so the popup can read it
const context = extractPageContext();
chrome.storage.session
  .set({ pageContext: context })
  .catch(() => {
    // storage.session may not be available in all contexts — fail silently
  });

// Also respond to direct requests from the popup
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "GET_PAGE_CONTEXT") {
    sendResponse(extractPageContext());
  }
});
