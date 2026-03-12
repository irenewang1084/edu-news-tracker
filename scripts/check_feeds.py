#!/usr/bin/env python3
"""
check_feeds.py — 本地运行，验证每个 RSS feed 返回的真实文章 URL
运行方式：python3 check_feeds.py
无需安装额外依赖，使用 Python 标准库
"""

import json, urllib.request, urllib.parse, sys

FEEDS = [
    {"name": "The PIE News",         "url": "https://thepienews.com/feed/"},
    {"name": "ICEF Monitor",         "url": "https://monitor.icef.com/feed/"},
    {"name": "Times Higher Ed",      "url": "https://www.timeshighereducation.com/news/rss.xml"},
    {"name": "Inside Higher Ed",     "url": "https://www.insidehighered.com/rss.xml"},
    {"name": "Higher Ed Dive",       "url": "https://www.highereddive.com/feeds/news/"},
    {"name": "Caixin Global",        "url": "https://www.caixinglobal.com/rss/"},
    {"name": "Sixth Tone",           "url": "https://www.sixthtone.com/rss"},
    {"name": "SCMP Education",       "url": "https://www.scmp.com/rss/318207/feed"},
    {"name": "界面新闻 Jiemian",      "url": "https://www.jiemian.com/lists/250.rss"},
    {"name": "Times of India (Edu)", "url": "https://timesofindia.indiatimes.com/rssfeeds/913168846.cms"},
    {"name": "The Hindu (Edu)",      "url": "https://www.thehindu.com/education/?service=rss"},
    {"name": "VnExpress EN",         "url": "https://e.vnexpress.net/rss/news.rss"},
    {"name": "VnExpress Giáo dục",   "url": "https://vnexpress.net/rss/giao-duc.rss"},
    {"name": "Straits Times (Edu)",  "url": "https://www.straitstimes.com/singapore/education.rss"},
    {"name": "Guardian Nigeria",     "url": "https://guardian.ng/education/feed/"},
    {"name": "Punch Nigeria",        "url": "https://punchng.com/topics/education/feed/"},
    {"name": "Premium Times NG",     "url": "https://www.premiumtimesng.com/category/education/feed/"},
    {"name": "El País (English)",    "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/english.elpais.com/portada"},
    {"name": "Folha de S.Paulo",     "url": "https://feeds.folha.uol.com.br/educacao/rss091.xml"},
]

RSS2JSON = "https://api.rss2json.com/v1/api.json?count=2&rss_url={}"

def check(feed):
    url = RSS2JSON.format(urllib.parse.quote(feed["url"], safe=""))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return None, str(e)

    if data.get("status") != "ok":
        return None, data.get("message", data.get("status", "unknown error"))

    items = data.get("items", [])[:2]
    results = []
    for item in items:
        title = (item.get("title") or "")[:70]
        link  = item.get("link") or "(none)"
        guid  = item.get("guid") or "(none)"
        if isinstance(guid, dict):
            guid = guid.get("_value") or guid.get("#text") or str(guid)
        results.append({"title": title, "link": link, "guid": str(guid)[:100]})
    return results, None

RESET = "\033[0m"
GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW= "\033[93m"
BOLD  = "\033[1m"

print(f"\n{'─'*70}")
print(f"{BOLD}RSS Feed URL Inspector{RESET}  — checking {len(FEEDS)} feeds via rss2json")
print(f"{'─'*70}\n")

good, bad = [], []

for feed in FEEDS:
    print(f"{BOLD}{feed['name']}{RESET}")
    items, err = check(feed)
    if err:
        print(f"  {RED}✗ FAILED: {err}{RESET}")
        bad.append(feed["name"])
    else:
        for item in items:
            print(f"  Title : {item['title']}…")
            print(f"  link  : {item['link']}")
            print(f"  guid  : {item['guid']}")
            # Simple heuristic: article URL has path depth >= 2 and no obvious homepage patterns
            link = item["link"]
            path_depth = len([p for p in link.split("/")[3:] if p])
            looks_ok = (
                link.startswith("http") and
                path_depth >= 2 and
                not link.rstrip("/").count("/") <= 3
            )
            status = f"{GREEN}✓ article URL looks good{RESET}" if looks_ok else f"{YELLOW}⚠ may be homepage/section{RESET}"
            print(f"  → {status}")
        good.append(feed["name"])
    print()

print(f"{'─'*70}")
print(f"{BOLD}SUMMARY{RESET}")
print(f"  Fetched OK : {len(good)}  |  Failed : {len(bad)}")
if bad:
    print(f"\n  {RED}Failed feeds:{RESET}")
    for n in bad: print(f"    • {n}")
print(f"{'─'*70}\n")
print("→ 把上面的输出截图或复制给 Claude，即可精确决定哪些 feed 保留。\n")
