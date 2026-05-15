# Full-Service Schools Register — Australia

Interactive map and dataset of schools and early childhood centres operating integrated community service models across Australia.

**Live map:** https://chlonsdale.github.io/full-service-schools/

---

## Programs included

| Program | States | Type |
|---|---|---|
| Schools as Community Centres (SaCC) | NSW | School-based wraparound |
| Connected Communities | NSW | School-based wraparound |
| National Community Hubs Program (CHA) | NSW, VIC, QLD, SA | School-based wraparound |
| Our Place | VIC | School-based wraparound |
| FamilyLinQ | QLD | School-based wraparound |
| WA Full-Service School Model Trial | WA | School-based wraparound |
| Child and Parent Centres (CPC) | WA | Early childhood integrated |
| Child and Family Learning Centres (CFLC) | TAS | Early childhood integrated |
| SA Children's Centres (ECDP) | SA | Early childhood integrated |
| Queensland Children and Family Centres | QLD | Early childhood integrated |
| NT Child and Family Centres | NT | Early childhood integrated |
| ACT Child and Family Centres | ACT | Early childhood integrated |
| Stronger Places, Stronger People | Multi | Community backbone |

---

## Files

| File | Description |
|---|---|
| `full_service_schools_australia.csv` | Master dataset — source of truth |
| `index.html` | Interactive map — generated from CSV, do not edit directly |
| `build_map.py` | Script that regenerates `index.html` from the CSV |

---

## Updating the map

The dataset is maintained weekly by an automated task. To regenerate the map manually after editing the CSV:

```bash
python build_map.py
git add index.html full_service_schools_australia.csv
git commit -m "Update dataset YYYY-MM-DD"
git push
```

GitHub Pages will reflect the updated map within ~60 seconds of the push.

---

## Dataset columns

| Column | Description |
|---|---|
| `site_name` | Full name of the school or centre |
| `suburb` | Suburb or locality |
| `postcode` | Postcode |
| `state` | State or territory |
| `program` | Full program name |
| `program_label` | Short label used in map legend |
| `program_type` | `School-based wraparound` / `Early childhood integrated` / `Community backbone` |
| `setting_type` | `School site` / `Co-located with school` / `Standalone / community` |
| `target_age` | Primary age group served |
| `status` | `Active` / `Announced` / `Pilot` / `Completed/Transitioned` |
| `needs_verification` | `True` if coordinates or details need independent confirmation |
| `source` | Description of data source |
| `source_url` | URL of program/policy source page |
| `latitude` | Latitude (suburb centroid unless exact address known) |
| `longitude` | Longitude |
| `site_url` | School or centre's own website |
| `dual_program` | Populated when a site appears in multiple programs |

---

*Maintained by the Office of the Provost, Australian Catholic University.*
*Dataset compiled May 2026. Coordinates are suburb-centroid level unless otherwise noted.*
