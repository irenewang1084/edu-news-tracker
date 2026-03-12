import { useState, useEffect } from "react";

// ── MEDIA SOURCES for RSS panel ──────────────────────────────────────────────
const MEDIA_SOURCES = {
  "🌐 International Specialist": [
    { name: "ICEF Monitor",          url: "https://monitor.icef.com/feed/",              color: "#1a3a5c" },
    { name: "The PIE News",          url: "https://thepienews.com/feed/",                color: "#7b341e" },
    { name: "Inside Higher Ed",      url: "https://www.insidehighered.com/rss.xml",      color: "#285e61" },
    { name: "HEPI",                  url: "https://www.hepi.ac.uk/category/blog/feed/",  color: "#4a235a" },
    { name: "Higher Ed Dive",        url: "https://www.highereddive.com/feeds/news/",    color: "#1e5631" },
    { name: "WENR (WES)",            url: "https://wenr.wes.org/feed",                                             color: "#0e4d8c" },
  ],
  "🇨🇳 China": [
    { name: "Sixth Tone",          url: "https://www.sixthtone.com/rss",                                             color: "#922b21" },
    { name: "SCMP (Education)",    url: "https://www.scmp.com/rss/318207/feed",                                      color: "#7b241c" },
    { name: "China Daily",         url: "https://www.chinadaily.com.cn/rss/china_rss.xml",                          color: "#c0392b" },
  ],
  "🇮🇳 India": [
    { name: "Times of India",      url: "https://timesofindia.indiatimes.com/rssfeeds/913168846.cms",                color: "#d4820a" },
    { name: "The Hindu (Edu)",     url: "https://www.thehindu.com/education/?service=rss",                          color: "#145a32" },
  ],
  "🌏 Southeast Asia": [
    { name: "VnExpress (EN)",      url: "https://e.vnexpress.net/rss/news.rss",                                     color: "#d35400" },
    { name: "VnExpress (Giáo dục)",url: "https://vnexpress.net/rss/giao-duc.rss",                                   color: "#b94500" },
  ],
  "🌐 Global": [
    { name: "Times Higher Ed",     url: "https://www.timeshighereducation.com/news/rss.xml",                      color: "#c0820a" },
  ],
  "🌎 Latin America": [
    { name: "El País (English)",   url: "https://feeds.elpais.com/mrss-s/pages/ep/site/english.elpais.com/portada", color: "#1a5276" },
    { name: "Folha de S.Paulo",    url: "https://feeds.folha.uol.com.br/educacao/rss091.xml",                      color: "#154360" },
  ],
};

const SRC_TAG = {
  China: "#c0392b", "Southeast Asia": "#d35400", India: "#c0820a",
  "South Asia": "#7d3c98", "West Africa": "#1e8449", "Latin America": "#1a5276",
};
const DST_TAG = {
  USA: "#1a3a5c", UK: "#1e5631", Canada: "#7b341e",
  Australia: "#0e6655", "New Zealand": "#4a235a",
};
const IMP = {
  High:   { bar: "#c0392b", bg: "#fdf2f2", fg: "#c0392b", icon: "⚡" },
  Medium: { bar: "#c9a84c", bg: "#fefce8", fg: "#9a6f00", icon: "●" },
  Low:    { bar: "#1e8449", bg: "#f0fdf4", fg: "#1e8449", icon: "○" },
};
const SRC_OPTS  = ["All","China","Southeast Asia","India","South Asia","West Africa","Latin America"];
const DEST_OPTS = ["All","USA","UK","Canada","Australia","New Zealand"];

function fmtDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}
function fmtUpdated(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit", timeZoneName: "short"
  });
}

// ── COMPONENT ─────────────────────────────────────────────────────────────────
export default function App() {
  const [articles,    setArticles]    = useState([]);
  const [updated,     setUpdated]     = useState("");
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState("");
  const [fSrc,        setFSrc]        = useState("All");
  const [showSources, setShowSources] = useState(false);

  // Load news.json on mount
  useEffect(() => {
    fetch("/news.json")
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => {
        setArticles(data.articles || []);
        setUpdated(data.updated || "");
        setLoading(false);
      })
      .catch(e => {
        setError("Could not load news data: " + e.message);
        setLoading(false);
      });
  }, []);

  const shown = articles
    .filter(a => fSrc === "All" || (a.sources || []).includes(fSrc))
    .sort((a, b) => (a.relevanceScore || 0) > (b.relevanceScore || 0) ? -1 : 1);

  const dateRange = (() => {
    const dates = articles.map(a => a.pubDate).filter(Boolean).sort();
    if (!dates.length) return "";
    return `${fmtDate(dates[0])} – ${fmtDate(dates[dates.length - 1])}`;
  })();

  return (
    <div style={{ fontFamily: "'Libre Baskerville',Georgia,serif", minHeight: "100vh", background: "#F4F1EB" }}>
      <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet" />

      {/* HEADER */}
      <header style={{ background: "#0f0f23", color: "#f0ede6", padding: "24px 20px 20px", borderBottom: "3px solid #c9a84c" }}>
        <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 14 }}>
          <div>
            <div style={{ fontSize: 10, letterSpacing: 4, color: "#c9a84c", fontFamily: "'DM Sans',sans-serif", fontStyle: "italic", marginBottom: 5 }}>
              INTERNATIONAL EDUCATION INTELLIGENCE DAILY
            </div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, lineHeight: 1.25 }}>
              Global Study Abroad News Tracker
            </h1>
            <div style={{ marginTop: 6, fontSize: 13, color: "#8a90a8", fontFamily: "'DM Sans',sans-serif", lineHeight: 1.7, maxWidth: 540 }}>
              Daily briefing for university international admissions teams — AI-curated from 15+ sources across 6 student origin regions, updated every morning.
            </div>
          </div>
          {/* Top-right: article date range */}
          <div style={{ textAlign: "right", fontFamily: "'DM Sans',sans-serif" }}>
            {dateRange && (
              <div style={{ background: "#c9a84c22", border: "1px solid #c9a84c55", borderRadius: 5, padding: "8px 13px", marginBottom: 6 }}>
                <div style={{ fontSize: 9, color: "#c9a84c", letterSpacing: 1.5, marginBottom: 3 }}>ARTICLES DATED</div>
                <div style={{ fontSize: 13, color: "#f0ede6", fontWeight: 600 }}>{dateRange}</div>
              </div>
            )}
            {updated && (
              <div style={{ fontSize: 11, color: "#555a70" }}>
                🔄 Auto-updated: {fmtUpdated(updated)}
              </div>
            )}
          </div>
        </div>
      </header>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "18px 16px" }}>

        {/* LOADING */}
        {loading && (
          <div style={{ textAlign: "center", padding: "80px 0", color: "#999", fontFamily: "'DM Sans',sans-serif" }}>
            <div style={{ fontSize: 36, marginBottom: 12 }}>📡</div>
            <div>Loading latest articles…</div>
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div style={{ background: "#fdf2f2", border: "1px solid #fecaca", borderRadius: 8, padding: 16, color: "#c0392b", fontFamily: "'DM Sans',sans-serif", fontSize: 13 }}>
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            {/* STATS */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginBottom: 16 }}>
              {[
                { label: "Today's Briefing", val: shown.length,                                              color: "#0f0f23" },
                { label: "AI-Selected",       val: articles.length,                                          color: "#c9a84c" },
                { label: "Source Regions",    val: [...new Set(shown.flatMap(a => a.sources))].length || "—", color: "#7d3c98" },
                { label: "Sources Monitored", val: "15+",                                                    color: "#1e5631" },
              ].map(s => (
                <div key={s.label} style={{ background: "white", border: "1px solid #e5e0d6", borderRadius: 8, padding: "10px 12px", textAlign: "center" }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: s.color, fontFamily: "'DM Sans',sans-serif" }}>{s.val}</div>
                  <div style={{ fontSize: 11, color: "#999", fontFamily: "'DM Sans',sans-serif", marginTop: 1 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* FILTERS — source region only */}
            <div style={{ background: "white", borderRadius: 8, border: "1px solid #e5e0d6", padding: "12px 15px", marginBottom: 14 }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 7, alignItems: "center" }}>
                <span style={{ fontSize: 10, color: "#bbb", letterSpacing: 1.5, fontFamily: "'DM Sans',sans-serif" }}>FILTER BY ORIGIN</span>
                {SRC_OPTS.map(f => (
                  <button key={f} onClick={() => setFSrc(f)} style={{
                    padding: "3px 10px", borderRadius: 20, fontSize: 12, cursor: "pointer", fontFamily: "'DM Sans',sans-serif",
                    border: `1.5px solid ${fSrc === f ? (SRC_TAG[f] || "#0f0f23") : "#e0dbd2"}`,
                    background: fSrc === f ? (SRC_TAG[f] || "#0f0f23") : "transparent",
                    color: fSrc === f ? "white" : "#666", transition: "all 0.15s",
                  }}>{f}</button>
                ))}
              </div>
              {fSrc !== "All" && (
                <div style={{ marginTop: 7, fontSize: 11, color: "#aaa", fontFamily: "'DM Sans',sans-serif" }}>
                  Showing {shown.length} article{shown.length !== 1 ? "s" : ""} from {fSrc} ·{" "}
                  <span style={{ color: "#c9a84c", cursor: "pointer" }} onClick={() => setFSrc("All")}>Clear</span>
                </div>
              )}
            </div>

            {/* ARTICLES */}
            {shown.length === 0 ? (
              <div style={{ textAlign: "center", padding: 50, color: "#aaa", fontFamily: "'DM Sans',sans-serif" }}>
                No articles match current filters.{" "}
                <span style={{ color: "#c9a84c", cursor: "pointer" }} onClick={() => setFSrc("All")}>Clear filters</span>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {shown.map(item => {
                  const imp = IMP[item.impact] || IMP.Low;
                  return (
                    <article key={item.id || item.url} style={{
                      background: "white", borderRadius: 8, border: "1px solid #e5e0d6",
                      overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", transition: "box-shadow 0.2s",
                    }}
                      onMouseEnter={e => e.currentTarget.style.boxShadow = "0 4px 18px rgba(0,0,0,0.09)"}
                      onMouseLeave={e => e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)"}
                    >
                      <div style={{ height: 3, background: imp.bar }} />
                      <div style={{ padding: "16px 20px" }}>
                        {/* Meta */}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 9, alignItems: "center" }}>
                          <span style={{ padding: "2px 8px", background: imp.bg, color: imp.fg, borderRadius: 3, fontSize: 11, fontWeight: 700, fontFamily: "'DM Sans',sans-serif" }}>
                            {imp.icon} {item.impact}
                          </span>
                          {(item.sources || []).map(s => (
                            <span key={s} style={{ padding: "2px 8px", background: SRC_TAG[s] || "#555", color: "white", borderRadius: 3, fontSize: 11, fontFamily: "'DM Sans',sans-serif" }}>{s}</span>
                          ))}
                          {(item.dests || []).map(d => (
                            <span key={d} style={{ padding: "2px 7px", border: `1.5px solid ${DST_TAG[d] || "#888"}`, color: DST_TAG[d] || "#888", borderRadius: 3, fontSize: 11, fontFamily: "'DM Sans',sans-serif" }}>→ {d}</span>
                          ))}
                          <span style={{ marginLeft: "auto", fontSize: 11, fontFamily: "'DM Sans',sans-serif", color: "#aaa", whiteSpace: "nowrap" }}>
                            <span style={{ color: item.color || "#555", fontWeight: 600 }}>{item.source}</span>
                            {" · "}
                            <span style={{ background: "#f4f1eb", padding: "1px 6px", borderRadius: 3 }}>{fmtDate(item.pubDate)}</span>
                          </span>
                        </div>
                        {/* Title */}
                        <h2 style={{ margin: "0 0 9px", fontSize: 16, fontWeight: 700, lineHeight: 1.5, color: "#0f0f23" }}>
                          {item.title}
                        </h2>
                        {/* Summary */}
                        {item.summary && (
                          <p style={{ margin: "0 0 12px", fontSize: 13.5, lineHeight: 1.85, color: "#4a5568", fontFamily: "'DM Sans',sans-serif" }}>
                            {item.summary}{item.summary.length >= 399 ? "…" : ""}
                          </p>
                        )}
                        {/* Professional Insight */}
                        {item.insight && (
                          <div style={{ background: "#faf7f0", borderLeft: "3px solid #c9a84c", padding: "9px 14px", borderRadius: "0 4px 4px 0", marginBottom: 13 }}>
                            <div style={{ fontSize: 9, letterSpacing: 2, color: "#c9a84c", fontFamily: "'DM Sans',sans-serif", fontWeight: 700, marginBottom: 3 }}>PROFESSIONAL INSIGHT</div>
                            <p style={{ margin: 0, fontSize: 13, color: "#2d3748", lineHeight: 1.75, fontStyle: "italic", fontFamily: "'DM Sans',sans-serif" }}>{item.insight}</p>
                          </div>
                        )}
                        {/* Footer */}
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <span style={{ fontSize: 11, color: "#ccc", fontFamily: "'DM Sans',sans-serif" }}>{item.source}</span>
                            {item.translated && (
                              <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, background: "#f0f4ff", color: "#3b5bdb", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, letterSpacing: 0.5 }}>
                                🌐 AUTO-TRANSLATED
                              </span>
                            )}
                          </div>
                          <a href={item.url} target="_blank" rel="noopener noreferrer" style={{
                            padding: "5px 14px", background: "#0f0f23", color: "#c9a84c",
                            borderRadius: 4, fontSize: 12, textDecoration: "none",
                            fontFamily: "'DM Sans',sans-serif", fontWeight: 600, whiteSpace: "nowrap",
                          }}>Read full article →</a>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}

            {/* RSS SOURCE PANEL */}
            <div style={{ marginTop: 28, background: "white", borderRadius: 8, border: "1px solid #e5e0d6", overflow: "hidden" }}>
              <button onClick={() => setShowSources(s => !s)} style={{
                width: "100%", padding: "13px 18px", background: "none", border: "none", cursor: "pointer",
                display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: "'DM Sans',sans-serif",
              }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: "#0f0f23" }}>
                  📡 RSS Feed Directory — add to Feedly / Inoreader for daily email digest
                </span>
                <span style={{ fontSize: 13, color: "#c9a84c" }}>{showSources ? "▲ Hide" : "▼ Show all feeds"}</span>
              </button>
              {showSources && (
                <div style={{ padding: "0 18px 18px", borderTop: "1px solid #f0ede6" }}>
                  {Object.entries(MEDIA_SOURCES).map(([group, feeds]) => (
                    <div key={group} style={{ marginTop: 16 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: "#666", fontFamily: "'DM Sans',sans-serif", letterSpacing: 1, marginBottom: 8 }}>{group}</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {feeds.map(f => (
                          <a key={f.name} href={f.url} target="_blank" rel="noopener noreferrer" style={{
                            fontSize: 12, padding: "4px 10px", borderRadius: 4,
                            background: f.color + "15", border: `1px solid ${f.color}55`,
                            color: f.color, fontFamily: "'DM Sans',sans-serif", textDecoration: "none", fontWeight: 500,
                          }}>{f.name} ↗</a>
                        ))}
                      </div>
                    </div>
                  ))}
                  <div style={{ marginTop: 16, padding: "12px 14px", background: "#f9f7f2", borderRadius: 6, fontSize: 12, color: "#666", fontFamily: "'DM Sans',sans-serif", lineHeight: 1.7 }}>
                    <strong>Get a daily email digest (no code):</strong> Paste any RSS link into{" "}
                    <a href="https://feedly.com" target="_blank" rel="noopener noreferrer" style={{ color: "#c9a84c" }}>Feedly</a> or{" "}
                    <a href="https://www.inoreader.com" target="_blank" rel="noopener noreferrer" style={{ color: "#c9a84c" }}>Inoreader</a>
                    {" "}→ enable "Daily Digest Email". Free tier, ~10 min setup.
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* FOOTER */}
        <footer style={{ marginTop: 20, paddingTop: 14, borderTop: "1px solid #e5e0d6", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
          <div style={{ fontSize: 11, color: "#ccc", fontFamily: "'DM Sans',sans-serif" }}>
            Caixin · Sixth Tone · ICEF Monitor · The PIE News · Times Higher Ed · Guardian Nigeria · and more
          </div>
          <div style={{ fontSize: 11, color: "#ccc", fontFamily: "'DM Sans',sans-serif" }}>For reference only · verify with official sources</div>
        </footer>
      </div>
    </div>
  );
}
