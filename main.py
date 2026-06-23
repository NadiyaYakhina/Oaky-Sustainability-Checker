
# ============================================================
# Sustainability Audit Backend - BeautifulSoup Audit Version
# SerpAPI is NOT required for brand audit. It is optional for product alternatives only.
# ============================================================

import os
import re
import time
import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin, quote_plus
from typing import Optional, List, Dict, Any

import requests
import spacy
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

app = FastAPI(title="Sustainability Audit Backend")
app.add_middleware(
    CORSMiddleware,
    # Allows local development and Chrome extension origins.
    allow_origins=["http://localhost", "http://127.0.0.1", "http://127.0.0.1:8000"],
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "sustainability_audit.db"
SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # optional; product alternatives only
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ============================================================
# WORD LISTS / CONFIGURATION
# ============================================================

def load_word_lists(path="sustainability_word_lists.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return WORD_LISTS_FALLBACK

WORD_LISTS_FALLBACK = {
    "OFFICIAL_PAGE_KEYWORDS": [
        "about",
        "our-story",
        "who-we-are",
        "values",
        "mission",
        "sustainability",
        "responsibility",
        "impact",
        "esg",
        "environment",
        "climate",
        "carbon",
        "emissions",
        "net-zero",
        "netzero",
        "decarbonisation",
        "decarbonization",
        "materials",
        "material",
        "fibres",
        "fibers",
        "cotton",
        "polyester",
        "recycled",
        "organic",
        "regenerative",
        "viscose",
        "supply-chain",
        "supplychain",
        "suppliers",
        "supplier-list",
        "factory",
        "factories",
        "traceability",
        "transparency",
        "human-rights",
        "labour",
        "labor",
        "workers",
        "wages",
        "modern-slavery",
        "forced-labour",
        "forced-labor",
        "circular",
        "circularity",
        "repair",
        "resale",
        "reuse",
        "recycling",
        "take-back",
        "takeback",
        "garment-collection",
        "annual-report",
        "sustainability-report",
        "impact-report",
        "esg-report",
        "modern-slavery-statement",
        "certifications",
        "certified",
        "gots",
        "fairtrade",
        "oeko-tex",
        "oekotex",
        "bluesign",
        "b-corp",
        "fair-wear"
    ],
    "TOPICS": {
        "carbon_emissions": [
            "carbon emissions",
            "greenhouse gas",
            "ghg",
            "scope 1",
            "scope 2",
            "scope 3",
            "net zero",
            "climate target",
            "carbon footprint",
            "decarbonisation",
            "decarbonization",
            "renewable energy",
            "science based targets",
            "sbt",
            "emissions reduction"
        ],
        "labour_practices": [
            "worker rights",
            "fair wages",
            "living wage",
            "factory conditions",
            "labour standards",
            "labor standards",
            "forced labour",
            "forced labor",
            "child labour",
            "child labor",
            "human rights",
            "modern slavery",
            "collective bargaining",
            "working hours",
            "health and safety"
        ],
        "material_sourcing": [
            "organic cotton",
            "recycled cotton",
            "recycled polyester",
            "responsible wool",
            "responsible viscose",
            "tencel",
            "lyocell",
            "linen",
            "hemp",
            "regenerative cotton",
            "preferred materials",
            "certified materials",
            "material composition",
            "fiber sourcing",
            "fibre sourcing"
        ],
        "supply_chain_transparency": [
            "supplier list",
            "factory list",
            "factory disclosure",
            "tier 1",
            "tier 2",
            "tier 3",
            "traceability",
            "supply chain",
            "audit",
            "supplier code of conduct",
            "manufacturing partners",
            "production country",
            "factory locations"
        ],
        "circular_fashion": [
            "circular fashion",
            "circularity",
            "repair",
            "resale",
            "reuse",
            "rental",
            "take back",
            "take-back",
            "garment collection",
            "closed loop",
            "product lifecycle",
            "durability",
            "repair service"
        ],
        "greenwashing_allegations": [
            "greenwashing",
            "misleading claims",
            "false sustainability claims",
            "unsubstantiated claims",
            "vague claims",
            "lawsuit",
            "investigation",
            "accused",
            "consumer deception",
            "misleading marketing"
        ],
        "recycling_initiatives": [
            "recycling",
            "recycled materials",
            "textile waste",
            "post-consumer waste",
            "pre-consumer waste",
            "closed loop recycling",
            "garment recycling",
            "waste reduction",
            "recycled fibers",
            "recycled fibres"
        ],
        "water_management": [
            "water use",
            "water consumption",
            "water footprint",
            "wastewater",
            "water pollution",
            "dyeing",
            "chemical discharge",
            "water stewardship",
            "wet processing"
        ],
        "chemical_management": [
            "chemical management",
            "restricted substances",
            "hazardous chemicals",
            "zdhc",
            "detox",
            "dyes",
            "finishing chemicals",
            "chemical safety",
            "oeko-tex",
            "bluesign"
        ],
        "animal_welfare": [
            "animal welfare",
            "wool",
            "leather",
            "down",
            "mulesing",
            "responsible wool standard",
            "responsible down standard",
            "cruelty-free",
            "fur-free",
            "vegan leather"
        ],
        "certifications": [
            "gots",
            "fairtrade",
            "oeko-tex",
            "bluesign",
            "fair wear foundation",
            "b corp",
            "global recycled standard",
            "grs",
            "responsible wool standard",
            "rws",
            "fsc",
            "rainforest alliance"
        ],
        "reporting_and_governance": [
            "sustainability report",
            "annual report",
            "impact report",
            "esg report",
            "third-party assurance",
            "independent verification",
            "kpi",
            "progress update",
            "governance",
            "board oversight"
        ]
    },
    "VAGUE_GREENWASHING_WORDS": [
        "eco-friendly",
        "green",
        "conscious",
        "planet-friendly",
        "better for the planet",
        "responsible",
        "sustainable choice",
        "kind to the planet",
        "earth friendly",
        "good for the planet",
        "low impact",
        "natural",
        "clean",
        "ethical collection",
        "conscious collection"
    ],
    "CERTIFICATION_NAMES": [
        "GOTS",
        "Fairtrade",
        "OEKO-TEX",
        "Bluesign",
        "Fair Wear Foundation",
        "GRS",
        "B Corp",
        "Responsible Wool Standard",
        "RWS",
        "FSC",
        "ZDHC",
        "Cradle to Cradle"
    ],
    "MATERIAL_TERMS": [
        "organic cotton",
        "recycled cotton",
        "recycled polyester",
        "cotton",
        "polyester",
        "linen",
        "wool",
        "responsible wool",
        "viscose",
        "responsible viscose",
        "tencel",
        "lyocell",
        "recycled nylon",
        "nylon",
        "hemp",
        "leather",
        "vegan leather",
        "elastane",
        "polyamide",
        "acrylic",
        "modal",
        "cashmere",
        "silk",
        "down",
        "recycled wool"
    ],
    "SUSTAINABLE_MATERIAL_TERMS": [
        "organic cotton",
        "recycled cotton",
        "recycled polyester",
        "recycled nylon",
        "recycled wool",
        "linen",
        "hemp",
        "tencel",
        "lyocell",
        "responsible wool",
        "responsible viscose",
        "regenerative cotton"
    ],
    "PRODUCT_CATEGORIES": {
        "t-shirt": [
            "t-shirt",
            "tee",
            "shirt"
        ],
        "jeans": [
            "jeans",
            "denim"
        ],
        "dress": [
            "dress"
        ],
        "jacket": [
            "jacket",
            "coat",
            "blazer"
        ],
        "shoes": [
            "shoes",
            "sneakers",
            "boots"
        ],
        "bag": [
            "bag",
            "tote",
            "handbag"
        ],
        "sweater": [
            "sweater",
            "jumper",
            "knitwear"
        ],
        "skirt": [
            "skirt"
        ],
        "trousers": [
            "trousers",
            "pants"
        ]
    },
    "NEWS_RSS_FEEDS": [
        "https://www.theguardian.com/fashion/rss",
        "https://www.theguardian.com/business/rss",
        "https://www.theguardian.com/environment/rss",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "https://www.retaildive.com/feeds/news/",
        "https://www.sourcingjournal.com/feed/"
    ],
    "CERTIFICATION_HOMEPAGES": [
        "https://global-standard.org",
        "https://www.fairtrade.net",
        "https://www.oeko-tex.com",
        "https://www.bluesign.com",
        "https://www.fairwear.org",
        "https://textileexchange.org",
        "https://www.bcorporation.net"
    ]
}

WORD_LISTS = load_word_lists()
OFFICIAL_PAGE_KEYWORDS = WORD_LISTS["OFFICIAL_PAGE_KEYWORDS"]
TOPICS = WORD_LISTS["TOPICS"]
VAGUE_GREENWASHING_WORDS = WORD_LISTS["VAGUE_GREENWASHING_WORDS"]
CERTIFICATION_NAMES = WORD_LISTS["CERTIFICATION_NAMES"]
MATERIAL_TERMS = WORD_LISTS["MATERIAL_TERMS"]
SUSTAINABLE_MATERIAL_TERMS = WORD_LISTS["SUSTAINABLE_MATERIAL_TERMS"]
PRODUCT_CATEGORIES = WORD_LISTS["PRODUCT_CATEGORIES"]
NEWS_RSS_FEEDS = WORD_LISTS["NEWS_RSS_FEEDS"]
CERTIFICATION_HOMEPAGES = WORD_LISTS["CERTIFICATION_HOMEPAGES"]

TRUSTED_NEWS = ["reuters.com", "bbc.com", "theguardian.com", "ft.com", "bloomberg.com", "voguebusiness.com", "businessoffashion.com"]
CERTIFICATION_DOMAINS = ["global-standard.org", "fairtrade.net", "oeko-tex.com", "bluesign.com", "fairwear.org", "textileexchange.org", "bcorporation.net"]

# Known parent-company or corporate domains where sustainability information is usually published.
# This prevents failed guesses such as H&M -> handm.com and Zara -> zara.com only.
KNOWN_BRAND_DOMAINS = {
    "h&m": "hmgroup.com",
    "h & m": "hmgroup.com",
    "hm": "hmgroup.com",
    "hennes mauritz": "hmgroup.com",
    "cos": "cos.com",
    "weekday": "hmgroup.com",
    "monki": "hmgroup.com",
    "arket": "hmgroup.com",
    "zara": "inditex.com",
    "inditex": "inditex.com",
    "pull&bear": "inditex.com",
    "pull and bear": "inditex.com",
    "bershka": "inditex.com",
    "stradivarius": "inditex.com",
    "massimo dutti": "inditex.com",
    "oysho": "inditex.com",
    "patagonia": "patagonia.com",
    "nike": "purpose.nike.com",
    "adidas": "adidas-group.com",
    "puma": "about.puma.com",
    "levi's": "levistrauss.com",
    "levis": "levistrauss.com",
    "levi strauss": "levistrauss.com",
    "uniqlo": "fastretailing.com",
    "gu": "fastretailing.com",
    "the north face": "thenorthface.com",
    "north face": "thenorthface.com",
    "allbirds": "allbirds.com",
    "everlane": "everlane.com",
    "reformation": "thereformation.com",
    "mango": "mangofashiongroup.com",
    "gap": "gapinc.com",
    "old navy": "gapinc.com",
    "banana republic": "gapinc.com",
    "primark": "primark.com",
    "marks and spencer": "marksandspencer.com",
    "m&s": "marksandspencer.com",
    "asics": "corp.asics.com",
    "lululemon": "corporate.lululemon.com",
    "shein": "sheingroup.com",
    "boohoo": "boohooplc.com",
    "asos": "asosplc.com"
}

# Extra high-value sustainability URLs for corporate groups and brands that use non-obvious paths.
KNOWN_SUSTAINABILITY_URLS = {
    "hmgroup.com": [
        "https://hmgroup.com/sustainability/",
        "https://hmgroup.com/sustainability/circularity-and-climate/",
        "https://hmgroup.com/sustainability/fair-and-equal/",
        "https://hmgroup.com/investors/annual-and-sustainability-report/"
    ],
    "inditex.com": [
        "https://www.inditex.com/itxcomweb/en/sustainability",
        "https://www.inditex.com/itxcomweb/en/sustainability/environment",
        "https://www.inditex.com/itxcomweb/en/sustainability/our-suppliers",
        "https://www.inditex.com/itxcomweb/en/investors/investor-relations/annual-reports"
    ],
    "cos.com": [
        "https://www.cos.com/en-us/sustainability",
        "https://www.cos.com/en-us/sustainability/planet/our-progress",
        "https://www.cos.com/en-us/sustainability/planet/materials"
    ],
    "patagonia.com": [
        "https://www.patagonia.com/our-footprint/",
        "https://www.patagonia.com/social-responsibility/",
        "https://www.patagonia.com/materials/",
        "https://www.patagonia.com/climate-goals/"
    ],
    "purpose.nike.com": [
        "https://purpose.nike.com/",
        "https://purpose.nike.com/sustainability",
        "https://purpose.nike.com/reporting"
    ],
    "adidas-group.com": [
        "https://www.adidas-group.com/en/sustainability/",
        "https://www.adidas-group.com/en/sustainability/reporting/"
    ],
    "levistrauss.com": [
        "https://www.levistrauss.com/sustainability/",
        "https://www.levistrauss.com/sustainability-report/"
    ],
    "fastretailing.com": [
        "https://www.fastretailing.com/eng/sustainability/",
        "https://www.fastretailing.com/eng/sustainability/report/"
    ],
    "gapinc.com": [
        "https://www.gapinc.com/en-us/values/sustainability",
        "https://www.gapinc.com/en-us/values/equality-and-belonging/human-rights"
    ],
    "sheingroup.com": [
        "https://www.sheingroup.com/sustainability/",
        "https://www.sheingroup.com/social-impact/"
    ]
}

# ============================================================
# MODEL LOADING
# ============================================================

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model missing. Run: python -m spacy download en_core_web_sm")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
sentiment_analyzer = SentimentIntensityAnalyzer()
topic_embeddings = {topic: embedding_model.encode(". ".join(words), convert_to_tensor=True) for topic, words in TOPICS.items()}

# ============================================================
# REQUEST MODELS
# ============================================================

class AuditRequest(BaseModel):
    brand_name: str
    official_domain: Optional[str] = None

class ProductAlternativeRequest(BaseModel):
    page_url: str
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    price_text: Optional[str] = None
    page_text: Optional[str] = None

# ============================================================
# DATABASE
# ============================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_name TEXT,
        source_url TEXT,
        source_type TEXT,
        raw_html TEXT,
        plain_text TEXT,
        cleaned_text TEXT,
        content_hash TEXT,
        evidence_strength REAL,
        scraped_at TEXT
    )
    """)
    # Schema migration for users who already created an older SQLite database.
    cur.execute("PRAGMA table_info(evidence)")
    existing_columns = [row[1] for row in cur.fetchall()]
    if "evidence_strength" not in existing_columns:
        cur.execute("ALTER TABLE evidence ADD COLUMN evidence_strength REAL DEFAULT 0")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS topic_labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER,
        paragraph TEXT,
        topic_name TEXT,
        keyword_score REAL,
        embedding_score REAL,
        final_confidence REAL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

# ============================================================
# FETCHING, HTML CLEANING, TEXT PREPROCESSING
# ============================================================

def fetch_html_lenient(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if response.status_code != 200:
            print(f"Fetch skipped {url} | status={response.status_code}")
            return None
        if len(response.text) < 300:
            print(f"Fetch skipped {url} | too little HTML")
            return None
        time.sleep(0.25)
        return response.text
    except Exception as e:
        print("Fetch failed:", url, e)
        return None

# Backward-compatible alias
fetch_html = fetch_html_lenient

def remove_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html or "", "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()
    return soup.get_text(" ")

def clean_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9%€$£.,;:!?()\- ]", "", text)
    return text.strip()

def hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

def split_paragraphs(text: str, min_length=70):
    parts = re.split(r"\n+|(?<=[.!?])\s+", text or "")
    return [p.strip() for p in parts if len(p.strip()) >= min_length]

def is_allowed_domain(url: str, allowed_domains: List[str]) -> bool:
    domain = urlparse(url).netloc.lower()
    return any(allowed in domain for allowed in allowed_domains)

# ============================================================
# BEAUTIFULSOUP-ONLY AUDIT EVIDENCE COLLECTION
# ============================================================



def parse_xml_safely(markup: str):
    """Parse RSS/sitemap XML robustly. Requires lxml for best results, with safe fallback."""
    try:
        return BeautifulSoup(markup, features="xml")
    except Exception:
        return BeautifulSoup(markup, "html.parser")

def normalize_brand_key(brand_name: str) -> str:
    key = (brand_name or "").strip().lower()
    key = key.replace("&amp;", "&")
    key = re.sub(r"\s+", " ", key)
    return key

def resolve_official_domain_no_api(brand_name: str):
    # Prefer known corporate sustainability domains. This is critical for brands whose
    # sustainability disclosures live on a parent-company site, such as H&M Group or Inditex.
    key = normalize_brand_key(brand_name)
    if key in KNOWN_BRAND_DOMAINS:
        return KNOWN_BRAND_DOMAINS[key]

    compact = key.replace(" ", "").replace("&", "and")
    if compact in KNOWN_BRAND_DOMAINS:
        return KNOWN_BRAND_DOMAINS[compact]

    # Conservative fallback only. Users can still pass official_domain from the extension.
    return compact + ".com"

def choose_audit_domain(brand_name: str, provided_domain: Optional[str] = None) -> str:
    # Brand mapping should override product-store domains when sustainability reporting
    # is known to live elsewhere. Example: H&M product pages may be hm.com, while
    # sustainability reporting is on hmgroup.com.
    mapped = resolve_official_domain_no_api(brand_name)
    if normalize_brand_key(brand_name) in KNOWN_BRAND_DOMAINS:
        return mapped
    if provided_domain:
        return provided_domain.replace("https://", "").replace("http://", "").strip("/")
    return mapped

def discover_official_pages(domain: str):
    domain = domain.replace("https://", "").replace("http://", "").strip("/").replace("www.", "")
    bases = [f"https://www.{domain}", f"https://{domain}"]
    direct_paths = [
        "", "about", "our-story", "sustainability", "responsibility", "impact", "esg",
        "environment", "climate", "materials", "supply-chain", "suppliers", "transparency",
        "human-rights", "modern-slavery", "reports", "sustainability-report", "annual-report",
        "impact-report", "en/sustainability", "en/about", "en/responsibility", "en-us/sustainability",
        "en-us/about", "en-us/responsibility"
    ]
    discovered = set()
    # Add known sustainability URLs first, if available.
    for known_url in KNOWN_SUSTAINABILITY_URLS.get(domain, []):
        discovered.add(known_url)
    for base in bases:
        for path in direct_paths:
            discovered.add(f"{base}/{path}".rstrip("/"))
    # Homepage links
    for base in bases:
        html = fetch_html_lenient(base)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(base, a["href"])
            href_lower = href.lower()
            if domain in urlparse(href).netloc.lower() and any(k in href_lower for k in OFFICIAL_PAGE_KEYWORDS):
                discovered.add(href)
    # Sitemap links
    sitemap_urls = [f"https://www.{domain}/sitemap.xml", f"https://{domain}/sitemap.xml", f"https://www.{domain}/sitemap_index.xml", f"https://{domain}/sitemap_index.xml"]
    for sitemap_url in sitemap_urls:
        sitemap_html = fetch_html_lenient(sitemap_url)
        if not sitemap_html:
            continue
        soup = parse_xml_safely(sitemap_html)
        for loc in soup.find_all("loc"):
            url = loc.get_text(strip=True)
            if domain in urlparse(url).netloc.lower() and any(k in url.lower() for k in OFFICIAL_PAGE_KEYWORDS):
                discovered.add(url)
    return list(discovered)[:60]

def collect_news_from_rss(brand_name: str):
    collected = []
    brand_lower = brand_name.lower()
    for feed_url in NEWS_RSS_FEEDS:
        feed_html = fetch_html_lenient(feed_url)
        if not feed_html:
            continue
        soup = parse_xml_safely(feed_html)
        for item in soup.find_all("item"):
            title = item.title.get_text(" ", strip=True) if item.title else ""
            description = item.description.get_text(" ", strip=True) if item.description else ""
            link = item.link.get_text(" ", strip=True) if item.link else feed_url
            combined = f"{title} {description}".lower()
            if brand_lower in combined:
                collected.append({
                    "url": link,
                    "html": f"<html><body><h1>{title}</h1><p>{description}</p><p>RSS source: {feed_url}</p></body></html>",
                    "source_type": "trusted_news"
                })
    print("RSS news collected:", len(collected))
    return collected[:10]

def collect_news_from_site_search(brand_name: str):
    # BeautifulSoup-only search over public search pages of trusted publishers.
    # If article pages cannot be scraped, titles/snippets from the search page still become evidence.
    queries = [
        f"{brand_name} sustainability",
        f"{brand_name} greenwashing",
        f"{brand_name} supply chain",
        f"{brand_name} labour practices",
        f"{brand_name} carbon emissions"
    ]
    search_templates = [
        "https://www.theguardian.com/search?q={q}",
        "https://www.bbc.co.uk/search?q={q}",
        "https://www.reuters.com/site-search/?query={q}",
        "https://www.voguebusiness.com/search?q={q}",
        "https://www.businessoffashion.com/search/?q={q}"
    ]
    collected, seen = [], set()
    for query in queries:
        for template in search_templates:
            search_url = template.format(q=quote_plus(query))
            html = fetch_html_lenient(search_url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = urljoin(search_url, a.get("href"))
                if href in seen:
                    continue
                if not is_allowed_domain(href, TRUSTED_NEWS):
                    continue
                title = a.get_text(" ", strip=True)
                if len(title) < 12:
                    continue
                title_lower = title.lower()
                if brand_name.lower() not in title_lower and not any(k in title_lower for k in ["sustain", "greenwash", "climate", "emission", "supply", "labour", "labor"]):
                    continue
                seen.add(href)
                article_html = fetch_html_lenient(href)
                if not article_html:
                    article_html = f"<html><body><h1>{title}</h1><p>Search query: {query}</p><p>Trusted news search source: {search_url}</p><p>Article URL: {href}</p></body></html>"
                collected.append({"url": href, "html": article_html, "source_type": "trusted_news"})
                if len(collected) >= 15:
                    print("Trusted news site-search collected:", len(collected))
                    return collected
    print("Trusted news site-search collected:", len(collected))
    return collected

def collect_trusted_news_no_api(brand_name: str):
    combined = []
    seen = set()
    for item in collect_news_from_rss(brand_name) + collect_news_from_site_search(brand_name):
        if item["url"] not in seen:
            seen.add(item["url"])
            combined.append(item)
    print("Trusted news total collected:", len(combined))
    return combined[:15]

def brand_slug(brand_name: str) -> str:
    slug = normalize_brand_key(brand_name)
    slug = slug.replace("&", "and")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug

def collect_external_sustainability_context(brand_name: str):
    # Non-news public context pages that often summarize or rate sustainability.
    # These are not treated as certification databases; they are wide context.
    slug = brand_slug(brand_name)
    urls = [
        f"https://directory.goodonyou.eco/brand/{slug}",
        f"https://directory.goodonyou.eco/brand/{slug.replace('-', '')}",
    ]
    collected = []
    for url in urls:
        html = fetch_html_lenient(url)
        if html:
            collected.append({"url": url, "html": html, "source_type": "wide_web_context"})
    return collected

def collect_wide_web_context_no_api(brand_name: str):
    # DuckDuckGo HTML page. No SerpAPI key required. Some networks return 202/blocked;
    # therefore we also include known external sustainability pages as fallback.
    queries = [
        f"{brand_name} sustainability", f"{brand_name} sustainable materials", f"{brand_name} supply chain transparency",
        f"{brand_name} labour practices", f"{brand_name} carbon emissions", f"{brand_name} greenwashing",
        f"{brand_name} ESG report", f"{brand_name} sustainability report", f"{brand_name} certifications"
    ]
    collected, seen = [], set()

    # Start with external context pages so we still have evidence if web search is blocked.
    for item in collect_external_sustainability_context(brand_name):
        seen.add(item["url"])
        collected.append(item)

    for query in queries:
        try:
            response = requests.get("https://duckduckgo.com/html/", params={"q": query}, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if response.status_code != 200:
                print("DuckDuckGo search failed:", query, response.status_code)
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.select(".result")
            print("DuckDuckGo query:", query, "| results:", len(results))
            for result in results[:6]:
                link_tag = result.select_one(".result__a")
                snippet_tag = result.select_one(".result__snippet")
                if not link_tag:
                    continue
                url = link_tag.get("href")
                title = link_tag.get_text(" ", strip=True)
                snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
                if not url or url in seen:
                    continue
                seen.add(url)
                html = fetch_html_lenient(url)
                if not html:
                    html = f"<html><body><h1>{title}</h1><p>{snippet}</p><p>Search query: {query}</p><p>Source URL: {url}</p></body></html>"
                collected.append({"url": url, "html": html, "source_type": "wide_web_context"})
        except Exception as e:
            print("Wide web search failed:", query, e)
    print("Wide web context collected:", len(collected))
    return collected[:25]

def check_certification_databases_no_api(brand_name: str):
    collected = []
    brand_lower = brand_name.lower()
    slug = quote_plus(brand_name)
    extra_search_urls = [
        f"https://www.bcorporation.net/en-us/find-a-b-corp/search?query={slug}",
        f"https://www.fairwear.org/brands?search={slug}",
        f"https://www.oeko-tex.com/en/buying-guide?search={slug}"
    ]
    for url in CERTIFICATION_HOMEPAGES + extra_search_urls:
        html = fetch_html_lenient(url)
        if not html:
            continue
        text = remove_html(html).lower()
        if brand_lower in text:
            collected.append({"url": url, "html": html, "source_type": "certification_database"})
    print("Certification pages collected:", len(collected))
    return collected[:10]

# Audit aliases: NO SERPAPI
collect_trusted_news = collect_trusted_news_no_api
check_certification_databases = check_certification_databases_no_api
collect_wide_web_context = collect_wide_web_context_no_api

# ============================================================
# EVIDENCE STORAGE AND EVALUATION
# ============================================================

def evaluate_evidence_strength(text: str, source_type: str):
    lower = (text or "").lower()
    score = 0
    if re.search(r"\d+%", lower): score += 20
    if re.search(r"\b20\d{2}\b", lower): score += 10
    if any(w in lower for w in ["certified", "verified", "third-party", "independent", "assurance"]): score += 20
    if any(w in lower for w in ["supplier", "factory", "tier 1", "tier 2", "audit", "traceability"]): score += 15
    if any(w in lower for w in ["scope 1", "scope 2", "scope 3", "carbon", "emissions", "net zero"]): score += 15
    source_bonus = {"official_website": 5, "trusted_news": 15, "certification_database": 25, "wide_web_context": 10}.get(source_type, 5)
    score += source_bonus
    return min(score, 100)

def store_evidence(brand_name, url, source_type, raw_html):
    plain_text = remove_html(raw_html)
    cleaned_text = clean_text(plain_text)
    content_hash = hash_text(f"{brand_name}|{url}|{cleaned_text}")
    evidence_strength = evaluate_evidence_strength(plain_text, source_type)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM evidence WHERE brand_name = ? AND source_url = ? AND content_hash = ?", (brand_name, url, content_hash))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return existing[0], plain_text
    cur.execute("""
    INSERT INTO evidence (brand_name, source_url, source_type, raw_html, plain_text, cleaned_text, content_hash, evidence_strength, scraped_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (brand_name, url, source_type, raw_html, plain_text, cleaned_text, content_hash, evidence_strength, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    evidence_id = cur.lastrowid
    conn.close()
    return evidence_id, plain_text

# ============================================================
# TOPIC MODELLING / CLASSIFICATION
# ============================================================

def keyword_score(paragraph, keywords):
    lower = paragraph.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in lower)
    return min(matches / 2, 1.0) if matches else 0.0

def embedding_score(paragraph, topic_name):
    paragraph_embedding = embedding_model.encode(paragraph, convert_to_tensor=True)
    score = util.cos_sim(paragraph_embedding, topic_embeddings[topic_name]).item()
    return max(0.0, min(score, 1.0))

def classify_and_store_topics(evidence_id, paragraphs):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    labelled = []
    for paragraph in paragraphs:
        for topic, words in TOPICS.items():
            ks = keyword_score(paragraph, words)
            es = embedding_score(paragraph, topic)
            final = round((0.35 * ks) + (0.65 * es), 4)
            if final >= 0.35:
                cur.execute("""
                INSERT INTO topic_labels (evidence_id, paragraph, topic_name, keyword_score, embedding_score, final_confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (evidence_id, paragraph, topic, ks, es, final, datetime.now(timezone.utc).isoformat()))
                labelled.append({"paragraph": paragraph, "topic": topic, "confidence": final})
    conn.commit(); conn.close()
    return labelled

# ============================================================
# CLAIMS, SENTIMENT, GREENWASHING
# ============================================================

def extract_claims(labelled_topics):
    claim_words = ["we aim", "we use", "we source", "we reduce", "committed", "certified", "sustainable", "recycled", "organic", "net zero", "responsible", "target", "goal"]
    claims = []
    for item in labelled_topics:
        lower = item["paragraph"].lower()
        if any(word in lower for word in claim_words):
            claims.append({"claim": item["paragraph"], "topic": item["topic"], "confidence": item["confidence"]})
    return claims

def analyse_sentiment(paragraphs):
    if not paragraphs:
        return 0  # avoid fake same 10/100 score when no evidence exists
    scores = [(sentiment_analyzer.polarity_scores(p)["compound"] + 1) / 2 for p in paragraphs]
    return round((sum(scores) / len(scores)) * 100, 2)

def detect_greenwashing(claims, external_text=""):
    risk_points = 0.0
    if claims:
        for claim in claims:
            text = claim["claim"].lower()
            if any(word in text for word in VAGUE_GREENWASHING_WORDS): risk_points += 0.25
            has_specific_data = bool(re.search(r"\d+%|\b20\d{2}\b|net zero|scope 1|scope 2|scope 3|certified|verified", text))
            if not has_specific_data: risk_points += 0.20
        base_risk = min(risk_points / len(claims), 1.0)
    else:
        base_risk = 0.0
    allegation_terms = ["greenwashing", "misleading", "false claim", "lawsuit", "investigation", "accused", "deceptive", "unsubstantiated"]
    external_lower = (external_text or "").lower()
    news_risk = min(sum(1 for t in allegation_terms if t in external_lower) * 0.15, 1.0)
    return round(min((base_risk * 0.7) + (news_risk * 0.3), 1.0) * 100, 2)

# ============================================================
# SCORING FUNCTIONS
# ============================================================

def analyse_materials(text):
    lower = (text or "").lower()
    found = sorted({m for m in MATERIAL_TERMS if m in lower})
    sustainable_found = sorted({m for m in SUSTAINABLE_MATERIAL_TERMS if m in lower})
    has_percentage = bool(re.search(r"\d+%", lower))
    score = 0
    score += min(len(found) * 5, 35)
    score += min(len(sustainable_found) * 10, 40)
    if has_percentage: score += 15
    if any(c.lower() in lower for c in CERTIFICATION_NAMES): score += 10
    return {"score": min(score, 100), "materials_found": found, "preferred_materials_found": sustainable_found, "has_percentage_disclosure": has_percentage}

def analyse_certifications(text):
    lower = (text or "").lower()
    found = sorted({c for c in CERTIFICATION_NAMES if c.lower() in lower})
    return {"found": found, "score": min(len(found) / 3 * 100, 100)}

def score_transparency(text):
    lower = (text or "").lower()
    score = 0
    if "sustainability report" in lower: score += 20
    if "annual report" in lower or "impact report" in lower or "esg report" in lower: score += 20
    if re.search(r"\d+%", lower): score += 15
    if any(w in lower for w in ["supplier", "factory", "traceability", "supplier list"]): score += 20
    if any(w in lower for w in ["third-party", "independent", "verified", "assurance"]): score += 15
    if any(w in lower for w in ["progress", "target", "kpi", "goal"]): score += 10
    return min(score, 100)

def score_supply_chain(text):
    lower = (text or "").lower()
    score = 0
    if "supplier" in lower: score += 25
    if "factory" in lower or "factories" in lower: score += 25
    if "traceability" in lower or "traceable" in lower: score += 25
    if "audit" in lower or "code of conduct" in lower: score += 15
    if "tier 1" in lower or "tier 2" in lower or "tier 3" in lower: score += 10
    return min(score, 100)

def score_esg(text):
    lower = (text or "").lower()
    score = 0
    if "esg" in lower: score += 20
    if "carbon" in lower or "emissions" in lower: score += 25
    if "water" in lower: score += 15
    if "biodiversity" in lower: score += 10
    if "climate" in lower or "net zero" in lower: score += 20
    if "human rights" in lower or "modern slavery" in lower: score += 10
    return min(score, 100)

def calculate_final_scores(material_score, esg_score, transparency_score, supply_chain_score, certification_score, public_perception_score, greenwashing_risk):
    positive_score = (material_score * 0.20 + esg_score * 0.15 + transparency_score * 0.20 + supply_chain_score * 0.15 + certification_score * 0.10 + public_perception_score * 0.20)
    greenwashing_penalty = greenwashing_risk * 0.20
    final_score = max(0, positive_score - greenwashing_penalty)
    authenticity_score = max(0, round((transparency_score * 0.4) + ((100 - greenwashing_risk) * 0.4) + (public_perception_score * 0.2), 2))
    return {"positive_score": round(positive_score, 2), "greenwashing_penalty": round(greenwashing_penalty, 2), "final_score": round(final_score, 2), "authenticity_score": authenticity_score}

def recommendation(final_score, greenwashing_risk, reasons):
    if final_score >= 80 and greenwashing_risk <= 20:
        return {
            "level": "Unconditionally Recommended",
            "icon": "✅",
            "message": "Strong sustainability performance, good transparency, and low greenwashing risk.",
            "why": reasons
        }

    if final_score >= 70 and greenwashing_risk <= 40:
        return {
            "level": "Conditionally Recommended",
            "icon": "⚠️",
            "message": "Acceptable sustainability performance, but some evidence should be reviewed.",
            "why": reasons
        }

    if final_score >= 70 and greenwashing_risk > 40:
        return {
            "level": "Conditionally Recommended",
            "icon": "⚠️",
            "message": "The score is acceptable, but greenwashing or transparency concerns require caution.",
            "why": reasons
        }

    return {
        "level": "Not Recommended",
        "icon": "❌",
        "message": "The brand does not show enough credible sustainability evidence.",
        "why": reasons
    }

def generate_recommendation_explanation(scores, greenwashing_risk, certifications, material_summary, source_counts, text_lengths):
    reasons = []
    if scores["material_analysis"] < 50:
        reasons.append("Brand-level material information is limited or does not show strong use of preferred materials.")
    if scores["transparency_score"] < 50:
        reasons.append("The brand has limited transparency in reporting, measurable targets, or third-party verification.")
    if scores["supply_chain_disclosure"] < 50:
        reasons.append("Supplier, factory, or traceability information is not strongly disclosed.")
    if scores["certifications"] < 40:
        reasons.append("Few recognised third-party certifications were found.")
    if scores["public_perception"] < 50:
        reasons.append("Independent public/news evidence is limited or sustainability sentiment is weak.")
    if greenwashing_risk > 40:
        reasons.append("Greenwashing risk is moderate/high due to vague, unsupported, or externally contested claims.")
    if source_counts.get("total_sources_used", 0) < 3:
        reasons.append("Only a small number of evidence sources could be processed, so the recommendation should be interpreted cautiously.")
    if text_lengths.get("all_text", 0) < 1500:
        reasons.append("The collected evidence text is short, so the system may not have captured the brand's full sustainability context.")
    if certifications:
        reasons.append(f"Recognised certifications found: {', '.join(certifications)}.")
    if material_summary.get("preferred_materials_found"):
        reasons.append(f"Preferred materials detected: {', '.join(material_summary['preferred_materials_found'][:6])}.")
    if not reasons:
        reasons.append("The available evidence generally supports the brand's sustainability claims.")
    return reasons

# ============================================================
# PRODUCT ALTERNATIVES HELPERS - SerpAPI optional
# ============================================================

def serpapi_search(query: str, max_results: int = 8):
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("SerpAPI key not loaded. Product alternative search will return empty results.")
        return []
    try:
        response = requests.get("https://serpapi.com/search.json", params={"engine": "google", "q": query, "api_key": api_key, "num": max_results}, timeout=20)
        response.raise_for_status()
        data = response.json()
        return [r.get("link") for r in data.get("organic_results", []) if r.get("link")][:max_results]
    except Exception as e:
        print("SerpAPI error:", e)
        return []

def detect_product_category(text):
    lower = (text or "").lower()
    for category, keywords in PRODUCT_CATEGORIES.items():
        if any(k in lower for k in keywords): return category
    return "fashion item"

def detect_product_materials(text):
    lower = (text or "").lower()
    return sorted({m for m in MATERIAL_TERMS if m in lower})

def extract_material_composition(text):
    matches = re.findall(r"(\d{1,3})\s?%\s?([a-z\s\-]+)", (text or "").lower())
    composition = []
    for percentage, material in matches:
        for known in MATERIAL_TERMS:
            if known in material:
                composition.append({"material": known, "percentage": int(percentage)})
    unique, seen = [], set()
    for item in composition:
        key = (item["material"], item["percentage"])
        if key not in seen:
            seen.add(key); unique.append(item)
    return unique

# ============================================================
# MAIN AUDIT ENDPOINT / FUNCTION
# ============================================================

@app.post("/audit")
def audit_brand(req: AuditRequest):
    init_db()
    brand_name = req.brand_name.strip()
    domain = choose_audit_domain(brand_name, req.official_domain)

    official_pages = discover_official_pages(domain)
    news_pages = collect_trusted_news(brand_name)
    certification_pages = check_certification_databases(brand_name)
    wide_web_pages = collect_wide_web_context(brand_name)

    all_sources = []
    for url in official_pages:
        html = fetch_html_lenient(url)
        if html:
            all_sources.append({"url": url, "html": html, "source_type": "official_website"})
    all_sources.extend(news_pages)
    all_sources.extend(certification_pages)
    all_sources.extend(wide_web_pages)

    all_text = official_text = news_text = certification_text = wide_web_text = ""
    all_labelled_topics, evidence_links, evidence_strengths = [], [], []

    for item in all_sources:
        evidence_id, plain_text = store_evidence(brand_name, item["url"], item["source_type"], item["html"])
        strength = evaluate_evidence_strength(plain_text, item["source_type"])
        evidence_strengths.append(strength)
        paragraphs = split_paragraphs(plain_text)
        labelled = classify_and_store_topics(evidence_id, paragraphs)
        all_text += "\n" + plain_text
        all_labelled_topics.extend(labelled)
        evidence_links.append(item["url"])
        if item["source_type"] == "official_website": official_text += "\n" + plain_text
        elif item["source_type"] == "trusted_news": news_text += "\n" + plain_text
        elif item["source_type"] == "certification_database": certification_text += "\n" + plain_text
        elif item["source_type"] == "wide_web_context": wide_web_text += "\n" + plain_text

    claims = extract_claims(all_labelled_topics)
    brand_material_summary = analyse_materials(official_text + "\n" + certification_text + "\n" + wide_web_text)
    certifications = analyse_certifications(certification_text + "\n" + all_text)

    material_score = brand_material_summary["score"]
    esg_score = score_esg(all_text)
    transparency_score = score_transparency(official_text + "\n" + all_text)
    supply_chain_score = score_supply_chain(all_text)
    certification_score = certifications["score"]
    public_perception_score = analyse_sentiment(split_paragraphs(news_text + "\n" + wide_web_text))
    greenwashing_risk = detect_greenwashing(claims, news_text + "\n" + wide_web_text)

    score_data = calculate_final_scores(material_score, esg_score, transparency_score, supply_chain_score, certification_score, public_perception_score, greenwashing_risk)
    

    scores_obj = {"material_analysis": material_score, "transparency_score": transparency_score, "supply_chain_disclosure": supply_chain_score, "certifications": certification_score, "public_perception": public_perception_score}
    source_counts = {"official_pages": len(official_pages), "trusted_news_pages": len(news_pages), "certification_pages": len(certification_pages), "wide_web_pages": len(wide_web_pages), "total_sources_used": len(all_sources)}
    text_lengths = {"all_text": len(all_text), "official_text": len(official_text), "news_text": len(news_text), "certification_text": len(certification_text), "wide_web_text": len(wide_web_text)}
    recommendation_explanation = generate_recommendation_explanation(
    scores_obj,
    greenwashing_risk,
    certifications["found"],
    brand_material_summary,
    source_counts,
    text_lengths
)

    rec = recommendation(
        score_data["final_score"],
        greenwashing_risk,
        recommendation_explanation
    )

    print(
        "\nAUDIT DEBUG",
        brand_name,
        source_counts,
        text_lengths,
        "final",
        score_data["final_score"]
    )

    print("\nAUDIT DEBUG", brand_name, source_counts, text_lengths, "final", score_data["final_score"])

    return {
        "brand": brand_name,
        "official_domain_used": domain,
        "audit_uses_serpapi": False,
        "sustainability_summary": {"final_score": score_data["final_score"], "positive_score_before_penalty": score_data["positive_score"], "greenwashing_penalty": score_data["greenwashing_penalty"], "recommendation": rec},
        "scores": {"authenticity_score": score_data["authenticity_score"], "transparency_score": transparency_score, "greenwashing_risk": greenwashing_risk, "public_perception": public_perception_score, "material_analysis": material_score, "esg_performance": esg_score, "supply_chain_disclosure": supply_chain_score, "certifications": certification_score},
        "brand_material_summary": brand_material_summary,
        "certifications_found": certifications["found"],
        "recommendation_explanation": recommendation_explanation,
        "claims_extracted": claims[:10],
        "topics_detected": all_labelled_topics[:15],
        "evidence_links": evidence_links[:30],
        "source_counts": source_counts,
        "debug": {"text_lengths": text_lengths, "average_evidence_strength": round(sum(evidence_strengths)/len(evidence_strengths), 2) if evidence_strengths else 0, "claims_found": len(claims), "topics_found": len(all_labelled_topics)}
    }

@app.post("/product-alternatives")
def product_alternatives(req: ProductAlternativeRequest):
    combined = f"{req.title or ''}\n{req.description or ''}\n{req.page_text or ''}"
    category = detect_product_category(combined)
    materials = detect_product_materials(combined)
    query = f"sustainable ethical {' '.join(materials[:2])} {category} material composition"
    urls = serpapi_search(query, max_results=8)
    alternatives = []
    seen_brands = set()
    for url in urls:
        html = fetch_html_lenient(url)
        if not html: continue
        title = BeautifulSoup(html, "html.parser").find("title")
        product_title = title.get_text(" ", strip=True) if title else url
        brand = urlparse(url).netloc.replace("www.", "").split(".")[0].title()
        if brand.lower() in seen_brands: continue
        seen_brands.add(brand.lower())
        plain = remove_html(html)
        alternatives.append({"product_info": {"title": product_title, "brand": brand, "url": url, "price": "Not detected"}, "material_analysis": {"materials_detected": detect_product_materials(plain), "material_composition": extract_material_composition(plain)}, "alternative_ranking_score": 50})
    return {"detected_product": {"title": req.title, "page_url": req.page_url, "category": category, "materials": materials, "material_composition": extract_material_composition(combined)}, "alternative_search_query": query, "alternatives": alternatives}

@app.get("/")
def root():
    return {
        "status": "Sustainability audit backend running",
        "audit_uses_serpapi": bool(SERPAPI_KEY)
    }

# ============================================================
# NOTEBOOK TEST HELPER
# ============================================================

def print_audit_debug(brand_name, official_domain=None):
    result = audit_brand(AuditRequest(brand_name=brand_name, official_domain=official_domain))
    print("\n" + "="*80)
    print("BRAND:", result["brand"])
    print("DOMAIN:", result["official_domain_used"])
    print("FINAL SCORE:", result["sustainability_summary"]["final_score"])
    print("RECOMMENDATION:", result["sustainability_summary"]["recommendation"]["level"], result["sustainability_summary"]["recommendation"]["icon"])
    print("SOURCE COUNTS:", result["source_counts"])
    print("DEBUG:", result["debug"])
    print("BRAND MATERIAL SUMMARY:", result["brand_material_summary"])
    print("REASONS:")
    for r in result["recommendation_explanation"]:
        print("-", r)
    print("EVIDENCE LINKS:")
    for link in result["evidence_links"][:10]:
        print("-", link)
    return result
