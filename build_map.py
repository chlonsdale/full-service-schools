#!/usr/bin/env python3
"""
build_map.py
Reads full_service_schools_australia.csv from the same directory
and writes index.html (the interactive map).

Usage:
    python build_map.py

Run this any time the CSV changes to regenerate the map.
The Cowork weekly task runs this automatically after updating the dataset.
"""

import csv
import json
import sys
from pathlib import Path
from datetime import date

HERE = Path(__file__).parent
CSV_PATH  = HERE / "full_service_schools_australia.csv"
HTML_PATH = HERE / "index.html"

def load_data():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("latitude") and r.get("longitude"):
                try:
                    rows.append({
                        "n":      r["site_name"],
                        "su":     r["suburb"],
                        "st":     r["state"],
                        "p":      r["program"],
                        "pl":     r["program_label"],
                        "pt":     r["program_type"],
                        "se":     r["setting_type"],
                        "ta":     r["target_age"],
                        "status": r["status"],
                        "src":    r.get("source_url", ""),
                        "site":   r.get("site_url", ""),
                        "dp":     r.get("dual_program", ""),
                        "lat":    float(r["latitude"]),
                        "lon":    float(r["longitude"]),
                    })
                except ValueError:
                    pass
    return rows

def build_html(rows):
    colors = {
        "Connected Communities":      "#C2410C",
        "SaCC":                       "#1D4ED8",
        "Community Hub":              "#0891B2",
        "Our Place":                  "#7C3AED",
        "SA Children's Centre":       "#BE185D",
        "CPC":                        "#15803D",
        "CFLC":                       "#B45309",
        "SPSP Community":             "#52525B",
        "QLD Child & Family Centre":  "#0369A1",
        "NT Child & Family Centre":   "#DC2626",
        "ACT Child & Family Centre":  "#4338CA",
        "FSS Pilot":                  "#65A30D",
        "FamilyLinQ":                 "#DB2777",
    }

    pt_labels = sorted(set(r["pt"] for r in rows))
    states    = sorted(set(r["st"] for r in rows))
    ta_labels = sorted(set(r["ta"] for r in rows))
    total     = len(rows)
    built     = date.today().isoformat()

    data_js   = json.dumps(rows)
    colors_js = json.dumps(colors)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Australian Full-Service School Infrastructure</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
  :root {{
    --bg:#F7F6F3; --panel:#FFFFFF; --border:#E2E0D8;
    --text:#1C1917; --muted:#78716C;
    --accent:#390752; --accent2:#DB2516;
    --shadow:0 1px 3px rgba(0,0,0,.08),0 4px 16px rgba(0,0,0,.06);
  }}
  html,body {{ height:100%; font-family:'DM Sans',sans-serif; background:var(--bg); color:var(--text); }}
  #layout {{ display:flex; height:100vh; }}
  #sidebar {{ width:300px; min-width:300px; background:var(--panel);
    border-right:1px solid var(--border); display:flex; flex-direction:column;
    overflow:hidden; box-shadow:var(--shadow); z-index:1000; }}
  #sidebar-header {{ padding:18px 20px 14px; border-bottom:1px solid var(--border); flex-shrink:0; }}
  #sidebar-header h1 {{ font-size:13px; font-weight:600; letter-spacing:.04em;
    text-transform:uppercase; color:var(--accent); margin-bottom:2px; }}
  #sidebar-header p {{ font-size:11px; color:var(--muted); line-height:1.4; }}
  #sidebar-header .meta {{ font-size:10px; color:var(--muted); margin-top:5px; }}
  #count-bar {{ padding:8px 20px; background:var(--accent); color:#fff;
    font-size:12px; font-weight:500; display:flex; align-items:center; gap:6px; flex-shrink:0; }}
  #count-bar span {{ font-weight:700; font-size:15px; }}
  #filters {{ flex:1; overflow-y:auto; padding:14px 16px; }}
  .filter-section {{ margin-bottom:18px; }}
  .filter-label {{ font-size:10px; font-weight:600; letter-spacing:.08em;
    text-transform:uppercase; color:var(--muted); margin-bottom:8px; display:block; }}
  .pill-group {{ display:flex; flex-wrap:wrap; gap:5px; }}
  .pill {{ padding:3px 9px; border-radius:20px; font-size:11px; cursor:pointer;
    border:1px solid var(--border); background:var(--bg); color:var(--text);
    transition:all .15s; user-select:none; font-weight:500; }}
  .pill.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .pill:hover:not(.active) {{ border-color:var(--accent); color:var(--accent); }}
  .pt-pill {{ padding:4px 10px; border-radius:4px; font-size:11px; cursor:pointer;
    border:1px solid var(--border); background:var(--bg); color:var(--text);
    transition:all .15s; font-weight:500; width:100%; text-align:left;
    margin-bottom:4px; display:block; }}
  .pt-pill.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .legend-item {{ display:flex; align-items:center; gap:8px; padding:4px 6px;
    border-radius:4px; cursor:pointer; font-size:11.5px; margin-bottom:2px;
    transition:background .12s; }}
  .legend-item:hover {{ background:var(--bg); }}
  .legend-item.dim {{ opacity:.35; }}
  .legend-dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; border:1px solid rgba(0,0,0,.12); }}
  .legend-name {{ flex:1; color:var(--text); }}
  .legend-count {{ font-family:'DM Mono',monospace; font-size:10px; color:var(--muted); min-width:22px; text-align:right; }}
  #reset-btn {{ margin:0 16px 14px; padding:8px; border-radius:6px;
    border:1px solid var(--border); background:var(--bg); color:var(--muted);
    font-size:11px; font-weight:600; cursor:pointer; letter-spacing:.04em;
    text-transform:uppercase; transition:all .15s; }}
  #reset-btn:hover {{ border-color:var(--accent2); color:var(--accent2); }}
  #map {{ flex:1; }}
  .leaflet-popup-content-wrapper {{ border-radius:8px;
    box-shadow:0 4px 20px rgba(0,0,0,.14); border:1px solid var(--border); padding:0; }}
  .leaflet-popup-content {{ margin:0; width:280px !important; }}
  .popup-inner {{ padding:14px 16px; }}
  .popup-tag {{ font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
    padding:2px 7px; border-radius:3px; color:#fff; display:inline-block; margin-bottom:8px; }}
  .popup-name {{ font-size:13px; font-weight:600; line-height:1.35; margin-bottom:8px; }}
  .popup-row {{ display:flex; gap:6px; align-items:baseline; margin-bottom:3px; }}
  .popup-key {{ font-size:10px; color:var(--muted); min-width:60px; flex-shrink:0; }}
  .popup-val {{ font-size:11px; color:var(--text); }}
  .popup-dp {{ font-size:10px; color:var(--muted); font-style:italic; margin-top:4px; }}
  .popup-links {{ margin-top:10px; display:flex; gap:10px; flex-wrap:wrap; }}
  .popup-link {{ font-size:11px; color:var(--accent); font-weight:500; text-decoration:none; }}
  .popup-link:hover {{ text-decoration:underline; }}
  .popup-link.site {{ color:var(--accent2); }}
  .status-badge {{ display:inline-block; font-size:9.5px; font-weight:600;
    padding:2px 7px; border-radius:3px; margin-top:6px; }}
  .status-active    {{ background:#DCFCE7; color:#15803D; }}
  .status-announced {{ background:#FEF9C3; color:#A16207; }}
  .status-completed {{ background:#F3F4F6; color:#6B7280; }}
  .status-pilot     {{ background:#EDE9FE; color:#7C3AED; }}
  .status-backbone  {{ background:#F1F5F9; color:#475569; }}
  .status-dedup     {{ background:#FEF2F2; color:#B91C1C; }}
  .marker-cluster-small   {{ background-color:rgba(57,7,82,.25); }}
  .marker-cluster-small   div {{ background-color:rgba(57,7,82,.75); }}
  .marker-cluster-medium  {{ background-color:rgba(219,37,22,.25); }}
  .marker-cluster-medium  div {{ background-color:rgba(219,37,22,.75); }}
  .marker-cluster-large   {{ background-color:rgba(28,25,23,.25); }}
  .marker-cluster-large   div {{ background-color:rgba(28,25,23,.75); }}
  .marker-cluster div {{ color:#fff; font-family:'DM Sans',sans-serif; font-weight:600; }}
  #filters::-webkit-scrollbar {{ width:4px; }}
  #filters::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:2px; }}
  .divider {{ border:none; border-top:1px solid var(--border); margin:14px 0; }}
</style>
</head>
<body>
<div id="layout">
  <aside id="sidebar">
    <div id="sidebar-header">
      <h1>Full-Service School Infrastructure</h1>
      <p>Australia-wide map of schools and early childhood centres operating integrated community service models.</p>
      <p class="meta">Dataset: {total} sites &nbsp;·&nbsp; Updated {built}</p>
    </div>
    <div id="count-bar">Showing <span id="vis-count">{total}</span> of {total} sites</div>
    <div id="filters">
      <div class="filter-section">
        <span class="filter-label">State / Territory</span>
        <div class="pill-group" id="state-filters"></div>
      </div>
      <hr class="divider">
      <div class="filter-section">
        <span class="filter-label">Program Type</span>
        <div id="pt-filters"></div>
      </div>
      <hr class="divider">
      <div class="filter-section">
        <span class="filter-label">Target Age Group</span>
        <div class="pill-group" id="ta-filters"></div>
      </div>
      <hr class="divider">
      <div class="filter-section">
        <span class="filter-label">Program — click to isolate</span>
        <div id="legend"></div>
      </div>
    </div>
    <button id="reset-btn">Reset all filters</button>
  </aside>
  <div id="map"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.min.js"></script>
<script>
const DATA   = {data_js};
const COLORS = {colors_js};
const TOTAL  = {total};

const map = L.map('map',{{center:[-27.5,134],zoom:5}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{
  attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  subdomains:'abcd', maxZoom:19
}}).addTo(map);

let activeStates=new Set(), activePTypes=new Set(), activeTAs=new Set(), activePL=null;
const plCounts={{}};
DATA.forEach(d=>plCounts[d.pl]=(plCounts[d.pl]||0)+1);

const cluster=L.markerClusterGroup({{maxClusterRadius:40,showCoverageOnHover:false}});
map.addLayer(cluster);

function makeIcon(color){{
  return L.divIcon({{className:'',
    html:`<svg width="18" height="24" viewBox="0 0 18 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 0C4.03 0 0 4.03 0 9c0 6.75 9 15 9 15s9-8.25 9-15C18 4.03 13.97 0 9 0z" fill="${{color}}"/>
      <circle cx="9" cy="9" r="4" fill="white" opacity="0.85"/>
    </svg>`,
    iconSize:[18,24], iconAnchor:[9,24], popupAnchor:[0,-26]
  }});
}}

const iconCache={{}};
function getIcon(pl){{ if(!iconCache[pl]) iconCache[pl]=makeIcon(COLORS[pl]||'#52525B'); return iconCache[pl]; }}

function statusClass(s){{
  if(!s) return '';
  const sl=s.toLowerCase();
  if(sl.includes('dedup')) return 'status-dedup';
  if(sl.includes('announ')||sl.includes('construct')) return 'status-announced';
  if(sl.includes('complet')||sl.includes('transit')) return 'status-completed';
  if(sl.includes('pilot')) return 'status-pilot';
  if(sl.includes('backbone')) return 'status-backbone';
  return 'status-active';
}}
function statusLabel(s){{
  if(!s) return '';
  const sl=s.toLowerCase();
  if(sl.includes('dedup')) return 'Deduplicated';
  if(sl.includes('announ')||sl.includes('construct')) return 'Announced';
  if(sl.includes('complet')||sl.includes('transit')) return 'Completed / Transitioned';
  if(sl.includes('pilot')) return 'Pilot';
  if(sl.includes('backbone')) return 'Community Backbone';
  return 'Active';
}}

let allMarkers=[];
DATA.forEach(d=>{{
  const m=L.marker([d.lat,d.lon],{{icon:getIcon(d.pl)}});
  const color=COLORS[d.pl]||'#52525B';
  const links=[];
  if(d.site) links.push(`<a href="${{d.site}}" target="_blank" class="popup-link site">Site ↗</a>`);
  if(d.src)  links.push(`<a href="${{d.src}}"  target="_blank" class="popup-link">Program ↗</a>`);
  const dpLine = d.dp ? `<div class="popup-dp">Also: ${{d.dp}}</div>` : '';
  m.bindPopup(`
    <div class="popup-inner">
      <span class="popup-tag" style="background:${{color}}">${{d.pl}}</span>
      <div class="popup-name">${{d.n}}</div>
      <div class="popup-row"><span class="popup-key">Location</span><span class="popup-val">${{d.su}}, ${{d.st}}</span></div>
      <div class="popup-row"><span class="popup-key">Program</span><span class="popup-val">${{d.p}}</span></div>
      <div class="popup-row"><span class="popup-key">Type</span><span class="popup-val">${{d.pt}}</span></div>
      <div class="popup-row"><span class="popup-key">Setting</span><span class="popup-val">${{d.se}}</span></div>
      <div class="popup-row"><span class="popup-key">Age focus</span><span class="popup-val">${{d.ta}}</span></div>
      <span class="status-badge ${{statusClass(d.status)}}">${{statusLabel(d.status)}}</span>
      ${{dpLine}}
      ${{links.length ? `<div class="popup-links">${{links.join('')}}</div>` : ''}}
    </div>
  `,{{maxWidth:300}});
  m._data=d;
  allMarkers.push(m);
}});

function applyFilters(){{
  cluster.clearLayers();
  let visible=0;
  allMarkers.forEach(m=>{{
    const d=m._data;
    const ok=
      (activeStates.size===0||activeStates.has(d.st))&&
      (activePTypes.size===0||activePTypes.has(d.pt))&&
      (activeTAs.size===0||activeTAs.has(d.ta))&&
      (!activePL||activePL===d.pl);
    if(ok){{ cluster.addLayer(m); visible++; }}
  }});
  document.getElementById('vis-count').textContent=visible;
  document.querySelectorAll('.legend-item').forEach(el=>
    el.classList.toggle('dim', activePL!==null && activePL!==el.dataset.pl));
}}

const states={json.dumps(states)};
document.getElementById('state-filters') && states.forEach(st=>{{
  const b=document.createElement('button');
  b.className='pill'; b.textContent=st;
  b.addEventListener('click',()=>{{
    if(activeStates.has(st)){{activeStates.delete(st);b.classList.remove('active');}}
    else{{activeStates.add(st);b.classList.add('active');}}
    applyFilters();
  }});
  document.getElementById('state-filters').appendChild(b);
}});

const ptLabels={json.dumps(pt_labels)};
ptLabels.forEach(pt=>{{
  const b=document.createElement('button');
  b.className='pt-pill'; b.textContent=pt;
  b.addEventListener('click',()=>{{
    if(activePTypes.has(pt)){{activePTypes.delete(pt);b.classList.remove('active');}}
    else{{activePTypes.add(pt);b.classList.add('active');}}
    applyFilters();
  }});
  document.getElementById('pt-filters').appendChild(b);
}});

const taLabels={json.dumps(ta_labels)};
taLabels.forEach(ta=>{{
  const b=document.createElement('button');
  b.className='pill'; b.textContent=ta;
  b.addEventListener('click',()=>{{
    if(activeTAs.has(ta)){{activeTAs.delete(ta);b.classList.remove('active');}}
    else{{activeTAs.add(ta);b.classList.add('active');}}
    applyFilters();
  }});
  document.getElementById('ta-filters').appendChild(b);
}});

Object.keys(COLORS).sort().forEach(pl=>{{
  if(!plCounts[pl]) return;
  const item=document.createElement('div');
  item.className='legend-item'; item.dataset.pl=pl;
  item.innerHTML=`
    <span class="legend-dot" style="background:${{COLORS[pl]}}"></span>
    <span class="legend-name">${{pl}}</span>
    <span class="legend-count">${{plCounts[pl]}}</span>`;
  item.addEventListener('click',()=>{{
    activePL = activePL===pl ? null : pl;
    applyFilters();
  }});
  document.getElementById('legend').appendChild(item);
}});

document.getElementById('reset-btn').addEventListener('click',()=>{{
  activeStates.clear(); activePTypes.clear(); activeTAs.clear(); activePL=null;
  document.querySelectorAll('.pill.active,.pt-pill.active').forEach(b=>b.classList.remove('active'));
  applyFilters();
}});

applyFilters();
</script>
</body>
</html>"""

def main():
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {CSV_PATH} ...")
    rows = load_data()
    print(f"  {len(rows)} records loaded")

    print(f"Writing {HTML_PATH} ...")
    html = build_html(rows)
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"  Done. ({len(html):,} bytes)")
    print(f"\nMap URL (after push): https://chlonsdale.github.io/full-service-schools/")

if __name__ == "__main__":
    main()
