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
# Coordinates interpolated along the polyline of Odos Andrea Stratou
# extracted from the KMZ file provided (Αμφιλοχία_φώτα.kmz).
# Total route length: ~1025m, ~10.4m spacing between poles.
# Right-hand side of the road, following the road direction.
#
# NOTE: Entries AM048–AM055 have placeholder MACs because rows 48–55
# were missing from the source document. Replace with actual MACs once
# the original spreadsheet is available.
# ---------------------------------------------------------------------------
LUMINAIRES: list[dict] = [
    {"sl_id": "AM001", "mac": "00124B001CE3258C", "latitude": 38.8635302, "longitude": 21.1666433, "wattage": 40},
    {"sl_id": "AM002", "mac": "00124B001CE32616", "latitude": 38.8634537, "longitude": 21.1665751, "wattage": 40},
    {"sl_id": "AM003", "mac": "00124B001CE325C1", "latitude": 38.8633823, "longitude": 21.1665788, "wattage": 40},
    {"sl_id": "AM004", "mac": "00124B001CE32685", "latitude": 38.8633493, "longitude": 21.1666768, "wattage": 40},
    {"sl_id": "AM005", "mac": "00124B001CE32682", "latitude": 38.8633759, "longitude": 21.166782, "wattage": 40},
    {"sl_id": "AM006", "mac": "00124B001CDE960A", "latitude": 38.8634576, "longitude": 21.1668226, "wattage": 40},
    {"sl_id": "AM007", "mac": "00124B001CDE965A", "latitude": 38.8635018, "longitude": 21.1669279, "wattage": 40},
    {"sl_id": "AM008", "mac": "00124B001CE32660", "latitude": 38.8635228, "longitude": 21.1670423, "wattage": 40},
    {"sl_id": "AM009", "mac": "00124B001CE32560", "latitude": 38.8635422, "longitude": 21.1671574, "wattage": 40},
    {"sl_id": "AM010", "mac": "00124B001CE32540", "latitude": 38.8635858, "longitude": 21.1672631, "wattage": 40},
    {"sl_id": "AM011", "mac": "00124B001CDE95BE", "latitude": 38.8636294, "longitude": 21.1673688, "wattage": 40},
    {"sl_id": "AM012", "mac": "00124B001CE32604", "latitude": 38.863673, "longitude": 21.1674746, "wattage": 40},
    {"sl_id": "AM013", "mac": "00124B001CE327A8", "latitude": 38.8637166, "longitude": 21.1675803, "wattage": 40},
    {"sl_id": "AM014", "mac": "00124B001CE3272E", "latitude": 38.8637602, "longitude": 21.167686, "wattage": 40},
    {"sl_id": "AM015", "mac": "00124B001CE32586", "latitude": 38.8638037, "longitude": 21.1677918, "wattage": 40},
    {"sl_id": "AM016", "mac": "00124B001CE324C5", "latitude": 38.8638473, "longitude": 21.1678975, "wattage": 40},
    {"sl_id": "AM017", "mac": "00124B001CE3271F", "latitude": 38.8638964, "longitude": 21.1679992, "wattage": 40},
    {"sl_id": "AM018", "mac": "00124B001CE325C0", "latitude": 38.8639459, "longitude": 21.1681005, "wattage": 40},
    {"sl_id": "AM019", "mac": "00124B001CE32695", "latitude": 38.8639954, "longitude": 21.1682019, "wattage": 40},
    {"sl_id": "AM020", "mac": "00124B001CE32652", "latitude": 38.8640449, "longitude": 21.1683032, "wattage": 40},
    {"sl_id": "AM021", "mac": "00124B001CE32686", "latitude": 38.8640944, "longitude": 21.1684046, "wattage": 40},
    {"sl_id": "AM022", "mac": "00124B001CE326D6", "latitude": 38.8641439, "longitude": 21.1685059, "wattage": 40},
    {"sl_id": "AM023", "mac": "00124B00193F3FC1", "latitude": 38.8641934, "longitude": 21.1686072, "wattage": 40},
    {"sl_id": "AM024", "mac": "00124B001CE325DA", "latitude": 38.8642429, "longitude": 21.1687086, "wattage": 40},
    {"sl_id": "AM025", "mac": "00124B001CE32585", "latitude": 38.8642889, "longitude": 21.1688126, "wattage": 40},
    {"sl_id": "AM026", "mac": "00124B001CE325B0", "latitude": 38.8643346, "longitude": 21.1689169, "wattage": 40},
    {"sl_id": "AM027", "mac": "00124B001CE325E6", "latitude": 38.8643802, "longitude": 21.1690212, "wattage": 40},
    {"sl_id": "AM028", "mac": "00124B001CE32649", "latitude": 38.8644259, "longitude": 21.1691255, "wattage": 40},
    {"sl_id": "AM029", "mac": "00124B001CE32667", "latitude": 38.8644715, "longitude": 21.1692298, "wattage": 40},
    {"sl_id": "AM030", "mac": "00124B001CE325DB", "latitude": 38.8645172, "longitude": 21.1693341, "wattage": 40},
    {"sl_id": "AM031", "mac": "00124B001CE32877", "latitude": 38.8645628, "longitude": 21.1694384, "wattage": 40},
    {"sl_id": "AM032", "mac": "00124B00193F3FB0", "latitude": 38.8646085, "longitude": 21.1695426, "wattage": 40},
    {"sl_id": "AM033", "mac": "00124B001CE325CF", "latitude": 38.8646484, "longitude": 21.1696505, "wattage": 40},
    {"sl_id": "AM034", "mac": "00124B001CDE95A1", "latitude": 38.8646845, "longitude": 21.1697608, "wattage": 40},
    {"sl_id": "AM035", "mac": "00124B001CE32790", "latitude": 38.8647206, "longitude": 21.1698711, "wattage": 40},
    {"sl_id": "AM036", "mac": "00124B001CE3261E", "latitude": 38.8647566, "longitude": 21.1699814, "wattage": 40},
    {"sl_id": "AM037", "mac": "00124B001CE3266C", "latitude": 38.8647927, "longitude": 21.1700917, "wattage": 40},
    {"sl_id": "AM038", "mac": "00124B001CE32772", "latitude": 38.8648288, "longitude": 21.170202, "wattage": 40},
    {"sl_id": "AM039", "mac": "00124B001CE32597", "latitude": 38.8648648, "longitude": 21.1703124, "wattage": 40},
    {"sl_id": "AM040", "mac": "00124B001CE3274B", "latitude": 38.8649009, "longitude": 21.1704227, "wattage": 40},
    {"sl_id": "AM041", "mac": "00124B001CE32657", "latitude": 38.864937, "longitude": 21.170533, "wattage": 40},
    {"sl_id": "AM042", "mac": "00124B001CE3267E", "latitude": 38.8649731, "longitude": 21.1706433, "wattage": 40},
    {"sl_id": "AM043", "mac": "00124B001CE32738", "latitude": 38.8650184, "longitude": 21.1707475, "wattage": 40},
    {"sl_id": "AM044", "mac": "00124B001CE326B8", "latitude": 38.8650671, "longitude": 21.1708495, "wattage": 40},
    {"sl_id": "AM045", "mac": "00124B001CE32609", "latitude": 38.8651158, "longitude": 21.1709514, "wattage": 40},
    {"sl_id": "AM046", "mac": "00124B001CE325C8", "latitude": 38.8651646, "longitude": 21.1710534, "wattage": 40},
    {"sl_id": "AM047", "mac": "00124B001CE3263B", "latitude": 38.8652133, "longitude": 21.1711554, "wattage": 40},
    {"sl_id": "AM048", "mac": "00124B00PLACEHOLDER0048", "latitude": 38.865262, "longitude": 21.1712574, "wattage": 40},
    {"sl_id": "AM049", "mac": "00124B00PLACEHOLDER0049", "latitude": 38.8653107, "longitude": 21.1713593, "wattage": 40},
    {"sl_id": "AM050", "mac": "00124B00PLACEHOLDER0050", "latitude": 38.8653594, "longitude": 21.1714613, "wattage": 40},
    {"sl_id": "AM051", "mac": "00124B00PLACEHOLDER0051", "latitude": 38.8654081, "longitude": 21.1715633, "wattage": 40},
    {"sl_id": "AM052", "mac": "00124B00PLACEHOLDER0052", "latitude": 38.8654569, "longitude": 21.1716653, "wattage": 40},
    {"sl_id": "AM053", "mac": "00124B00PLACEHOLDER0053", "latitude": 38.8655062, "longitude": 21.1717668, "wattage": 40},
    {"sl_id": "AM054", "mac": "00124B00PLACEHOLDER0054", "latitude": 38.8655562, "longitude": 21.1718677, "wattage": 40},
    {"sl_id": "AM055", "mac": "00124B00PLACEHOLDER0055", "latitude": 38.8656062, "longitude": 21.1719686, "wattage": 40},
    {"sl_id": "AM056", "mac": "00124B00193F3F88", "latitude": 38.8656563, "longitude": 21.1720695, "wattage": 40},
    {"sl_id": "AM057", "mac": "00124B00193F3FB7", "latitude": 38.8657063, "longitude": 21.1721704, "wattage": 40},
    {"sl_id": "AM058", "mac": "00124B001CDE966D", "latitude": 38.8657563, "longitude": 21.1722713, "wattage": 40},
    {"sl_id": "AM059", "mac": "00124B001CE327D8", "latitude": 38.8658064, "longitude": 21.1723723, "wattage": 40},
    {"sl_id": "AM060", "mac": "00124B001CE325ED", "latitude": 38.8658564, "longitude": 21.1724732, "wattage": 40},
    {"sl_id": "AM061", "mac": "00124B001CDE95CE", "latitude": 38.8659065, "longitude": 21.1725741, "wattage": 40},
    {"sl_id": "AM062", "mac": "00124B001CE32799", "latitude": 38.8659565, "longitude": 21.172675, "wattage": 40},
    {"sl_id": "AM063", "mac": "00124B001CE324CC", "latitude": 38.8660065, "longitude": 21.1727759, "wattage": 40},
    {"sl_id": "AM064", "mac": "00124B001CE32684", "latitude": 38.8660566, "longitude": 21.1728769, "wattage": 40},
    {"sl_id": "AM065", "mac": "00124B001CE32665", "latitude": 38.8661066, "longitude": 21.1729778, "wattage": 40},
    {"sl_id": "AM066", "mac": "00124B001CE326E8", "latitude": 38.8661522, "longitude": 21.1730819, "wattage": 40},
    {"sl_id": "AM067", "mac": "00124B001CE32545", "latitude": 38.8661928, "longitude": 21.1731895, "wattage": 40},
    {"sl_id": "AM068", "mac": "00124B001CE32661", "latitude": 38.8662335, "longitude": 21.1732972, "wattage": 40},
    {"sl_id": "AM069", "mac": "00124B001CDE967C", "latitude": 38.8662741, "longitude": 21.1734048, "wattage": 40},
    {"sl_id": "AM070", "mac": "00124B001CDE967D", "latitude": 38.8663148, "longitude": 21.1735125, "wattage": 40},
    {"sl_id": "AM071", "mac": "00124B001CE32566", "latitude": 38.8663554, "longitude": 21.1736202, "wattage": 40},
    {"sl_id": "AM072", "mac": "00124B001CE3277C", "latitude": 38.8663961, "longitude": 21.1737278, "wattage": 40},
    {"sl_id": "AM073", "mac": "00124B001CE327CE", "latitude": 38.8664367, "longitude": 21.1738355, "wattage": 40},
    {"sl_id": "AM074", "mac": "00124B001CDE962E", "latitude": 38.8664773, "longitude": 21.1739431, "wattage": 40},
    {"sl_id": "AM075", "mac": "00124B001CDE9595", "latitude": 38.866518, "longitude": 21.1740508, "wattage": 40},
    {"sl_id": "AM076", "mac": "00124B001CE32506", "latitude": 38.8665586, "longitude": 21.1741584, "wattage": 40},
    {"sl_id": "AM077", "mac": "00124B00193F3FAD", "latitude": 38.8666101, "longitude": 21.1742581, "wattage": 40},
    {"sl_id": "AM078", "mac": "00124B001CE32535", "latitude": 38.8666617, "longitude": 21.1743577, "wattage": 40},
    {"sl_id": "AM079", "mac": "00124B001CDE9648", "latitude": 38.8667133, "longitude": 21.1744573, "wattage": 40},
    {"sl_id": "AM080", "mac": "00124B001CE32516", "latitude": 38.8667649, "longitude": 21.174557, "wattage": 40},
    {"sl_id": "AM081", "mac": "00124B001CE32519", "latitude": 38.8668165, "longitude": 21.1746566, "wattage": 40},
    {"sl_id": "AM082", "mac": "00124B001CE32550", "latitude": 38.8668681, "longitude": 21.1747562, "wattage": 40},
    {"sl_id": "AM083", "mac": "00124B001CDE961F", "latitude": 38.8669197, "longitude": 21.1748558, "wattage": 40},
    {"sl_id": "AM084", "mac": "00124B001CDE9641", "latitude": 38.8669713, "longitude": 21.1749554, "wattage": 40},
    {"sl_id": "AM085", "mac": "00124B001CDE9664", "latitude": 38.867023, "longitude": 21.175055, "wattage": 40},
    {"sl_id": "AM086", "mac": "00124B001CDE95B8", "latitude": 38.8670936, "longitude": 21.1751292, "wattage": 40},
    {"sl_id": "AM087", "mac": "00124B001CDE95C9", "latitude": 38.867173, "longitude": 21.1751917, "wattage": 40},
    {"sl_id": "AM088", "mac": "00124B001CE32531", "latitude": 38.8672524, "longitude": 21.1752542, "wattage": 40},
    {"sl_id": "AM089", "mac": "00124B001CDE95D1", "latitude": 38.8673319, "longitude": 21.1753167, "wattage": 40},
    {"sl_id": "AM090", "mac": "00124B001CE324E7", "latitude": 38.8674113, "longitude": 21.1753792, "wattage": 40},
    {"sl_id": "AM091", "mac": "00124B001CE32555", "latitude": 38.8674907, "longitude": 21.1754417, "wattage": 40},
    {"sl_id": "AM092", "mac": "00124B001CE32515", "latitude": 38.8675702, "longitude": 21.1755042, "wattage": 40},
    {"sl_id": "AM093", "mac": "00124B001CE3268A", "latitude": 38.8676496, "longitude": 21.1755667, "wattage": 40},
    {"sl_id": "AM094", "mac": "00124B001CE32641", "latitude": 38.8677318, "longitude": 21.1756207, "wattage": 40},
    {"sl_id": "AM095", "mac": "00124B001CDE9597", "latitude": 38.8678226, "longitude": 21.1756473, "wattage": 40},
    {"sl_id": "AM096", "mac": "00124B001CE3265A", "latitude": 38.8679134, "longitude": 21.175674, "wattage": 40},
    {"sl_id": "AM097", "mac": "00124B001CE32574", "latitude": 38.8680042, "longitude": 21.1757007, "wattage": 40},
    {"sl_id": "AM098", "mac": "00124B00193F3FBD", "latitude": 38.868095, "longitude": 21.1757274, "wattage": 40},
    {"sl_id": "AM099", "mac": "00124B001CE3262E", "latitude": 38.8681858, "longitude": 21.175754, "wattage": 40},
    {"sl_id": "AM100", "mac": "00124B001CE325D2", "latitude": 38.8682766, "longitude": 21.1757807, "wattage": 40},
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
