import { useState } from "react";
import { Star, X, Info, MapPin, MoreHorizontal, Play } from "lucide-react";

// Character images from Figma imports
import imgHappyOaky from "@/imports/ReportHappyOaky/10b6c7e91cb1a74dd5a00fbbe3c03174575c0ec3.png";
import imgMediocreOaky from "@/imports/ReportMediocreOaky/aed497fcfb2ce65b64670bc7e14ddd2477837f20.png";
import imgSadOaky from "@/imports/ReportSadOaky/2e932ff9eeed1871773a1f4b05b32ad5b28d71c3.png";

// ─── Backend contract ────────────────────────────────────────────────────────
// Replace the placeholder values in src/background/service-worker.ts with a
// real API call. This interface is the shared type across popup ↔ background.
export interface ReportData {
  overallScore: number;        // 1–10
  brandReputation: number;     // 1–10
  materialComposition: number; // 1–10
  numberOfWears: number;       // 0–1000+
}

// ─── Scoring logic ───────────────────────────────────────────────────────────
type MetricColor = "red" | "yellow" | "green";

function getMetricColor(metric: keyof ReportData, value: number): MetricColor {
  if (metric === "overallScore") {
    if (value <= 3) return "red";
    if (value <= 6) return "yellow";
    return "green";
  }
  if (metric === "numberOfWears") return value <= 40 ? "red" : "green";
  return value <= 5 ? "red" : "green"; // brandReputation, materialComposition
}

function getOakyVariant(report: ReportData): "happy" | "mediocre" | "sad" {
  const metrics: Array<keyof ReportData> = [
    "overallScore",
    "brandReputation",
    "materialComposition",
    "numberOfWears",
  ];
  let reds = 0;
  let greens = 0;
  for (const m of metrics) {
    const c = getMetricColor(m, report[m]);
    if (c === "red") reds++;
    else if (c === "green") greens++;
  }
  if (reds > greens) return "sad";
  if (greens > reds) return "happy";
  return "mediocre";
}

const STAT_BG: Record<MetricColor, string> = {
  red: "#dba2b2",
  yellow: "#ebddc2",
  green: "#7db493",
};

const PROGRESS_COLOR: Record<MetricColor, string> = {
  red: "#dba2b2",
  yellow: "#f0b100",
  green: "#7db493",
};

// Placeholder data shown when no backend response is available
const FALLBACK_REPORT: ReportData = {
  overallScore: 5,
  brandReputation: 6,
  materialComposition: 3,
  numberOfWears: 50,
};

// ─── Styles ──────────────────────────────────────────────────────────────────
const SERIF = "'Instrument Serif', serif";

// ─── Oaky character components ───────────────────────────────────────────────
// Each component replicates the crop from the Figma import using percentage
// offsets derived from the original container/image dimensions.

function HappyOaky({ width = 190 }: { width?: number }) {
  const height = Math.round(width * (2293 / 1374));
  return (
    <div style={{ width, height, position: "relative", overflow: "hidden", flexShrink: 0 }}>
      <img
        src={imgHappyOaky}
        alt="Happy Oaky"
        style={{
          position: "absolute",
          width: "354.33%",
          height: "212.23%",
          left: "-23.53%",
          top: "-45.8%",
          maxWidth: "none",
        }}
      />
    </div>
  );
}

function MediocreOaky({ width = 150 }: { width?: number }) {
  const height = Math.round(width * (1813 / 1029));
  return (
    <div style={{ width, height, position: "relative", overflow: "hidden", flexShrink: 0 }}>
      <img
        src={imgMediocreOaky}
        alt="Mediocre Oaky"
        style={{
          position: "absolute",
          width: "469.72%",
          height: "266.67%",
          left: "-188.07%",
          top: "-82.68%",
          maxWidth: "none",
        }}
      />
    </div>
  );
}

function SadOaky({ width = 145 }: { width?: number }) {
  const height = Math.round(width * (1946 / 962));
  return (
    <div style={{ width, height, position: "relative", overflow: "hidden", flexShrink: 0 }}>
      <img
        src={imgSadOaky}
        alt="Sad Oaky"
        style={{
          position: "absolute",
          width: "518.48%",
          height: "256.32%",
          left: "-356.2%",
          top: "-77.72%",
          maxWidth: "none",
        }}
      />
    </div>
  );
}

// ─── Shared header ────────────────────────────────────────────────────────────
function Header({
  showStreak = true,
  streak = 2,
  onClose,
  onInfo,
}: {
  showStreak?: boolean;
  streak?: number;
  onClose?: () => void;
  onInfo?: () => void;
}) {
  return (
    <div className="flex justify-between items-center px-4 pt-5">
      {showStreak ? (
        <div
          className="flex items-center gap-2 px-5 py-2 rounded-3xl"
          style={{ background: "#7db493" }}
        >
          <Star size={20} fill="#282828" strokeWidth={0} />
          <span style={{ fontFamily: SERIF, fontSize: 34, lineHeight: 1, color: "#282828" }}>
            {streak}
          </span>
        </div>
      ) : (
        <div />
      )}

      <div
        className="flex items-center gap-3 px-5 py-2 rounded-3xl"
        style={{ background: "#f0e8d8" }}
      >
        <button
          onClick={onInfo}
          aria-label="Info"
          style={{ lineHeight: 0, background: "none", border: "none", cursor: "pointer" }}
        >
          <Info size={22} color="#282828" strokeWidth={1.5} />
        </button>
        {onClose && (
          <button
            onClick={onClose}
            aria-label="Close"
            style={{ lineHeight: 0, background: "none", border: "none", cursor: "pointer" }}
          >
            <X size={24} color="#282828" strokeWidth={1.5} />
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Screen: Intro ────────────────────────────────────────────────────────────
function IntroScreen({ onStart }: { onStart: () => void }) {
  return (
    <div
      style={{ background: "#f4f4f4", minHeight: "100vh", fontFamily: SERIF }}
      className="flex flex-col w-full"
    >
      <Header showStreak={false} />

      <p
        className="text-center px-10 mt-8"
        style={{ fontFamily: SERIF, fontSize: 22, lineHeight: 1.5, color: "#282828" }}
      >
        Hi there, my name is Oakly and I&apos;m here to help you check if the
        clothes you&apos;re buying are eco-friendly!
      </p>

      <div className="flex justify-center mt-6 relative" style={{ paddingBottom: 12 }}>
        <div style={{ position: "relative", zIndex: 1 }}>
          <HappyOaky width={195} />
        </div>
      </div>

      <div className="flex-1" />

      <div className="flex justify-center px-12 pb-14">
        <button
          onClick={onStart}
          style={{
            background: "#7db493",
            borderRadius: 40,
            fontFamily: SERIF,
            fontSize: 42,
            color: "#282828",
            border: "none",
            cursor: "pointer",
            padding: "10px 0",
            width: "100%",
          }}
        >
          Start
        </button>
      </div>
    </div>
  );
}

// ─── Screen: Loading ──────────────────────────────────────────────────────────
function LoadingScreen() {
  return (
    <div
      style={{ background: "#f4f4f4", minHeight: "100vh" }}
      className="flex flex-col w-full"
    >
      <Header showStreak={false} />

      <p
        className="text-center px-10 mt-14"
        style={{ fontFamily: SERIF, fontSize: 22, lineHeight: 1.5, color: "#282828" }}
      >
        One second, I&apos;m investigating!
      </p>

      <div className="flex justify-center mt-8 relative flex-1">
        <div style={{ position: "relative", zIndex: 1 }}>
          <HappyOaky width={195} />
        </div>
      </div>
    </div>
  );
}

// ─── Screen: Report ───────────────────────────────────────────────────────────
function ReportScreen({
  report,
  onClose,
}: {
  report: ReportData;
  onClose: () => void;
}) {
  const variant = getOakyVariant(report);
  const overallColor = getMetricColor("overallScore", report.overallScore);
  const brandColor = getMetricColor("brandReputation", report.brandReputation);
  const materialColor = getMetricColor("materialComposition", report.materialComposition);
  const wearsColor = getMetricColor("numberOfWears", report.numberOfWears);
  const progressPct = (report.overallScore / 10) * 100;

  const character =
    variant === "happy" ? (
      <HappyOaky width={165} />
    ) : variant === "mediocre" ? (
      <MediocreOaky width={155} />
    ) : (
      <SadOaky width={150} />
    );

  return (
    <div
      style={{ background: "#f4f4f4", fontFamily: SERIF }}
      className="flex flex-col w-full pb-5"
    >
      <Header showStreak streak={2} onClose={onClose} />

      {/* Character */}
      <div className="flex justify-center mt-3 relative" style={{ paddingBottom: 8 }}>
        <div style={{ position: "relative", zIndex: 1 }}>{character}</div>
      </div>

      {/* ── Report card ── */}
      <div
        className="mx-4 mt-3 rounded-[28px] px-4 pt-4 pb-5"
        style={{ background: "#f0e8d8" }}
      >
        {/* Title row */}
        <div className="flex items-center gap-3 mb-3">
          <span style={{ fontSize: 20 }}>☑</span>
          <span style={{ fontFamily: SERIF, fontSize: 22, color: "#282828" }}>
            Sustainability Report
          </span>
        </div>

        {/* Overall score */}
        <div className="rounded-[20px] px-4 pt-3 pb-3" style={{ background: "#ebddc2" }}>
          <div className="flex items-center justify-between mb-2">
            <span style={{ fontFamily: SERIF, fontSize: 17, color: "#282828" }}>
              Overall Score:
            </span>
            <MoreHorizontal size={18} color="#282828" />
          </div>
          <div
            className="rounded-full overflow-hidden"
            style={{ background: "#f4f4f4", height: 16 }}
          >
            <div
              className="h-full rounded-full"
              style={{
                width: `${progressPct}%`,
                background: PROGRESS_COLOR[overallColor],
                transition: "width 0.7s ease",
              }}
            />
          </div>
          <div
            className="text-right mt-1"
            style={{ fontFamily: SERIF, fontSize: 17, color: "#282828" }}
          >
            {report.overallScore}/10
          </div>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-3 gap-2 mt-3">
          {[
            {
              label: "Brand\nReputation:",
              value: `${report.brandReputation}/10`,
              color: brandColor,
            },
            {
              label: "Material\nComposition:",
              value: `${report.materialComposition}/10`,
              color: materialColor,
            },
            {
              label: "Number\nOf Wears:",
              value: String(report.numberOfWears),
              color: wearsColor,
            },
          ].map(({ label, value, color }) => (
            <div
              key={label}
              className="rounded-[18px] px-2 pt-3 pb-2 flex flex-col items-center"
              style={{ background: STAT_BG[color] }}
            >
              <span
                className="text-center whitespace-pre-line mb-1"
                style={{ fontFamily: SERIF, fontSize: 13, color: "#282828", lineHeight: 1.3 }}
              >
                {label}
              </span>
              <span
                style={{ fontFamily: SERIF, fontSize: 28, color: "#282828", lineHeight: 1 }}
              >
                {value}
              </span>
              <div className="mt-1 self-end">
                <MoreHorizontal size={14} color="#282828" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Suggestions section ── */}
      <div
        className="mx-4 mt-4 rounded-[28px] px-4 pt-4 pb-5"
        style={{ background: "#dba2b2" }}
      >
        <div className="flex items-start gap-3 mb-4">
          <MapPin size={22} color="#282828" strokeWidth={1.5} className="mt-0.5 flex-shrink-0" />
          <span style={{ fontFamily: SERIF, fontSize: 21, color: "#282828", lineHeight: 1.3 }}>
            Better composition/similar price
          </span>
        </div>
        <div className="flex gap-3 items-center">
          {/* Image placeholder 1 */}
          <div
            className="flex-1 rounded-[18px] border-2 border-[#828282]"
            style={{ background: "#f0e8d8", aspectRatio: "0.86" }}
          />
          {/* Image placeholder 2 */}
          <div
            className="flex-1 rounded-[18px] border-2 border-[#828282]"
            style={{ background: "#f0e8d8", aspectRatio: "0.86" }}
          />
          {/* Play button */}
          <div
            className="flex items-center justify-center rounded-[18px] flex-shrink-0"
            style={{ background: "#f0e8d8", width: 48, height: 48 }}
          >
            <Play size={18} color="#282828" strokeWidth={1.5} fill="#282828" />
          </div>
        </div>
      </div>

      {/* ── Disclaimer ── */}
      <div
        className="mx-4 mt-4 rounded-[28px] px-6 py-5"
        style={{ background: "#ebddc2" }}
      >
        <p style={{ fontFamily: SERIF, fontSize: 15, color: "#282828", lineHeight: 1.6 }}>
          We are trying our best to verify sources, but please be{" "}
          <em>mindful</em> and double check the information
        </p>
      </div>
    </div>
  );
}

// ─── Survey option ────────────────────────────────────────────────────────────
function SurveyOption({
  label,
  selected,
  onClick,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-start gap-4 w-full text-left px-5 py-4 rounded-[20px]"
      style={{ background: "#ebddc2", border: "none", cursor: "pointer" }}
    >
      {/* Radio circle */}
      <div
        style={{
          width: 22,
          height: 22,
          borderRadius: "50%",
          border: "2.5px solid #282828",
          background: selected ? "#282828" : "transparent",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          marginTop: 2,
        }}
      >
        {selected && (
          <div
            style={{ width: 9, height: 9, borderRadius: "50%", background: "#ebddc2" }}
          />
        )}
      </div>
      <span style={{ fontFamily: SERIF, fontSize: 18, color: "#282828", lineHeight: 1.45 }}>
        {label}
      </span>
    </button>
  );
}

const SURVEY_OPTIONS = [
  "Item that I was browsing initially (it was sustainble)",
  "Item that I was browsing initially (it was not sustainable but price was good)",
  "One of the suggested more sustainable items",
  "Haven't bought anything, decided to postpone/not make the purchase",
];

// ─── Screen: Survey ───────────────────────────────────────────────────────────
function SurveyScreen({
  selectedIndex,
  onSelect,
  onClose,
}: {
  selectedIndex: number | null;
  onSelect: (idx: number) => void;
  onClose: () => void;
}) {
  return (
    <div
      style={{ background: "#f4f4f4", fontFamily: SERIF }}
      className="flex flex-col w-full pb-6"
    >
      <Header showStreak streak={2} onClose={onClose} />

      <p className="px-6 mt-6" style={{ fontFamily: SERIF, fontSize: 26, color: "#282828" }}>
        What did you buy?
      </p>

      <div className="flex flex-col gap-3 px-4 mt-4">
        {SURVEY_OPTIONS.map((opt, i) => (
          <SurveyOption
            key={i}
            label={opt}
            selected={selectedIndex === i}
            onClick={() => onSelect(i)}
          />
        ))}
      </div>

      <div className="flex justify-center mt-8 relative" style={{ paddingBottom: 8 }}>
        <div style={{ position: "relative", zIndex: 1 }}>
          <HappyOaky width={175} />
        </div>
      </div>
    </div>
  );
}

// ─── Screen: Error ─────────────────────────────────────────────────────────────
function ErrorScreen({
  message,
  onClose,
}: {
  message: string;
  onClose: () => void;
}) {
  return (
    <div
      style={{ background: "#f4f4f4", minHeight: "100vh", fontFamily: SERIF }}
      className="flex flex-col w-full"
    >
      <Header showStreak={false} />

      <div className="flex-1 flex flex-col items-center justify-center px-8 pb-10">
        <p
          className="text-center mb-6"
          style={{ fontFamily: SERIF, fontSize: 22, color: "#282828", lineHeight: 1.5 }}
        >
          Something went wrong while checking sustainability:
        </p>
        <div
          className="w-full rounded-[20px] px-5 py-4 mb-8"
          style={{ background: "#ebddc2" }}
        >
          <p
            className="text-center"
            style={{ fontFamily: SERIF, fontSize: 16, color: "#282828", lineHeight: 1.5 }}
          >
            {message}
          </p>
        </div>
        <button
          onClick={onClose}
          style={{
            background: "#7db493",
            borderRadius: 40,
            fontFamily: SERIF,
            fontSize: 24,
            color: "#282828",
            border: "none",
            cursor: "pointer",
            padding: "10px 0",
            width: "100%",
            maxWidth: 300,
          }}
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────
type Screen = "intro" | "loading" | "report" | "survey-close" | "survey-chosen" | "error";

export default function App() {
  const [screen, setScreen] = useState<Screen>("intro");
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [surveySelection, setSurveySelection] = useState<number | null>(null);

  const handleStart = () => {
    setError(null);
    setScreen("loading");

    // In extension context: ask background worker for report data
    if (typeof chrome !== "undefined" && chrome.runtime?.sendMessage) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0]?.url ?? "";
        chrome.runtime.sendMessage(
          { type: "LOOKUP", productUrl: url },
          (response) => {
            if (response?.success === false) {
              setError(response.error || "Something went wrong while checking sustainability.");
              setScreen("error");
            } else {
              setReport(response?.data ?? null);
              setScreen("report");
            }
          }
        );
      });
    } else {
      // Dev fallback: simulate a network delay then use placeholder data
      setTimeout(() => {
        setReport(FALLBACK_REPORT);
        setScreen("report");
      }, 1500);
    }
  };

  const handleReportClose = () => setScreen("survey-close");

  const handleSurveySelect = (idx: number) => {
    setSurveySelection(idx);
    setScreen("survey-chosen");
  };

  const handleSurveyClose = () => {
    setScreen("intro");
    setReport(null);
    setSurveySelection(null);
  };

  const handleErrorClose = () => {
    setScreen("intro");
    setError(null);
  };

  switch (screen) {
    case "intro":
      return <IntroScreen onStart={handleStart} />;
    case "loading":
      return <LoadingScreen />;
    case "report":
      return (
        <ReportScreen
          report={report ?? FALLBACK_REPORT}
          onClose={handleReportClose}
        />
      );
    case "survey-close":
      return (
        <SurveyScreen
          selectedIndex={null}
          onSelect={handleSurveySelect}
          onClose={handleSurveyClose}
        />
      );
    case "survey-chosen":
      return (
        <SurveyScreen
          selectedIndex={surveySelection}
          onSelect={handleSurveySelect}
          onClose={handleSurveyClose}
        />
      );
    case "error":
      return <ErrorScreen message={error ?? "Unknown error"} onClose={handleErrorClose} />;
    default:
      return <IntroScreen onStart={handleStart} />;
  }
}
