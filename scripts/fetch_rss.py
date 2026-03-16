#!/usr/bin/env python3
"""
fetch_rss.py  —  Daily RSS fetcher for Global Study Abroad News Tracker
------------------------------------------------------------------------
Free stack, no paid API required:
  - rss2json.com     : free RSS-to-JSON proxy (1000 req/day)
  - Google Translate : free unofficial endpoint for non-English content
  - Rule engine      : region/destination classification + impact scoring
  - Insight engine   : template-based professional insights by article type

URL fix: RSS items sometimes give homepage URL in 'link' but the real
article URL in 'guid'. We try guid first, validate it looks like an
article URL, then fall back to link.

Output: public/news.json
"""

import json, re, os, sys, time, html, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# ── FEEDS ─────────────────────────────────────────────────────────────────────
FEEDS = [
    # ── Global / International specialist ────────────────────────────────────
    {"name": "ICEF Monitor",          "url": "https://monitor.icef.com/feed/",                                          "color": "#1a3a5c", "lang": "en"},
    {"name": "The PIE News",          "url": "https://thepienews.com/feed/",                                            "color": "#7b341e", "lang": "en"},
    {"name": "Inside Higher Ed",      "url": "https://www.insidehighered.com/rss.xml",                                  "color": "#285e61", "lang": "en"},
    {"name": "HEPI",                  "url": "https://www.hepi.ac.uk/category/blog/feed/",                              "color": "#4a235a", "lang": "en"},
    {"name": "Higher Ed Dive",        "url": "https://www.highereddive.com/feeds/news/",                                "color": "#1e5631", "lang": "en"},
    # NAFSA: world's largest intl education association — US visa/immigration policy RSS
    {"name": "NAFSA",                 "url": "https://www.nafsa.org/rss-feed.xml?feed=am_news",                         "color": "#0e4d8c", "lang": "en"},
    # ── China ─────────────────────────────────────────────────────────────────
    {"name": "Sixth Tone",            "url": "https://www.sixthtone.com/rss",                                           "color": "#922b21", "lang": "en"},
    {"name": "SCMP (Education)",      "url": "https://www.scmp.com/rss/318207/feed",                                    "color": "#7b241c", "lang": "en"},
    # Replaces Caixin (403) — China Daily is official EN paper, RSS open access
    {"name": "China Daily",           "url": "https://www.chinadaily.com.cn/rss/china_rss.xml",                        "color": "#c0392b", "lang": "en"},
    # ── India ─────────────────────────────────────────────────────────────────
    {"name": "Times of India (Edu)",  "url": "https://timesofindia.indiatimes.com/rssfeeds/913168846.cms",              "color": "#d4820a", "lang": "en"},
    {"name": "The Hindu (Edu)",       "url": "https://www.thehindu.com/education/?service=rss",                        "color": "#145a32", "lang": "en"},
    # ── Southeast Asia ────────────────────────────────────────────────────────
    {"name": "VnExpress (EN)",        "url": "https://e.vnexpress.net/rss/news.rss",                                    "color": "#d35400", "lang": "en"},
    {"name": "VnExpress (Giáo dục)",  "url": "https://vnexpress.net/rss/giao-duc.rss",                                 "color": "#b94500", "lang": "vi"},
    # ── West Africa / Global ──────────────────────────────────────────────────
    # ── Latin America ─────────────────────────────────────────────────────────
    {"name": "El País (English)",     "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/english.elpais.com/portada", "color": "#1a5276", "lang": "en"},
    {"name": "Folha de S.Paulo",      "url": "https://feeds.folha.uol.com.br/educacao/rss091.xml",                     "color": "#154360", "lang": "pt"},
]

# ── URL RESOLVER ──────────────────────────────────────────────────────────────
# Known homepage / channel URLs that should never be used as article URLs.
# If resolved URL matches any of these patterns, we skip the item.
HOMEPAGE_PATTERNS = [
    r"^https?://[^/]+/?$",                       # bare domain
    r"^https?://[^/]+/rss",                      # RSS feed URL itself
    r"^https?://[^/]+/category/",               # category pages
    r"^https?://[^/]+/tag/",                    # tag pages
    r"^https?://[^/]+/education/?$",            # section index
    r"^https?://[^/]+/giao-duc/?$",             # VnExpress section
    r"^https?://[^/]+/educacion/?$",            # El País section
    r"^https?://[^/]+/educacao/?$",             # Folha section
    r"thepaper\.cn/rss",                        # Thepaper feed URL
    r"jyb\.cn/rmtzgjyb/rss",                   # jyb feed URL
]

def is_article_url(url):
    """Return True if the URL looks like a real article (not a homepage/section)."""
    if not url or not url.startswith("http"):
        return False
    for pattern in HOMEPAGE_PATTERNS:
        if re.search(pattern, url):
            return False
    # Must have a meaningful path (at least one slash after domain + some slug)
    path = urllib.parse.urlparse(url).path.rstrip("/")
    return len(path) > 5

def resolve_url(item):
    """
    Pick the best article URL from an RSS item.
    Priority: guid (if it looks like an article URL) > link > None
    Also handles guid wrapped in a dict (rss2json sometimes returns {"_value": url, "isPermaLink": ...})
    """
    candidates = []

    # guid can be a string or a dict
    guid = item.get("guid", "")
    if isinstance(guid, dict):
        guid = guid.get("_value") or guid.get("#text") or ""
    if guid:
        candidates.append(str(guid).strip())

    link = item.get("link", "")
    if link:
        candidates.append(str(link).strip())

    for url in candidates:
        if is_article_url(url):
            return url

    # Last resort: return link even if it looks like a homepage
    return link or ""


# ── GOOGLE TRANSLATE ──────────────────────────────────────────────────────────
def google_translate(text, src_lang, retries=3):
    if not text or src_lang == "en":
        return text
    text = text[:800]
    params = urllib.parse.urlencode({
        "client": "gtx", "sl": src_lang, "tl": "en", "dt": "t", "q": text
    })
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
            return "".join(seg[0] for seg in data[0] if seg[0]).strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                print(f"    translate error ({src_lang}): {e}", file=sys.stderr)
    return text


# ── CLASSIFIERS ───────────────────────────────────────────────────────────────
SOURCE_KW = {
    "China":          ["china", "chinese", "beijing", "shanghai", "mainland", "prc", "sino",
                       "中国", "留学生", "出国留学"],
    "Southeast Asia": ["southeast asia", "vietnam", "vietnamese", "malaysia", "indonesia",
                       "thailand", "philippines", "myanmar", "cambodia", "singapore", "asean",
                       "sinh viên", "du học"],
    "India":          ["india", "indian", "delhi", "mumbai", "bangalore", "hyderabad"],
    "South Asia":     ["pakistan", "bangladesh", "sri lanka", "nepal", "south asia"],
    "West Africa":    ["nigeria", "nigerian", "ghana", "ghanaian", "cameroon", "west africa",
                       "senegal"],
    "Latin America":  ["latin america", "brazil", "brazilian", "mexico", "mexican", "colombia",
                       "venezuela", "argentina", "chile", "brasil", "latinoamérica",
                       "estudiante internacional", "estudante"],
    "MENA":           ["middle east", "north africa", "saudi arabia", "saudi", "uae",
                       "united arab emirates", "egypt", "egyptian", "jordan", "jordanian",
                       "iran", "iranian", "iraq", "iraqi", "kuwait", "qatar", "bahrain",
                       "oman", "lebanon", "lebanese", "morocco", "moroccan", "tunisia",
                       "algeria", "algerian", "libya", "mena", "gulf"],
}
DEST_KW = {
    "USA":         ["united states", " u.s.", "american universit", "sevis", "f-1",
                    "opt ", "stem opt", "us visa", "dhs"],
    "UK":          ["united kingdom", " u.k.", " uk ", "british", "ucas", "home office",
                    "ukvi", "graduate route", "reino unido"],
    "Canada":      ["canada", "canadian", "ircc", "study permit", "pgwp", "ontario",
                    "vancouver", "toronto", "montreal"],
    "Australia":   ["australia", "australian", "esos", "cricos", "485 visa",
                    "subclass 500", "australi"],
    "New Zealand": ["new zealand", " nz ", "nzqa", "auckland", "wellington"],
}
EDU_KW = [
    "international student", "study abroad", "foreign student", "student visa",
    "enrolment", "enrollment", "higher education", "university", "college",
    "tuition", "scholarship", "overseas student", "postgraduate", "undergraduate",
    "留学", "签证", "大学", "奖学金", "du học", "estudiante internacional",
]
HIGH_KW = ["ban", "suspend", "restrict", "halt", "block", "cancel", "cap", "surge",
           "crisis", "record", "historic", "emergency", "doubles", "halts", "revokes",
           "禁止", "限制", "取消"]
MED_KW  = ["policy", "update", "reform", "announce", "increase", "decrease",
           "new programme", "partnership", "agreement", "target", "launches", "raises",
           "政策", "宣布", "合作"]

def classify(text):
    t = text.lower()
    sources = [k for k, kws in SOURCE_KW.items() if any(w in t for w in kws)]
    dests   = [k for k, kws in DEST_KW.items()   if any(w in t for w in kws)]
    is_edu  = any(w in t for w in EDU_KW) or bool(sources) or bool(dests)
    return sources, dests, is_edu

def score_impact(title):
    t = title.lower()
    if any(w in t for w in HIGH_KW): return "High"
    if any(w in t for w in MED_KW):  return "Medium"
    return "Low"


# ── PROFESSIONAL INSIGHT TEMPLATES ───────────────────────────────────────────
def _alts(dests):
    mapping = {
        "USA":         ["Canada", "UK", "Australia"],
        "UK":          ["Canada", "Australia", "Germany"],
        "Canada":      ["Australia", "UK", "New Zealand"],
        "Australia":   ["Canada", "New Zealand", "UK"],
        "New Zealand": ["Australia", "Canada"],
    }
    out, seen = [], set()
    for d in (dests or []):
        for s in mapping.get(d, []):
            if s not in seen and s not in (dests or []):
                out.append(s); seen.add(s)
    return ", ".join(out[:2])

def generate_insight(title, summary, sources, dests, impact):
    t   = (title + " " + summary).lower()
    src = " & ".join(sources) if sources else "affected markets"
    dst = " & ".join(dests)   if dests   else "target destinations"
    alt = _alts(dests)

    if any(w in t for w in ["ban", "suspend", "halt", "restrict", "block", "revoke", "emergency brake"]):
        return (
            f"Immediate action required for {src} students with pending or planned "
            f"applications to {dst}. Audit your current pipeline and prepare contingency "
            f"pathways{(' — consider ' + alt) if alt else ''}. "
            f"Students already enrolled are typically unaffected; clarify status proactively."
        )
    if any(w in t for w in ["fee", "doubles", "cost"]) and any(w in t for w in ["visa", "tuition"]):
        return (
            f"Cost shock for {src} applicants targeting {dst}. Update ROI calculations "
            f"in student consultations immediately."
            + (f" Position {alt} as a cost-competitive alternative." if alt else "")
            + " Highlight scholarships and on-campus work rights to offset sticker shock."
        )
    if any(w in t for w in ["decline", "fall", "drop", "decrease", "down", "contract"]) and \
       any(w in t for w in ["enrol", "student", "applicant"]):
        return (
            f"Structural decline signal for {dst} from {src}. Diversify destination "
            f"portfolio now. Focus messaging on post-study work rights, PR pathways, "
            f"and safety — these consistently outrank prestige for cost-sensitive markets."
        )
    if any(w in t for w in ["scholarship", "fund", "invest", "new pathway", "partnership", "mou", "agreement"]):
        return (
            f"Opportunity signal for {src} applicants: new initiative opens in {dst}. "
            f"Fast-track pipeline building while competition is low — early awareness "
            f"creates strong conversion advantage. Research eligibility criteria now."
        )
    if any(w in t for w in ["cap", "quota", "limit", "allocation", "planning level"]):
        return (
            f"Capacity constraint in {dst} affecting {src} pipeline. Prioritise "
            f"high-quality applications and submit early. Graduate students often sit "
            f"under separate (higher) caps — segment your pipeline accordingly."
        )
    if any(w in t for w in ["transnational", "tne", "joint", "domestic campus"]):
        return (
            f"TNE expansion in {src} may reduce outbound demand over a 3–5 year horizon. "
            f"Institutions with {src} partnerships should renegotiate value propositions; "
            f"those without should establish a presence before domestic alternatives consolidate."
        )
    if any(w in t for w in ["ai", "artificial intelligence", "technology", "digital"]):
        return (
            f"Domestic education quality signals from {src}. Monitor whether AI-driven "
            f"upgrades begin closing the quality gap that drives outbound mobility. "
            f"Medium-term pipeline risk is low but worth tracking in annual strategy reviews."
        )
    return (
        f"Monitor closely: this development affects the {src} → {dst} corridor. "
        f"Review implications for your current pipeline and update student briefings. "
        f"{'High-impact — recommend immediate client communication.' if impact == 'High' else 'File for quarterly market review.'}"
    )


# ── HELPERS ───────────────────────────────────────────────────────────────────
def strip_html(text):
    if not text: return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def parse_date(s):
    if not s: return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try: return datetime.strptime(s[:30], fmt).strftime("%Y-%m-%d")
        except ValueError: pass
    try: return parsedate_to_datetime(s).strftime("%Y-%m-%d")
    except: pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def is_recent(date_str, days=14):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - d) <= timedelta(days=days)
    except: return True


# ── FETCH ONE FEED (direct XML, no third-party proxy) ────────────────────────
# Namespaces used in RSS/Atom feeds
NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "media":   "http://search.yahoo.com/mrss/",
}

def _text(el, *tags):
    """Return first non-empty text found among tag names (supports namespace prefixes)."""
    for tag in tags:
        if ":" in tag:
            prefix, local = tag.split(":", 1)
            uri = NS.get(prefix, "")
            child = el.find(f"{{{uri}}}{local}")
        else:
            child = el.find(tag)
        if child is not None and child.text:
            return child.text.strip()
    return ""

def fetch_feed(feed):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; EduNewsTracker/2.0; +https://github.com)",
        "Accept":     "application/rss+xml, application/xml, text/xml, */*",
    }
    req = urllib.request.Request(feed["url"], headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
    except Exception as e:
        print(f"  ✗ {feed['name']}: {e}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  ✗ {feed['name']}: XML parse error: {e}", file=sys.stderr)
        return []

    # Support both RSS 2.0 (<item>) and Atom (<entry>)
    items = root.findall(".//item") or root.findall(f".//{{{NS['atom']}}}entry")

    lang     = feed.get("lang", "en")
    articles = []

    for item in items[:30]:
        # Title
        raw_title = strip_html(_text(item, "title", "atom:title")).strip()

        # Summary / description
        raw_summary = strip_html(
            _text(item, "description", "content:encoded", "atom:summary", "atom:content", "dc:description")
        )[:500]

        # Date
        pub = parse_date(_text(item, "pubDate", "dc:date", "atom:published", "atom:updated"))

        # URL: try guid, then link, then atom:link href
        guid = _text(item, "guid")
        link = _text(item, "link", "atom:link")
        # atom:link is often an empty element with href attribute
        if not link:
            al = item.find(f"{{{NS['atom']}}}link")
            if al is not None:
                link = al.get("href", "")

        url = resolve_url({"guid": guid, "link": link})

        if not raw_title or not url:
            continue
        if not is_recent(pub):
            continue

        # Translate non-English content
        if lang != "en":
            title      = google_translate(raw_title,   lang)
            summary    = google_translate(raw_summary, lang)
            translated = True
            time.sleep(0.3)
        else:
            title, summary, translated = raw_title, raw_summary, False

        full_text = f"{title} {summary}"
        sources, dests, is_edu = classify(full_text)
        if not is_edu:
            continue

        impact  = score_impact(title)
        insight = generate_insight(title, summary, sources, dests, impact)

        articles.append({
            "id":         0,
            "title":      title,
            "source":     feed["name"],
            "color":      feed["color"],
            "url":        url,
            "pubDate":    pub,
            "summary":    summary,
            "insight":    insight,
            "impact":     impact,
            "sources":    sources,
            "dests":      dests,
            "translated": translated,
            "origLang":   lang if translated else None,
        })

    tag = " [translated]" if lang != "en" else ""
    print(f"  ✓ {feed['name']}: {len(articles)} articles{tag}")
    return articles


# ── QWEN API HELPER ───────────────────────────────────────────────────────────
def qwen_call(api_key, prompt, max_tokens=200, temperature=0.3):
    """Single call to Qwen via DashScope compatible-mode endpoint."""
    payload = json.dumps({
        "model": "qwen-plus",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def load_previous_urls():
    """Load URLs that were shown in the last run to avoid repeats."""
    try:
        with open("public/news.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        urls = {a["url"] for a in data.get("articles", [])}
        print(f"  📋 Loaded {len(urls)} previously shown URLs")
        return urls
    except Exception:
        return set()


# ── STEP 1: AI RELEVANCE SCORING & SELECTION (top 10) ────────────────────────
def qwen_select_top(articles, api_key, prev_urls, top_n=10):
    """
    Score articles 1-10 for recruitment relevance, then apply a freshness
    penalty (-3) to any article already shown in the previous run, so that
    new articles are preferred over repeated ones at equal quality.
    """
    if not api_key:
        rank = {"High": 0, "Medium": 1, "Low": 2}
        articles.sort(key=lambda a: (rank.get(a["impact"], 2), a["pubDate"]))
        print(f"  ℹ No API key — top {top_n} selected by rule-based impact score")
        return articles[:top_n]

    print(f"  🤖 Qwen scoring {len(articles)} articles for recruitment relevance…")

    # Build numbered list — titles only to keep prompt short and avoid truncation
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. {a['title'][:100]}")
    article_list = "\n".join(lines)

    prompt = (
        "You are a senior international student recruitment strategist advising university "
        "admissions teams in the USA, UK, Australia, and New Zealand. "
        "Score each article 1–10 on how directly it affects international student recruitment "
        "at these destination universities — considering visa policy changes, student flow data, "
        "geopolitical risks affecting source markets, compliance requirements, competitor moves, "
        "or shifts in student demand from China, India, Southeast Asia, South Asia, West Africa, "
        "and Latin America. Score 10 = immediate action required by admissions teams today; "
        "Score 1 = no relevance to university international recruitment.\n\n"
        f"{article_list}\n\n"
        "Reply with ONLY a JSON array, one object per article, no markdown, no explanation:\n"
        '[{"i":1,"score":8},{"i":2,"score":3}, ...]'
    )

    try:
        raw = qwen_call(api_key, prompt, max_tokens=1800, temperature=0.1)
        raw = re.sub(r"```[a-z]*", "", raw).strip().strip("`")
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)
        scores = json.loads(raw)
        score_map = {int(s["i"]): int(s["score"]) for s in scores}
    except Exception as e:
        print(f"  ⚠ Qwen scoring error: {e} — falling back to impact sort", file=sys.stderr)
        rank = {"High": 0, "Medium": 1, "Low": 2}
        articles.sort(key=lambda a: (rank.get(a["impact"], 2), a["pubDate"]))
        return articles[:top_n]

    # Attach base scores, then apply freshness penalty for repeated articles
    repeat_count = 0
    for i, a in enumerate(articles, 1):
        base = score_map.get(i, 5)
        if a["url"] in prev_urls:
            a["relevanceScore"] = max(1, base - 3)  # -3 penalty, floor at 1
            repeat_count += 1
        else:
            a["relevanceScore"] = base

    if repeat_count:
        print(f"  🔄 Freshness penalty applied to {repeat_count} repeated articles")

    articles.sort(key=lambda a: a["relevanceScore"], reverse=True)
    selected = articles[:top_n]
    fresh = sum(1 for a in selected if a["url"] not in prev_urls)
    print(f"  ✓ Top {len(selected)} selected — {fresh} new, {len(selected)-fresh} repeated "
          f"(scores: {[a['relevanceScore'] for a in selected]})")
    return selected


# ── STEP 2: AI INSIGHT GENERATION for selected articles ──────────────────────
def qwen_generate_insights(articles, api_key):
    """Generate professional 2-sentence insight for each selected article."""
    if not api_key:
        print("  ℹ No API key — using template insights", file=sys.stderr)
        return articles

    print(f"  🤖 Generating Qwen insights for {len(articles)} articles…")

    for a in articles:
        src = ", ".join(a["sources"]) if a["sources"] else "international students"
        dst = ", ".join(a["dests"])   if a["dests"]   else "major study destinations"
        prompt = (
            f"Article: {a['title']}\n"
            f"Summary: {a['summary']}\n"
            f"Student origin regions: {src}\n\n"
            "You are a strategic advisor to international student recruitment teams at universities "
            "in the USA, UK, Australia, and New Zealand. Analyse how this news may be relevant to "
            "international student recruitment — consider whether it signals changes in student demand, "
            "visa conditions, source market sentiment, or competitive dynamics. "
            "Write exactly 2 sentences, 25–35 words each: "
            "sentence 1 explains what this news means for the international student recruitment landscape "
            "(be measured — acknowledge uncertainty where the link is indirect); "
            "sentence 2 suggests what admissions teams may want to monitor or consider, without overstating urgency. "
            "Do NOT start with 'This article'. Plain text only."
        )
        try:
            text = qwen_call(api_key, prompt, max_tokens=150, temperature=0.4)
            if text:
                a["insight"] = text
                a["insightSource"] = "qwen"
            time.sleep(0.4)
        except Exception as e:
            print(f"  ⚠ Insight error [{a['title'][:40]}]: {e}", file=sys.stderr)

    upgraded = sum(1 for a in articles if a.get("insightSource") == "qwen")
    print(f"  ✓ Qwen insights generated: {upgraded}/{len(articles)}")
    return articles


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\nFetching {len(FEEDS)} RSS feeds  [{now}]")

    api_key = os.environ.get("DASHSCOPE_API_KEY", "")

    # 1. Load previously shown URLs for freshness deduplication
    prev_urls = load_previous_urls()

    # 2. Fetch all feeds
    all_articles = []
    for feed in FEEDS:
        all_articles.extend(fetch_feed(feed))

    # 3. Deduplicate by URL
    seen, unique = set(), []
    for a in all_articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    print(f"\n  Total after dedup: {len(unique)} articles")

    # 4. AI scoring: select top 10, penalising repeated articles
    selected = qwen_select_top(unique, api_key, prev_urls, top_n=10)

    # 5. AI insights: generate professional insight for each selected article
    selected = qwen_generate_insights(selected, api_key)

    # 5. Final sort: by relevance score (desc), then impact, then date
    rank = {"High": 0, "Medium": 1, "Low": 2}
    selected.sort(key=lambda a: (
        -a.get("relevanceScore", 5),
        rank.get(a["impact"], 2),
        a["pubDate"]
    ))

    # 6. Assign sequential IDs
    for i, a in enumerate(selected, 1):
        a["id"] = i

    output = {
        "updated":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count":        len(selected),
        "totalFetched": len(unique),
        "articles":     selected,
    }

    os.makedirs("public", exist_ok=True)
    with open("public/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    by_imp     = {k: sum(1 for a in selected if a["impact"] == k) for k in ["High", "Medium", "Low"]}
    translated = sum(1 for a in selected if a.get("translated"))
    ai_insights = sum(1 for a in selected if a.get("insightSource") == "qwen")
    print(f"\n✓ {len(selected)} articles saved → public/news.json")
    print(f"  (selected from {len(unique)} total fetched)")
    print(f"  High: {by_imp['High']}  Medium: {by_imp['Medium']}  Low: {by_imp['Low']}")
    print(f"  AI insights: {ai_insights}  |  Translated: {translated}")

if __name__ == "__main__":
    main()
