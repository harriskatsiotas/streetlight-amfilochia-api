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
# extracted from Αμφιλοχία_φώτα.kmz, offset 4m to the RIGHT of travel
# direction to place luminaires at the road edge.
# Total route length: ~1025m, ~10.4m spacing between poles.
#
# NOTE: Entries AM048–AM055 have placeholder MACs because rows 48–55
# were missing from the source document. Replace with actual MACs once
# the original spreadsheet is available.
# ---------------------------------------------------------------------------
LUMINAIRES: list[dict] = [
    {"sl_id": "AM001", "mac": "00124B001CE3258C", "latitude": 38.8635508, "longitude": 21.1666054, "wattage": 40},
    {"sl_id": "AM002", "mac": "00124B001CE32616", "latitude": 38.8634742, "longitude": 21.1665371, "wattage": 40},
    {"sl_id": "AM003", "mac": "00124B001CE325C1", "latitude": 38.8633568, "longitude": 21.1665463, "wattage": 40},
    {"sl_id": "AM004", "mac": "00124B001CE32685", "latitude": 38.8633139, "longitude": 21.166685, "wattage": 40},
    {"sl_id": "AM005", "mac": "00124B001CE32682", "latitude": 38.8633687, "longitude": 21.1668272, "wattage": 40},
    {"sl_id": "AM006", "mac": "00124B001CDE960A", "latitude": 38.863426, "longitude": 21.1668445, "wattage": 40},
    {"sl_id": "AM007", "mac": "00124B001CDE965A", "latitude": 38.8634701, "longitude": 21.1669498, "wattage": 40},
    {"sl_id": "AM008", "mac": "00124B001CE32660", "latitude": 38.863487, "longitude": 21.1670467, "wattage": 40},
    {"sl_id": "AM009", "mac": "00124B001CE32560", "latitude": 38.8635104, "longitude": 21.167179, "wattage": 40},
    {"sl_id": "AM010", "mac": "00124B001CE32540", "latitude": 38.863554, "longitude": 21.1672847, "wattage": 40},
    {"sl_id": "AM011", "mac": "00124B001CDE95BE", "latitude": 38.8635976, "longitude": 21.1673904, "wattage": 40},
    {"sl_id": "AM012", "mac": "00124B001CE32604", "latitude": 38.8636412, "longitude": 21.1674962, "wattage": 40},
    {"sl_id": "AM013", "mac": "00124B001CE327A8", "latitude": 38.8636848, "longitude": 21.1676019, "wattage": 40},
    {"sl_id": "AM014", "mac": "00124B001CE3272E", "latitude": 38.8637284, "longitude": 21.1677076, "wattage": 40},
    {"sl_id": "AM015", "mac": "00124B001CE32586", "latitude": 38.8637719, "longitude": 21.1678134, "wattage": 40},
    {"sl_id": "AM016", "mac": "00124B001CE324C5", "latitude": 38.8638155, "longitude": 21.1679191, "wattage": 40},
    {"sl_id": "AM017", "mac": "00124B001CE3271F", "latitude": 38.8638659, "longitude": 21.1680237, "wattage": 40},
    {"sl_id": "AM018", "mac": "00124B001CE325C0", "latitude": 38.8639154, "longitude": 21.1681251, "wattage": 40},
    {"sl_id": "AM019", "mac": "00124B001CE32695", "latitude": 38.8639649, "longitude": 21.1682264, "wattage": 40},
    {"sl_id": "AM020", "mac": "00124B001CE32652", "latitude": 38.8640144, "longitude": 21.1683278, "wattage": 40},
    {"sl_id": "AM021", "mac": "00124B001CE32686", "latitude": 38.8640639, "longitude": 21.1684291, "wattage": 40},
    {"sl_id": "AM022", "mac": "00124B001CE326D6", "latitude": 38.8641134, "longitude": 21.1685305, "wattage": 40},
    {"sl_id": "AM023", "mac": "00124B00193F3FC1", "latitude": 38.8641629, "longitude": 21.1686318, "wattage": 40},
    {"sl_id": "AM024", "mac": "00124B001CE325DA", "latitude": 38.8642125, "longitude": 21.1687331, "wattage": 40},
    {"sl_id": "AM025", "mac": "00124B001CE32585", "latitude": 38.8642576, "longitude": 21.1688352, "wattage": 40},
    {"sl_id": "AM026", "mac": "00124B001CE325B0", "latitude": 38.8643032, "longitude": 21.1689395, "wattage": 40},
    {"sl_id": "AM027", "mac": "00124B001CE325E6", "latitude": 38.8643489, "longitude": 21.1690438, "wattage": 40},
    {"sl_id": "AM028", "mac": "00124B001CE32649", "latitude": 38.8643945, "longitude": 21.1691481, "wattage": 40},
    {"sl_id": "AM029", "mac": "00124B001CE32667", "latitude": 38.8644402, "longitude": 21.1692524, "wattage": 40},
    {"sl_id": "AM030", "mac": "00124B001CE325DB", "latitude": 38.8644858, "longitude": 21.1693567, "wattage": 40},
    {"sl_id": "AM031", "mac": "00124B001CE32877", "latitude": 38.8645315, "longitude": 21.169461, "wattage": 40},
    {"sl_id": "AM032", "mac": "00124B00193F3FB0", "latitude": 38.8645771, "longitude": 21.1695653, "wattage": 40},
    {"sl_id": "AM033", "mac": "00124B001CE325CF", "latitude": 38.8646152, "longitude": 21.1696684, "wattage": 40},
    {"sl_id": "AM034", "mac": "00124B001CDE95A1", "latitude": 38.8646513, "longitude": 21.1697787, "wattage": 40},
    {"sl_id": "AM035", "mac": "00124B001CE32790", "latitude": 38.8646874, "longitude": 21.169889, "wattage": 40},
    {"sl_id": "AM036", "mac": "00124B001CE3261E", "latitude": 38.8647235, "longitude": 21.1699993, "wattage": 40},
    {"sl_id": "AM037", "mac": "00124B001CE3266C", "latitude": 38.8647595, "longitude": 21.1701096, "wattage": 40},
    {"sl_id": "AM038", "mac": "00124B001CE32772", "latitude": 38.8647956, "longitude": 21.1702199, "wattage": 40},
    {"sl_id": "AM039", "mac": "00124B001CE32597", "latitude": 38.8648317, "longitude": 21.1703302, "wattage": 40},
    {"sl_id": "AM040", "mac": "00124B001CE3274B", "latitude": 38.8648678, "longitude": 21.1704406, "wattage": 40},
    {"sl_id": "AM041", "mac": "00124B001CE32657", "latitude": 38.8649038, "longitude": 21.1705509, "wattage": 40},
    {"sl_id": "AM042", "mac": "00124B001CE3267E", "latitude": 38.8649399, "longitude": 21.1706612, "wattage": 40},
    {"sl_id": "AM043", "mac": "00124B001CE32738", "latitude": 38.8649877, "longitude": 21.1707716, "wattage": 40},
    {"sl_id": "AM044", "mac": "00124B001CE326B8", "latitude": 38.8650365, "longitude": 21.1708736, "wattage": 40},
    {"sl_id": "AM045", "mac": "00124B001CE32609", "latitude": 38.8650852, "longitude": 21.1709756, "wattage": 40},
    {"sl_id": "AM046", "mac": "00124B001CE325C8", "latitude": 38.8651339, "longitude": 21.1710776, "wattage": 40},
    {"sl_id": "AM047", "mac": "00124B001CE3263B", "latitude": 38.8651826, "longitude": 21.1711795, "wattage": 40},
    {"sl_id": "AM048", "mac": "00124B00PLACEHOLDER0048", "latitude": 38.8652313, "longitude": 21.1712815, "wattage": 40},
    {"sl_id": "AM049", "mac": "00124B00PLACEHOLDER0049", "latitude": 38.86528, "longitude": 21.1713835, "wattage": 40},
    {"sl_id": "AM050", "mac": "00124B00PLACEHOLDER0050", "latitude": 38.8653288, "longitude": 21.1714855, "wattage": 40},
    {"sl_id": "AM051", "mac": "00124B00PLACEHOLDER0051", "latitude": 38.8653775, "longitude": 21.1715874, "wattage": 40},
    {"sl_id": "AM052", "mac": "00124B00PLACEHOLDER0052", "latitude": 38.8654262, "longitude": 21.1716894, "wattage": 40},
    {"sl_id": "AM053", "mac": "00124B00PLACEHOLDER0053", "latitude": 38.8654758, "longitude": 21.1717916, "wattage": 40},
    {"sl_id": "AM054", "mac": "00124B00PLACEHOLDER0054", "latitude": 38.8655259, "longitude": 21.1718925, "wattage": 40},
    {"sl_id": "AM055", "mac": "00124B00PLACEHOLDER0055", "latitude": 38.8655759, "longitude": 21.1719934, "wattage": 40},
    {"sl_id": "AM056", "mac": "00124B00193F3F88", "latitude": 38.8656259, "longitude": 21.1720943, "wattage": 40},
    {"sl_id": "AM057", "mac": "00124B00193F3FB7", "latitude": 38.865676, "longitude": 21.1721952, "wattage": 40},
    {"sl_id": "AM058", "mac": "00124B001CDE966D", "latitude": 38.865726, "longitude": 21.1722962, "wattage": 40},
    {"sl_id": "AM059", "mac": "00124B001CE327D8", "latitude": 38.865776, "longitude": 21.1723971, "wattage": 40},
    {"sl_id": "AM060", "mac": "00124B001CE325ED", "latitude": 38.8658261, "longitude": 21.172498, "wattage": 40},
    {"sl_id": "AM061", "mac": "00124B001CDE95CE", "latitude": 38.8658761, "longitude": 21.1725989, "wattage": 40},
    {"sl_id": "AM062", "mac": "00124B001CE32799", "latitude": 38.8659261, "longitude": 21.1726998, "wattage": 40},
    {"sl_id": "AM063", "mac": "00124B001CE324CC", "latitude": 38.8659762, "longitude": 21.1728008, "wattage": 40},
    {"sl_id": "AM064", "mac": "00124B001CE32684", "latitude": 38.8660262, "longitude": 21.1729017, "wattage": 40},
    {"sl_id": "AM065", "mac": "00124B001CE32665", "latitude": 38.8660763, "longitude": 21.1730026, "wattage": 40},
    {"sl_id": "AM066", "mac": "00124B001CE326E8", "latitude": 38.8661198, "longitude": 21.173102, "wattage": 40},
    {"sl_id": "AM067", "mac": "00124B001CE32545", "latitude": 38.8661605, "longitude": 21.1732097, "wattage": 40},
    {"sl_id": "AM068", "mac": "00124B001CE32661", "latitude": 38.8662011, "longitude": 21.1733174, "wattage": 40},
    {"sl_id": "AM069", "mac": "00124B001CDE967C", "latitude": 38.8662418, "longitude": 21.173425, "wattage": 40},
    {"sl_id": "AM070", "mac": "00124B001CDE967D", "latitude": 38.8662824, "longitude": 21.1735327, "wattage": 40},
    {"sl_id": "AM071", "mac": "00124B001CE32566", "latitude": 38.866323, "longitude": 21.1736403, "wattage": 40},
    {"sl_id": "AM072", "mac": "00124B001CE3277C", "latitude": 38.8663637, "longitude": 21.173748, "wattage": 40},
    {"sl_id": "AM073", "mac": "00124B001CE327CE", "latitude": 38.8664043, "longitude": 21.1738556, "wattage": 40},
    {"sl_id": "AM074", "mac": "00124B001CDE962E", "latitude": 38.866445, "longitude": 21.1739633, "wattage": 40},
    {"sl_id": "AM075", "mac": "00124B001CDE9595", "latitude": 38.8664856, "longitude": 21.1740709, "wattage": 40},
    {"sl_id": "AM076", "mac": "00124B001CE32506", "latitude": 38.8665263, "longitude": 21.1741786, "wattage": 40},
    {"sl_id": "AM077", "mac": "00124B00193F3FAD", "latitude": 38.8665801, "longitude": 21.1742837, "wattage": 40},
    {"sl_id": "AM078", "mac": "00124B001CE32535", "latitude": 38.8666318, "longitude": 21.1743833, "wattage": 40},
    {"sl_id": "AM079", "mac": "00124B001CDE9648", "latitude": 38.8666834, "longitude": 21.1744829, "wattage": 40},
    {"sl_id": "AM080", "mac": "00124B001CE32516", "latitude": 38.866735, "longitude": 21.1745825, "wattage": 40},
    {"sl_id": "AM081", "mac": "00124B001CE32519", "latitude": 38.8667866, "longitude": 21.1746822, "wattage": 40},
    {"sl_id": "AM082", "mac": "00124B001CE32550", "latitude": 38.8668382, "longitude": 21.1747818, "wattage": 40},
    {"sl_id": "AM083", "mac": "00124B001CDE961F", "latitude": 38.8668898, "longitude": 21.1748814, "wattage": 40},
    {"sl_id": "AM084", "mac": "00124B001CDE9641", "latitude": 38.8669414, "longitude": 21.174981, "wattage": 40},
    {"sl_id": "AM085", "mac": "00124B001CDE9664", "latitude": 38.866993, "longitude": 21.1750806, "wattage": 40},
    {"sl_id": "AM086", "mac": "00124B001CDE95B8", "latitude": 38.8670748, "longitude": 21.1751686, "wattage": 40},
    {"sl_id": "AM087", "mac": "00124B001CDE95C9", "latitude": 38.8671542, "longitude": 21.1752311, "wattage": 40},
    {"sl_id": "AM088", "mac": "00124B001CE32531", "latitude": 38.8672336, "longitude": 21.1752936, "wattage": 40},
    {"sl_id": "AM089", "mac": "00124B001CDE95D1", "latitude": 38.8673131, "longitude": 21.1753561, "wattage": 40},
    {"sl_id": "AM090", "mac": "00124B001CE324E7", "latitude": 38.8673925, "longitude": 21.1754186, "wattage": 40},
    {"sl_id": "AM091", "mac": "00124B001CE32555", "latitude": 38.8674719, "longitude": 21.1754811, "wattage": 40},
    {"sl_id": "AM092", "mac": "00124B001CE32515", "latitude": 38.8675514, "longitude": 21.1755436, "wattage": 40},
    {"sl_id": "AM093", "mac": "00124B001CE3268A", "latitude": 38.8676308, "longitude": 21.1756061, "wattage": 40},
    {"sl_id": "AM094", "mac": "00124B001CE32641", "latitude": 38.8677237, "longitude": 21.1756657, "wattage": 40},
    {"sl_id": "AM095", "mac": "00124B001CDE9597", "latitude": 38.8678146, "longitude": 21.1756924, "wattage": 40},
    {"sl_id": "AM096", "mac": "00124B001CE3265A", "latitude": 38.8679054, "longitude": 21.1757191, "wattage": 40},
    {"sl_id": "AM097", "mac": "00124B001CE32574", "latitude": 38.8679962, "longitude": 21.1757457, "wattage": 40},
    {"sl_id": "AM098", "mac": "00124B00193F3FBD", "latitude": 38.868087, "longitude": 21.1757724, "wattage": 40},
    {"sl_id": "AM099", "mac": "00124B001CE3262E", "latitude": 38.8681778, "longitude": 21.1757991, "wattage": 40},
    {"sl_id": "AM100", "mac": "00124B001CE325D2", "latitude": 38.8682686, "longitude": 21.1758257, "wattage": 40},
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
