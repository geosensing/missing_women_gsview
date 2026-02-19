## StreetSight: Auditing Public Spaces for Missing Women and Urban Infrastructure Using Google Street View


Analyzing gender representation and infrastructure quality in Mumbai, Delhi, and Navi Mumbai using Google Street View imagery.

## Key Findings

### Proportion Women

| City | Women (avg) | Men (avg) | Prop. Women | N Locations |
|------|-------------|-----------|-------------|-------------|
| Mumbai | 0.73 | 3.12 | 0.21 | 498 |
| Delhi | 0.38 | 1.58 | 0.21 | 500 |
| Navi Mumbai | 0.48 | 1.49 | 0.24 | 437 |

Women are significantly underrepresented in public spaces across all three cities, comprising only 21-24% of visible pedestrians.

### By Road Type

| Road Type | Prop. Women | N Annotations |
|-----------|-------------|---------------|
| Primary | 0.11 | 79 |
| Secondary | 0.17 | 166 |
| Tertiary | 0.19 | 293 |
| Residential | 0.24 | 1,362 |

Proportion of women is lowest on primary/secondary roads and highest in residential areas.

### Infrastructure

- **Potholes**: ~1% of locations across all cities
- **Litter**: 21-28% of locations
- **Lane markings**: 17-29% (more common in Mumbai)
- **Footpaths**: 19-50% (most common in Mumbai at 50%)

## Data Pipeline

```
scripts/01_sample_locations.py    Sample random road segments from OSM
         ↓
scripts/02_check_coverage.py      Check Street View coverage (free API)
         ↓
scripts/03_download_images.py     Download images (paid API, ~$7/1000 images)
         ↓
scripts/create_labelstudio_tasks.py    Generate Label Studio import file
         ↓
Label Studio                      Human annotation of images
         ↓
notebooks/01_pipeline.ipynb       Pipeline quality & bias assessment
         ↓
notebooks/02_annotations.ipynb    Analysis and visualization
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

# 5. Run analysis notebooks
uv run jupyter notebook notebooks/01_pipeline.ipynb
uv run jupyter notebook notebooks/02_annotations.ipynb
```

## Data

- **Sampled locations**: 7,000 road segments (2,500 Mumbai, 2,500 Delhi, 2,000 Navi Mumbai)
- **Annotated images**: 1,942 tasks with human annotations
- **Annotation fields**: women_count, men_count, potholes, litter, footpath, lane_markings, land_use

## Directory Structure

```
data/
  annotations/       Raw Label Studio exports
  coverage/          Street View coverage results
  images/            Downloaded Street View images
  samples/           Sampled road locations
  roads/             OSM road data
  labelstudio_tasks.json
notebooks/
  01_pipeline.ipynb  Pipeline quality & bias assessment
  02_annotations.ipynb  Annotation analysis
  outputs/           Generated outputs (CSVs, PNGs, HTMLs)
```

## Output Files

| File | Description |
|------|-------------|
| `notebooks/outputs/combined_annotations.csv` | Merged annotation dataset |
| `notebooks/outputs/city_summary.csv` | Summary statistics by city |
| `notebooks/outputs/annotated_locations_map.html` | Interactive map |
| `notebooks/outputs/sex_ratio_heatmap.html` | Prop. women heatmap |

## License

MIT
