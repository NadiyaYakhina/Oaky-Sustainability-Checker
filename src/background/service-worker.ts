// src/background/service-worker.ts

const API_BASE = "http://127.0.0.1:8000";

export interface ReportData {
  overallScore: number;        // 1–10
  brandReputation: number;     // 1–10
  materialComposition: number; // 1–10
  numberOfWears: number;
}

type LookupMessage = {
  type: "LOOKUP";
  productUrl?: string;
};

function scoreTo10(value?: number): number {
  if (value === undefined || value === null || Number.isNaN(value)) return 5;
  return Math.max(1, Math.min(10, Math.round(value / 10)));
}

function estimateWears(finalScore?: number): number {
  if (!finalScore) return 50;
  if (finalScore >= 80) return 100;
  if (finalScore >= 70) return 80;
  if (finalScore >= 50) return 50;
  if (finalScore >= 30) return 35;
  return 20;
}

function extractBrandFromUrl(url?: string): string {
  if (!url) return "Unknown";

  try {
    const host = new URL(url).hostname.replace(/^www\./, "").toLowerCase();

    if (host.includes("hm") || host.includes("handm")) return "H&M";
    if (host.includes("zara") || host.includes("inditex")) return "Zara";
    if (host.includes("mango")) return "Mango";
    if (host.includes("cos")) return "COS";
    if (host.includes("uniqlo")) return "Uniqlo";
    if (host.includes("nike")) return "Nike";
    if (host.includes("adidas")) return "Adidas";

    return host.split(".")[0].replace(/-/g, " ");
  } catch {
    return "Unknown";
  }
}

function extractDomainFromUrl(url?: string): string | null {
  if (!url) return null;

  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
}

chrome.runtime.onMessage.addListener(
  (message: LookupMessage, sender, sendResponse) => {
    if (message.type !== "LOOKUP") {
      return false;
    }

    const brandName = extractBrandFromUrl(message.productUrl);
    const officialDomain = extractDomainFromUrl(message.productUrl);

    fetch(`${API_BASE}/audit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        brand_name: brandName,
        official_domain: officialDomain
      })
    })
      .then(async (res) => {
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || data.error || `Backend returned ${res.status}`);
        }

        const finalScore = data.sustainability_summary?.final_score;
        const scores = data.scores || {};

        const report: ReportData = {
          overallScore: scoreTo10(finalScore),
          brandReputation: scoreTo10(
            scores.public_perception ?? scores.authenticity_score
          ),
          materialComposition: scoreTo10(scores.material_analysis),
          numberOfWears: estimateWears(finalScore)
        };

        sendResponse({
          success: true,
          data: report,

          // Extra backend data is included here for future UI upgrades.
          rawAudit: data,
          recommendation: data.sustainability_summary?.recommendation,
          recommendationExplanation: data.recommendation_explanation || [],
          evidenceLinks: data.evidence_links || [],
          detailedScores: data.scores || {},
          brandMaterialSummary: data.brand_material_summary || {},
          certificationsFound: data.certifications_found || []
        });
      })
      .catch((error) => {
        console.error("Oaky backend lookup failed:", error);

        sendResponse({
          success: false,
          error: error.message,
          data: {
            overallScore: 5,
            brandReputation: 5,
            materialComposition: 5,
            numberOfWears: 50
          }
        });
      });

    return true;
  }
);
