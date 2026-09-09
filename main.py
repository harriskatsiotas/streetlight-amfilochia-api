from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timezone

app = FastAPI(
    title="Luminaires API – Δήμος Αμφιλοχίας",
    description="Geolocation and real-time status for 100 street luminaires in Amfilochia.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # επιτρέπει όλα τα origins
    allow_methods=["GET"], # μόνο GET (read-only API)
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Luminaire registry – 100 LCU devices
#
# Coordinates interpolated directly along the user-drawn polyline
# from Amfilochia_lighting.kmz (35 waypoints, road edge, right side).
# Total route length: ~960m, ~9.7m spacing between poles.
#
# NOTE: Entries AM048–AM055 have placeholder MACs because rows 48–55
# were missing from the source document. Replace with actual MACs once
# the original spreadsheet is available.
# ---------------------------------------------------------------------------
LUMINAIRES: list[dict] = [
    {"sl_id": "AM001", "mac": "00124B001CE3258C", "latitude": 38.8634102, "longitude": 21.1667806, "wattage": 40},
    {"sl_id": "AM002", "mac": "00124B001CE32616", "latitude": 38.8633864, "longitude": 21.1666729, "wattage": 40},
    {"sl_id": "AM003", "mac": "00124B001CE325C1", "latitude": 38.863437, "longitude": 21.1666111, "wattage": 40},
    {"sl_id": "AM004", "mac": "00124B001CE32685", "latitude": 38.8634955, "longitude": 21.1666355, "wattage": 40},
    {"sl_id": "AM005", "mac": "00124B001CE32682", "latitude": 38.8635036, "longitude": 21.1667319, "wattage": 40},
    {"sl_id": "AM006", "mac": "00124B001CDE960A", "latitude": 38.8634575, "longitude": 21.1668161, "wattage": 40},
    {"sl_id": "AM007", "mac": "00124B001CDE965A", "latitude": 38.8634792, "longitude": 21.1669227, "wattage": 40},
    {"sl_id": "AM008", "mac": "00124B001CE32660", "latitude": 38.8634959, "longitude": 21.1670325, "wattage": 40},
    {"sl_id": "AM009", "mac": "00124B001CE32560", "latitude": 38.8635274, "longitude": 21.1671361, "wattage": 40},
    {"sl_id": "AM010", "mac": "00124B001CE32540", "latitude": 38.8635656, "longitude": 21.1672368, "wattage": 40},
    {"sl_id": "AM011", "mac": "00124B001CDE95BE", "latitude": 38.8636089, "longitude": 21.167334, "wattage": 40},
    {"sl_id": "AM012", "mac": "00124B001CE32604", "latitude": 38.8636523, "longitude": 21.1674311, "wattage": 40},
    {"sl_id": "AM013", "mac": "00124B001CE327A8", "latitude": 38.8636961, "longitude": 21.167528, "wattage": 40},
    {"sl_id": "AM014", "mac": "00124B001CE3272E", "latitude": 38.8637399, "longitude": 21.1676249, "wattage": 40},
    {"sl_id": "AM015", "mac": "00124B001CE32586", "latitude": 38.8637836, "longitude": 21.1677218, "wattage": 40},
    {"sl_id": "AM016", "mac": "00124B001CE324C5", "latitude": 38.8638274, "longitude": 21.1678187, "wattage": 40},
    {"sl_id": "AM017", "mac": "00124B001CE3271F", "latitude": 38.8638705, "longitude": 21.1679161, "wattage": 40},
    {"sl_id": "AM018", "mac": "00124B001CE325C0", "latitude": 38.8639135, "longitude": 21.1680136, "wattage": 40},
    {"sl_id": "AM019", "mac": "00124B001CE32695", "latitude": 38.8639564, "longitude": 21.168111, "wattage": 40},
    {"sl_id": "AM020", "mac": "00124B001CE32652", "latitude": 38.8639994, "longitude": 21.1682085, "wattage": 40},
    {"sl_id": "AM021", "mac": "00124B001CE32686", "latitude": 38.8640424, "longitude": 21.168306, "wattage": 40},
    {"sl_id": "AM022", "mac": "00124B001CE326D6", "latitude": 38.8640867, "longitude": 21.1684024, "wattage": 40},
    {"sl_id": "AM023", "mac": "00124B00193F3FC1", "latitude": 38.864132, "longitude": 21.1684982, "wattage": 40},
    {"sl_id": "AM024", "mac": "00124B001CE325DA", "latitude": 38.8641773, "longitude": 21.1685939, "wattage": 40},
    {"sl_id": "AM025", "mac": "00124B001CE32585", "latitude": 38.8642226, "longitude": 21.1686897, "wattage": 40},
    {"sl_id": "AM026", "mac": "00124B001CE325B0", "latitude": 38.8642679, "longitude": 21.1687854, "wattage": 40},
    {"sl_id": "AM027", "mac": "00124B001CE325E6", "latitude": 38.8643133, "longitude": 21.168881, "wattage": 40},
    {"sl_id": "AM028", "mac": "00124B001CE32649", "latitude": 38.8643588, "longitude": 21.1689766, "wattage": 40},
    {"sl_id": "AM029", "mac": "00124B001CE32667", "latitude": 38.8644043, "longitude": 21.1690722, "wattage": 40},
    {"sl_id": "AM030", "mac": "00124B001CE325DB", "latitude": 38.8644497, "longitude": 21.1691677, "wattage": 40},
    {"sl_id": "AM031", "mac": "00124B001CE32877", "latitude": 38.8644952, "longitude": 21.1692633, "wattage": 40},
    {"sl_id": "AM032", "mac": "00124B00193F3FB0", "latitude": 38.8645386, "longitude": 21.1693605, "wattage": 40},
    {"sl_id": "AM033", "mac": "00124B001CE325CF", "latitude": 38.8645815, "longitude": 21.1694581, "wattage": 40},
    {"sl_id": "AM034", "mac": "00124B001CDE95A1", "latitude": 38.8646148, "longitude": 21.1695611, "wattage": 40},
    {"sl_id": "AM035", "mac": "00124B001CE32790", "latitude": 38.8646436, "longitude": 21.1696669, "wattage": 40},
    {"sl_id": "AM036", "mac": "00124B001CE3261E", "latitude": 38.8646723, "longitude": 21.1697727, "wattage": 40},
    {"sl_id": "AM037", "mac": "00124B001CE3266C", "latitude": 38.864704, "longitude": 21.169877, "wattage": 40},
    {"sl_id": "AM038", "mac": "00124B001CE32772", "latitude": 38.8647363, "longitude": 21.169981, "wattage": 40},
    {"sl_id": "AM039", "mac": "00124B001CE32597", "latitude": 38.8647687, "longitude": 21.1700851, "wattage": 40},
    {"sl_id": "AM040", "mac": "00124B001CE3274B", "latitude": 38.8648032, "longitude": 21.1701878, "wattage": 40},
    {"sl_id": "AM041", "mac": "00124B001CE32657", "latitude": 38.8648428, "longitude": 21.1702876, "wattage": 40},
    {"sl_id": "AM042", "mac": "00124B001CE3267E", "latitude": 38.8648824, "longitude": 21.1703874, "wattage": 40},
    {"sl_id": "AM043", "mac": "00124B001CE32738", "latitude": 38.864922, "longitude": 21.1704873, "wattage": 40},
    {"sl_id": "AM044", "mac": "00124B001CE326B8", "latitude": 38.8649613, "longitude": 21.1705873, "wattage": 40},
    {"sl_id": "AM045", "mac": "00124B001CE32609", "latitude": 38.8649995, "longitude": 21.1706879, "wattage": 40},
    {"sl_id": "AM046", "mac": "00124B001CE325C8", "latitude": 38.8650378, "longitude": 21.1707886, "wattage": 40},
    {"sl_id": "AM047", "mac": "00124B001CE3263B", "latitude": 38.8650761, "longitude": 21.1708892, "wattage": 40},
    {"sl_id": "AM048", "mac": "00124B00PLACEHOLDER0048", "latitude": 38.8651144, "longitude": 21.1709899, "wattage": 40},
    {"sl_id": "AM049", "mac": "00124B00PLACEHOLDER0049", "latitude": 38.8651546, "longitude": 21.1710891, "wattage": 40},
    {"sl_id": "AM050", "mac": "00124B00PLACEHOLDER0050", "latitude": 38.865202, "longitude": 21.1711831, "wattage": 40},
    {"sl_id": "AM051", "mac": "00124B00PLACEHOLDER0051", "latitude": 38.8652495, "longitude": 21.1712771, "wattage": 40},
    {"sl_id": "AM052", "mac": "00124B00PLACEHOLDER0052", "latitude": 38.8652974, "longitude": 21.1713707, "wattage": 40},
    {"sl_id": "AM053", "mac": "00124B00PLACEHOLDER0053", "latitude": 38.8653493, "longitude": 21.1714607, "wattage": 40},
    {"sl_id": "AM054", "mac": "00124B00PLACEHOLDER0054", "latitude": 38.8654013, "longitude": 21.1715507, "wattage": 40},
    {"sl_id": "AM055", "mac": "00124B00PLACEHOLDER0055", "latitude": 38.8654532, "longitude": 21.1716407, "wattage": 40},
    {"sl_id": "AM056", "mac": "00124B00193F3F88", "latitude": 38.8655051, "longitude": 21.1717307, "wattage": 40},
    {"sl_id": "AM057", "mac": "00124B00193F3FB7", "latitude": 38.8655555, "longitude": 21.171822, "wattage": 40},
    {"sl_id": "AM058", "mac": "00124B001CDE966D", "latitude": 38.8656001, "longitude": 21.1719183, "wattage": 40},
    {"sl_id": "AM059", "mac": "00124B001CE327D8", "latitude": 38.8656446, "longitude": 21.1720147, "wattage": 40},
    {"sl_id": "AM060", "mac": "00124B001CE325ED", "latitude": 38.8656891, "longitude": 21.172111, "wattage": 40},
    {"sl_id": "AM061", "mac": "00124B001CDE95CE", "latitude": 38.8657336, "longitude": 21.1722073, "wattage": 40},
    {"sl_id": "AM062", "mac": "00124B001CE32799", "latitude": 38.8657797, "longitude": 21.1723023, "wattage": 40},
    {"sl_id": "AM063", "mac": "00124B001CE324CC", "latitude": 38.8658289, "longitude": 21.1723948, "wattage": 40},
    {"sl_id": "AM064", "mac": "00124B001CE32684", "latitude": 38.8658781, "longitude": 21.1724873, "wattage": 40},
    {"sl_id": "AM065", "mac": "00124B001CE32665", "latitude": 38.8659274, "longitude": 21.1725798, "wattage": 40},
    {"sl_id": "AM066", "mac": "00124B001CE326E8", "latitude": 38.8659761, "longitude": 21.1726726, "wattage": 40},
    {"sl_id": "AM067", "mac": "00124B001CE32545", "latitude": 38.8660204, "longitude": 21.1727691, "wattage": 40},
    {"sl_id": "AM068", "mac": "00124B001CE32661", "latitude": 38.8660647, "longitude": 21.1728657, "wattage": 40},
    {"sl_id": "AM069", "mac": "00124B001CDE967C", "latitude": 38.8661089, "longitude": 21.1729622, "wattage": 40},
    {"sl_id": "AM070", "mac": "00124B001CDE967D", "latitude": 38.8661532, "longitude": 21.1730587, "wattage": 40},
    {"sl_id": "AM071", "mac": "00124B001CE32566", "latitude": 38.8661975, "longitude": 21.1731552, "wattage": 40},
    {"sl_id": "AM072", "mac": "00124B001CE3277C", "latitude": 38.8662359, "longitude": 21.1732556, "wattage": 40},
    {"sl_id": "AM073", "mac": "00124B001CE327CE", "latitude": 38.8662711, "longitude": 21.1733581, "wattage": 40},
    {"sl_id": "AM074", "mac": "00124B001CDE962E", "latitude": 38.866307, "longitude": 21.1734602, "wattage": 40},
    {"sl_id": "AM075", "mac": "00124B001CDE9595", "latitude": 38.8663431, "longitude": 21.1735622, "wattage": 40},
    {"sl_id": "AM076", "mac": "00124B001CE32506", "latitude": 38.8663794, "longitude": 21.173664, "wattage": 40},
    {"sl_id": "AM077", "mac": "00124B00193F3FAD", "latitude": 38.8664177, "longitude": 21.1737647, "wattage": 40},
    {"sl_id": "AM078", "mac": "00124B001CE32535", "latitude": 38.866456, "longitude": 21.1738653, "wattage": 40},
    {"sl_id": "AM079", "mac": "00124B001CDE9648", "latitude": 38.8664944, "longitude": 21.1739659, "wattage": 40},
    {"sl_id": "AM080", "mac": "00124B001CE32516", "latitude": 38.8665368, "longitude": 21.1740634, "wattage": 40},
    {"sl_id": "AM081", "mac": "00124B001CE32519", "latitude": 38.8665866, "longitude": 21.1741554, "wattage": 40},
    {"sl_id": "AM082", "mac": "00124B001CE32550", "latitude": 38.866625, "longitude": 21.1742555, "wattage": 40},
    {"sl_id": "AM083", "mac": "00124B001CDE961F", "latitude": 38.8666594, "longitude": 21.1743584, "wattage": 40},
    {"sl_id": "AM084", "mac": "00124B001CDE9641", "latitude": 38.8666938, "longitude": 21.1744614, "wattage": 40},
    {"sl_id": "AM085", "mac": "00124B001CDE9664", "latitude": 38.8667364, "longitude": 21.174559, "wattage": 40},
    {"sl_id": "AM086", "mac": "00124B001CDE95B8", "latitude": 38.8667801, "longitude": 21.174656, "wattage": 40},
    {"sl_id": "AM087", "mac": "00124B001CDE95C9", "latitude": 38.8668277, "longitude": 21.1747495, "wattage": 40},
    {"sl_id": "AM088", "mac": "00124B001CE32531", "latitude": 38.8668812, "longitude": 21.174838, "wattage": 40},
    {"sl_id": "AM089", "mac": "00124B001CDE95D1", "latitude": 38.8669347, "longitude": 21.1749265, "wattage": 40},
    {"sl_id": "AM090", "mac": "00124B001CE324E7", "latitude": 38.8669882, "longitude": 21.1750149, "wattage": 40},
    {"sl_id": "AM091", "mac": "00124B001CE32555", "latitude": 38.8670543, "longitude": 21.1750871, "wattage": 40},
    {"sl_id": "AM092", "mac": "00124B001CE32515", "latitude": 38.8671237, "longitude": 21.175155, "wattage": 40},
    {"sl_id": "AM093", "mac": "00124B001CE3268A", "latitude": 38.8671934, "longitude": 21.1752223, "wattage": 40},
    {"sl_id": "AM094", "mac": "00124B001CE32641", "latitude": 38.8672652, "longitude": 21.1752858, "wattage": 40},
    {"sl_id": "AM095", "mac": "00124B001CDE9597", "latitude": 38.8673371, "longitude": 21.1753494, "wattage": 40},
    {"sl_id": "AM096", "mac": "00124B001CE3265A", "latitude": 38.8674129, "longitude": 21.1754042, "wattage": 40},
    {"sl_id": "AM097", "mac": "00124B001CE32574", "latitude": 38.8674907, "longitude": 21.175455, "wattage": 40},
    {"sl_id": "AM098", "mac": "00124B00193F3FBD", "latitude": 38.8675686, "longitude": 21.1755054, "wattage": 40},
    {"sl_id": "AM099", "mac": "00124B001CE3262E", "latitude": 38.8676486, "longitude": 21.17555, "wattage": 40},
    {"sl_id": "AM100", "mac": "00124B001CE325D2", "latitude": 38.8677286, "longitude": 21.1755946, "wattage": 40},
]

LUMINAIRE_MAP_BY_MAC: dict[str, dict] = {l["mac"]: l for l in LUMINAIRES}
LUMINAIRE_MAP_BY_SL:  dict[str, dict] = {l["sl_id"]: l for l in LUMINAIRES}


# ---------------------------------------------------------------------------
# Status logic: active 20:00–06:00 UTC, inactive otherwise
# ---------------------------------------------------------------------------
def is_active_now() -> bool:
    return datetime.now(timezone.utc).hour >= 20 or datetime.now(timezone.utc).hour < 6


def luminaire_status(active: bool) -> str:
    return "active" if active else "inactive"


def enrich(lum: dict, active: bool) -> dict:
    return {
        "sl_id": lum["sl_id"],
        "mac": lum["mac"],
        "latitude": lum["latitude"],
        "longitude": lum["longitude"],
        "wattage": lum["wattage"],
        "status": luminaire_status(active),
        "schedule": "20:00–06:00 UTC",
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def health():
    active = is_active_now()
    return {
        "status": "ok",
        "service": "Luminaires API – Δήμος Αμφιλοχίας",
        "utc_time": datetime.now(timezone.utc).isoformat(),
        "luminaires_active": active,
        "total_luminaires": len(LUMINAIRES),
    }


@app.get("/status", tags=["Status"])
def get_current_status():
    """Current global status of the luminaire network."""
    active = is_active_now()
    return {
        "utc_time": datetime.now(timezone.utc).isoformat(),
        "status": luminaire_status(active),
        "schedule": "Active: 20:00–06:00 UTC | Inactive: 06:00–20:00 UTC",
        "total_luminaires": len(LUMINAIRES),
    }


@app.get("/luminaires", tags=["Luminaires"])
def get_all_luminaires(
    status: Optional[str] = Query(None, description="Filter by 'active' or 'inactive'"),
):
    """All luminaires with geolocation and current status."""
    active = is_active_now()
    result = [enrich(l, active) for l in LUMINAIRES]
    if status in ("active", "inactive"):
        result = [r for r in result if r["status"] == status]
    return {
        "utc_time": datetime.now(timezone.utc).isoformat(),
        "current_status": luminaire_status(active),
        "count": len(result),
        "luminaires": result,
    }


@app.get("/luminaires/geojson/all", tags=["GeoJSON"])
def get_geojson():
    """GeoJSON FeatureCollection – ready for Leaflet, QGIS, Google Maps, etc."""
    active = is_active_now()
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [l["longitude"], l["latitude"]]},
            "properties": {
                "sl_id": l["sl_id"],
                "mac": l["mac"],
                "wattage": l["wattage"],
                "status": luminaire_status(active),
                "schedule": "20:00–06:00 UTC",
            },
        }
        for l in LUMINAIRES
    ]
    return {
        "type": "FeatureCollection",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feature_count": len(features),
        "features": features,
    }


@app.get("/luminaires/{identifier}", tags=["Luminaires"])
def get_luminaire(identifier: str):
    """Single luminaire by SL-ID (e.g. AM001) or MAC address."""
    lum = LUMINAIRE_MAP_BY_SL.get(identifier.upper()) or LUMINAIRE_MAP_BY_MAC.get(identifier.upper())
    if not lum:
        raise HTTPException(status_code=404, detail=f"Luminaire '{identifier}' not found.")
    return enrich(lum, is_active_now())
