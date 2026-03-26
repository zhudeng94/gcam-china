#!/usr/bin/env python3
"""
fetch_carbon_monitor.py - Download and process Carbon Monitor CO2 emission data.

Downloads near-real-time daily CO2 emission data from Carbon Monitor
(https://carbonmonitor.org/) and processes it into formats compatible
with GCAM-China model calibration and scenario validation.

Carbon Monitor provides daily CO2 emissions by country and sector:
  - Power (electricity and heat generation)
  - Industry (industrial combustion)
  - Ground Transport (road transport)
  - Residential (buildings and heating)
  - Domestic Aviation
  - International Aviation

Usage:
    python fetch_carbon_monitor.py [--output-dir OUTPUT_DIR] [--country COUNTRY]

Output files:
    - carbon_monitor_raw.csv: Full downloaded dataset
    - carbon_monitor_China_annual.csv: China annual CO2 by sector (MtCO2)
    - carbon_monitor_China_annual_MtC.csv: China annual CO2 by sector (MtC, GCAM units)
    - carbon_monitor_global_annual.csv: Global annual CO2 by country (MtCO2)

References:
    Liu et al. (2020). "Near-real-time monitoring of global CO2 emissions
    reveals the effects of the COVID-19 pandemic." Nature Communications.
    https://doi.org/10.1038/s41467-020-18922-7
"""

import argparse
import os
import sys
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)


# Carbon Monitor API endpoint
CARBON_MONITOR_URL = (
    "https://datas.carbonmonitor.org/API/downloadFullDataset.php"
    "?source=carbon_global"
)

# Conversion factor from MtCO2 to MtC (GCAM uses MtC internally)
MTCO2_TO_MTC = 12.0 / 44.0  # ~0.2727

# Sector mapping from Carbon Monitor to GCAM sectors
SECTOR_MAPPING = {
    "Power": "electricity",
    "Industry": "industry",
    "Ground Transport": "transportation",
    "Residential": "building",
    "Domestic Aviation": "transportation",
    "International Aviation": "transportation",
}


def download_carbon_monitor(output_dir):
    """Download full Carbon Monitor dataset."""
    raw_path = os.path.join(output_dir, "carbon_monitor_raw.csv")

    print(f"Downloading Carbon Monitor data from:\n  {CARBON_MONITOR_URL}")
    print("This may take a minute...")

    try:
        response = requests.get(CARBON_MONITOR_URL, timeout=120)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading data: {e}")
        print("\nIf the download fails, you can manually download the file from:")
        print(f"  {CARBON_MONITOR_URL}")
        print(f"  Save it as: {raw_path}")
        return None

    with open(raw_path, "wb") as f:
        f.write(response.content)

    print(f"Raw data saved to: {raw_path}")
    return raw_path


def load_carbon_monitor(raw_path):
    """Load and parse the Carbon Monitor CSV data."""
    df = pd.read_csv(raw_path)

    # Carbon Monitor columns: country, date, sector, value (MtCO2 per day), timestamp
    # Standardize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename common variations
    rename_map = {}
    for col in df.columns:
        if "country" in col:
            rename_map[col] = "country"
        elif "date" in col:
            rename_map[col] = "date"
        elif "sector" in col:
            rename_map[col] = "sector"
        elif "value" in col or "emission" in col:
            rename_map[col] = "value"
    df = df.rename(columns=rename_map)

    # Parse date and extract year
    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=False)
    df["year"] = df["date"].dt.year

    # Ensure value is numeric
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


def process_china_annual(df, output_dir):
    """Process China-specific annual emissions by sector."""
    china_df = df[df["country"].str.contains("China", case=False, na=False)].copy()

    if china_df.empty:
        print("Warning: No China data found in dataset")
        return None

    # Aggregate daily to annual (sum daily MtCO2 to get annual MtCO2)
    china_annual = (
        china_df.groupby(["year", "sector"])["value"]
        .sum()
        .reset_index()
    )
    china_annual.columns = ["year", "sector", "MtCO2"]

    # Also compute total
    china_total = (
        china_df.groupby("year")["value"]
        .sum()
        .reset_index()
    )
    china_total.columns = ["year", "MtCO2"]
    china_total["sector"] = "Total"

    china_annual = pd.concat([china_annual, china_total], ignore_index=True)
    china_annual = china_annual.sort_values(["year", "sector"]).reset_index(drop=True)

    # Save in MtCO2
    path_co2 = os.path.join(output_dir, "carbon_monitor_China_annual.csv")
    header = (
        "# File: carbon_monitor_China_annual.csv\n"
        "# Title: China annual CO2 emissions by sector from Carbon Monitor\n"
        "# Units: MtCO2/yr\n"
        "# Source: https://carbonmonitor.org/ (Liu et al., 2020, Nature Communications)\n"
        "# Column types: icn\n"
        "# ----------\n"
    )
    with open(path_co2, "w") as f:
        f.write(header)
        china_annual.to_csv(f, index=False)
    print(f"China annual data (MtCO2) saved to: {path_co2}")

    # Convert to MtC (GCAM units)
    china_annual_mtc = china_annual.copy()
    china_annual_mtc["MtC"] = china_annual_mtc["MtCO2"] * MTCO2_TO_MTC
    china_annual_mtc = china_annual_mtc.drop(columns=["MtCO2"])

    # Add GCAM sector mapping
    china_annual_mtc["gcam_sector"] = (
        china_annual_mtc["sector"].map(SECTOR_MAPPING).fillna("other")
    )

    path_mtc = os.path.join(output_dir, "carbon_monitor_China_annual_MtC.csv")
    header_mtc = (
        "# File: carbon_monitor_China_annual_MtC.csv\n"
        "# Title: China annual CO2 emissions by sector from Carbon Monitor\n"
        "# Units: MtC/yr (converted from MtCO2 using factor 12/44)\n"
        "# Source: https://carbonmonitor.org/ (Liu et al., 2020, Nature Communications)\n"
        "# Column types: icnc\n"
        "# ----------\n"
    )
    with open(path_mtc, "w") as f:
        f.write(header_mtc)
        china_annual_mtc.to_csv(f, index=False)
    print(f"China annual data (MtC) saved to: {path_mtc}")

    return china_annual


def process_global_annual(df, output_dir):
    """Process global annual emissions by country."""
    global_annual = (
        df.groupby(["year", "country"])["value"]
        .sum()
        .reset_index()
    )
    global_annual.columns = ["year", "country", "MtCO2"]
    global_annual = global_annual.sort_values(["year", "country"]).reset_index(
        drop=True
    )

    path = os.path.join(output_dir, "carbon_monitor_global_annual.csv")
    header = (
        "# File: carbon_monitor_global_annual.csv\n"
        "# Title: Global annual CO2 emissions by country from Carbon Monitor\n"
        "# Units: MtCO2/yr\n"
        "# Source: https://carbonmonitor.org/ (Liu et al., 2020, Nature Communications)\n"
        "# Column types: icn\n"
        "# ----------\n"
    )
    with open(path, "w") as f:
        f.write(header)
        global_annual.to_csv(f, index=False)
    print(f"Global annual data saved to: {path}")

    return global_annual


def print_china_summary(china_annual):
    """Print a summary of China's emission data."""
    if china_annual is None:
        return

    total = china_annual[china_annual["sector"] == "Total"]

    print("\n" + "=" * 60)
    print("China CO2 Emissions Summary (Carbon Monitor)")
    print("=" * 60)

    for _, row in total.iterrows():
        year = int(row["year"])
        mtco2 = row["MtCO2"]
        mtc = mtco2 * MTCO2_TO_MTC
        print(f"  {year}: {mtco2:,.1f} MtCO2 ({mtc:,.1f} MtC)")

    print("\nNote: GCAM-China uses MtC as the emission unit internally.")
    print(f"Conversion: MtC = MtCO2 × {MTCO2_TO_MTC:.4f}")

    if len(total) >= 2:
        latest = total.iloc[-1]
        previous = total.iloc[-2]
        change = latest["MtCO2"] - previous["MtCO2"]
        pct = (change / previous["MtCO2"]) * 100
        print(
            f"\nYear-over-year change ({int(previous['year'])}"
            f"→{int(latest['year'])}): "
            f"{change:+,.1f} MtCO2 ({pct:+.1f}%)"
        )

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Download and process Carbon Monitor CO2 emission data"
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
        ),
        help="Output directory for processed data files",
    )
    parser.add_argument(
        "--raw-file",
        default=None,
        help="Path to already-downloaded raw Carbon Monitor CSV "
        "(skip download)",
    )

    args = parser.parse_args()
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Step 1: Download or load raw data
    if args.raw_file:
        raw_path = args.raw_file
        print(f"Using provided raw file: {raw_path}")
    else:
        raw_path = download_carbon_monitor(output_dir)

    if raw_path is None or not os.path.exists(raw_path):
        print("Error: Could not obtain raw data file.")
        sys.exit(1)

    # Step 2: Load and parse
    print("\nParsing Carbon Monitor data...")
    df = load_carbon_monitor(raw_path)
    print(
        f"Loaded {len(df):,} records, "
        f"{df['country'].nunique()} countries, "
        f"years {df['year'].min()}-{df['year'].max()}"
    )

    # Step 3: Process China annual data
    print("\nProcessing China annual emissions...")
    china_annual = process_china_annual(df, output_dir)

    # Step 4: Process global annual data
    print("\nProcessing global annual emissions...")
    process_global_annual(df, output_dir)

    # Step 5: Print summary
    print_china_summary(china_annual)

    print("\nDone! Files are ready for GCAM-China scenario validation.")


if __name__ == "__main__":
    main()
