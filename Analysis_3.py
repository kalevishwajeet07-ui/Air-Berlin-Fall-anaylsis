#!/usr/bin/env python3
"""
===============================================================================
ANALYSIS 3: AIRPORT-LEVEL HHI (HERFINDAHL-HIRSCHMAN INDEX) CALCULATION
===============================================================================

Goal:
    Calculate the Herfindahl-Hirschman Index (HHI) for each German airport
    across multiple seasons to measure market concentration and competitive
    dynamics following the Air Berlin collapse.

Business Context:
    The HHI is a widely-used antitrust metric that quantifies market
    concentration. Following Air Berlin's insolvency in August 2017, this
    analysis examines whether Lufthansa Group consolidated excessive market
    power at German airports, potentially creating monopolistic conditions.

HHI Formula:
    HHI = Σ(Market Share_i)²
    where Market Share is expressed as a percentage (0-100)

    Example: If three airlines have shares of 50%, 30%, and 20%:
    HHI = 50² + 30² + 20² = 2500 + 900 + 400 = 3,800 (Highly Concentrated)

HHI Interpretation:
    - Below 1,500: Unconcentrated (Competitive) Market
      → Healthy competition among multiple carriers
    - 1,500 to 2,500: Moderately Concentrated Market
      → Some concentration, potential antitrust concerns
    - Above 2,500: Highly Concentrated Market
      → Significant market power, likely anticompetitive
    - Maximum: 10,000 (Pure Monopoly - Single firm with 100% market share)
    - Minimum: Approaching 0 (Perfect competition - Many firms with tiny shares)

Output Files:
    - Result3/<AIRPORT>_HHI_Analysis.csv
      → Per-airport breakdown with group market shares and seasonal HHI values
    - Result3/HHI_Summary_All_Airports.csv
      → Comprehensive summary across all airports and seasons
    - Result3/Airport_HHI_Comparison.csv
      → High-level comparison of average HHI by airport with trend analysis

Methodology:
    1. For each airport and season, aggregate market shares by airline group
    2. Calculate HHI by summing the squared market shares
    3. Classify market concentration level based on HHI thresholds
    4. Analyze trends over time to identify increasing/decreasing concentration
    5. Generate detailed reports with metadata and interpretation

Key Insights:
    - Track Lufthansa Group's market dominance post-Air Berlin
    - Identify airports where competition deteriorated
    - Assess effectiveness of slot redistribution policies
    - Detect potential antitrust violations

===============================================================================
"""

import os
import re
import pandas as pd
from datetime import datetime

# ============================================================================
# AIRLINE GROUP DEFINITIONS
# ============================================================================
# These groups classify airlines operating in German airports during 2015-2019.
# Market concentration analysis requires accurate grouping to assess competitive
# dynamics between incumbent carriers and new entrants.

# Lufthansa Group: Germany's flag carrier and its subsidiaries
# Post-Air Berlin collapse, this group's market share expansion is a key focus
LUFTHANSA_GROUP = [
    {"airlineName": "Deutsche Lufthansa AG", "iataCode": "LH"},
    {"airlineName": "SunExpress Deutschland GmbH", "iataCode": "XG"},
    {"airlineName": "SunExpress", "iataCode": "XQ"},
    {"airlineName": "Austrian Airlines AG dba Austrian", "iataCode": "OS"},
    {"airlineName": "Swiss International Air Lines Ltd", "iataCode": "LX"},
    {"airlineName": "Brussels Airlines", "iataCode": "SN"},
    {"airlineName": "Eurowings GmbH", "iataCode": "EW"},
    {"airlineName": "Edelweiss Air AG", "iataCode": "WK"},
    {"airlineName": "Germanwings GmbH", "iataCode": "4U"},
    {"airlineName": "Lufthansa CityLine Gmbh", "iataCode": "CL"},
    {"airlineName": "Air Dolomiti S.p.A. Aeree Regionali Europee", "iataCode": "EN"},
    {"airlineName": "Swiss Global Air Lines AG", "iataCode": "LZ"},
    {"airlineName": "Eurowings Europe GmbH", "iataCode": "E2"},
]

# Air Berlin Group: Germany's second-largest airline group before insolvency
# Filed for bankruptcy in August 2017, ceased operations October 2017
# Tracking their market share decline is central to understanding HHI changes
AIR_BERLIN_GROUP = [
    {"airlineName": "Air Berlin Aviation Gmbh", "iataCode": "AB"},
    {"airlineName": "Air Berlin Aviation Gmbh", "iataCode": "H3"},
    {"airlineName": "NL LUFTFAHRT GMBH", "iataCode": "HG*"},
    {"airlineName": "LGW - Luftfahrtgesellschaft Walter GmbH", "iataCode": "HE"},
    {"airlineName": "LAUDAMOTION GMBH", "iataCode": "OE"}
]

# Low-Cost Carriers: Budget airlines competing in European markets
# These carriers' ability to fill Air Berlin's capacity gap affects HHI
LowCostCarrier_GROUP = [
    {"airlineName":"Jet2.com Limited", "iataCode": "LS"},
    {"airlineName":"Norwegian Air Shuttle A.S", "iataCode": "DY"},
    {"airlineName":"Pegasus Hava Tasimaciligi A.S.", "iataCode": "PC"},
    {"airlineName":"Ryanair Ltd.", "iataCode": "FR"},
    {"airlineName":"Transavia Airlines", "iataCode": "HV"},
    {"airlineName":"Volotea, S.A.", "iataCode": "V7"},
    {"airlineName":"Vueling Airlines S.A.", "iataCode": "VY"},
    {"airlineName":"Wizz Air Hungary Ltd.", "iataCode": "W6"},
    {"airlineName":"Easyjet Airline Company Limited", "iataCode": "U2"},
    {"airlineName":"Easyjet Austria", "iataCode": "EJU"},
    {"airlineName":"EASYJET SWITZERLAND", "iataCode": "EZS"},
    {"airlineName":"EASYJET UK", "iataCode": "EZY"},
    {"airlineName":"Blue Air Aviation", "iataCode": "SA"},
    {"airlineName":"Turistik Hava Tasimacilik A.S. (Corendon Airlines)", "iataCode": "XC"},
    {"airlineName":"Condor Flugdienst GmbH", "iataCode": "DE"},
    {"airlineName":"Flybe Limited", "iataCode": "BE"},
    {"airlineName":"Cobaltair Ltd", "iataCode": "CO"},
    {"airlineName":"Easyjet Switzerland S.A.", "iataCode": "DS"},
    {"airlineName":"Germania Fluggessellschaft mbH", "iataCode": "ST"},
    {"airlineName":"Helvetic Airways AG", "iataCode": "2L"},
    {"airlineName":"Onur Air Tasimacilik A.S", "iataCode": "8Q"},
    {"airlineName":"Smartwings a.s.", "iataCode": "QS"},
    {"airlineName":"Transavia France", "iataCode": "TO"},
    {"airlineName":"TUI Airlines Belgium N.V", "iataCode": "TB"},
    {"airlineName":"TUIfly GmbH", "iataCode": "X3"},
    {"airlineName":"Ellinair S.A", "iataCode": "EL"}
]

# Legacy Carriers: Traditional full-service European airlines
# Established carriers with comprehensive route networks
legacy_group = [
    {"iataCode":"KF", "airlineName":"Air Belgium SA"},
    {"iataCode":"SK", "airlineName":"Scandinavian Airlines System"},
    {"iataCode":"IG", "airlineName":"Air Italy S.p.A dba Air Italy S.p.A."},
    {"iataCode":"FB", "airlineName":"Bulgaria Air"},
    {"iataCode":"OU", "airlineName":"Croatia Airlines"},
    {"iataCode":"LG", "airlineName":"Luxair"},
    {"iataCode":"KM", "airlineName":"Air Malta p.l.c."},
    {"iataCode":"SU", "airlineName":"PJSC Aeroflot"},
    {"iataCode":"A3", "airlineName":"Aegean Airlines S.A."},
    {"iataCode":"BT", "airlineName":"Air Baltic Corporation AS"},
    {"iataCode":"JP", "airlineName":"Adria Airways d.o.o."},
    {"iataCode":"FI", "airlineName":"Icelandair"},
    {"iataCode":"JU", "airlineName":"JSC for Air Traffic-Air SERBIA Belgrade t/a Air Serbia a.d. Beograd"},
    {"iataCode":"PS", "airlineName":"Private Stock Company Ukraine International Airlines"},
    {"iataCode":"TK", "airlineName":"Turkish Airlines Inc."},
    {"iataCode":"KL", "airlineName": "KLM Royal Dutch Airlines"},
    {"iataCode":"LO", "airlineName": "LOT  Polish Airlines"},
    {"iataCode":"TP", "airlineName": "TAP Portugal"},
    {"iataCode":"EI", "airlineName": "Aer Lingus Limited"},
    {"iataCode":"AF", "airlineName": "Air France"},
    {"iataCode":"AZ", "airlineName": "Alitalia - Societa Aerea Italiana S.p.A"},
    {"iataCode":"BA", "airlineName": "British Airways p.l.c."},
    {"iataCode":"AY", "airlineName":"Finnair Oyj"},
    {"iataCode":"OK", "airlineName":"Czech Airlines a.s., CSA"},
    {"iataCode":"RO", "airlineName":"Compania Nationala de Transporturi Aeriene Romane TAROM S.A."},
    {"iataCode":"IB", "airlineName":"Iberia Lineas Aereas de Espana Sociedad Anonima Operadora"},
]

# Regional and Other carriers: Smaller airlines and charter operators
regional_and_others = [
    {"iataCode":"MT", "airlineName":"Thomas Cook Airlines"},
    {"iataCode":"BY", "airlineName":"TUI Airways"},
    {"iataCode":"LM", "airlineName":"Loganair"},
    {"iataCode":"WF", "airlineName":"Widerøe"},
    {"iataCode":"H6", "airlineName":"European Air Charter"},
    {"iataCode":"NT", "airlineName":"Binter Canarias"},
]

# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================

# Focus airports: Major German coordinated airports analyzed in this study
# DUS: Düsseldorf, FRA: Frankfurt, HAM: Hamburg, MUC: Munich
# STR: Stuttgart, SXF: Berlin-Schönefeld, TXL: Berlin-Tegel
AIRPORT_CODES = ["DUS", "FRA", "HAM", "MUC", "STR", "SXF", "TXL"]

# Analysis periods: Summer seasons from 2015 to 2019
# Air Berlin collapse occurred between S17 (Summer 2017) and S18 (Summer 2018)
SEASONS = ["S15", "S16", "S17", "S18", "S19"]

# Human-readable season names for output formatting
SEASON_NAMES = {
    "S15": "Summer 2015",
    "S16": "Summer 2016",
    "S17": "Summer 2017",
    "S18": "Summer 2018",
    "S19": "Summer 2019"
}

# Input directory containing slot allocation data with market share percentages
SLOTS_DIR = "slots"

# Output directory for HHI analysis results
OUTPUT_DIR = "Result3"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_iata_codes_from_group(group):
    """
    Extract IATA codes from an airline group definition.

    Args:
        group (list): List of airline dictionaries with 'iataCode' or 'iata' field

    Returns:
        list: IATA codes (uppercase, stripped) for all airlines in the group

    Note:
        Normalizes codes to uppercase for consistent matching across datasets.
    """
    codes = []
    for e in group:
        code = e.get("iataCode") or e.get("iata")
        if code:
            codes.append(str(code).strip().upper())
    return codes


def parse_percent(s):
    """
    Parse percentage value from string, handling various formats.

    Args:
        s: Value to parse (can be string, numeric, or NA)

    Returns:
        float: Parsed percentage value, defaults to 0.0 for invalid inputs

    Handles:
        - Percentage signs (e.g., "45.5%")
        - Comma decimal separators (European format)
        - Whitespace and empty strings
        - Negative values
        - NA/None values
    """
    if s is None:
        return 0.0
    s = str(s).strip()
    if s == "":
        return 0.0
    
    # Remove percentage sign and handle comma decimals
    s = s.replace("%", "").replace(",", "")
    
    # Extract numeric value
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    if not match:
        return 0.0
    
    try:
        return float(match.group(0))
    except Exception:
        return 0.0


def get_market_classification(hhi):
    """
    Classify market concentration based on HHI value using DOJ/FTC guidelines.

    Args:
        hhi (float): Herfindahl-Hirschman Index value

    Returns:
        str: Market classification category

    Classification Guidelines (US DOJ/FTC):
        - HHI < 1,500: Unconcentrated (competitive market)
        - 1,500 ≤ HHI ≤ 2,500: Moderately concentrated
        - HHI > 2,500: Highly concentrated (antitrust concerns)
    """
    if hhi < 1500:
        return "Unconcentrated (Competitive)"
    elif hhi <= 2500:
        return "Moderately Concentrated"
    else:
        return "Highly Concentrated"


def get_market_trend(hhi_values):
    """
    Analyze trend in HHI over time to identify concentration patterns.

    Args:
        hhi_values (list): List of HHI values ordered chronologically

    Returns:
        str: Trend description with percentage change

    Methodology:
        Compares average HHI in first half of period vs. second half.
        - Stable: Change < 5%
        - Increasing: Significant upward trend (market consolidation)
        - Decreasing: Significant downward trend (market fragmentation)

    Business Context:
        Rising HHI post-Air Berlin suggests Lufthansa consolidation.
        Falling HHI would indicate successful new entrant competition.
    """
    if len(hhi_values) < 2:
        return "Insufficient data"
    
    first_half_avg = sum(hhi_values[:len(hhi_values)//2]) / (len(hhi_values)//2)
    second_half_avg = sum(hhi_values[len(hhi_values)//2:]) / (len(hhi_values) - len(hhi_values)//2)
    
    change = second_half_avg - first_half_avg
    pct_change = (change / first_half_avg * 100) if first_half_avg > 0 else 0
    
    if abs(pct_change) < 5:
        return f"Stable (±{abs(pct_change):.1f}%)"
    elif change > 0:
        return f"Increasing Concentration (+{pct_change:.1f}%)"
    else:
        return f"Decreasing Concentration ({pct_change:.1f}%)"


def read_new_entrants_for_airport(airport_code):
    """
    Read new entrant airlines for a specific airport from CSV file.

    Args:
        airport_code (str): Three-letter airport IATA code

    Returns:
        list: IATA codes of new entrant airlines for this airport

    Note:
        New entrants are airlines that entered the market after Air Berlin's
        collapse, potentially filling the capacity gap left behind. Their
        market participation affects HHI calculations.

    File Format:
        Expected file: {airport_code}_NEW_ENTRANT.csv with airline code column
    """
    fname = os.path.join(SLOTS_DIR, f"{airport_code}_NEW_ENTRANT.csv")
    if not os.path.isfile(fname):
        return []
    
    try:
        df = pd.read_csv(fname, dtype=str)
    except Exception:
        return []
    
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Find the airline code column
    col = None
    for candidate in ("AIRLINE_CODE", "AIRLINE", "IATA", "AIRLINECODE"):
        if candidate in df.columns:
            col = candidate
            break
    
    if col is None:
        if len(df.columns) >= 2:
            col = df.columns[1]
        else:
            return []
    
    codes = df[col].dropna().astype(str).str.strip().str.upper().tolist()
    return [c for c in codes if c]


# ============================================================================
# MAIN HHI COMPUTATION FUNCTION
# ============================================================================

def compute_hhi():
    """
    Main function to compute HHI for all airports and seasons.

    Process:
        1. Initialize airline groups and track all existing codes
        2. For each airport:
           a. Load slot allocation data with market share percentages
           b. Read airport-specific new entrants
           c. Aggregate market shares by airline group and season
           d. Calculate HHI for each season (sum of squared market shares)
           e. Classify market concentration level
           f. Generate detailed breakdown CSV
        3. Create comprehensive summary across all airports
        4. Generate comparison report with trends

    Returns:
        str: Path to combined HHI summary file

    Output Structure:
        Per-airport files include:
        - Market share breakdown by group and season
        - HHI values with interpretations
        - Metadata and generation timestamp

    HHI Calculation:
        For each season: HHI = Σ(market_share²) for all airline groups
        Market shares are aggregated percentages (0-100 scale)
    """
    
    print("=" * 80)
    print("HHI ANALYSIS - POST AIR BERLIN COLLAPSE")
    print("Market Concentration Analysis for German Airports")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize airline groups with descriptive names
    # These groups represent different competitive segments in the German aviation market
    groups = {
        "Lufthansa Group": get_iata_codes_from_group(LUFTHANSA_GROUP),
        "Air Berlin Group": get_iata_codes_from_group(AIR_BERLIN_GROUP),
        "Low Cost Carriers": get_iata_codes_from_group(LowCostCarrier_GROUP),
        "Legacy Carriers": get_iata_codes_from_group(legacy_group),
        "Regional & Others": get_iata_codes_from_group(regional_and_others),
    }

    # Track all existing airline codes to prevent duplicate classification
    # This ensures new entrants are only counted if they're truly new
    existing_codes_set = set()
    for lst in groups.values():
        for c in lst:
            existing_codes_set.add(c.upper())

    # Data structures for output generation
    combined_rows = []        # All airport-season HHI values
    diagnostics = []          # Processing log messages
    airport_summaries = []    # High-level airport statistics

    # Process each airport individually
    for airport in AIRPORT_CODES:
        print(f"\nProcessing {airport}...")
        
        airport_file = os.path.join(SLOTS_DIR, f"{airport}.csv")
        if not os.path.isfile(airport_file):
            diagnostics.append(f"⚠ Missing airport file: {airport_file}")
            print(f"  ⚠ Missing data file")
            continue

        try:
            df_air = pd.read_csv(airport_file, dtype=str)
        except Exception as e:
            diagnostics.append(f"⚠ Error reading {airport_file}: {e}")
            print(f"  ⚠ Error reading file: {e}")
            continue

        # Identify airline code column
        df_air.columns = [c.strip() for c in df_air.columns]
        code_col = None
        for c in df_air.columns:
            if c.strip().lower() in ("airline code", "airlinecode", "iata", "code"):
                code_col = c
                break
        if code_col is None:
            code_col = df_air.columns[0]

        df_air[code_col] = df_air[code_col].astype(str).str.strip()
        
        # Create airline lookup
        airline_map = {}
        for _, r in df_air.iterrows():
            key = str(r.get(code_col, "")).strip().upper()
            if key:
                airline_map[key] = r

        # Process new entrants
        ne_codes_raw = read_new_entrants_for_airport(airport)
        new_entrants_codes = []
        for code in ne_codes_raw:
            if code and code.upper() not in existing_codes_set:
                new_entrants_codes.append(code.upper())

        # Create local groups including new entrants
        groups_local = {k: list(v) for k, v in groups.items()}
        if new_entrants_codes:
            groups_local["New Entrants"] = new_entrants_codes

        # Calculate market shares by airline group for each season
        # This data will be used both for output display and HHI calculation
        breakdown = {"Airline Group": []}
        for s in SEASONS:
            breakdown[SEASON_NAMES[s]] = []

        # Track group-level percentages for HHI computation
        group_pct_by_season = {s: {} for s in SEASONS}

        # Aggregate market shares by summing individual airline shares within each group
        for group_name, codes in groups_local.items():
            sums = {s: 0.0 for s in SEASONS}
            
            for code in codes:
                code_u = str(code).strip().upper()
                row = airline_map.get(code_u)
                
                if row is None:
                    continue
                
                for s in SEASONS:
                    share_val = None
                    # Try different column name patterns
                    candidates = [f"Share_{s}", f"Share {s}", s, f"Share_{s}%"]
                    for cand in candidates:
                        if cand in df_air.columns:
                            share_val = row.get(cand)
                            break
                    
                    if share_val is None:
                        for colname in df_air.columns:
                            if s in colname.upper() and "SHARE" in colname.upper():
                                share_val = row.get(colname)
                                break
                    
                    pct = parse_percent(share_val)
                    sums[s] += pct
            
            breakdown["Airline Group"].append(group_name)
            for s in SEASONS:
                breakdown[SEASON_NAMES[s]].append(round(sums[s], 2))
                group_pct_by_season[s][group_name] = sums[s]

        # Calculate HHI for each season using the formula: HHI = Σ(market_share²)
        # HHI measures market concentration on a scale of 0-10,000
        # Higher values indicate greater concentration (less competition)
        hhi_by_season = {}
        for s in SEASONS:
            total_hhi = 0.0
            # Sum the squared market shares across all airline groups
            for gname, pctsum in group_pct_by_season[s].items():
                total_hhi += (pctsum ** 2)  # Square each group's market share
            hhi_by_season[s] = round(total_hhi, 4)
            
            combined_rows.append({
                "Airport": airport,
                "Season": s,
                "Season Name": SEASON_NAMES[s],
                "HHI": round(total_hhi, 4),
                "Market Classification": get_market_classification(total_hhi)
            })

        # Create detailed breakdown DataFrame
        df_break = pd.DataFrame(breakdown).set_index("Airline Group")
        
        # Add separator row
        separator_row = pd.DataFrame({season: ["---"] for season in SEASON_NAMES.values()}, 
                                    index=[""])
        
        # Add HHI row
        hhi_row = pd.DataFrame({
            SEASON_NAMES[s]: [hhi_by_season[s]] for s in SEASONS
        }, index=["HHI (Market Concentration Index)"])
        
        # Add classification row
        classification_row = pd.DataFrame({
            SEASON_NAMES[s]: [get_market_classification(hhi_by_season[s])] for s in SEASONS
        }, index=["Market Classification"])
        
        # Combine all sections
        df_out = pd.concat([df_break, separator_row, hhi_row, classification_row])
        
        # Add metadata header
        metadata = {
            "Airline Group": [
                f"HHI ANALYSIS FOR {airport}",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "Market Share by Airline Group (%):",
                ""
            ]
        }
        for season in SEASON_NAMES.values():
            metadata[season] = ["", "", "", "", ""]
        
        df_metadata = pd.DataFrame(metadata).set_index("Airline Group")
        df_out = pd.concat([df_metadata, df_out])
        
        # Save airport breakdown
        out_path = os.path.join(OUTPUT_DIR, f"{airport}_HHI_Analysis.csv")
        df_out.to_csv(out_path)
        
        # Track trend
        hhi_vals = [hhi_by_season[s] for s in SEASONS]
        trend = get_market_trend(hhi_vals)
        
        airport_summaries.append({
            "Airport": airport,
            "Avg HHI": round(sum(hhi_vals) / len(hhi_vals), 2),
            "Min HHI": min(hhi_vals),
            "Max HHI": max(hhi_vals),
            "Trend": trend
        })
        
        diagnostics.append(f"✓ Wrote detailed analysis for {airport} -> {out_path}")
        print(f"  ✓ HHI Range: {min(hhi_vals):.2f} - {max(hhi_vals):.2f}")
        print(f"  ✓ Trend: {trend}")

    # Create comprehensive summary file
    print("\n" + "=" * 80)
    print("Creating comprehensive summary...")
    
    df_combined = pd.DataFrame(combined_rows)
    
    # Add analysis header
    header_data = {
        "Airport": [
            "COMPREHENSIVE HHI ANALYSIS - GERMAN AIRPORTS",
            "Post Air Berlin Collapse Market Concentration Study",
            "",
            "HHI INTERPRETATION GUIDE:",
            "Below 1,500 = Unconcentrated (Competitive) Market",
            "1,500 to 2,500 = Moderately Concentrated Market", 
            "Above 2,500 = Highly Concentrated Market",
            "Maximum = 10,000 (Monopoly)",
            "",
            "SEASONAL DATA:",
            ""
        ],
        "Season": [""] * 11,
        "Season Name": [""] * 11,
        "HHI": [""] * 11,
        "Market Classification": [""] * 11
    }
    
    df_header = pd.DataFrame(header_data)
    df_combined_with_header = pd.concat([df_header, df_combined], ignore_index=True)
    
    combined_path = os.path.join(OUTPUT_DIR, "HHI_Summary_All_Airports.csv")
    df_combined_with_header.to_csv(combined_path, index=False)
    diagnostics.append(f"✓ Wrote comprehensive summary -> {combined_path}")

    # Create airport comparison summary
    df_summary = pd.DataFrame(airport_summaries)
    summary_path = os.path.join(OUTPUT_DIR, "Airport_HHI_Comparison.csv")
    
    summary_header = {
        "Airport": [
            "AIRPORT COMPARISON - HHI SUMMARY",
            "Average Market Concentration Across All Seasons",
            ""
        ],
        "Avg HHI": [""] * 3,
        "Min HHI": [""] * 3,
        "Max HHI": [""] * 3,
        "Trend": [""] * 3
    }
    
    df_summary_header = pd.DataFrame(summary_header)
    df_summary_with_header = pd.concat([df_summary_header, df_summary], ignore_index=True)
    df_summary_with_header.to_csv(summary_path, index=False)
    diagnostics.append(f"✓ Wrote airport comparison -> {summary_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nFiles Generated:")
    for d in diagnostics:
        print(f"  {d}")
    
    print("\n" + "=" * 80)
    print("MARKET INSIGHTS:")
    print("=" * 80)
    for summary in airport_summaries:
        classification = get_market_classification(summary["Avg HHI"])
        print(f"\n{summary['Airport']}:")
        print(f"  Average HHI: {summary['Avg HHI']} ({classification})")
        print(f"  Range: {summary['Min HHI']} - {summary['Max HHI']}")
        print(f"  Trend: {summary['Trend']}")
    
    print("\n" + "=" * 80)
    
    return combined_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    compute_hhi()