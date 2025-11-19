#!/usr/bin/env python3
"""
===============================================================================
ANALYSIS 5: LUFTHANSA EXPANSION INTO AIR BERLIN ROUTES (AIRPORTS & REGIONS)
===============================================================================

Goal:
    Identify all routes that Air Berlin Group operated and measure Lufthansa
    Group's year-over-year expansion on those same routes following Air Berlin's
    insolvency. This analysis provides direct evidence of market consolidation
    and reveals which Air Berlin capacity was absorbed by Lufthansa vs. other
    competitors.

Business Context:
    Following Air Berlin's bankruptcy filing in August 2017, the German aviation
    market underwent significant restructuring. European regulators and consumer
    advocates raised concerns that Lufthansa Group would consolidate excessive
    market power by acquiring Air Berlin's slots, aircraft, and routes. This
    analysis tests that hypothesis by tracking Lufthansa's capacity changes on
    every route Air Berlin served.

Analysis Approach:
    Unlike traditional route analysis (airport-to-airport only), this script
    treats endpoints flexibly as either:
    - Focused airports (DUS, FRA, HAM, MUC, STR, SXF, TXL), or
    - Focused regions (Western Europe, Eastern Europe, North Africa, Gulf/Middle East)

    This captures both point-to-point routes (e.g., DUS→FRA) and regional routes
    (e.g., MUC→Western Europe) that aggregate multiple destination airports within
    a region. Air Berlin operated extensive regional networks, making this granular
    view essential for comprehensive analysis.

Route Classification Examples:
    - Airport → Airport: DUS → FRA (traditional point-to-point)
    - Airport → Region: MUC → Western Europe (aggregated regional analysis)
    - Region → Airport: North Africa → TXL (inbound regional traffic)
    - Region → Region: Eastern Europe → Western Europe (transit flows)

Focused Airports:
    DUS: Düsseldorf, FRA: Frankfurt, HAM: Hamburg, MUC: Munich
    STR: Stuttgart, SXF: Berlin-Schönefeld, TXL: Berlin-Tegel

Focused Regions:
    - Western Europe: Core EU markets (competitive battleground)
    - Eastern Europe: Growing markets with legacy competition
    - North Africa: Leisure/diaspora routes (Air Berlin stronghold)
    - Gulf/Middle East: Premium connections (combined for market similarity)

Region Normalization:
    "GULF" and "MIDDLE EAST" are consolidated into "GULF & MIDDLE EAST" to
    reflect operational and competitive similarities. This prevents artificial
    route fragmentation in the analysis.

Output Files:
    1. Result5/ab_routes_frequency_per_year.csv
       - Lists all routes Air Berlin Group operated (any year)
       - Shows Air Berlin departure counts per year per route
       - Identifies which routes disappeared after insolvency
       - Sorted by route and year for trend analysis

    2. Result5/lufthansa_on_ab_routes_with_increase.csv
       - Comprehensive route-by-route analysis of Lufthansa expansion
       - Columns:
         * Year: Calendar year (2015-2019)
         * Origin: Origin endpoint (airport or region)
         * Destination: Destination endpoint (airport or region)
         * Route: Full route identifier (Origin→Destination)
         * AB_Departures: Air Berlin departures for this route-year
         * LH_Departures: Lufthansa departures for this route-year
         * LH_Delta: Year-over-year change in Lufthansa departures
         * LH_Pct_Change: Year-over-year percentage change in Lufthansa capacity

Key Metrics:
    - LH_Delta > 0: Lufthansa increased capacity (potential market filling)
    - LH_Delta >> AB_Departures decline: Lufthansa absorbed Air Berlin capacity
    - LH_Delta < 0: Lufthansa reduced capacity (competitive dynamics)
    - LH_Pct_Change: Relative growth rate (contextualized expansion)

Business Insights:
    - Identify routes where Lufthansa directly replaced Air Berlin
    - Detect routes where LCCs or other carriers filled the gap
    - Measure timing of Lufthansa expansion relative to Air Berlin exit
    - Assess whether expansion correlates with increased market concentration

Methodology:
    1. Load schedule data and normalize region names
    2. Filter for routes where both endpoints are in focus sets
    3. Classify airlines into Lufthansa Group vs. Air Berlin Group
    4. Aggregate departures by route, year, and airline group
    5. Identify all routes Air Berlin ever operated
    6. For those routes, calculate Lufthansa's year-over-year capacity changes
    7. Generate detailed CSV outputs with trend metrics

Limitations:
    - Analysis focuses on departures (frequency) not seats (capacity)
    - Does not account for aircraft size differences
    - Regional aggregation may mask airport-specific dynamics
    - Assumes all Lufthansa expansion on AB routes is substitutive (may be complementary)

===============================================================================
"""

import pandas as pd
from pathlib import Path

# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================

# Input data file path
CSV_PATH = Path("schedule.csv")

# Output file paths
OUTPUT_AB = Path("Result5/ab_routes_frequency_per_year.csv")
OUTPUT_LH = Path("Result5/lufthansa_on_ab_routes_with_increase.csv")

# ============================================================================
# FOCUSED ENDPOINTS CONFIGURATION
# ============================================================================

# Focused airports: Major German coordinated airports
FOCUS_AIRPORTS = {"DUS", "FRA", "HAM", "MUC", "STR", "SXF", "TXL"}

# Focused regions: Strategic destination markets
# Note: GULF and MIDDLE EAST will be normalized to "GULF & MIDDLE EAST"
FOCUS_REGIONS = {"WESTERN EUROPE", "EASTERN EUROPE", "NORTH AFRICA", "GULF", "MIDDLE EAST"}

# ============================================================================
# AIRLINE GROUP DEFINITIONS (IATA Codes)
# ============================================================================

# Lufthansa Group: Germany's dominant carrier and subsidiaries
# Hypothesis: This group expanded significantly into Air Berlin routes post-collapse
LUFTHANSA_GROUP_CODES = {
    "LH",   # Deutsche Lufthansa AG
    "XG",   # SunExpress Deutschland
    "XQ",   # SunExpress
    "OS",   # Austrian Airlines
    "LX",   # Swiss International Air Lines
    "SN",   # Brussels Airlines
    "EW",   # Eurowings
    "WK",   # Edelweiss Air
    "4U",   # Germanwings
    "CL",   # Lufthansa CityLine
    "EN",   # Air Dolomiti
    "LZ",   # Swiss Global Air Lines
    "E2"    # Eurowings Europe
}

# Air Berlin Group: Former second-largest German carrier (bankrupt Aug 2017)
# Tracking their route exit reveals capacity gaps filled by others
AIR_BERLIN_GROUP_CODES = {
    "AB",   # Air Berlin Aviation
    "H3",   # Air Berlin (alternative code)
    "HG*",  # NL Luftfahrt
    "HE",   # LGW Luftfahrtgesellschaft Walter
    "OE"    # Laudamotion
}

# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

# Load schedule data (all flights)
df = pd.read_csv(CSV_PATH, dtype=str)

# Normalize column names (strip whitespace for consistent access)
df.columns = [c.strip() for c in df.columns]

# Convert Year to integer for chronological operations
if "Year" in df.columns:
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
else:
    df["Year"] = pd.NA

# Convert Departures to numeric (handle string formats with coercion)
# Missing/invalid values default to 0 for aggregation purposes
df["Departures"] = pd.to_numeric(df.get("Departures", 0), errors="coerce").fillna(0).astype(float)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_region(region_name):
    """
    Normalize region names to consolidate Gulf and Middle East.

    Args:
        region_name (str): Raw region name from schedule data

    Returns:
        str: Normalized region name (uppercase, stripped, consolidated)

    Business Logic:
        GULF and MIDDLE EAST are combined into "GULF & MIDDLE EAST" because:
        - Air Berlin operated both markets with similar strategic intent
        - Competitive dynamics are comparable (premium long-haul connections)
        - Prevents artificial route fragmentation in analysis
    """
    if pd.isna(region_name):
        return region_name
    region_name = str(region_name).strip().upper()
    if region_name in {"GULF", "MIDDLE EAST"}:
        return "GULF & MIDDLE EAST"
    return region_name

# ============================================================================
# DATA CLEANING AND NORMALIZATION
# ============================================================================

# Ensure required columns exist (create with NA if missing)
for col in ["Origin Airport", "Destination Airport", "Origin Region Name", "Destination Region Name"]:
    if col not in df.columns:
        df[col] = pd.NA

# Normalize airport codes: strip whitespace and convert to uppercase
# Ensures consistent matching with FOCUS_AIRPORTS set
df["Origin Airport"] = df["Origin Airport"].astype(str).str.strip().str.upper()
df["Destination Airport"] = df["Destination Airport"].astype(str).str.strip().str.upper()

# Normalize region names using consolidation function
df["Origin Region Name"] = df["Origin Region Name"].apply(normalize_region)
df["Destination Region Name"] = df["Destination Region Name"].apply(normalize_region)

# Create normalized focus regions set (includes "GULF & MIDDLE EAST" consolidation)
NORMALIZED_FOCUS_REGIONS = set(normalize_region(r) for r in FOCUS_REGIONS)

# ============================================================================
# ENDPOINT RESOLUTION LOGIC
# ============================================================================

def resolve_endpoint(airport_code, region_name):
    """
    Resolve route endpoint to either a focused airport or focused region.

    Args:
        airport_code (str): Three-letter IATA airport code
        region_name (str): Normalized region name

    Returns:
        str or None: Resolved endpoint identifier (airport code or region name)
                     Returns None if neither is in focused sets

    Priority Logic:
        1. If airport_code is in FOCUS_AIRPORTS → return airport_code
        2. Else if region_name is in NORMALIZED_FOCUS_REGIONS → return region_name
        3. Else → return None (endpoint not in scope of analysis)

    Business Rationale:
        Airport-level specificity is preferred when available, but regional
        aggregation captures Air Berlin's network breadth beyond point-to-point routes.
    """
    airport_code = (str(airport_code).strip().upper() if pd.notna(airport_code) else "")
    if airport_code in FOCUS_AIRPORTS:
        return airport_code
    # region_name already normalized
    if pd.notna(region_name) and region_name in NORMALIZED_FOCUS_REGIONS:
        return region_name
    return None

# ============================================================================
# ROUTE FILTERING AND CLASSIFICATION
# ============================================================================

# Add resolved endpoints to the dataframe
# Each row now has Origin_Endpoint and Destination_Endpoint (airport or region)
df["Origin_Endpoint"] = df.apply(lambda r: resolve_endpoint(r.get("Origin Airport"), r.get("Origin Region Name")), axis=1)
df["Destination_Endpoint"] = df.apply(lambda r: resolve_endpoint(r.get("Destination Airport"), r.get("Destination Region Name")), axis=1)

# Filter to only routes where BOTH endpoints are in focus sets
# This ensures we're analyzing Air Berlin's core strategic network
filtered = df[df["Origin_Endpoint"].notna() & df["Destination_Endpoint"].notna()].copy()

print(f"\nFiltered to {len(filtered):,} rows where endpoints belong to focus airports/regions")
print(f"Focus Airports: {', '.join(sorted(FOCUS_AIRPORTS))}")
print(f"Focus Regions: {', '.join(sorted(FOCUS_REGIONS))}\n")

# Create route identifier: "ORIGIN→DESTINATION" format
filtered["Route"] = filtered["Origin_Endpoint"].astype(str) + "->" + filtered["Destination_Endpoint"].astype(str)

# Normalize Operating Airline codes for group matching
filtered["Operating Airline"] = filtered["Operating Airline"].astype(str).str.strip().str.upper()

# ============================================================================
# AIRLINE GROUP CLASSIFICATION
# ============================================================================

def label_group(iata_code):
    """
    Classify airline by group membership.

    Args:
        iata_code (str): Airline IATA code

    Returns:
        str: Group label ("AIR_BERLIN_GROUP", "LUFTHANSA_GROUP", or "OTHER")

    Business Logic:
        - Air Berlin Group: Track capacity exit from the market
        - Lufthansa Group: Measure capacity expansion into AB routes
        - OTHER: All other airlines (LCCs, legacy carriers, etc.)
    """
    if iata_code in AIR_BERLIN_GROUP_CODES:
        return "AIR_BERLIN_GROUP"
    if iata_code in LUFTHANSA_GROUP_CODES:
        return "LUFTHANSA_GROUP"
    return "OTHER"

# Apply group classification to all filtered flights
filtered["Group"] = filtered["Operating Airline"].apply(label_group)

# ============================================================================
# DEPARTURE AGGREGATION BY ROUTE AND GROUP
# ============================================================================

# Aggregate departures by Year, Route, and Airline Group
# This creates time series of capacity by group for each route
agg = (
    filtered
    .groupby(["Year", "Route", "Group"], dropna=False, observed=False)["Departures"]
    .sum()
    .reset_index()
)

# Also aggregate by Origin Region (use Origin_Endpoint if it is a region else use original Origin Region Name)
# We'll create an "Origin Region Key" that is the normalized region when endpoint is region, otherwise keep original normalized region

def origin_region_key(row):
    # if endpoint is a normalized focus region, use that
    if row["Origin_Endpoint"] in NORMALIZED_FOCUS_REGIONS:
        return row["Origin_Endpoint"]
    # else fall back to normalized Origin Region Name
    return row["Origin Region Name"]

filtered["Origin Region Key"] = filtered.apply(origin_region_key, axis=1)

region_agg = (
    filtered
    .groupby(["Year", "Origin Region Key", "Group"], dropna=False, observed=False)["Departures"]
    .sum()
    .reset_index()
)

# Pivot to have AB and LH side-by-side
pivot = agg.pivot_table(
    index=["Year", "Route"],
    columns="Group",
    values="Departures",
    aggfunc="sum",
    fill_value=0
).reset_index()

# Pivot for regions
region_pivot = region_agg.pivot_table(
    index=["Year", "Origin Region Key"],
    columns="Group",
    values="Departures",
    aggfunc="sum",
    fill_value=0
).reset_index()

# Ensure columns exist for both pivots
for col in ["AIR_BERLIN_GROUP", "LUFTHANSA_GROUP", "OTHER"]:
    if col not in pivot.columns:
        pivot[col] = 0.0
    if col not in region_pivot.columns:
        region_pivot[col] = 0.0

# Split Route back to Origin / Destination for clarity
pivot[["Origin", "Destination"]] = pivot["Route"].str.split("->", expand=True)

# Save Air Berlin route frequencies per year (only AB departures)
ab_freq = pivot[["Year", "Origin", "Destination", "Route", "AIR_BERLIN_GROUP"]].rename(
    columns={"AIR_BERLIN_GROUP": "AB_Departures"}
).sort_values(["Route", "Year"])
ab_freq.to_csv(OUTPUT_AB, index=False)

# Keep only routes that Air Berlin group ever flew (any year)
ab_routes_set = set(ab_freq["Route"].unique())

# Filter overall years for these routes and compute LH per year
lh_on_ab_routes = pivot[pivot["Route"].isin(ab_routes_set)].copy()
lh_on_ab_routes = lh_on_ab_routes[["Year", "Route", "Origin", "Destination", "LUFTHANSA_GROUP", "AIR_BERLIN_GROUP"]]
lh_on_ab_routes = lh_on_ab_routes.sort_values(["Route", "Year"])

# ============================================================================
# YEAR-OVER-YEAR CHANGE CALCULATION
# ============================================================================

def compute_yoy(df_group):
    """
    Compute year-over-year changes in Lufthansa departures for a single route.

    Args:
        df_group (DataFrame): Route-specific data sorted by year

    Returns:
        DataFrame: Enhanced with YoY metrics (LH_Delta, LH_Pct_Change)

    Metrics Calculated:
        - LH_Departures: Lufthansa Group departures in current year
        - LH_Delta: Change from previous year (raw departures)
        - LH_Pct_Change: Percentage change from previous year

    Business Interpretation:
        - Positive LH_Delta during AB decline → Lufthansa filling gap
        - Large LH_Pct_Change → Rapid market expansion (red flag for concentration)
        - LH_Delta > AB departure loss → Overcompensation (market growth or substitution)
    """
    # Sort chronologically for time series calculations
    df_group = df_group.sort_values("Year").copy()

    # Extract Lufthansa departures
    df_group["LH_Departures"] = df_group["LUFTHANSA_GROUP"]

    # Calculate year-over-year absolute change
    df_group["LH_Delta"] = df_group["LH_Departures"].diff().fillna(pd.NA)

    # Calculate year-over-year percentage change
    # Handle division by zero (previous year = 0) → result is NA
    prev = df_group["LH_Departures"].shift(1)
    pct = (df_group["LH_Departures"] - prev) / prev.replace({0: pd.NA}) * 100
    df_group["LH_Pct_Change"] = pd.to_numeric(pct, errors='coerce').round(2)

    # Include AB departures for comparative context
    df_group = df_group[["Year", "Origin", "Destination", "Route", "AIR_BERLIN_GROUP", "LH_Departures", "LH_Delta", "LH_Pct_Change"]]
    df_group = df_group.rename(columns={"AIR_BERLIN_GROUP": "AB_Departures"})

    return df_group

# ============================================================================
# OUTPUT GENERATION
# ============================================================================

# Process each route to compute year-over-year changes
result_list = []
for route, g in lh_on_ab_routes.groupby("Route", sort=True):
    # Remove rows with missing Year values
    gg = g[g["Year"].notna()].copy()

    # Convert Year to integer for proper chronological sorting
    gg["Year"] = gg["Year"].astype(int)

    # Compute YoY metrics for this route
    gg = compute_yoy(gg)
    result_list.append(gg)

# Combine all routes into single output DataFrame
if result_list:
    final = pd.concat(result_list, ignore_index=True).sort_values(["Route", "Year"])
else:
    # Handle edge case: no Air Berlin routes found
    final = pd.DataFrame(columns=["Year","Origin","Destination","Route","AB_Departures","LH_Departures","LH_Delta","LH_Pct_Change"])

# ============================================================================
# SAVE RESULTS
# ============================================================================

# Save detailed Lufthansa expansion analysis
final.to_csv(OUTPUT_LH, index=False)

# Output file paths and summary
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE - LUFTHANSA EXPANSION INTO AIR BERLIN ROUTES")
print("=" * 80)
print("\nSaved:")
print(f" - Air Berlin route frequencies per year -> {OUTPUT_AB.resolve()}")
print(f" - Lufthansa on AB routes with year-over-year change -> {OUTPUT_LH.resolve()}\n")

print("Route Analysis Notes:")
print("- Routes include both airport-to-airport and airport-to-region combinations")
print("- Examples: 'DUS->WESTERN EUROPE', 'WESTERN EUROPE->MUC', 'DUS->FRA'")
print("- GULF and MIDDLE EAST consolidated to 'GULF & MIDDLE EAST'")
print("\nKey Output Columns:")
print("- LH_Delta: Year-over-year change in Lufthansa departures")
print("- LH_Pct_Change: Percentage change (highlights rapid expansion)")
print("- AB_Departures: Air Berlin capacity for comparison")
print("\n" + "=" * 80)
