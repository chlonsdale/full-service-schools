# Cowork Scheduled Task: Full-Service Schools Dataset — Weekly Update

**Schedule:** Weekly (suggested: Monday 7:00 AM)
**Task name:** full-service-schools-update
**Output:** Updated CSV + change report

---

## Your role

You are maintaining the Australian Full-Service Schools dataset on behalf of Chris Lonsdale. Each week, you check designated source pages for changes, compare against the current dataset, update the CSV, and produce a concise change report.

---

## Dataset location

The current dataset is stored at:
```
/Users/chlonsdale/Library/CloudStorage/GoogleDrive-cslonsdale@gmail.com/My Drive/0 Claude/Impact Platform Proposal/Project Resources/Full Service Schools Register/full_service_schools_australia.csv
```

It contains the following columns:
`site_name`, `suburb`, `postcode`, `state`, `program`, `program_label`, `program_type`, `setting_type`, `target_age`, `status`, `needs_verification`, `source`, `source_url`, `latitude`, `longitude`, `site_url`, `dual_program`

The `dual_program` field is populated when a school appears in more than one program (e.g. `Connected Communities + SaCC`). In these cases only one row is kept — see deduplication rules below.

---

## Programs and source URLs to check each week

Check each of the following source pages for additions, removals, or status changes. Only check the pages listed — do not browse beyond them.

| Program label | Source URL to check |
|---|---|
| SaCC | https://education.nsw.gov.au/teaching-and-learning/curriculum/early-learning/schools-as-community-centres/sacc-project-locations |
| Connected Communities | https://education.nsw.gov.au/student-wellbeing/connected-communities |
| Community Hub | https://www.communityhubs.org.au/hubs/ (check all pages) |
| Our Place | https://ourplace.org.au/our-sites/ |
| CFLC | https://greatstart.tas.gov.au/out-and-about/child-and-family-learning-centres/ |
| CPC | https://childandparentcentres.wa.edu.au/our-centre-locations/ |
| FSS Pilot | https://www.pm.gov.au/media/landmark-agreement-signed-fully-fund-western-australian-public-schools |
| SA Children's Centre | https://www.education.sa.gov.au/parents-and-families/child-care-services/childrens-centres |
| QLD Child & Family Centre | https://www.families.qld.gov.au/support-services/child-and-family-services/ |
| NT Child & Family Centre | https://nt.gov.au/learning/early-childhood/early-childhood-support-for-remote-children-and-families |
| ACT Child & Family Centre | https://www.act.gov.au/community/families/child-and-family-centres |
| SPSP Community | https://www.dss.gov.au/stronger-places-stronger-people |
| FamilyLinQ | https://tqkp.org.au/child-family-hubs/ |

---

## What to look for on each source page

For each source page, identify:

1. **New sites** — any named school, centre, or community location not already in the dataset for that program
2. **Removed sites** — any site previously listed that no longer appears (check carefully; some pages paginate)
3. **Status changes** — any site whose status has changed (e.g. announced → active, active → closed)
4. **Name changes** — any site that has been renamed

Do not add sites unless the source page explicitly names them. If a page indicates new sites are coming but does not name them, note this in the change report but do not add a record.

---

## Duplicate detection

Run duplicate detection **after** fetching all source pages but **before** writing any changes to the CSV.

### Step 1: Exact name duplicates

Group all rows in the current CSV by `site_name` (case-insensitive). Flag any `site_name` that appears more than once.

For each duplicate group, apply the following resolution priority (highest wins):

| Priority | program_label |
|---|---|
| 1 (keep) | SaCC |
| 2 (keep) | Our Place |
| 3 (keep) | Community Hub |
| 4 (keep) | Connected Communities |
| 5 (keep) | CPC |
| 6 (keep) | CFLC |
| 7 (keep) | SA Children's Centre |
| 8 (keep) | QLD Child & Family Centre |
| 9 (keep) | NT Child & Family Centre |
| 10 (keep) | ACT Child & Family Centre |
| 11 (keep) | FamilyLinQ |
| lowest | FSS Pilot / SPSP Community |

When a lower-priority row is removed in favour of a higher-priority row:
- Do **not** delete the lower-priority row — set its `status` to `Deduplicated – retained under [winning program_label]`
- Set `dual_program` on the retained row to `[removed program_label] + [kept program_label]`
- Log the resolution in the change report under **Duplicates resolved**

### Step 2: Fuzzy name duplicates

Check for near-matches that are likely the same site under slightly different names. Flag (do not auto-resolve) any pair where:
- The `site_name` values share 80%+ of characters after stripping school-type suffixes ("Public School", "State School", "Primary School", "High School", "College", "Centre", "CFLC", "CPC"), **and**
- The `state` values match, **and**
- The `latitude` values are within 0.05 degrees of each other

List all flagged pairs in the change report under **Possible duplicates — human review required**. Do not modify the CSV for fuzzy matches.

### Step 3: Coordinate proximity check

For records with the same `program_label` and `state`, flag any pair where:
- `latitude` values differ by less than 0.002 degrees **and**
- `longitude` values differ by less than 0.002 degrees **and**
- `site_name` values are **different**

These may be distinct sites that are genuinely co-located (e.g. two schools on the same campus), or they may be data errors. List them under **Coordinate proximity flags — human review required** in the change report. Do not modify the CSV.

### Known dual-program schools (do not re-flag)

These schools legitimately appear in two programs and have already been resolved. Their `dual_program` field is already set. Do not re-flag them as duplicates:
- Curran Public School (Connected Communities + SaCC)
- Dareton Public School (Connected Communities + SaCC)
- Kempsey West Public School (Connected Communities + SaCC)
- Moree East Public School (Connected Communities + SaCC)

---



### Adding a new record
Set these fields:
- `site_name`: exact name as shown on source page
- `suburb`, `postcode`, `state`: from the source page or infer from the site name
- `program`, `program_label`: match the existing convention for that program (see existing records)
- `program_type`: `School-based wraparound` | `Early childhood integrated` | `Community backbone`
- `setting_type`: `School site` | `Co-located with school` | `Standalone / community`
- `target_age`: `Birth–5` | `Birth–8` | `Primary school-age` | `Secondary school-age` | `All ages / community`
- `status`: `Active` | `Announced – commencing [year]` | `Pilot`
- `needs_verification`: `False` if sourced from the page; `True` if inferred
- `source`: programme source description (match convention for that program)
- `source_url`: the source page URL
- `latitude`, `longitude`: use suburb centroid (5 decimal places); flag in change report that exact coordinates need verification
- `site_url`: search for the site's own website using the URL patterns below

### URL patterns by program
- NSW public schools: `https://[slug]-p.schools.nsw.gov.au/` (primary), `-h` (high), `-c` (central)
- QLD state schools: `https://[slug]ss.eq.edu.au/`
- WA CPCs: `https://childandparentcentres.wa.edu.au/[slug]/`
- Our Place VIC: `https://ourplace.org.au/our-sites/[slug]/`
- SA Children's Centres: `https://www.preschools.sa.gov.au/[slug]-childrens-centre/`
- TAS CFLCs: `https://greatstart.tas.gov.au/out-and-about/child-and-family-learning-centres/`
- ACT CFCs: `https://www.act.gov.au/community/families/child-and-family-centres/[slug]`
- Community organisations: search `[site_name] [suburb]` to find official website

For slug construction: lowercase the site name, replace spaces and punctuation with hyphens, remove "public school", "state school", "primary school", "high school" etc.

### Updating an existing record
- Change `status` field if the status has changed
- Update `site_url` if a previously blank URL can now be filled
- Do not change `latitude` or `longitude` unless a confirmed address is available
- Do not change `needs_verification` from `True` to `False` unless you have a verified source

### Removing a record
Do not delete records. Instead:
- Set `status` to `Closed` or `Decommissioned – [year]` as appropriate
- Add a note to the change report

---

## Output 1: Updated CSV

Save the updated CSV back to:
```
/Users/chlonsdale/Library/CloudStorage/GoogleDrive-cslonsdale@gmail.com/My Drive/0 Claude/Impact Platform Proposal/Project Resources/Full Service Schools Register/full_service_schools_australia.csv
```

Only write the file if at least one change was made. If no changes were found, do not overwrite the file.

---

## Output 2: Change report

Save a markdown change report to:
```
/Users/chlonsdale/Library/CloudStorage/GoogleDrive-cslonsdale@gmail.com/My Drive/0 Claude/Impact Platform Proposal/Project Resources/Full Service Schools Register/updates/update_YYYY-MM-DD.md
```

Create the folder if it does not exist.

Format the report as follows:

```markdown
# Full-Service Schools Dataset — Weekly Update
**Run date:** YYYY-MM-DD
**Sources checked:** [n]
**Changes found:** [n]

---

## Duplicates resolved ([n])
| site_name | kept under | removed label | dual_program set |
|---|---|---|---|

## Possible duplicates — human review required ([n])
| site_name_a | site_name_b | program_label | reason |
|---|---|---|---|

## Coordinate proximity flags — human review required ([n])
| site_name_a | site_name_b | program_label | distance (deg) |
|---|---|---|---|

## New sites ([n])
| site_name | program_label | state | status | coordinates |
|---|---|---|---|---|
| ... | ... | ... | ... | suburb centroid ⚠ |

## Status changes ([n])
| site_name | program_label | old_status | new_status |
|---|---|---|---|

## Sites no longer listed ([n])
| site_name | program_label | state | action taken |
|---|---|---|---|

## Sources with no changes ([n])
- [program_label]: no changes detected

## Flags requiring human review
- [any items needing Chris to verify — coordinates, ambiguous names, sites mentioned but not named, etc.]

---
*Dataset total after update: [n] records ([n] active, [n] announced, [n] closed)*
```

If no changes were found on any source, still produce the report with all sources listed under "no changes" and a note confirming the dataset is current.

---

## Error handling

- If a source URL returns a 403, 404, or timeout: note it in the report under "Flags requiring human review" and skip that source — do not guess at changes
- If pagination is unclear (e.g. Community Hubs Australia has multiple pages): check all pages before concluding no changes
- If a site appears with a slightly different name than an existing record: flag it for human review rather than auto-updating
- If coordinates cannot be reliably inferred: use the state capital centroid and flag in the report

---

## Output 3: Email delivery

After saving the change report file, send it by email using Gmail.

**To:** chris.lonsdale@acu.edu.au
**From:** your connected Gmail account
**Subject:** Full-Service Schools — Weekly Update [YYYY-MM-DD] ([n] changes)
**Body:** The full change report as inline plain text. Do not attach any files — no attachments, no links to files.

The email body must contain the entire report. The recipient should be able to read the complete report without opening anything.

If Gmail is unavailable or auth fails: note this in the terminal output and skip — the report file is the primary record.

---

## Output 4: Publish updated map to GitHub Pages

Run this step only if the CSV was changed in Output 1. If no changes were made to the CSV, skip this step entirely.

**Repo:** `https://github.com/chlonsdale/full-service-schools`
**Local clone:** `~/full-service-schools` (clone it here on first run if it does not exist)

### Step 1: Pull latest
```bash
cd ~/full-service-schools
git pull origin main
```

### Step 2: Copy updated CSV into repo
```bash
cp "/Users/chlonsdale/Library/CloudStorage/GoogleDrive-cslonsdale@gmail.com/My Drive/0 Claude/Impact Platform Proposal/Project Resources/Full Service Schools Register/full_service_schools_australia.csv" \
   ~/full-service-schools/full_service_schools_australia.csv
```

### Step 3: Regenerate the map
```bash
cd ~/full-service-schools
python build_map.py
```

Confirm `build_map.py` exits successfully and reports the correct record count before continuing.

### Step 4: Commit and push
```bash
git add index.html full_service_schools_australia.csv
git commit -m "Weekly update YYYY-MM-DD — [n] changes"
git push origin main
```

### Authentication
Git push requires a GitHub Personal Access Token (PAT) with `repo` scope, stored in the macOS keychain or Git credential store. If authentication fails, stop and report the error — do not retry more than once.

### If the repo is not yet cloned locally
```bash
git clone https://github.com/chlonsdale/full-service-schools.git ~/full-service-schools
```
Then repeat from Step 1.

The live map will update at `https://chlonsdale.github.io/full-service-schools/` within ~60 seconds of a successful push.

---

## Completion

When done, confirm:
1. Whether the CSV was updated (and how many records changed)
2. Whether the map was regenerated and pushed to GitHub (or skipped — no changes)
3. The live map URL: `https://chlonsdale.github.io/full-service-schools/`
4. Any items flagged for Chris to review
