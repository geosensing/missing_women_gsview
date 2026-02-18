"""Location sampling for Indian cities using OSM Overpass API."""

import random
from dataclasses import dataclass
from pathlib import Path

import folium
import pandas as pd
import requests

DATA_DIR = Path("data")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@dataclass
class CityConfig:
    """Configuration for sampling a city."""

    name: str
    osm_relation_id: int
    default_samples: int
    bbox: tuple[float, float, float, float] | None = None


CITY_CONFIGS = {
    "mumbai": CityConfig(
        name="Mumbai",
        osm_relation_id=7888990,
        default_samples=2500,
    ),
    "delhi": CityConfig(
        name="Delhi",
        osm_relation_id=1942586,
        default_samples=2500,
    ),
    "navi_mumbai": CityConfig(
        name="Navi Mumbai",
        osm_relation_id=7965697,
        default_samples=2000,
        bbox=(18.95, 72.95, 19.25, 73.15),
    ),
}


def _fetch_roads_from_overpass(
    relation_id: int,
    bbox: tuple[float, float, float, float] | None = None,
) -> list[dict]:
    """
    Fetch road segments from OSM Overpass API.

    Returns list of road segments with coordinates.
    """
    if bbox:
        min_lat, min_lon, max_lat, max_lon = bbox
        bbox_str = f"{min_lat},{min_lon},{max_lat},{max_lon}"
        query = f"""
        [out:json][timeout:180];
        (
          way["highway"~"^(primary|secondary|tertiary|residential|unclassified)$"]({bbox_str});
        );
        out body;
        >;
        out skel qt;
        """
    else:
        query = f"""
        [out:json][timeout:180];
        area(id:{3600000000 + relation_id})->.searchArea;
        (
          way["highway"~"^(primary|secondary|tertiary|residential|unclassified)$"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """

    print("Fetching roads from Overpass API...")
    response = requests.post(OVERPASS_URL, data={"data": query}, timeout=300)
    response.raise_for_status()
    data = response.json()

    nodes = {}
    for element in data["elements"]:
        if element["type"] == "node":
            nodes[element["id"]] = (element["lat"], element["lon"])

    roads = []
    for element in data["elements"]:
        if element["type"] == "way":
            way_nodes = element.get("nodes", [])
            if len(way_nodes) >= 2:
                coords = [nodes.get(n) for n in way_nodes if n in nodes]
                if len(coords) >= 2:
                    roads.append(
                        {
                            "osm_id": element["id"],
                            "name": element.get("tags", {}).get("name", ""),
                            "highway": element.get("tags", {}).get("highway", ""),
                            "coords": coords,
                        }
                    )

    print(f"Found {len(roads)} road segments")
    return roads


def _segment_roads(roads: list[dict], segment_length_m: float = 500) -> list[dict]:
    """
    Split roads into segments of approximately segment_length_m meters.

    Returns list of segment midpoints.
    """
    from math import atan2, cos, radians, sin, sqrt

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlam = radians(lon2 - lon1)
        a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    segments = []
    for road in roads:
        coords = road["coords"]
        for i in range(len(coords) - 1):
            lat1, lon1 = coords[i]
            lat2, lon2 = coords[i + 1]

            distance = haversine(lat1, lon1, lat2, lon2)
            n_segments = max(1, int(distance / segment_length_m))

            for j in range(n_segments):
                t = (j + 0.5) / n_segments
                mid_lat = lat1 + t * (lat2 - lat1)
                mid_lon = lon1 + t * (lon2 - lon1)

                segments.append(
                    {
                        "lat": mid_lat,
                        "lon": mid_lon,
                        "osm_id": road["osm_id"],
                        "osm_name": road["name"],
                        "osm_type": road["highway"],
                    }
                )

    return segments


def get_roads_for_city(
    city: str,
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Get road segments for a city.

    Parameters
    ----------
    city : str
        City name: 'mumbai', 'delhi', or 'navi_mumbai'
    force_download : bool
        Re-download even if data exists

    Returns
    -------
    pd.DataFrame
        DataFrame with road segment data
    """
    city_key = city.lower().replace(" ", "_").replace("-", "_")
    if city_key not in CITY_CONFIGS:
        raise ValueError(
            f"Unknown city: {city}. Choose from: {list(CITY_CONFIGS.keys())}"
        )

    config = CITY_CONFIGS[city_key]
    roads_dir = DATA_DIR / "roads"
    roads_dir.mkdir(parents=True, exist_ok=True)

    roads_path = roads_dir / f"{city_key}_roads.csv"

    if roads_path.exists() and not force_download:
        print(f"Using existing roads data: {roads_path}")
        return pd.read_csv(roads_path)

    print(f"Downloading road data for {config.name}...")
    roads = _fetch_roads_from_overpass(config.osm_relation_id, config.bbox)

    print("Segmenting roads...")
    segments = _segment_roads(roads)

    df = pd.DataFrame(segments)
    df["segment_id"] = range(len(df))
    df.to_csv(roads_path, index=False)
    print(f"Saved {len(df)} segments to {roads_path}")

    return df


def sample_city(
    city: str,
    n_samples: int | None = None,
    seed: int | None = None,
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Sample road locations from a city.

    Parameters
    ----------
    city : str
        City name: 'mumbai', 'delhi', or 'navi_mumbai'
    n_samples : int, optional
        Number of samples. Uses city default if not specified.
    seed : int, optional
        Random seed for reproducibility.
    force_download : bool
        Re-download road data even if it exists

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: lat, lon, city, segment_id, osm_name, osm_type
    """
    city_key = city.lower().replace(" ", "_").replace("-", "_")
    if city_key not in CITY_CONFIGS:
        raise ValueError(
            f"Unknown city: {city}. Choose from: {list(CITY_CONFIGS.keys())}"
        )

    config = CITY_CONFIGS[city_key]
    n = n_samples or config.default_samples

    roads_df = get_roads_for_city(city, force_download=force_download)

    if len(roads_df) < n:
        print(
            f"Warning: Only {len(roads_df)} segments available "
            f"(requested {n}). Using all available."
        )
        n = len(roads_df)

    if seed is not None:
        random.seed(seed)

    sampled = roads_df.sample(n=n, random_state=seed)
    sampled = sampled.copy()
    sampled["city"] = config.name

    return sampled[
        ["lat", "lon", "city", "segment_id", "osm_name", "osm_type"]
    ].reset_index(drop=True)


def sample_all_cities(
    n_samples: dict[str, int] | None = None,
    seed: int | None = None,
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Sample from all configured cities.

    Parameters
    ----------
    n_samples : dict, optional
        Number of samples per city. Uses defaults if not specified.
    seed : int, optional
        Base random seed (incremented per city).
    force_download : bool
        Re-download road data even if it exists

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with all samples.
    """
    n_samples = n_samples or {}
    dfs = []

    for i, city in enumerate(CITY_CONFIGS.keys()):
        city_seed = seed + i if seed is not None else None
        n = n_samples.get(city)
        df = sample_city(
            city, n_samples=n, seed=city_seed, force_download=force_download
        )
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined["location_id"] = [f"loc_{i:05d}" for i in range(len(combined))]
    return combined[
        ["location_id", "city", "lat", "lon", "segment_id", "osm_name", "osm_type"]
    ]


CITY_COLORS = {
    "Mumbai": "#e41a1c",
    "Delhi": "#377eb8",
    "Navi Mumbai": "#4daf4a",
}


def plot_samples(df: pd.DataFrame, output_path: str = "data/samples/map.html") -> str:
    """
    Create interactive map of sampled locations.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with lat, lon, and city columns
    output_path : str
        Path to save HTML map file

    Returns
    -------
    str
        Path to saved map file
    """
    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    for city in df["city"].unique():
        city_df = df[df["city"] == city]
        color = CITY_COLORS.get(city, "#999999")

        fg = folium.FeatureGroup(name=city)

        for _, row in city_df.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=3,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=f"{city}: ({row['lat']:.4f}, {row['lon']:.4f})",
            ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl().add_to(m)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output))

    return str(output)
