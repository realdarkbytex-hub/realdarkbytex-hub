#!/usr/bin/env python3
"""Render Naitik's GitHub profile cards (Nixplayzz dark-purple theme).
Reads contributions.json, writes cards/*.svg + preview.html.
Real data only - no invented numbers.
"""
import json, math, re, urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent

def fetch_contributions(username="realdarkbytex-hub"):
    """Fetch the public contribution calendar and parse exact daily counts.
    Returns dict with days/monthly/total/streaks. Falls back to existing
    contributions.json when the fetch fails."""
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("fetch failed, using cached contributions.json:", e)
        return json.loads((HERE / "contributions.json").read_text())
    td = dict(re.findall(r'<td[^>]*id="(contribution-day-component-[\d-]+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html))
    td2 = dict(re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[\d-]+)"', html))
    id2date = dict(td)
    for d, k in td2.items():
        id2date[k] = d
    tips = re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', html)
    counts = {}
    for tid, text in tips:
        text = text.strip()
        if text.startswith("No contributions"):
            c = 0
        else:
            m = re.match(r"(\d+) contributions?", text)
            c = int(m.group(1)) if m else None
        if tid in id2date and c is not None:
            counts[id2date[tid]] = c
    data = [{"date": d, "count": c} for d, c in sorted(counts.items())]
    monthly = defaultdict(int)
    for x in data:
        monthly[x["date"][:7]] += x["count"]
    best = cur = 0
    for x in data:
        cur = cur + 1 if x["count"] > 0 else 0
        best = max(best, cur)
    cur = 0
    for x in reversed(data):
        if x["count"] > 0:
            cur += 1
        else:
            break
    out = {"days": data, "monthly": dict(sorted(monthly.items())),
           "total": sum(x["count"] for x in data),
           "current_streak": cur, "best_streak": best}
    (HERE / "contributions.json").write_text(json.dumps(out, indent=1))
    return out

DATA = fetch_contributions()
DAYS = DATA["days"]            # [{date, count}]
MONTHLY = DATA["monthly"]      # {"YYYY-MM": n}
TOTAL = DATA["total"]
CUR_STREAK = DATA["current_streak"]
BEST_STREAK = DATA["best_streak"]
ACTIVE_DAYS = sum(1 for d in DAYS if d["count"] > 0)
BUSIEST = max(DAYS, key=lambda d: d["count"]) if DAYS else {"date": "", "count": 0}
import os as _os
STATIC = _os.environ.get("STATIC") == "1"   # STATIC=1 renders the final frame (no animation) for screenshots

# ---- Nixplayzz palette (his own, from HireHunt) ----
BG      = "#0E0B1D"
CARD    = "#17112E"
CARD2   = "#1E1538"
BORDER  = "#2A1E4D"
PRIMARY = "#5A3B8C"
ACCENT  = "#8B7CC7"
TEXT    = "#EDE9FE"
MUTED   = "#A99FC7"
RED     = "#E5484D"   # YouTube
TEAL    = "#2DD4BF"   # automate
SANS    = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
MONO    = "ui-monospace, 'SF Mono', 'Cascadia Code', Consolas, monospace"

OUT = HERE / "cards"
OUT.mkdir(exist_ok=True)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------- shared CSS ----------
BASE_CSS = """
  * { font-family: __SANS__; }
  .fade { opacity: 0; animation: fadeUp .7s ease forwards; }
  @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .shine { animation: shine 4.5s ease-in-out infinite; }
  @keyframes shine { 0%,100% { opacity: .0; } 50% { opacity: .55; } }
  .blink { animation: blink 1.1s steps(1) infinite; }
  @keyframes blink { 0%,55% { opacity: 1; } 56%,100% { opacity: 0; } }
  .grow { transform-origin: bottom; transform-box: fill-box; animation: grow .8s cubic-bezier(.2,.9,.3,1.2) both; }
  @keyframes grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
  .pop { animation: pop .5s cubic-bezier(.2,.9,.3,1.4) both; }
  @keyframes pop { from { opacity: 0; transform: scale(.6); } to { opacity: 1; transform: scale(1); } }
  @media (prefers-reduced-motion: reduce) {
    .fade, .shine, .blink, .grow, .pop { animation: none !important; opacity: 1 !important; transform: none !important; }
  }
""".replace("__SANS__", SANS)

def svg_open(w, h, css_extra=""):
    static_css = ""
    if STATIC:
        static_css = (" .fade, .shine, .blink, .grow, .pop { animation: none !important; "
                      "opacity: 1 !important; transform: none !important; }")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">'
            f'<style>{BASE_CSS}{static_css}{css_extra}</style>')

# ---------- HERO ----------
def hero():
    w, h = 800, 196
    s = [svg_open(w, h)]
    s.append(f'<rect width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>')
    # top accent line
    s.append(f'<rect x="0" y="0" width="{w}" height="4" rx="2" fill="{PRIMARY}"/>')
    # left purple glow block
    s.append(f'<rect x="28" y="34" width="6" height="128" rx="3" fill="{PRIMARY}"/>')
    # name
    s.append(f'<text x="52" y="72" font-size="42" font-weight="800" fill="{TEXT}" class="fade" style="animation-delay:.05s">Naitik Kashyap</text>')
    # nixplayzz tag
    s.append(f'<text x="52" y="100" font-size="15" font-weight="700" fill="{ACCENT}" font-family="{MONO}" class="fade" style="animation-delay:.25s">nixplayzz</text>')
    s.append(f'<text x="140" y="100" font-size="15" fill="{MUTED}" font-family="{MONO}" class="fade" style="animation-delay:.3s">· BCA · Invertis University, Bareilly</text>')
    # tagline
    s.append(f'<text x="52" y="132" font-size="17" fill="{TEXT}" class="fade" style="animation-delay:.5s">Building AI tools in public — agents, bots &amp; YouTube automation.</text>')
    # cursor + meta
    s.append(f'<text x="52" y="164" font-size="14" fill="{MUTED}" font-family="{MONO}" class="fade" style="animation-delay:.7s">$ whoami → ai-automation · delhi/noida<tspan class="blink" fill="{ACCENT}">▊</tspan></text>')
    # shine sweep across name
    s.append(f'<rect x="40" y="30" width="90" height="50" fill="{ACCENT}" opacity="0" class="shine" style="animation-delay:1.2s" transform="skewX(-18)"/>')
    s.append('</svg>')
    return "".join(s)

# ---------- TILE ----------
def tile(number, unit, label, sub, color, delay, link_label):
    w, h = 258, 148
    s = [svg_open(w, h)]
    s.append(f'<rect width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>')
    s.append(f'<rect x="0" y="0" width="{w}" height="4" rx="2" fill="{color}"/>')
    # number (count-up feel via pop)
    s.append(f'<text x="20" y="62" font-size="44" font-weight="800" fill="{TEXT}" class="pop" style="animation-delay:{delay}s">{esc(number)}<tspan font-size="20" fill="{MUTED}" font-weight="600"> {esc(unit)}</tspan></text>')
    s.append(f'<text x="20" y="92" font-size="15" font-weight="700" fill="{color}" class="fade" style="animation-delay:{delay+0.25}s">{esc(label)}</text>')
    s.append(f'<text x="20" y="114" font-size="12.5" fill="{MUTED}" class="fade" style="animation-delay:{delay+0.4}s">{esc(sub)}</text>')
    s.append(f'<text x="20" y="136" font-size="11.5" fill="{MUTED}" font-family="{MONO}" class="fade" style="animation-delay:{delay+0.55}s">{esc(link_label)} ↗</text>')
    # corner ring pulse (SMIL)
    s.append(f'<circle cx="{w-26}" cy="26" r="7" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.7">'
            f'<animate attributeName="r" values="5;11" dur="2.2s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.7;0" dur="2.2s" repeatCount="indefinite"/></circle>')
    s.append(f'<circle cx="{w-26}" cy="26" r="4" fill="{color}"/>')
    s.append('</svg>')
    return "".join(s)

# ---------- MONTHLY ----------
def monthly():
    # last 12 months ending Nov 2026
    months = ["Dec 25","Jan 26","Feb 26","Mar 26","Apr 26","May 26","Jun 26","Jul 26","Aug 26","Sep 26","Oct 26","Nov 26"]
    keys   = ["2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10","2026-11"]
    vals   = [MONTHLY.get(k, 0) for k in keys]
    best_i = max(range(len(vals)), key=lambda i: vals[i])
    best_v = vals[best_i]
    w, h = 800, 236
    base_y, top_y = 168, 46
    max_v = max(best_v, 1)
    bw, gap = 44, 18
    x0 = 34
    s = [svg_open(w, h)]
    s.append(f'<rect width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>')
    s.append(f'<text x="24" y="32" font-size="15" font-weight="700" fill="{TEXT}" class="fade">Contributions / month</text>')
    _bd = BUSIEST["date"]
    _bday = ""
    if _bd:
        from datetime import datetime as _dt
        _bday = _dt.strptime(_bd, "%Y-%m-%d").strftime("%b %-d")
    s.append(f'<text x="{w-24}" y="32" font-size="13" fill="{MUTED}" text-anchor="end" class="fade" style="animation-delay:.2s">total {TOTAL} · {ACTIVE_DAYS} active days · best streak {BEST_STREAK}d · busiest day {_bday} ({BUSIEST["count"]})</text>')
    for i, (m, v) in enumerate(zip(months, vals)):
        x = x0 + i * (bw + gap)
        bh = max(4, round((v / max_v) * (base_y - top_y))) if v > 0 else 4
        y = base_y - bh
        col = PRIMARY if i == best_i else (ACCENT if v > 0 else "#241A3E")
        d = 0.15 + i * 0.06
        s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="6" fill="{col}" class="grow" style="animation-delay:{d:.2f}s"/>')
        if i == best_i:
            s.append(f'<text x="{x+bw/2}" y="{y-10}" font-size="14" font-weight="800" fill="{TEXT}" text-anchor="middle" class="pop" style="animation-delay:{d+0.7:.2f}s">{v}</text>')
        elif v > 0:
            s.append(f'<text x="{x+bw/2}" y="{y-8}" font-size="11" font-weight="700" fill="{MUTED}" text-anchor="middle" class="fade" style="animation-delay:{d+0.6:.2f}s">{v}</text>')
        s.append(f'<text x="{x+bw/2}" y="{base_y+20}" font-size="11" fill="{MUTED}" text-anchor="middle" class="fade" style="animation-delay:{d+0.5:.2f}s">{m}</text>')
    s.append(f'<line x1="24" y1="{base_y}" x2="{w-24}" y2="{base_y}" stroke="{BORDER}" stroke-width="1.5"/>')
    s.append('</svg>')
    return "".join(s)

# ---------- REPO CARD ----------
def repo(name, desc, lang, lang_col, note, link):
    w, h = 392, 132
    s = [svg_open(w, h)]
    s.append(f'<rect width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>')
    s.append(f'<circle cx="22" cy="26" r="5" fill="{lang_col}"/>')
    s.append(f'<text x="34" y="31" font-size="15" font-weight="800" fill="{TEXT}" class="fade">{esc(name)}</text>')
    s.append(f'<text x="{w-18}" y="31" font-size="12" fill="{ACCENT}" text-anchor="end" class="fade" style="animation-delay:.2s">{esc(link)} ↗</text>')
    # wrap desc to two lines
    words, lines, cur = desc.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 <= 46: cur = (cur + " " + wd).strip()
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    for j, ln in enumerate(lines[:2]):
        s.append(f'<text x="20" y="{62 + j*20}" font-size="13.5" fill="{MUTED}" class="fade" style="animation-delay:{0.3 + j*0.15:.2f}s">{esc(ln)}</text>')
    s.append(f'<text x="20" y="116" font-size="12.5" fill="{MUTED}" font-family="{MONO}" class="fade" style="animation-delay:.6s">{esc(lang)} · {esc(note)}</text>')
    s.append('</svg>')
    return "".join(s)

# ---------- CONTRIBUTION GRAPH ----------
LEVEL_COLS = ["#1A1430", "#3B2A6B", "#5A3B8C", "#7A5CC8", "#8B7CC7"]
def level(count):
    if count == 0: return 0
    if count <= 1: return 1
    if count <= 3: return 2
    if count <= 6: return 3
    return 4

def graph():
    # build date->count
    cmap = {d["date"]: d["count"] for d in DAYS}
    start = date(2025, 11, 23)
    end = date(2026, 11, 28)
    # first Sunday on/before start
    first = start - timedelta(days=(start.weekday() + 1) % 7)
    weeks = []
    d = first
    while d <= end:
        col = []
        for _ in range(7):
            col.append((d, cmap.get(d.isoformat(), 0) if start <= d <= end else None))
            d += timedelta(days=1)
        weeks.append(col)
    cw, ch, gap = 13, 13, 4
    x0, y0 = 34, 34
    w = x0 + len(weeks) * (cw + gap) + 10
    h = y0 + 7 * (ch + gap) + 34
    s = [svg_open(w, h)]
    s.append(f'<rect width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>')
    s.append(f'<text x="24" y="24" font-size="14" font-weight="700" fill="{TEXT}" class="fade">{TOTAL} contributions in the last year</text>')
    for wi, col in enumerate(weeks):
        for di, (dt, c) in enumerate(col):
            if c is None: continue
            x = x0 + wi * (cw + gap)
            y = y0 + di * (ch + gap)
            colr = LEVEL_COLS[level(c)]
            delay = 0.1 + wi * 0.03
            s.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="3.5" fill="{colr}" class="pop" style="animation-delay:{delay:.2f}s">'
                     f'<title>{dt} — {c} contribution{"s" if c != 1 else ""}</title></rect>')
    # month labels (first day of each month column)
    seen = set()
    for wi, col in enumerate(weeks):
        m = col[0][0].strftime("%b")
        key = (col[0][0].year, col[0][0].month)
        if key not in seen and col[0][0].day <= 7:
            seen.add(key)
            x = x0 + wi * (cw + gap)
            s.append(f'<text x="{x}" y="{h-10}" font-size="10.5" fill="{MUTED}">{m}</text>')
    s.append(f'<text x="{w-24}" y="24" font-size="12" fill="{MUTED}" text-anchor="end">Less</text>')
    for i, c in enumerate(LEVEL_COLS):
        x = w - 118 + i * 18
        s.append(f'<rect x="{x}" y="14" width="12" height="12" rx="3" fill="{c}"/>')
    s.append(f'<text x="{w-24}" y="24" font-size="12" fill="{MUTED}" text-anchor="end" dx="0"></text>')
    s.append('</svg>')
    return "".join(s)

def main():
    hero_svg = hero()
    tile_build = tile("2", "", "BUILD", "AI agents & bots shipped", PRIMARY, 0.15, "bot · hermes")
    tile_create = tile("3", "", "CREATE", "YouTube channels", RED, 0.35, "noya owns · vice city · stickman")
    tile_auto = tile("2", "/day", "AUTOMATE", "Shorts on autopilot", TEAL, 0.55, "noya owns · 8 + 10 PM IST")
    monthly_svg = monthly()
    repo_bot = repo("telegram-video-downloader-bot",
                    "Paste a link, get the video back. YouTube, Instagram, Facebook + 1,700 sites.",
                    "Python", "#3572A5", "runs 24/7 · try it", "@videoo_waleagyebot")
    repo_her = repo("hermes-vps-setup",
                    "Run Hermes Agent 24/7 on a free Oracle VPS. Gemini + NVIDIA fallback.",
                    "Shell", "#89E051", "₹0/month · telegram control", "hermes-vps-setup")
    graph_svg = graph()

    for name, svg in [("hero.svg", hero_svg), ("tile-build.svg", tile_build),
                      ("tile-create.svg", tile_create), ("tile-automate.svg", tile_auto),
                      ("monthly.svg", monthly_svg), ("repo-bot.svg", repo_bot),
                      ("repo-hermes.svg", repo_her), ("graph.svg", graph_svg)]:
        (OUT / name).write_text(svg)
        print("wrote", OUT / name, len(svg), "bytes")

    # ---- preview page (GitHub-dark frame, cards stacked as in README) ----
    def img(svg, w):
        import base64
        b64 = base64.b64encode(svg.encode()).decode()
        return f'<img src="data:image/svg+xml;base64,{b64}" style="width:{w}px;max-width:100%;height:auto;display:block;border-radius:14px;" alt="card"/>'

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Naitik Kashyap — GitHub profile preview</title>
<style>
  body {{ margin:0; background:#0d1117; color:#e6edf3; font-family:system-ui,-apple-system,'Segoe UI',sans-serif; }}
  .wrap {{ max-width:860px; margin:0 auto; padding:28px 16px 48px; }}
  .top {{ display:flex; gap:16px; align-items:center; margin-bottom:22px; }}
  .av {{ width:64px; height:64px; border-radius:50%; background:#5A3B8C; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:24px; color:#EDE9FE; flex:none; }}
  .top h1 {{ margin:0; font-size:24px; }} .top p {{ margin:4px 0 0; color:#8b949e; font-size:14px; }}
  .card {{ margin-bottom:18px; }}
  .row {{ display:flex; gap:14px; }} .row>* {{ flex:1; min-width:0; }}
  .note {{ color:#8b949e; font-size:13px; line-height:1.6; border:1px solid #30363d; border-radius:10px; padding:12px 14px; margin-top:8px; }}
  .note b {{ color:#e6edf3; }}
  @media (max-width:640px) {{ .row {{ flex-direction:column; }} }}
</style></head>
<body><div class="wrap">
  <div class="top"><div class="av">NK</div><div>
    <h1>Naitik Kashyap</h1>
    <p>realdarkbytex-hub · BCA · Invertis University, Bareilly · nixplayzz.tech</p>
  </div></div>
  <div class="card">{img(hero_svg, 828)}</div>
  <div class="row card">
    <div>{img(tile_build, 258)}</div>
    <div>{img(tile_create, 258)}</div>
    <div>{img(tile_auto, 258)}</div>
  </div>
  <div class="card">{img(monthly_svg, 828)}</div>
  <div class="row card">
    <div>{img(repo_bot, 392)}</div>
    <div>{img(repo_her, 392)}</div>
  </div>
  <div class="card">{img(graph_svg, 828)}</div>
  <div class="note"><b>Preview — ye waisa dikhega jaisa GitHub profile pe lagega.</b><br>
  Dark-purple Nixplayzz theme (tumhara apna, Avi wala paper/ink nahi). Numbers real hain — 24 contributions, Nov best month (11), busiest day Nov 25 (7). Cards roz subah GitHub Action se refresh honge. Pasand aaye to batao, main isi ko tumhare profile repo me daal dunga.</div>
</div></body></html>"""
    (HERE / "preview.html").write_text(html)
    print("wrote", HERE / "preview.html", len(html), "bytes")

if __name__ == "__main__":
    main()
