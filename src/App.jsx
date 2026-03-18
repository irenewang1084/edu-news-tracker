import { useState, useEffect } from "react";

const SRC_TAG = {
  China: "#c0392b", "Southeast Asia": "#d35400", India: "#c0820a",
  "South Asia": "#7d3c98", "West Africa": "#1e8449", "Latin America": "#1a5276",
  "MENA": "#0e6655",
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
const SRC_OPTS  = ["All","China","Southeast Asia","India","South Asia","West Africa","Latin America","MENA"];
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
    .sort((a, b) => (a.pubDate > b.pubDate ? -1 : 1));

  const dateRange = (() => {
    const dates = articles.map(a => a.pubDate).filter(Boolean).sort();
    if (!dates.length) return "";
    return `${fmtDate(dates[0])} – ${fmtDate(dates[dates.length - 1])}`;
  })();

  return (
    <div style={{ fontFamily: "'Libre Baskerville',Georgia,serif", minHeight: "100vh", background: "#fff" }}>
      <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@1,8..60,400&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet" />

      {/* MASTHEAD */}
      <header style={{ background: "#fff", padding: "20px 20px 0", borderBottom: "3px double #0f0f23" }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <h1 style={{ margin: "0 0 8px", fontSize: 52, fontWeight: 700, lineHeight: 1.05, color: "#0f0f23", letterSpacing: -1, fontFamily: "'Libre Baskerville',Georgia,serif" }}>
            Global Study Abroad Intelligence
          </h1>
          <div style={{ borderTop: "1px solid #0f0f23", borderBottom: "1px solid #0f0f23", padding: "5px 0", margin: "0 0 0", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 6 }}>
            <span style={{ fontSize: 12, fontFamily: "'DM Sans',sans-serif", color: "#444" }}>International Education Intelligence Daily</span>
            <span style={{ fontSize: 12, fontFamily: "'DM Sans',sans-serif", color: "#444" }}>AI-curated from 15+ sources · 6 student origin regions</span>
            <span style={{ fontSize: 12, fontFamily: "'DM Sans',sans-serif", color: "#444" }}>
              Auto-updated daily
              {updated && ` · ${new Date(updated).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}`}
            </span>
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
            <div style={{ display: "flex", borderTop: "2px solid #0f0f23", borderBottom: "1px solid #d6d1c8", marginBottom: 16 }}>
              {[
                { label: "SOURCE REGIONS",    val: [...new Set(shown.flatMap(a => a.sources))].length || "—", color: "#0f0f23" },
                { label: "SOURCES MONITORED", val: "15+", color: "#0f0f23" },
              ].map((s, i) => (
                <div key={s.label} style={{ flex: 1, padding: "12px 0", textAlign: "center", borderRight: i === 0 ? "1px solid #d6d1c8" : "none" }}>
                  <div style={{ fontSize: 26, fontWeight: 700, color: s.color, fontFamily: "'Libre Baskerville',Georgia,serif" }}>{s.val}</div>
                  <div style={{ fontSize: 10, color: "#888", fontFamily: "'DM Sans',sans-serif", letterSpacing: 2, marginTop: 3 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* FILTERS */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center", marginBottom: 16, paddingBottom: 14, borderBottom: "1px solid #d6d1c8" }}>
              <span style={{ fontSize: 10, color: "#888", letterSpacing: 2, fontFamily: "'DM Sans',sans-serif", marginRight: 4 }}>FILTER BY ORIGIN</span>
              {SRC_OPTS.map(f => (
                <button key={f} onClick={() => setFSrc(f)} style={{
                  padding: "4px 14px", fontSize: 12, cursor: "pointer", fontFamily: "'DM Sans',sans-serif",
                  border: `1px solid ${fSrc === f ? "#0f0f23" : "#c8c3ba"}`,
                  borderRadius: 20,
                  background: fSrc === f ? "#0f0f23" : "transparent",
                  color: fSrc === f ? "white" : "#555",
                }}>{f}</button>
              ))}
              {fSrc !== "All" && (
                <span style={{ fontSize: 11, color: "#c9a84c", cursor: "pointer", fontFamily: "'DM Sans',sans-serif", marginLeft: 4 }} onClick={() => setFSrc("All")}>✕ Clear</span>
              )}
            </div>

            {/* SECTION LABEL */}
            <div style={{ fontSize: 11, fontFamily: "'DM Sans',sans-serif", fontWeight: 600, letterSpacing: 3, color: "#555", marginBottom: 0 }}>TODAY'S BRIEFING</div>

            {/* ARTICLES */}
            {shown.length === 0 ? (
              <div style={{ textAlign: "center", padding: 50, color: "#aaa", fontFamily: "'DM Sans',sans-serif" }}>
                No articles match current filters.{" "}
                <span style={{ color: "#c9a84c", cursor: "pointer" }} onClick={() => setFSrc("All")}>Clear filters</span>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column" }}>
                {shown.map((item, idx) => (
                  <article key={item.id || item.url} style={{
                    borderTop: idx === 0 ? "2px solid #0f0f23" : "1px solid #d6d1c8",
                    padding: "22px 0 24px",
                  }}>
                    {/* Source · Date */}
                    <div style={{ fontSize: 11, fontFamily: "'DM Sans',sans-serif", color: "#888", letterSpacing: 0.5, marginBottom: 8 }}>
                      <span style={{ fontWeight: 600, color: item.color || "#555" }}>{item.source}</span>
                      {" · "}{fmtDate(item.pubDate)}
                    </div>

                    {/* Tags */}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 12 }}>
                      {(item.sources || []).map(s => (
                        <span key={s} style={{ padding: "1px 8px", border: "1px solid #bbb", color: "#555", borderRadius: 2, fontSize: 11, fontFamily: "'DM Sans',sans-serif" }}>{s}</span>
                      ))}
                      {(item.dests || []).map(d => (
                        <span key={d} style={{ padding: "1px 8px", border: "1px solid #bbb", color: "#555", borderRadius: 2, fontSize: 11, fontFamily: "'DM Sans',sans-serif" }}>→ {d}</span>
                      ))}
                    </div>

                    {/* Headline */}
                    <h2 style={{ margin: "0 0 12px", fontSize: 20, fontWeight: 700, lineHeight: 1.35, color: "#0f0f23", fontFamily: "'Libre Baskerville',Georgia,serif" }}>
                      {item.title}
                    </h2>

                    {/* Summary */}
                    {item.summary && (
                      <p style={{ margin: "0 0 14px", fontSize: 14.5, lineHeight: 1.85, color: "#333", fontFamily: "'Libre Baskerville',Georgia,serif" }}>
                        {item.summary}
                      </p>
                    )}

                    {/* Insight */}
                    {item.insight && (
                      <div style={{ background: "#f0efed", borderLeft: "3px solid #c9a84c", padding: "11px 14px", marginBottom: 14 }}>
                        <div style={{ fontSize: 9, letterSpacing: 2, color: "#c9a84c", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, marginBottom: 6 }}>RECRUITMENT INSIGHT</div>
                        <p style={{ margin: 0, fontSize: 13, color: "#2d2d2d", lineHeight: 1.75, fontStyle: "italic", fontFamily: "'Source Serif 4',Georgia,serif" }}>{item.insight}</p>
                      </div>
                    )}

                    {/* Footer */}
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 4 }}>
                      <div>
                        {item.translated && (
                          <span style={{ fontSize: 10, padding: "1px 6px", background: "#f0f4ff", color: "#3b5bdb", fontFamily: "'DM Sans',sans-serif", letterSpacing: 0.5, border: "1px solid #c7d2fe" }}>
                            🌐 AUTO-TRANSLATED
                          </span>
                        )}
                      </div>
                      <a href={item.url} target="_blank" rel="noopener noreferrer" style={{
                        fontSize: 13, color: "#0f0f23", fontFamily: "'Libre Baskerville',Georgia,serif",
                        textDecoration: "none", borderBottom: "1px solid #0f0f23", paddingBottom: 1,
                      }}>Read full article →</a>
                    </div>
                  </article>
                ))}
                <div style={{ borderTop: "2px solid #0f0f23" }} />
              </div>
            )}

            {/* RSS SOURCE PANEL */}
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
