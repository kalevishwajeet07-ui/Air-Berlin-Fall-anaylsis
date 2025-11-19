"""
===============================================================================
ANALYSIS 4: ROUTE-LEVEL HHI ANALYSIS FOR FOCUSED AIRPORTS AND REGIONS
===============================================================================

Goal:
    Calculate route-specific Herfindahl-Hirschman Index (HHI) values for
    connections between focused German airports and key destination regions
    to identify where Lufthansa Group consolidated market power after the
    Air Berlin collapse.

Business Context:
    While Analysis 3 examines overall airport concentration, this analysis
    drills down to the route level to identify specific market segments where
    competition deteriorated. Air Berlin operated significant capacity on
    routes to Western Europe, Eastern Europe, North Africa, and Gulf/Middle
    East regions. Understanding which routes became monopolized vs. which
    remained competitive reveals the strategic impact of the collapse.

Route-Level Analysis Rationale:
    Airport-wide HHI can mask route-specific monopolization. An airport may
    appear moderately concentrated overall, but individual routes could be
    highly concentrated. Route-level HHI provides granular insights into
    where Lufthansa Group achieved dominance and where LCCs maintained
    competitive pressure.

HHI Calculation (Route-Specific):
    For each origin airport → destination region route:
    HHI = Σ(Market Share_i)² × 10,000
    where Market Share = (Group Departures / Total Route Departures)

Focused Airports:
    DUS: Düsseldorf, FRA: Frankfurt, HAM: Hamburg, MUC: Munich
    STR: Stuttgart, SXF: Berlin-Schönefeld, TXL: Berlin-Tegel

Focused Regions:
    - Western Europe: Core European markets (major competitive battleground)
    - Eastern Europe: Growing markets with legacy carrier competition
    - North Africa: Leisure and diaspora traffic (Air Berlin stronghold)
    - Gulf/Middle East: Premium long-haul connections

Output Files:
    CSV Files:
    - Result4/hhi_results.csv
      → HHI values for each route-year combination
    - Result4/hhi_pivot_table.csv
      → HHI values in pivot format (routes × years) for easy comparison
    - Result4/detailed_market_shares.csv
      → Market share breakdown by airline group for each route-year
    - Result4/market_shares_by_group.csv
      → Raw market share data with departure counts

    Visualizations:
    - Result4/hhi_trends_all_routes.png
      → Grid visualization of HHI trends for all route combinations
    - Result4/hhi_trends_<AIRPORT>.png
      → Individual trend charts for each origin airport (7 files)
    - Result4/hhi_contribution_<ROUTE>.png
      → Stacked bar charts showing each group's contribution to HHI (~35 files)
    - Result4/hhi_contribution_summary_all_routes.png
      → Average HHI contribution by airline group
    - Result4/hhi_contribution_by_year.png
      → Year-over-year trends in group contributions
    - Result4/hhi_contribution_by_airport.png
      → Airport comparison of group market power
    - Result4/hhi_contribution_by_region.png
      → Regional analysis of competitive dynamics

Methodology:
    1. Load schedule data and filter for summer months (April-October)
    2. Classify airlines into groups (Lufthansa, Air Berlin, LCC, Legacy, etc.)
    3. Handle new entrants with airport-specific logic (avoid double-counting)
    4. Normalize Gulf/Middle East regions into single category
    5. For each route-year: aggregate departures by group, calculate shares
    6. Compute HHI and generate comprehensive visualizations

Key Metrics:
    - HHI < 1,500: Competitive route (multiple strong competitors)
    - 1,500-2,500: Moderately concentrated route
    - HHI > 2,500: Highly concentrated route (potential monopoly concern)
    - HHI > 5,000: Near-monopoly (single carrier dominance)

===============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# AIRLINE GROUP DEFINITIONS
# ============================================================================
# Airline classifications for route-level competitive analysis
# Accurate grouping is critical for measuring market concentration

# Lufthansa Group: Dominant German carrier and subsidiaries
# Key thesis: This group expanded significantly into Air Berlin routes
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

# Air Berlin Group: Former second-largest German carrier (bankrupt Aug 2017)
# Tracking their disappearance reveals which routes became monopolized
AIR_BERLIN_GROUP = [
    {"airlineName": "Air Berlin Aviation Gmbh", "iataCode": "AB"},
    {"airlineName": "Air Berlin Aviation Gmbh", "iataCode": "H3"},
    {"airlineName": "NL LUFTFAHRT GMBH", "iataCode": "HG*"},
    {"airlineName": "LGW - Luftfahrtgesellschaft Walter GmbH", "iataCode": "HE"},
    {"airlineName": "LAUDAMOTION GMBH", "iataCode": "OE"}
]

# Low-Cost Carriers: Budget airlines that could have filled Air Berlin's gap
# LCC penetration on routes is key to assessing competitive health post-collapse
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

# Focused airports: Major German airports for route-level analysis
AIRPORT_CODES = ["DUS", "FRA", "HAM", "MUC", "STR", "SXF", "TXL"]

# Focused regions: Strategic destination markets served from German airports
# These regions represent key competitive battlegrounds post-Air Berlin
FOCUS_REGIONS = ["WESTERN EUROPE", "EASTERN EUROPE", "NORTH AFRICA", "GULF/MIDDLE EAST"]

# Summer months filter: IATA summer season (April-October)
# Ensures consistent seasonal comparison across years
SUMMER_MONTHS = [4, 5, 6, 7, 8, 9, 10]

# Analysis time period: 2015-2019 (pre- and post-Air Berlin collapse)
YEARS = [2015, 2016, 2017, 2018, 2019]

# Directory path for new entrant files
NEW_ENTRANT_DIR = "/mnt/user-data/uploads/slots"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_new_entrants(new_entrant_dir):
    """
    Load new entrant airlines for each airport from CSV files.

    Args:
        new_entrant_dir (str): Directory containing <AIRPORT>_NEW_ENTRANT.csv files

    Returns:
        dict: {airport_code: [list of new entrant IATA codes]}

    Business Context:
        New entrants represent airlines that entered German markets after Air
        Berlin's collapse. Their presence indicates whether slots were distributed
        to promote competition or consolidated by incumbents (primarily Lufthansa).
        Airport-specific tracking prevents double-counting across analyses.
    """
    new_entrants = {}
    
    for airport in AIRPORT_CODES:
        filepath = Path(new_entrant_dir) / f"{airport}_NEW_ENTRANT.csv"
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                # Extract airline codes for this airport
                airline_codes = df['AIRLINE_CODE'].unique().tolist()
                new_entrants[airport] = airline_codes
                print(f"Loaded {len(airline_codes)} new entrant airlines for {airport}")
            except Exception as e:
                print(f"Warning: Could not load new entrants for {airport}: {e}")
                new_entrants[airport] = []
        else:
            print(f"Warning: New entrant file not found for {airport}: {filepath}")
            new_entrants[airport] = []
    
    return new_entrants


def create_airline_mapping(new_entrants):
    """
    Create a mapping of airline IATA codes to their group names with conflict resolution.

    Args:
        new_entrants (dict): Airport-specific new entrant airline codes

    Returns:
        tuple: (airline_to_group dict, new_entrant_mappings dict, conflicts list)
            - airline_to_group: {iata_code: group_name} for regular groups
            - new_entrant_mappings: {airport: [new entrant codes]} airport-specific
            - conflicts: List of airlines appearing in multiple groups

    Priority Logic:
        Regular groups (Lufthansa, Air Berlin, LCC, Legacy, Regional) take precedence
        over new entrant classification to prevent double-counting. This ensures
        accurate HHI calculation by avoiding inflated group counts.
    """
    airline_to_group = {}
    conflicts = []
    
    # Define groups with their names
    groups = [
        ("LUFTHANSA_GROUP", LUFTHANSA_GROUP),
        ("AIR_BERLIN_GROUP", AIR_BERLIN_GROUP),
        ("LowCostCarrier_GROUP", LowCostCarrier_GROUP),
        ("legacy_group", legacy_group),
        ("regional_and_others", regional_and_others),
    ]
    
    # First pass: add all regular groups
    for group_name, group_list in groups:
        for airline in group_list:
            iata_code = airline['iataCode']
            if iata_code in airline_to_group:
                conflicts.append({
                    'iata_code': iata_code,
                    'group1': airline_to_group[iata_code],
                    'group2': group_name
                })
            else:
                airline_to_group[iata_code] = group_name
    
    # Second pass: add new entrants (lowest priority)
    # Create airport-specific mappings for new entrants
    new_entrant_mappings = {}
    for airport, codes in new_entrants.items():
        for code in codes:
            # Check if already in a regular group
            if code in airline_to_group:
                conflicts.append({
                    'iata_code': code,
                    'airport': airport,
                    'group1': airline_to_group[code],
                    'group2': 'NEW_ENTRANT',
                    'resolution': f'Keeping {airline_to_group[code]} (NEW_ENTRANT has lowest priority)'
                })
            else:
                # Store as airport-specific new entrant
                if airport not in new_entrant_mappings:
                    new_entrant_mappings[airport] = []
                new_entrant_mappings[airport].append(code)
    
    return airline_to_group, new_entrant_mappings, conflicts


def normalize_region(region_name):
    """
    Normalize region names to handle Gulf/Middle East consolidation.

    Args:
        region_name (str): Raw region name from schedule data

    Returns:
        str: Normalized region name

    Business Logic:
        Combines "GULF" and "MIDDLE EAST" into single category "GULF/MIDDLE EAST"
        to match focused region definitions. This consolidation reflects similar
        competitive dynamics and Air Berlin's operational strategy in these markets.
    """
    if region_name in ["GULF", "MIDDLE EAST"]:
        return "GULF/MIDDLE EAST"
    return region_name


def calculate_hhi(market_shares):
    """
    Calculate Herfindahl-Hirschman Index from market shares.

    Args:
        market_shares (list): List of market shares as decimals (0.0-1.0)

    Returns:
        float: HHI value (0-10,000 scale)

    Formula:
        HHI = Σ(s_i)² × 10,000
        where s_i is each firm's market share expressed as a decimal

    Example:
        market_shares = [0.50, 0.30, 0.20]
        HHI = (0.50² + 0.30² + 0.20²) × 10,000 = (0.25 + 0.09 + 0.04) × 10,000 = 3,800
    """
    return sum(share ** 2 for share in market_shares) * 10000


def load_and_filter_schedule(schedule_path):
    """
    Load schedule data and filter for relevant periods
    """
    print(f"Loading schedule data from {schedule_path}...")
    df = pd.read_csv(schedule_path)
    
    print(f"Initial dataset size: {len(df)} rows")
    
    # Filter for summer months (April to October)
    df = df[df['Month'].isin(SUMMER_MONTHS)]
    print(f"After filtering for summer months (4-10): {len(df)} rows")
    
    # Filter for focused airports as origin
    df = df[df['Origin Airport'].isin(AIRPORT_CODES)]
    print(f"After filtering for focused airports: {len(df)} rows")
    
    # Normalize destination regions
    df['Destination Region Normalized'] = df['Destination Region Name'].apply(normalize_region)
    
    # Filter for focused regions
    df = df[df['Destination Region Normalized'].isin(FOCUS_REGIONS)]
    print(f"After filtering for focused regions: {len(df)} rows")
    
    return df


def assign_airline_groups(df, airline_to_group, new_entrant_mappings):
    """
    Assign each airline to its group
    """
    def get_group(row):
        airline_code = row['Operating Airline']
        airport = row['Origin Airport']
        
        # Check regular groups first
        if airline_code in airline_to_group:
            return airline_to_group[airline_code]
        
        # Check if it's a new entrant for this specific airport
        if airport in new_entrant_mappings and airline_code in new_entrant_mappings[airport]:
            return 'NEW_ENTRANT'
        
        # Not in any group
        return None
    
    df['Airline_Group'] = df.apply(get_group, axis=1)
    
    # Report statistics
    total_rows = len(df)
    grouped_rows = len(df[df['Airline_Group'].notna()])
    ungrouped_rows = len(df[df['Airline_Group'].isna()])
    
    print(f"\nAirline grouping statistics:")
    print(f"  Total rows: {total_rows}")
    print(f"  Grouped airlines: {grouped_rows} ({100*grouped_rows/total_rows:.1f}%)")
    print(f"  Ungrouped airlines: {ungrouped_rows} ({100*ungrouped_rows/total_rows:.1f}%)")
    
    if ungrouped_rows > 0:
        print(f"\nAirlines not in any group (will be excluded from HHI calculation):")
        ungrouped_airlines = df[df['Airline_Group'].isna()][['Operating Airline', 'Operating Airline Name']].drop_duplicates()
        for _, row in ungrouped_airlines.iterrows():
            print(f"  {row['Operating Airline']}: {row['Operating Airline Name']}")
    
    # Remove ungrouped airlines from analysis
    df = df[df['Airline_Group'].notna()]
    
    return df


def calculate_route_hhi(df):
    """
    Calculate HHI for each route-year combination
    """
    print("\nCalculating HHI for each route-year combination...")
    
    # Group by route, year, and airline group, sum departures
    grouped = df.groupby([
        'Origin Airport',
        'Destination Region Normalized',
        'Year',
        'Airline_Group'
    ])['Departures'].sum().reset_index()
    
    # Calculate total market departures for each route-year
    market_totals = grouped.groupby([
        'Origin Airport',
        'Destination Region Normalized',
        'Year'
    ])['Departures'].sum().reset_index()
    market_totals.rename(columns={'Departures': 'Total_Market_Departures'}, inplace=True)
    
    # Merge to get market shares
    grouped = grouped.merge(
        market_totals,
        on=['Origin Airport', 'Destination Region Normalized', 'Year']
    )
    
    grouped['Market_Share'] = grouped['Departures'] / grouped['Total_Market_Departures']
    grouped['Market_Share_Squared'] = grouped['Market_Share'] ** 2
    
    # Calculate HHI for each route-year
    hhi_results = grouped.groupby([
        'Origin Airport',
        'Destination Region Normalized',
        'Year'
    ])['Market_Share_Squared'].sum().reset_index()
    
    hhi_results['HHI'] = hhi_results['Market_Share_Squared'] * 10000
    hhi_results.drop('Market_Share_Squared', axis=1, inplace=True)
    
    # Add route identifier
    hhi_results['Route'] = hhi_results['Origin Airport'] + ' → ' + hhi_results['Destination Region Normalized']
    
    return hhi_results, grouped


def create_detailed_analysis(grouped_df):
    """
    Create detailed breakdown of market shares by group for each route-year
    """
    detailed = grouped_df.pivot_table(
        index=['Origin Airport', 'Destination Region Normalized', 'Year', 'Route'],
        columns='Airline_Group',
        values=['Departures', 'Market_Share'],
        fill_value=0
    )
    
    # Flatten column names
    detailed.columns = [f'{col[1]}_{col[0]}' for col in detailed.columns]
    detailed = detailed.reset_index()
    
    # Add route column if not exists
    if 'Route' not in detailed.columns:
        detailed['Route'] = detailed['Origin Airport'] + ' → ' + detailed['Destination Region Normalized']
    
    return detailed


def create_visualizations(hhi_results, output_dir):
    """
    Create visualizations of HHI trends
    """
    print("\nCreating visualizations...")
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (16, 10)
    
    # Get unique routes
    routes = hhi_results['Route'].unique()
    
    # Create a grid of subplots (7 rows x 5 columns for 35 routes)
    fig, axes = plt.subplots(7, 5, figsize=(25, 28))
    fig.suptitle('HHI Trends by Route (2015-2019)', fontsize=20, y=0.995)
    
    for idx, route in enumerate(sorted(routes)):
        row = idx // 5
        col = idx % 5
        ax = axes[row, col]
        
        route_data = hhi_results[hhi_results['Route'] == route].sort_values('Year')
        
        if len(route_data) > 0:
            ax.plot(route_data['Year'], route_data['HHI'], marker='o', linewidth=2, markersize=8)
            ax.set_title(route, fontsize=10, fontweight='bold')
            ax.set_xlabel('Year', fontsize=8)
            ax.set_ylabel('HHI', fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 10000)
            
            # Add HHI threshold lines
            ax.axhline(y=1500, color='g', linestyle='--', alpha=0.5, label='Unconcentrated')
            ax.axhline(y=2500, color='orange', linestyle='--', alpha=0.5, label='Moderate')
            
            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(route, fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/hhi_trends_all_routes.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/hhi_trends_all_routes.png")
    plt.close()
    
    # Create individual charts for each airport
    for airport in AIRPORT_CODES:
        airport_data = hhi_results[hhi_results['Origin Airport'] == airport]
        
        if len(airport_data) == 0:
            continue
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        for region in FOCUS_REGIONS:
            region_data = airport_data[airport_data['Destination Region Normalized'] == region].sort_values('Year')
            if len(region_data) > 0:
                ax.plot(region_data['Year'], region_data['HHI'], 
                       marker='o', linewidth=2, markersize=8, label=region)
        
        ax.set_title(f'HHI Trends for {airport} Routes (2015-2019)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('HHI', fontsize=12)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 10000)
        
        # Add HHI threshold lines
        ax.axhline(y=1500, color='g', linestyle='--', alpha=0.5, label='Unconcentrated (<1500)')
        ax.axhline(y=2500, color='orange', linestyle='--', alpha=0.5, label='Moderate (1500-2500)')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/hhi_trends_{airport}.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {output_dir}/hhi_trends_{airport}.png")
        plt.close()


def create_hhi_contribution_charts(grouped_df, output_dir):
    """
    Create bar charts showing HHI contribution (Market Share²) by airline group
    """
    print("\nCreating HHI contribution bar charts...")
    
    # Get unique combinations
    routes = grouped_df['Route'].unique()
    years = sorted(grouped_df['Year'].unique())
    
    # Color mapping for airline groups
    group_colors = {
        'LUFTHANSA_GROUP': '#003366',
        'AIR_BERLIN_GROUP': '#CC0000',
        'LowCostCarrier_GROUP': '#FF9900',
        'legacy_group': '#006633',
        'regional_and_others': '#9966CC',
        'NEW_ENTRANT': '#FF6699'
    }
    
    # 1. Create bar chart for each route showing HHI contribution over years
    print("  Creating route-specific HHI contribution charts...")
    for route in sorted(routes):
        route_data = grouped_df[grouped_df['Route'] == route].copy()
        
        if len(route_data) == 0:
            continue
        
        # Pivot to get groups as columns
        pivot_data = route_data.pivot_table(
            index='Year',
            columns='Airline_Group',
            values='Market_Share_Squared',
            fill_value=0
        )
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Get colors for groups present in this route
        colors = [group_colors.get(col, '#CCCCCC') for col in pivot_data.columns]
        
        pivot_data.plot(kind='bar', stacked=True, ax=ax, color=colors, width=0.7)
        
        ax.set_title(f'HHI Contribution by Airline Group - {route}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('HHI Contribution (Market Share²)', fontsize=12)
        ax.legend(title='Airline Group', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis to show as contribution to 10000 scale
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*10000:.0f}'))
        
        plt.xticks(rotation=0)
        plt.tight_layout()
        
        # Safe filename (replace special characters)
        safe_route = route.replace('→', 'to').replace('/', '_').replace(' ', '_')
        plt.savefig(f'{output_dir}/hhi_contribution_{safe_route}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"  Saved route-specific charts to {output_dir}/hhi_contribution_*.png")
    
    # 2. Create summary chart showing average HHI contribution by group across all routes
    print("  Creating overall HHI contribution summary chart...")
    
    # Calculate average contribution by group across all routes and years
    avg_contribution = grouped_df.groupby('Airline_Group')['Market_Share_Squared'].mean().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    colors_list = [group_colors.get(group, '#CCCCCC') for group in avg_contribution.index]
    
    bars = ax.bar(range(len(avg_contribution)), avg_contribution.values * 10000, color=colors_list, width=0.6)
    ax.set_xticks(range(len(avg_contribution)))
    ax.set_xticklabels(avg_contribution.index, rotation=45, ha='right')
    ax.set_ylabel('Average HHI Contribution', fontsize=12)
    ax.set_title('Average HHI Contribution by Airline Group (All Routes, 2015-2019)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/hhi_contribution_summary_all_routes.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_dir}/hhi_contribution_summary_all_routes.png")
    
    # 3. Create comparison chart by year
    print("  Creating year-by-year HHI contribution comparison...")
    
    year_group_contribution = grouped_df.groupby(['Year', 'Airline_Group'])['Market_Share_Squared'].mean().reset_index()
    pivot_year = year_group_contribution.pivot(index='Year', columns='Airline_Group', values='Market_Share_Squared').fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = [group_colors.get(col, '#CCCCCC') for col in pivot_year.columns]
    
    pivot_year.plot(kind='bar', ax=ax, color=colors, width=0.7)
    
    ax.set_title('Average HHI Contribution by Airline Group per Year (All Routes)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Average HHI Contribution', fontsize=12)
    ax.legend(title='Airline Group', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*10000:.0f}'))
    
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/hhi_contribution_by_year.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_dir}/hhi_contribution_by_year.png")
    
    # 4. Create comparison chart by airport
    print("  Creating airport-by-airport HHI contribution comparison...")
    
    airport_group_contribution = grouped_df.groupby(['Origin Airport', 'Airline_Group'])['Market_Share_Squared'].mean().reset_index()
    pivot_airport = airport_group_contribution.pivot(index='Origin Airport', columns='Airline_Group', values='Market_Share_Squared').fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = [group_colors.get(col, '#CCCCCC') for col in pivot_airport.columns]
    
    pivot_airport.plot(kind='bar', ax=ax, color=colors, width=0.7)
    
    ax.set_title('Average HHI Contribution by Airline Group per Airport (All Years)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Airport', fontsize=12)
    ax.set_ylabel('Average HHI Contribution', fontsize=12)
    ax.legend(title='Airline Group', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*10000:.0f}'))
    
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/hhi_contribution_by_airport.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_dir}/hhi_contribution_by_airport.png")
    
    # 5. Create comparison chart by region
    print("  Creating region-by-region HHI contribution comparison...")
    
    region_group_contribution = grouped_df.groupby(['Destination Region Normalized', 'Airline_Group'])['Market_Share_Squared'].mean().reset_index()
    pivot_region = region_group_contribution.pivot(index='Destination Region Normalized', columns='Airline_Group', values='Market_Share_Squared').fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = [group_colors.get(col, '#CCCCCC') for col in pivot_region.columns]
    
    pivot_region.plot(kind='bar', ax=ax, color=colors, width=0.7)
    
    ax.set_title('Average HHI Contribution by Airline Group per Region (All Years)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Destination Region', fontsize=12)
    ax.set_ylabel('Average HHI Contribution', fontsize=12)
    ax.legend(title='Airline Group', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*10000:.0f}'))
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/hhi_contribution_by_region.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {output_dir}/hhi_contribution_by_region.png")
    
    print("\nHHI contribution charts completed!")


def generate_summary_statistics(hhi_results):
    """
    Generate summary statistics for HHI analysis
    """
    summary = {
        'Overall Statistics': {
            'Mean HHI': hhi_results['HHI'].mean(),
            'Median HHI': hhi_results['HHI'].median(),
            'Min HHI': hhi_results['HHI'].min(),
            'Max HHI': hhi_results['HHI'].max(),
            'Std Dev': hhi_results['HHI'].std()
        },
        'By Year': hhi_results.groupby('Year')['HHI'].agg(['mean', 'median', 'min', 'max']).to_dict(),
        'By Airport': hhi_results.groupby('Origin Airport')['HHI'].agg(['mean', 'median', 'count']).to_dict(),
        'By Region': hhi_results.groupby('Destination Region Normalized')['HHI'].agg(['mean', 'median', 'count']).to_dict()
    }
    
    return summary


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(schedule_path, new_entrant_dir, output_dir):
    """
    Main execution function
    """
    print("="*80)
    print("HHI MARKET CONCENTRATION ANALYSIS")
    print("="*80)
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load new entrants
    print("\n" + "="*80)
    print("STEP 1: Loading New Entrant Airlines")
    print("="*80)
    new_entrants = load_new_entrants(new_entrant_dir)
    
    # Step 2: Create airline mappings
    print("\n" + "="*80)
    print("STEP 2: Creating Airline Group Mappings")
    print("="*80)
    airline_to_group, new_entrant_mappings, conflicts = create_airline_mapping(new_entrants)
    
    if conflicts:
        print("\n⚠️  CONFLICTS DETECTED - Airlines appearing in multiple groups:")
        print("-" * 80)
        for conflict in conflicts:
            if 'resolution' in conflict:
                print(f"  {conflict['iata_code']} ({conflict.get('airport', 'N/A')}): "
                      f"{conflict['group1']} vs {conflict['group2']} → {conflict['resolution']}")
            else:
                print(f"  {conflict['iata_code']}: {conflict['group1']} vs {conflict['group2']}")
        print("-" * 80)
    
    # Step 3: Load and filter schedule data
    print("\n" + "="*80)
    print("STEP 3: Loading and Filtering Schedule Data")
    print("="*80)
    df = load_and_filter_schedule(schedule_path)
    
    # Step 4: Assign airline groups
    print("\n" + "="*80)
    print("STEP 4: Assigning Airlines to Groups")
    print("="*80)
    df = assign_airline_groups(df, airline_to_group, new_entrant_mappings)
    
    # Step 5: Calculate HHI
    print("\n" + "="*80)
    print("STEP 5: Calculating HHI")
    print("="*80)
    hhi_results, grouped_df = calculate_route_hhi(df)
    
    print(f"\nCalculated HHI for {len(hhi_results)} route-year combinations")
    print(f"Routes analyzed: {hhi_results['Route'].nunique()}")
    print(f"Years covered: {sorted(hhi_results['Year'].unique())}")
    
    # Step 6: Create detailed analysis
    print("\n" + "="*80)
    print("STEP 6: Creating Detailed Market Share Analysis")
    print("="*80)
    
    # Add Route column to grouped_df if not exists
    if 'Route' not in grouped_df.columns:
        grouped_df['Route'] = grouped_df['Origin Airport'] + ' → ' + grouped_df['Destination Region Normalized']
    
    detailed_df = create_detailed_analysis(grouped_df)
    
    # Step 7: Generate summary statistics
    print("\n" + "="*80)
    print("STEP 7: Generating Summary Statistics")
    print("="*80)
    summary_stats = generate_summary_statistics(hhi_results)
    
    print("\nOverall HHI Statistics:")
    for key, value in summary_stats['Overall Statistics'].items():
        print(f"  {key}: {value:.2f}")
    
    # Step 8: Save results
    print("\n" + "="*80)
    print("STEP 8: Saving Results")
    print("="*80)
    
    # Save HHI results
    hhi_output_path = f'{output_dir}/hhi_results.csv'
    hhi_results.to_csv(hhi_output_path, index=False)
    print(f"Saved: {hhi_output_path}")
    
    # Save detailed market share analysis
    detailed_output_path = f'{output_dir}/detailed_market_shares.csv'
    detailed_df.to_csv(detailed_output_path, index=False)
    print(f"Saved: {detailed_output_path}")
    
    # Save market share by group
    market_share_path = f'{output_dir}/market_shares_by_group.csv'
    grouped_df.to_csv(market_share_path, index=False)
    print(f"Saved: {market_share_path}")
    
    # Create pivot table for easier viewing
    pivot_hhi = hhi_results.pivot_table(
        index='Route',
        columns='Year',
        values='HHI',
        fill_value=0
    ).reset_index()
    pivot_output_path = f'{output_dir}/hhi_pivot_table.csv'
    pivot_hhi.to_csv(pivot_output_path, index=False)
    print(f"Saved: {pivot_output_path}")
    
    # Step 9: Create visualizations
    print("\n" + "="*80)
    print("STEP 9: Creating Visualizations")
    print("="*80)
    create_visualizations(hhi_results, output_dir)
    
    # Step 10: Create HHI contribution charts
    print("\n" + "="*80)
    print("STEP 10: Creating HHI Contribution Bar Charts")
    print("="*80)
    create_hhi_contribution_charts(grouped_df, output_dir)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nAll outputs saved to: {output_dir}")
    print("\nGenerated files:")
    print("  CSV Files:")
    print("    1. hhi_results.csv - HHI values for each route-year")
    print("    2. hhi_pivot_table.csv - HHI values in pivot format (routes x years)")
    print("    3. detailed_market_shares.csv - Detailed market share breakdown by group")
    print("    4. market_shares_by_group.csv - Raw market share data")
    print("\n  HHI Trend Visualizations:")
    print("    5. hhi_trends_all_routes.png - Grid visualization of all routes")
    print("    6. hhi_trends_<AIRPORT>.png - Individual charts for each airport (7 files)")
    print("\n  HHI Contribution Bar Charts:")
    print("    7. hhi_contribution_<ROUTE>.png - HHI contribution by group for each route (35 files)")
    print("    8. hhi_contribution_summary_all_routes.png - Average contribution across all routes")
    print("    9. hhi_contribution_by_year.png - Contribution by group per year")
    print("   10. hhi_contribution_by_airport.png - Contribution by group per airport")
    print("   11. hhi_contribution_by_region.png - Contribution by group per region")
    
    return hhi_results, detailed_df, summary_stats


if __name__ == "__main__":
    # Configuration
    SCHEDULE_PATH = "schedule.csv"
    NEW_ENTRANT_DIR = "slots"
    OUTPUT_DIR = "Result4"
    
    # Run analysis
    hhi_results, detailed_df, summary_stats = main(SCHEDULE_PATH, NEW_ENTRANT_DIR, OUTPUT_DIR)