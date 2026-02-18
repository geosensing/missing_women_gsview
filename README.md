# Missing Women in Public Spaces

Analyzing sex ratios and infrastructure quality in Mumbai, Delhi, and Navi Mumbai using Google Street View imagery.

## Key Findings

### Sex Ratios (Women per Man)

| City | Women (avg) | Men (avg) | Sex Ratio | N Locations |
|------|-------------|-----------|-----------|-------------|
| Mumbai | 2.0 | 5.1 | 0.54 | 498 |
| Delhi | 1.7 | 3.6 | 0.65 | 500 |
| Navi Mumbai | 2.1 | 3.5 | 0.89 | 437 |

Women are significantly underrepresented in public spaces across all three cities, with Mumbai showing the lowest sex ratio (0.54 women per man).

### By Road Type

| Road Type | Sex Ratio | N Locations |
|-----------|-----------|-------------|
| Primary | 0.43 | 63 |
| Secondary | 0.45 | 120 |
| Tertiary | 0.51 | 215 |
| Residential | 0.75 | 1,003 |

Sex ratios are lowest on primary/secondary roads and highest in residential areas.

### Infrastructure

- **Litter**: Present in 90-95% of locations across all cities
- **Potholes**: 15-20% of locations
- **Lane markings**: More common in Mumbai (96%) vs Delhi (80%)
- **Footpaths**: Rare across all cities

## Data Pipeline

```
01_sample_locations.py    Sample random road segments from OSM
         ↓
02_check_coverage.py      Check Street View coverage (free API)
         ↓
03_download_images.py     Download images (paid API, ~$7/1000 images)
         ↓
create_labelstudio_tasks.py    Generate Label Studio import file
         ↓
Label Studio              Human annotation of images
         ↓
notebooks/analysis.ipynb  Analysis and visualization
```

## Setup

```bash
# Clone and install
git clone https://github.com/soodoku/missing_women_gsview
cd missing_women_gsview
uv sync

# Set up API key
cp .env.example .env
# Edit .env with your Google Street View API key
```

## Usage

```bash
# 1. Sample locations from OpenStreetMap
uv run python scripts/01_sample_locations.py

# 2. Check Street View coverage
uv run python scripts/02_check_coverage.py

# 3. Download images (requires API key, costs money)
uv run python scripts/03_download_images.py

# 4. Create Label Studio tasks
uv run python scripts/create_labelstudio_tasks.py

# 5. Run analysis notebook
uv run jupyter notebook notebooks/analysis.ipynb
```

## Data

- **Sampled locations**: 7,000 road segments (2,500 Mumbai, 2,500 Delhi, 2,000 Navi Mumbai)
- **Annotated images**: 1,942 tasks with human annotations
- **Annotation fields**: women_count, men_count, potholes, litter, footpath, lane_markings, land_use

## Output Files

| File | Description |
|------|-------------|
| `data/analysis/combined_annotations.csv` | Merged annotation dataset |
| `data/analysis/city_summary.csv` | Summary statistics by city |
| `data/analysis/annotated_locations_map.html` | Interactive map |
| `data/analysis/sex_ratio_heatmap.html` | Spatial heatmap |

## License

MIT
