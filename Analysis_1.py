#!/usr/bin/env python3
"""
===============================================================================
ANALYSIS 1: AIRPORT SLOT ALLOCATION BY AIRLINE GROUP
===============================================================================

Goal:
    Analyze how many slots each airline group holds at each German airport
    across multiple seasons (S15-S19) to understand market distribution
    following the Air Berlin collapse.

Output:
    - One CSV per airport in ./Result_1/<AIRPORT>.csv
    - Each CSV contains slot counts per airline group per season
    - Excludes PRE_SUM/POST_SUM/DIFF columns for clarity
    - New entrants are filtered per-airport and exclude codes in other groups

Business Context:
    Following Air Berlin's insolvency in 2017, this analysis tracks how airport
    slots were redistributed among various airline groups, with particular focus
    on Lufthansa Group's market position and new entrant participation.

===============================================================================
"""

import os
import re
import sys
import pandas as pd
from collections import defaultdict

# ============================================================================
# AIRLINE GROUP DEFINITIONS
# ============================================================================
# These groups classify airlines operating in German airports during 2015-2019.
# Each group represents a different business model and market strategy.

# Lufthansa Group: Germany's flag carrier and its subsidiaries
# This group consolidated market power post-Air Berlin collapse
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
AIR_BERLIN_GROUP = [
    {"airlineName": "Air Berlin Aviation Gmbh", "iataCode": "AB"},
    {"airlineName": "Air Berlin Aviation Gmbh", "iataCode": "H3"},
    {"airlineName": "NL LUFTFAHRT GMBH", "iataCode": "HG*"},
    {"airlineName": "LGW - Luftfahrtgesellschaft Walter GmbH", "iataCode": "HE"},
    {"airlineName": "LAUDAMOTION GMBH", "iataCode": "OE"}
]

# Low-Cost Carriers: Budget airlines competing in European markets
# Key competitors to legacy carriers, especially post-Air Berlin
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
    {"iataCode":"AY", "airlineName": "Finnair Oyj"},
    {"iataCode":"OK", "airlineName": "Czech Airlines a.s., CSA"},
    {"iataCode":"RO", "airlineName": "Compania Nationala de Transporturi Aeriene Romane TAROM S.A."},
    {"iataCode":"IB", "airlineName": "Iberia Lineas Aereas de Espana Sociedad Anonima Operadora"},
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

# Focus airports: Major German airports analyzed in this study
# DUS: Düsseldorf, FRA: Frankfurt, HAM: Hamburg, MUC: Munich
# STR: Stuttgart, SXF: Berlin-Schönefeld, TXL: Berlin-Tegel
AIRPORT_CODES = ["DUS", "FRA", "HAM", "MUC", "STR", "SXF", "TXL"]

# Analysis periods: Summer seasons from 2015 to 2019
# Air Berlin collapse occurred between S17 (Summer 2017) and S18 (Summer 2018)
SEASONS = ["S15", "S16", "S17", "S18", "S19"]

# Input directory containing slot allocation CSV files
SLOTS_DIR = "slots"

# Output directory for aggregated results
OUTPUT_DIR_NAME = "Result1"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_iata_codes_for_airport(group, airport_code=None):
    """
    Extract IATA codes from an airline group definition.

    Args:
        group (list): List of airline dictionaries with 'iataCode' field
        airport_code (str, optional): Filter by specific airport if specified

    Returns:
        list: IATA codes for the group, filtered by airport if provided

    Note:
        Current group data doesn't include 'airport' field, but this function
        supports it for future extensibility.
    """
    codes = []
    for entry in group:
        code = entry.get("iataCode") or entry.get("iata")
        if code:
            # Airport-specific filtering (if 'airport' field exists)
            if airport_code and "airport" in entry:
                if entry["airport"] == airport_code:
                    codes.append(code)
            else:
                # Include entries without airport field (global entries)
                if "airport" not in entry:
                    codes.append(code)
    return codes


def parse_int_departures(x):
    """
    Robustly parse numeric values from various string formats.

    Args:
        x: Value to parse (can be string, int, float, or NA)

    Returns:
        int: Parsed integer value, defaults to 0 for invalid inputs

    Handles:
        - Comma-separated numbers (e.g., "1,234")
        - Percentage signs
        - Whitespace
        - Empty strings and NA values
    """
    if pd.isna(x):
        return 0
    s = str(x).strip()
    if s == "":
        return 0

    # Extract numeric pattern with optional commas
    m = re.search(r"(-?\d{1,3}(?:[,\d]{0,15})?)", s)
    if not m:
        return 0

    # Remove commas and convert to integer
    num = m.group(1).replace(',', '')
    try:
        return int(float(num))
    except Exception:
        return 0


def read_new_entrants_for_airport(airport_code, slots_dir=SLOTS_DIR):
    """
    Read new entrant airlines for a specific airport.

    Args:
        airport_code (str): Three-letter airport IATA code
        slots_dir (str): Directory containing new entrant CSV files

    Returns:
        list: IATA codes of new entrant airlines for this airport

    Note:
        New entrants are airlines that entered the market after Air Berlin's
        collapse, potentially filling the capacity gap left behind.

    File Format:
        Expected file: {airport_code}_NEW_ENTRANT.csv with 'AIRLINE_CODE' column
    """
    fname = os.path.join(slots_dir, f"{airport_code}_NEW_ENTRANT.csv")

    if not os.path.isfile(fname):
        return []

    try:
        df = pd.read_csv(fname, dtype=str)
    except Exception:
        return []

    # Normalize column names to uppercase
    df.columns = [c.strip().upper() for c in df.columns]

    # Find the airline code column with various possible names
    if "AIRLINE_CODE" not in df.columns:
        for alt in ("AIRLINE", "AIRLINE_IATA", "IATA", "AIRLINECODE"):
            if alt in df.columns:
                df = df.rename(columns={alt: "AIRLINE_CODE"})
                break

    if "AIRLINE_CODE" not in df.columns:
        return []

    # Extract and clean airline codes
    codes = df["AIRLINE_CODE"].dropna().astype(str).str.strip().tolist()
    codes = [c for c in codes if c]
    return codes


def read_airport_csv(path):
    """
    Read airport CSV file and extract departure counts by airline and season.

    Args:
        path (str): Path to airport CSV file

    Returns:
        dict: Nested dictionary {airline_code: {season: departure_count}}

    Data Structure:
        The CSV contains one row per airline with columns for each season (S15-S19).
        This function pivots the data into a format suitable for group aggregation.
    """
    df = pd.read_csv(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # Identify the airline code column
    code_col = None
    for c in df.columns:
        if c.lower().replace(' ', '') in ("airlinecode", "iata", "airline_iata", "code"):
            code_col = c
            break

    # Default to first column if no match found
    if code_col is None:
        code_col = df.columns[0]

    # Build airline-to-seasons dictionary
    data = {}
    for _, row in df.iterrows():
        airline_code = str(row.get(code_col, "")).strip()
        if airline_code == "":
            continue

        # Extract departure counts for each season
        season_values = {}
        for s in SEASONS:
            # Try direct column match first
            if s in df.columns:
                raw = row[s]
            else:
                # Try prefix match (e.g., "S15 Departures")
                cand = None
                for c in df.columns:
                    if c.strip().upper().startswith(s.upper()):
                        cand = c
                        break
                raw = row[cand] if cand else None

            season_values[s] = parse_int_departures(raw)

        data[airline_code] = season_values

    return data


def write_csv_for_airport(airport_code, df, out_dir):
    """
    Write aggregated slot data to CSV file for a specific airport.

    Args:
        airport_code (str): Three-letter airport IATA code
        df (DataFrame): Aggregated data with groups as rows and seasons as columns
        out_dir (str): Output directory path

    Output:
        Writes CSV file to: {out_dir}/{airport_code}.csv
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{airport_code}.csv")
    df.to_csv(out_path)
    print(f"Wrote: {out_path}")

# ============================================================================
# MAIN AGGREGATION LOGIC
# ============================================================================

def aggregate_slots(airport_codes, slots_dir=SLOTS_DIR, output_dir=OUTPUT_DIR_NAME):
    """
    Main function to aggregate slot data across all airports and airline groups.

    Process:
        1. For each airport, read the slot allocation CSV
        2. Load new entrants specific to that airport
        3. Classify each airline into its appropriate group
        4. Aggregate slot counts by group and season
        5. Write results to individual airport CSV files

    Args:
        airport_codes (list): List of airport IATA codes to process
        slots_dir (str): Directory containing input slot CSV files
        output_dir (str): Directory for output CSV files

    Business Logic:
        - New entrants are filtered to exclude airlines already in other groups
        - This prevents double-counting and ensures accurate market share analysis
        - Each airport gets its own output file for detailed examination
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for airport in airport_codes:
        path = os.path.join(slots_dir, f"{airport}.csv")

        # Check if airport data file exists
        if not os.path.isfile(path):
            print(f"Warning: file not found for {airport} at {path} -- skipping")
            continue

        # Read slot data for this airport
        data = read_airport_csv(path)

        # Extract IATA codes for each airline group
        lufthansa_codes = get_iata_codes_for_airport(LUFTHANSA_GROUP, airport)
        air_berlin_codes = get_iata_codes_for_airport(AIR_BERLIN_GROUP, airport)
        lowcost_codes = get_iata_codes_for_airport(LowCostCarrier_GROUP, airport)
        legacy_codes = get_iata_codes_for_airport(legacy_group, airport)
        regional_codes = get_iata_codes_for_airport(regional_and_others, airport)

        # Build set of existing codes (case-normalized) to prevent duplicates
        existing_codes = set()
        for c in (lufthansa_codes + air_berlin_codes + lowcost_codes + legacy_codes + regional_codes):
            if c:
                existing_codes.add(str(c).strip().upper())

        # Filter new entrants: exclude airlines already in other groups
        new_entrants_raw = read_new_entrants_for_airport(airport, slots_dir)
        new_entrants_filtered = []
        for c in new_entrants_raw:
            if not c:
                continue
            cs = str(c).strip()
            if cs.upper() in existing_codes:
                continue  # Skip if already classified in another group
            new_entrants_filtered.append(cs)

        # Map group names to their airline codes
        groups_map = {
            "LUFTHANSA_GROUP": lufthansa_codes,
            "AIR_BERLIN_GROUP": air_berlin_codes,
            "LowCostCarrier_GROUP": lowcost_codes,
            "legacy_group": legacy_codes,
            "regional_and_others": regional_codes,
            "new_entrants": new_entrants_filtered,
        }

        # Aggregate departure counts by group and season
        agg = {}
        for group_name, codes in groups_map.items():
            # Initialize season sums for this group
            season_sums = {s: 0 for s in SEASONS}

            # Sum departures across all airlines in this group
            for code in codes:
                code = str(code).strip()

                # Try multiple case variations to find airline data
                row = data.get(code) or data.get(code.upper()) or data.get(code.lower())

                if row:
                    for s in SEASONS:
                        season_sums[s] += int(row.get(s, 0) or 0)

            agg[group_name] = season_sums

        # Convert aggregated data to DataFrame (groups as rows, seasons as columns)
        df = pd.DataFrame.from_dict(agg, orient='index')
        df.index.name = "GROUP"

        # Ensure correct column order
        df = df[SEASONS]

        # Write output CSV for this airport
        write_csv_for_airport(airport, df, output_dir)

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("ANALYSIS 1: AIRPORT SLOT ALLOCATION BY AIRLINE GROUP")
    print("="*80)
    print()
    print(f"Analyzing {len(AIRPORT_CODES)} airports across {len(SEASONS)} seasons...")
    print(f"Input directory: {SLOTS_DIR}")
    print(f"Output directory: {OUTPUT_DIR_NAME}")
    print()

    aggregate_slots(AIRPORT_CODES, SLOTS_DIR, OUTPUT_DIR_NAME)

    print()
    print("="*80)
    print("Analysis complete. Results written to Result1/ directory.")
    print("="*80)
