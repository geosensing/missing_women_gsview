#!/usr/bin/env python
"""
Download Google Street View images for locations with coverage.

This script uses the PAID Static API to download images.
Estimated cost: ~$7 per 1000 images.

Usage:
    python scripts/03_download_images.py

Input:
    data/coverage/coverage.csv

Output:
    data/images/*.jpg
    data/images/download_results.csv
    data/annotation.csv
"""

from pathlib import Path

import pandas as pd

from gsview.downloader import download_images_batch, generate_annotation_csv

DATA_DIR = Path("data")
COVERAGE_PATH = DATA_DIR / "coverage" / "coverage.csv"
IMAGES_DIR = DATA_DIR / "images"
ANNOTATION_PATH = DATA_DIR / "annotation.csv"

HEADINGS = [0, 90, 180, 270]
PITCH = 0


def main():
    if not COVERAGE_PATH.exists():
        print(f"Error: {COVERAGE_PATH} not found. Run 02_check_coverage.py first.")
        return

    coverage_df = pd.read_csv(COVERAGE_PATH)
    locations = coverage_df[coverage_df["has_coverage"]].copy()

    total_images = len(locations) * len(HEADINGS)
    estimated_cost = (total_images / 1000) * 7

    print(f"Locations with coverage: {len(locations)}")
    print(f"Headings per location: {HEADINGS}")
    print(f"Total images to download: {total_images}")
    print(f"Estimated cost: ${estimated_cost:.2f}")
    print()

    confirm = input("Proceed with download? [y/N]: ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    print("\nDownloading images...")
    results = download_images_batch(
        locations,
        output_dir=IMAGES_DIR,
        headings=HEADINGS,
        pitch=PITCH,
        rate_limit=0.1,
        skip_existing=True,
    )

    results_path = IMAGES_DIR / "download_results.csv"
    results.to_csv(results_path, index=False)

    successful = results["success"].sum()
    failed = len(results) - successful
    print(f"\nDownloaded: {successful} images")
    print(f"Failed: {failed} images")
    print(f"Results: {results_path}")

    print("\nGenerating annotation CSV...")
    annotation_df = generate_annotation_csv(results, ANNOTATION_PATH)
    print(f"Generated {len(annotation_df)} annotation rows")
    print(f"Output: {ANNOTATION_PATH}")


if __name__ == "__main__":
    main()
