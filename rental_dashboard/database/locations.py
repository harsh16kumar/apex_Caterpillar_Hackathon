# database/locations.py
import re

# Canonical name -> (lat, lon)
LOCATIONS: dict[str, tuple[float, float]] = {
    "new delhi": (28.6139, 77.2090),
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bengaluru": (12.9716, 77.5946),
    "vellore": (12.9165, 79.1325),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "surat": (21.1702, 72.8311),
    "kochi": (9.9312, 76.2673),
    "chandigarh": (30.7333, 76.7794),
    "noida": (28.5355, 77.3910),
    "gurugram": (28.4595, 77.0266),
    "gurgaon": (28.4595, 77.0266),
    # add more canonical names here as needed
}

def _normalize(name: str | None) -> str | None:
    if not name or not isinstance(name, str):
        return None
    s = name.strip().lower()
    # collapse multiple spaces, remove trailing punctuation
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", "", s)
    return s

def geocode_name(name: str | None) -> tuple[float | None, float | None, str | None]:
    """
    Returns (lat, lon, source_key) for a given human location name,
    or (None, None, None) if unknown.
    """
    key = _normalize(name)
    if not key:
        return None, None, None

    # direct match
    if key in LOCATIONS:
        lat, lon = LOCATIONS[key]
        return lat, lon, key

    # very light fallback: try removing common suffixes like " india"
    key2 = re.sub(r"\bindia\b", "", key).strip()
    if key2 in LOCATIONS:
        lat, lon = LOCATIONS[key2]
        return lat, lon, key2

    return None, None, None

def allowed_location_names() -> list[str]:
    """Return all canonical location names (keys in LOCATIONS)."""
    return sorted(LOCATIONS.keys())
