#!/usr/bin/env python
"""
Sample road locations from Mumbai, Navi Mumbai, and Delhi.

This script:
1. Downloads road data from OpenStreetMap via geo-sampling
2. Samples random road segments
3. Saves midpoint coordinates

Usage:
    python scripts/01_sample_locations.py

Output:
    data/samples/locations.csv
"""

from pathlib import Path

from gsview.sampling import sample_all_cities

DATA_DIR = Path("data")
OUTPUT_PATH = DATA_DIR / "samples" / "locations.csv"

SEED = 42

N_SAMPLES = {
    "mumbai": 2500,
    "navi_mumbai": 2000,
    "delhi": 2500,
}


def main():
    print("Sampling road locations...")
    print(f"Seed: {SEED}")
    print(f"Samples per city: {N_SAMPLES}")
    print()

    df = sample_all_cities(n_samples=N_SAMPLES, seed=SEED)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSampled {len(df)} total locations")
    print("\nSamples per city:")
    for city in df["city"].unique():
        count = len(df[df["city"] == city])
        print(f"  {city}: {count}")

    print(f"\nOutput: {OUTPUT_PATH}")

    print("\nSample preview:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
