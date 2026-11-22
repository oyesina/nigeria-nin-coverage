# Nigeria NIN Coverage

**How many people in Nigeria are still missing from the National Identity Database, and where are they?**

An interactive page built from NIMC's monthly enrolment reports and two sets of population estimates.

👉 **Live page:** https://oyesina.github.io/nigeria-nin-coverage/

## Headline (latest NIMC report, 31 Oct 2025)

- **122.4M** people in Nigeria had a NIN (plus 1.5M in the diaspora).
- An estimated **111–117M** people (**48–49%**) had none. The range depends on the population source.
- Hitting the federal **95%-by-December-2026** target needs about **7.5–7.9M** new enrolments a month.
  The pace over the last six reported months was about **0.5M a month**.

## What you can do on the page

- Switch the **population estimate**: WorldPop 2025 (UN-scaled) or NPC/NBS projections.
- Count against **all ages** or **age 16+** only.
- Rank the 36 states + FCT by **people uncaptured** or **coverage %**. Click a state for its trend and detail.
- See coverage and women's share of enrolments **by region**.

## Data

| File | What it is |
|---|---|
| `data/nimc_state_tables.txt` | State tables as published on nimc.gov.ng, one block per monthly report |
| `data/nin_enrolment_by_state.csv` | Cleaned: report × state, female / male / total, as-of date (1,138 rows) |
| `data/nin_coverage_model.csv` | Enrolment joined to population under both scenarios, with coverage, uncaptured and gap-to-95% |
| `data/nin_coverage_app_data.csv` | The slice the page uses |
| `scripts/parse.py`, `scripts/model.py` | Parsing and validation; the population model |

**Sources**
- Enrolment: [NIMC enrolment reports](https://nimc.gov.ng/nin/enrolment-report). 30 reports with state tables, Sep 2021 – Oct 2025.
  NIMC published none for 2024 and nothing after Oct 2025. Earlier reports are images only.
- Population: [WorldPop Nigeria v3.0](https://data.worldpop.org/repo/wopr/NGA/population/v3.0/) 2025 state totals,
  scaled to UN WPP 2024 (237.5M). Also NPC/NBS 2022 state projections (216.8M), grown at the NPC national rate (~2.06%/yr).
  Both are interpolated to each report date.
- Age 16+ share: 57.2% (UN/World Bank 2025: 40.5% aged 0–14), applied evenly to every state.

**Corrections to the published tables:** Abia male count in Oct 2025 (16,849,120 → 1,684,912, so female + male = total).
Duplicate Taraba and Yobe rows in the Dec 2021 table were dropped. Sep 2021 column headers are mislabelled.
March 2023 has no stated date (end of March assumed).
Every other row passes female + male = total, and state rows sum to the published national total
(except May 2025, which is off by 585).

## Caveats

- Nigeria has had no census since 2006. Every population figure is a model, so read "uncaptured" as an estimate with a wide range.
- NIN counts include legal residents and children. They are recorded where people enrol, which is not always where they live,
  and are not reduced for deaths. That is why Lagos and the FCT can exceed 100% coverage.
  On the 16+ basis, 8–9 states exceed 100%.

## How it's built

A single static `index.html` with hand-written SVG charts and no external requests. The same app code also runs as a
Tableau data app (viz extension) on Tableau Cloud. A small stand-in for the Tableau Extensions API feeds it the
embedded data here.
