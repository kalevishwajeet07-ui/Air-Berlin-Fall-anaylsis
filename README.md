# Market Concentration Analysis: Air Berlin Collapse and Lufthansa Dominance

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Academic-green.svg)](LICENSE)

> **Academic Thesis Project:** Analyzing the competitive dynamics of German aviation markets following Air Berlin's insolvency in 2017, with focus on market concentration and Lufthansa Group's expansion.

---

## Table of Contents

- [Overview](#overview)
- [Research Context](#research-context)
- [Project Structure](#project-structure)
- [Analysis Scripts](#analysis-scripts)
  - [Analysis 1: Airport Slot Allocation](#analysis-1-airport-slot-allocation-by-airline-group)
  - [Analysis 2: New Entrants Coverage](#analysis-2-new-entrants-slot-coverage--50-rule-compliance)
  - [Analysis 3: Airport-Level HHI](#analysis-3-airport-level-market-concentration-hhi)
  - [Analysis 4: Route-Level HHI](#analysis-4-route-level-market-concentration-hhi)
  - [Analysis 5: Lufthansa Route Expansion](#analysis-5-lufthansa-expansion-into-air-berlin-routes)
- [Data](#data)
- [Results](#results)
- [Installation & Usage](#installation--usage)
- [Technical Documentation](#technical-documentation)
- [Algorithms and Methodologies](#algorithms-and-methodologies)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This repository contains the complete analytical codebase for a thesis studying the **market concentration effects** of Air Berlin's insolvency (August 2017) on German aviation markets. The analysis focuses on:

1. **Slot Redistribution** - How Air Berlin's airport slots were reallocated among competing carriers
2. **Market Concentration** - Measurement of competitive intensity using the Herfindahl-Hirschman Index (HHI)
3. **New Entrant Access** - Evaluation of regulatory compliance with EU slot allocation rules
4. **Lufthansa Dominance** - Assessment of Lufthansa Group's market position expansion
5. **Route-Level Competition** - Granular analysis of concentration on specific origin-destination pairs

### Key Findings Preview

- **7 German airports** analyzed (DUS, FRA, HAM, MUC, STR, SXF, TXL)
- **5 seasons** tracked (Summer 2015 - Summer 2019)
- **6 airline groups** classified (Lufthansa, Air Berlin, LCC, Legacy, Regional, New Entrants)
- **HHI calculations** at both airport and route levels
- **EU 50% Rule** compliance verification for new entrant slot allocation

---

## Research Context

### The Air Berlin Collapse

**Air Berlin**, Germany's second-largest airline, filed for insolvency on **August 15, 2017**, and ceased operations by **October 28, 2017**. This event created significant capacity gaps in German aviation markets, raising critical questions:

- Would **Lufthansa Group** exploit the vacuum to establish monopolistic control?
- Entry barriers for **new entrants** and **low-cost carriers**.
- Did regulators ensure **competitive market access** through slot allocation rules?
- How did **market concentration levels** change across different airports and routes?

### Regulatory Framework

This research examines compliance with:
- **EU Regulation 95/93** - Slot allocation at coordinated airports
- **50% Rule** - Requirement to allocate ≥50% of new slots to new entrants
- **Antitrust thresholds** - HHI benchmarks from DOJ/FTC Horizontal Merger Guidelines

### Academic Significance

This thesis contributes to understanding:
- **Airline market dynamics** during industry consolidation
- **Effectiveness of slot regulation** in promoting competition
- **Applicability of HHI** to aviation market analysis
- **Policy implications** for preventing excessive market concentration

---

## Project Structure

```
airberlin_code_share/
│
├── Analysis_1.py              # Airport slot allocation aggregation
├── Analysis_2.py              # New entrants coverage & 50% rule
├── Analysis_3.py              # Airport-level HHI calculation
├── Analysis_4.py              # Route-level HHI analysis
├── Analysis_5.py              # Lufthansa expansion tracking
│
├── Data/
│   ├── schedule.csv           # Flight schedule data (sample: 10 rows)
│   └── slots/                 # Airport slot allocation files
│       ├── DUS.csv            # Düsseldorf slot data
│       ├── FRA.csv            # Frankfurt slot data
│       ├── HAM.csv            # Hamburg slot data
│       ├── MUC.csv            # Munich slot data
│       ├── STR.csv            # Stuttgart slot data
│       ├── SXF.csv            # Berlin-Schönefeld slot data
│       ├── TXL.csv            # Berlin-Tegel slot data
│       ├── *_NEW_ENTRANT.csv  # New entrant airline lists per airport
│       └── ...
│
├── Result_1/                  # Analysis 1 outputs (slot aggregation)
│   ├── DUS.csv
│   ├── FRA.csv
│   └── ...
│
├── Result_2/                  # Analysis 2 outputs (new entrants)
│   └── new_entrants_coverage_s19_50_percent_rule.csv
│
├── Result_3/                  # Analysis 3 outputs (airport HHI)
│   ├── HHI_Summary_All_Airports.csv
│   ├── Airport_HHI_Comparison.csv
│   ├── DUS_HHI_Analysis.csv
│   └── ...
│
├── Result_4/                  # Analysis 4 outputs (route HHI)
│   ├── hhi_results.csv
│   ├── hhi_pivot_table.csv
│   ├── detailed_market_shares.csv
│   ├── graphs/                # Visualization outputs
│   └── ...
│
├── Result_5/                  # Analysis 5 outputs (Lufthansa expansion)
│   ├── ab_routes_frequency_per_year.csv
│   ├── lufthansa_on_ab_routes_with_increase.csv
│   └── ...
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Analysis Scripts

### Analysis 1: Airport Slot Allocation by Airline Group

**File:** `Analysis_1.py`

**Purpose:**
Aggregates airport slot allocations by airline group across five summer seasons (S15-S19).

**Key Features:**
- Classifies airlines into 6 strategic groups:
  - **Lufthansa Group** - Flag carrier and subsidiaries
  - **Air Berlin Group** - Defunct competitor (pre-collapse)
  - **Low-Cost Carriers** - Budget airlines (Ryanair, EasyJet, etc.)
  - **Legacy Carriers** - Traditional full-service airlines
  - **Regional & Others** - Smaller operators
  - **New Entrants** - Airlines entering post-collapse
- Prevents double-counting through conflict resolution
- Outputs one CSV per airport with seasonal slot counts

**Output:**
- `Result_1/<AIRPORT>.csv` - Slot counts per group per season

**Business Insight:**
Reveals which airline groups gained or lost market access at each airport, establishing baseline for concentration analysis.

---

### Analysis 2: New Entrants Slot Coverage & 50% Rule Compliance

**File:** `Analysis_2.py`

**Purpose:**
Verifies compliance with EU regulation requiring ≥50% of new slots be allocated to new entrants.

**Key Features:**
- Analyzes Summer 2019 (S19) slot pool data
- Compares available slots vs. new entrant allocation
- Calculates percentage taken by new entrants
- Flags non-compliance with EU 50% rule

**Output:**
- `Result_2/new_entrants_coverage_s19_50_percent_rule.csv`

**Regulatory Context:**
EU Regulation 95/93 mandates slot coordinators reserve 50% of newly available slots for new entrants to prevent incumbent dominance.

**Business Insight:**
Identifies whether airports favored established carriers (Lufthansa) over new market participants during post-collapse redistribution.

---

### Analysis 3: Airport-Level Market Concentration (HHI)

**File:** `Analysis_3.py`

**Purpose:**
Calculates Herfindahl-Hirschman Index (HHI) to measure market concentration at each airport.

**Key Features:**
- Computes HHI using market share data (not slot counts)
- Classifies markets as:
  - **Unconcentrated** (HHI < 1,500) - Competitive
  - **Moderately Concentrated** (1,500 ≤ HHI ≤ 2,500)
  - **Highly Concentrated** (HHI > 2,500) - Oligopolistic/Monopolistic
- Tracks concentration trends over 5 seasons
- Generates comprehensive airport comparisons

**Output:**
- `Result_3/HHI_Summary_All_Airports.csv` - Consolidated HHI data
- `Result_3/Airport_HHI_Comparison.csv` - Cross-airport comparison
- `Result_3/<AIRPORT>_HHI_Analysis.csv` - Individual airport details

**HHI Formula:**
```
HHI = Σ (Market Share_i)²   where i = each airline group

Example:
  Lufthansa: 50% → 50² = 2,500
  LCC:       30% → 30² =   900
  Legacy:    20% → 20² =   400
  ─────────────────────────────
  HHI             = 3,800  (Highly Concentrated)
```

**Business Insight:**
Quantifies Lufthansa's market power expansion and identifies airports with potential antitrust concerns.

---

### Analysis 4: Route-Level Market Concentration (HHI)

**File:** `Analysis_4.py`

**Purpose:**
Performs granular HHI analysis at the route level (origin-destination pairs) rather than airport aggregate.

**Key Features:**
- Analyzes routes from German airports to 4 focused regions:
  - Western Europe
  - Eastern Europe
  - North Africa
  - Gulf/Middle East
- Calculates HHI per route per year
- Filters for summer season departures (April-October)
- Generates extensive visualizations:
  - HHI trend charts per route
  - HHI contribution bar charts by airline group
  - Airport/region/year comparisons

**Output:**
- `Result_4/hhi_results.csv` - HHI per route-year
- `Result_4/hhi_pivot_table.csv` - Routes × Years matrix
- `Result_4/detailed_market_shares.csv` - Market share breakdown
- `Result_4/graphs/` - PNG visualizations (35+ charts)

**Why Route-Level Analysis?**
Airport-level HHI can mask route monopolization. For example:
- Airport HHI = 2,200 (Moderate) might seem acceptable
- But Route A: HHI = 8,500 (near-monopoly)
- And Route B: HHI = 1,200 (competitive)

Route-level analysis reveals hidden concentration patterns.

**Business Insight:**
Identifies specific routes where Lufthansa established dominance, enabling targeted antitrust intervention.

---

### Analysis 5: Lufthansa Expansion into Air Berlin Routes

**File:** `Analysis_5.py`

**Purpose:**
Tracks Lufthansa Group's year-over-year departure changes on routes previously served by Air Berlin.

**Key Features:**
- Identifies all routes Air Berlin operated (2015-2017)
- Measures Lufthansa departures on those routes across all years
- Computes year-over-year changes:
  - **LH_Delta:** Absolute change in departures
  - **LH_Pct_Change:** Percentage growth rate
- Flexible endpoint treatment:
  - Airport → Airport (e.g., DUS → FRA)
  - Airport → Region (e.g., DUS → Western Europe)
  - Region → Airport (reverse)
  - Region → Region (aggregated analysis)
- Normalizes Gulf/Middle East regions for consistency

**Output:**
- `Result_5/ab_routes_frequency_per_year.csv` - Air Berlin route operations
- `Result_5/lufthansa_on_ab_routes_with_increase.csv` - Lufthansa expansion metrics

**Business Insight:**
Directly measures Lufthansa's **route substitution strategy** - did they systematically replace Air Berlin service to consolidate market control?

---

## Data

### Primary Data Sources

#### 1. **schedule.csv**
- **Description:** Flight schedule database covering 2015-2019
- **Contents:** Origin/destination airports, airline codes, passengers, departures, distances, market shares
- **Size:** 235,000+ rows (sample: 10 rows included in repository for privacy)
- **Columns:**
  - `Origin Airport`, `Destination Airport` - IATA codes
  - `Operating Airline` - Carrier code
  - `Year`, `Month` - Temporal identifiers
  - `Departures` - Flight frequency
  - `Airline Share` - Market share percentage
  - `Origin/Destination Region Name` - Geographic classification

#### 2. **slots/** Directory
- **Description:** Airport slot allocation data per season
- **File Format:** `<AIRPORT>.csv` with columns for S15-S19
- **New Entrant Files:** `<AIRPORT>_NEW_ENTRANT.csv` listing qualifying airlines
- **Size:** Full datasets (sample files included)

### Data Privacy Note

**Full datasets contain proprietary airport coordination data and cannot be publicly released.**
Sample files (10-100 rows) are included for:
- Code verification
- Methodology demonstration
- Academic review

To **replicate** this analysis with full data:
1. Contact German airport coordination authorities
2. Obtain slot allocation records for 2015-2019
3. Replace sample files in `Data/` directory
4. Run analysis scripts unchanged

---

## Results

### Output Directories

| Directory   | Contents | Key Files |
|-------------|----------|-----------|
| **Result_1/** | Slot allocation aggregation | `<AIRPORT>.csv` (7 files) |
| **Result_2/** | New entrants compliance | `new_entrants_coverage_s19_50_percent_rule.csv` |
| **Result_3/** | Airport HHI analysis | `HHI_Summary_All_Airports.csv`, `Airport_HHI_Comparison.csv`, `<AIRPORT>_HHI_Analysis.csv` (7 files) |
| **Result_4/** | Route HHI analysis | `hhi_results.csv`, `hhi_pivot_table.csv`, `detailed_market_shares.csv`, `graphs/` (35+ charts) |
| **Result_5/** | Lufthansa expansion tracking | `ab_routes_frequency_per_year.csv`, `lufthansa_on_ab_routes_with_increase.csv` |

### Sample Result Interpretations

#### **Result_3: Airport HHI Example**
```csv
Airport,Season,HHI,Market Classification
DUS,S17,2100,Moderately Concentrated
DUS,S18,3200,Highly Concentrated  ← Post-collapse spike
DUS,S19,2950,Highly Concentrated
```
**Interpretation:** Düsseldorf became highly concentrated after Air Berlin's collapse, suggesting Lufthansa market power expansion.

#### **Result_2: 50% Rule Compliance Example**
```csv
Airport Code,Slots available,Slots taken by new_entrants,Pct_taken_by_new_entrants
DUS,23981,8500,35.44  ← Non-compliant (< 50%)
MUC,11249,6100,54.23  ← Compliant (≥ 50%)
```
**Interpretation:** Düsseldorf failed to allocate 50% to new entrants, potentially favoring incumbents.

---

## Installation & Usage

### Prerequisites

- **Python 3.7+**
- **pip** package manager

### Setup

```bash
# Clone the repository (or download ZIP)
cd airberlin_code_share

# Install dependencies
pip install -r requirements.txt
```

### Running Analyses

Execute scripts in order (each depends on prior outputs):

```bash
# Step 1: Aggregate slot allocations by group
python Analysis_1.py
# Output: Result_1/*.csv

# Step 2: Check new entrants coverage
python Analysis_2.py
# Output: Result_2/new_entrants_coverage_s19_50_percent_rule.csv

# Step 3: Calculate airport-level HHI
python Analysis_3.py
# Output: Result_3/*.csv

# Step 4: Calculate route-level HHI (includes visualizations)
python Analysis_4.py
# Output: Result_4/*.csv + Result_4/graphs/*.png

# Step 5: Track Lufthansa expansion on Air Berlin routes
python Analysis_5.py
# Output: Result_5/*.csv
```

---

## Technical Documentation

### Libraries and Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **pandas** | ≥1.3.0 | Data manipulation, CSV I/O, aggregation |
| **numpy** | ≥1.21.0 | Numerical computations, array operations |
| **matplotlib** | ≥3.4.0 | Base plotting library for visualizations |
| **seaborn** | ≥0.11.0 | Statistical graphics, enhanced aesthetics |

### Key Data Structures

#### Airline Group Definitions (Python Dictionaries)
```python
LUFTHANSA_GROUP = [
    {"airlineName": "Deutsche Lufthansa AG", "iataCode": "LH"},
    {"airlineName": "Eurowings GmbH", "iataCode": "EW"},
    # ... 13 airlines total
]
```

#### Season Mapping
```python
SEASONS = ["S15", "S16", "S17", "S18", "S19"]
SEASON_NAMES = {
    "S15": "Summer 2015",
    "S16": "Summer 2016",
    "S17": "Summer 2017",  # Air Berlin operational
    "S18": "Summer 2018",  # Post-collapse
    "S19": "Summer 2019"   # Market stabilization
}
```

#### Airport Codes
```python
AIRPORT_CODES = [
    "DUS",  # Düsseldorf
    "FRA",  # Frankfurt
    "HAM",  # Hamburg
    "MUC",  # Munich
    "STR",  # Stuttgart
    "SXF",  # Berlin-Schönefeld
    "TXL"   # Berlin-Tegel
]
```

---

## Algorithms and Methodologies

### 1. Herfindahl-Hirschman Index (HHI)

**Definition:**
The HHI measures market concentration by summing the squared market shares of all competitors.

**Formula:**
```
HHI = Σ(s_i)²  ×  10,000

Where:
  s_i = Market share of firm i (as percentage, e.g., 30 for 30%)
  Σ   = Sum across all firms in the market
```

**Example Calculation:**
```
Market with 3 competitors:
  Firm A: 50% market share
  Firm B: 30% market share
  Firm C: 20% market share

HHI = (50)² + (30)² + (20)²
    = 2,500 + 900 + 400
    = 3,800

Interpretation: Highly Concentrated Market
```

**HHI Interpretation Thresholds:**

| HHI Range | Classification | Antitrust Concern |
|-----------|----------------|-------------------|
| **< 1,500** | Unconcentrated | Low risk - Competitive market |
| **1,500 - 2,500** | Moderately Concentrated | Moderate scrutiny - Monitor mergers |
| **> 2,500** | Highly Concentrated | High risk - Potential for monopolistic behavior |
| **> 5,000** | Severe Concentration | Very high risk - Near-monopoly conditions |

**Source:** U.S. Department of Justice & Federal Trade Commission *Horizontal Merger Guidelines* (2010)

**Implementation in Code:**
- **Analysis 3 (Airport HHI):**
  - Aggregates market shares by airline group per airport
  - Calculates HHI = Σ(group_share²) for each season
  - Tracks temporal trends (increasing concentration = Lufthansa expansion)

- **Analysis 4 (Route HHI):**
  - More granular: HHI per origin-destination route
  - Reveals concentration masked by airport-level averages
  - Example: Munich airport HHI = 2,200 (moderate), but Munich→Istanbul HHI = 7,800 (monopolistic)

### 2. Market Share Calculation

**Formula:**
```
Market Share_i = (Departures_i / Total Departures) × 100

Where:
  Departures_i     = Number of flights operated by airline/group i
  Total Departures = Sum of all flights on the route or at the airport
```

**Alternative Metrics Considered:**
- **Seats Offered:** Captures capacity, but doesn't reflect actual utilization
- **Passengers Carried:** Best demand metric, but not consistently available
- **Departures (Used):** Proxy for market presence, consistently available across datasets

**Justification for Departures:**
Flight frequency is a strong indicator of market control - higher frequency provides:
- **Schedule convenience** for passengers
- **Brand visibility** at airports
- **Slot utilization** efficiency

### 3. Year-over-Year Growth Calculation

Used in **Analysis 5** to track Lufthansa expansion:

**Formula:**
```
LH_Delta = Departures_t - Departures_(t-1)

LH_Pct_Change = (LH_Delta / Departures_(t-1)) × 100

Where:
  t     = Current year
  t-1   = Previous year
```

**Example:**
```
Route: DUS → PMI (Palma de Mallorca)
  Air Berlin 2017: 250 departures
  Lufthansa 2017:  50 departures
  Lufthansa 2018: 180 departures  ← Post-collapse

LH_Delta        = 180 - 50 = +130 departures
LH_Pct_Change   = (130 / 50) × 100 = +260%

Interpretation: Lufthansa tripled service, likely capturing Air Berlin passengers
```

### 4. New Entrant Conflict Resolution

**Challenge:**
Airlines may appear in multiple group definitions (e.g., Eurowings in both Lufthansa Group and LCC lists).

**Algorithm:**
```python
1. Build set of all existing airline codes from predefined groups
2. Load airport-specific new entrant CSV
3. For each airline in new entrant list:
   a. If airline code exists in existing groups → EXCLUDE
   b. Else → INCLUDE as genuine new entrant
4. Aggregate slots for filtered new entrant list
```

**Rationale:**
Prevents double-counting. Eurowings is a Lufthansa subsidiary, not a new market entrant despite recent entry to specific airports.

### 5. Region Normalization

**Problem:**
"GULF" and "MIDDLE EAST" are used inconsistently in schedule data.

**Solution:**
```python
def normalize_region(region_name):
    if region_name in {"GULF", "MIDDLE EAST"}:
        return "GULF/MIDDLE EAST"
    return region_name
```

**Impact:**
Ensures routes to Dubai (Gulf) and Tel Aviv (Middle East) are aggregated correctly for HHI calculation.

### 6. Endpoint Resolution (Analysis 5)

**Challenge:**
Routes can terminate at either a specific airport OR a region.

**Resolution Logic:**
```python
def resolve_endpoint(airport_code, region_name):
    # Priority 1: If airport is in focus set → return airport
    if airport_code in FOCUS_AIRPORTS:
        return airport_code

    # Priority 2: If region is in focus set → return region
    if region_name in FOCUS_REGIONS:
        return region_name

    # Neither in focus → exclude from analysis
    return None
```

**Enables:**
- Airport-to-Airport routes: `DUS → FRA`
- Airport-to-Region routes: `DUS → Western Europe` (aggregates DUS to all Western European airports)
- Region-to-Airport routes: `Western Europe → MUC`
- Region-to-Region routes: `Western Europe → Eastern Europe`

---

## Contributing

This is an **academic research project** supporting a thesis on aviation market concentration. Contributions are welcome for:

- **Data Validation:** Verify slot allocation data accuracy
- **Methodology Review:** Suggest improvements to HHI calculation or market definition
- **Visualization Enhancements:** Additional charts or dashboards
- **Code Optimization:** Performance improvements for large datasets
- **Documentation:** Typos, clarity improvements, additional examples

**Contribution Guidelines:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-improvement`)
3. Commit changes with clear messages
4. Open a Pull Request with detailed description

---

## License

**Academic Use License**

This project is released for **academic and research purposes only**.

- ✅ **Permitted:** Citation in academic papers, thesis research, educational use
- ✅ **Permitted:** Adaptation for non-commercial research projects
- ❌ **Prohibited:** Commercial use without explicit permission
- ❌ **Prohibited:** Redistribution of proprietary data

**Citation:**
```
[Vishwajeet]. (2024). Market Concentration Analysis Following Air Berlin Insolvency.
[University Name], Master's Thesis. GitHub: [Repository URL]
```

---

## Acknowledgments

- **German Airport Coordination Authorities** - For providing slot allocation data
- **Eurocontrol** - For schedule and traffic data sources
- **Academic Advisors** - For methodology guidance and review
- **Open Source Community** - For pandas, matplotlib, and seaborn libraries

---

## Contact

For questions, collaboration inquiries, or data requests:

- **Email:** [Your Academic Email]
- **Institution:** [Your University]
- **Thesis Supervisor:** [Supervisor Name]

---

**Last Updated:** November 2024
**Version:** 1.0.0
**Status:** Active Thesis Research Project
