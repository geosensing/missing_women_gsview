#!/usr/bin/env python
"""
Check Google Street View coverage for sampled locations.

This script uses the FREE metadata API to check which locations have Street View coverage
before downloading images.

Usage:
    python scripts/02_check_coverage.py

Input:
    data/samples/locations.csv

Output:
    data/coverage/coverage.csv
"""

from pathlib import Path

import pandas as pd

from gsview.downloader import check_coverage_batch, print_coverage_stats

DATA_DIR = Path("data")
INPUT_PATH = DATA_DIR / "samples" / "locations.csv"
OUTPUT_PATH = DATA_DIR / "coverage" / "coverage.csv"


def main():
    if not INPUT_PATH.exists():
        print(f"Error: {INPUT_PATH} not found. Run 01_sample_locations.py first.")
        return

    locations = pd.read_csv(INPUT_PATH)
    print(f"Checking coverage for {len(locations)} locations...")
    print("(This uses the FREE metadata API)")

    results = check_coverage_batch(
        locations,
        output_path=OUTPUT_PATH,
        rate_limit=0.1,
    )

    print_coverage_stats(results)

    covered = results[results["has_coverage"]]
    print(f"\nLocations with coverage: {len(covered)}")
    print(f"Output: {OUTPUT_PATH}")

    if len(covered) > 0:
        print("\nSample of covered locations:")
        print(covered.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
