from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from datetime import datetime, timezone

app = FastAPI(
    title="Luminaires API – Δήμος Αμφιλοχίας",
    description="Geolocation and real-time status for 100 street luminaires in Amfilochia.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Luminaire registry – 100 LCU devices
#
# Coordinates generated along the route:
#   Start: 38.863446022936316, 21.166522068248813
#   End:   38.86797971908025,  21.175660592048647
#
# NOTE: Entries AM048–AM055 have placeholder MACs because rows 48–55
# were missing from the source document. Replace with actual MACs once
# the original spreadsheet is available.
# ---------------------------------------------------------------------------
LUMINAIRES: list[dict] = [
    {"sl_id": "AM001", "mac": "00124B001CE3258C", "latitude": 38.863446, "longitude": 21.1665221, "wattage": 40},
    {"sl_id": "AM002", "mac": "00124B001CE32616", "latitude": 38.8634918, "longitude": 21.1666144, "wattage": 40},
    {"sl_id": "AM003", "mac": "00124B001CE325C1", "latitude": 38.8635376, "longitude": 21.1667067, "wattage": 40},
    {"sl_id": "AM004", "mac": "00124B001CE32685", "latitude": 38.8635834, "longitude": 21.166799, "wattage": 40},
    {"sl_id": "AM005", "mac": "00124B001CE32682", "latitude": 38.8636292, "longitude": 21.1668913, "wattage": 40},
    {"sl_id": "AM006", "mac": "00124B001CDE960A", "latitude": 38.863675, "longitude": 21.1669836, "wattage": 40},
    {"sl_id": "AM007", "mac": "00124B001CDE965A", "latitude": 38.8637208, "longitude": 21.1670759, "wattage": 40},
    {"sl_id": "AM008", "mac": "00124B001CE32660", "latitude": 38.8637666, "longitude": 21.1671682, "wattage": 40},
    {"sl_id": "AM009", "mac": "00124B001CE32560", "latitude": 38.8638124, "longitude": 21.1672605, "wattage": 40},
    {"sl_id": "AM010", "mac": "00124B001CE32540", "latitude": 38.8638582, "longitude": 21.1673528, "wattage": 40},
    {"sl_id": "AM011", "mac": "00124B001CDE95BE", "latitude": 38.863904, "longitude": 21.1674452, "wattage": 40},
    {"sl_id": "AM012", "mac": "00124B001CE32604", "latitude": 38.8639498, "longitude": 21.1675375, "wattage": 40},
    {"sl_id": "AM013", "mac": "00124B001CE327A8", "latitude": 38.8639956, "longitude": 21.1676298, "wattage": 40},
    {"sl_id": "AM014", "mac": "00124B001CE3272E", "latitude": 38.8640414, "longitude": 21.1677221, "wattage": 40},
    {"sl_id": "AM015", "mac": "00124B001CE32586", "latitude": 38.8640872, "longitude": 21.1678144, "wattage": 40},
    {"sl_id": "AM016", "mac": "00124B001CE324C5", "latitude": 38.8641329, "longitude": 21.1679067, "wattage": 40},
    {"sl_id": "AM017", "mac": "00124B001CE3271F", "latitude": 38.8641787, "longitude": 21.167999, "wattage": 40},
    {"sl_id": "AM018", "mac": "00124B001CE325C0", "latitude": 38.8642245, "longitude": 21.1680913, "wattage": 40},
    {"sl_id": "AM019", "mac": "00124B001CE32695", "latitude": 38.8642703, "longitude": 21.1681836, "wattage": 40},
    {"sl_id": "AM020", "mac": "00124B001CE32652", "latitude": 38.8643161, "longitude": 21.1682759, "wattage": 40},
    {"sl_id": "AM021", "mac": "00124B001CE32686", "latitude": 38.8643619, "longitude": 21.1683682, "wattage": 40},
    {"sl_id": "AM022", "mac": "00124B001CE326D6", "latitude": 38.8644077, "longitude": 21.1684605, "wattage": 40},
    {"sl_id": "AM023", "mac": "00124B00193F3FC1", "latitude": 38.8644535, "longitude": 21.1685529, "wattage": 40},
    {"sl_id": "AM024", "mac": "00124B001CE325DA", "latitude": 38.8644993, "longitude": 21.1686452, "wattage": 40},
    {"sl_id": "AM025", "mac": "00124B001CE32585", "latitude": 38.8645451, "longitude": 21.1687375, "wattage": 40},
    {"sl_id": "AM026", "mac": "00124B001CE325B0", "latitude": 38.8645909, "longitude": 21.1688298, "wattage": 40},
    {"sl_id": "AM027", "mac": "00124B001CE325E6", "latitude": 38.8646367, "longitude": 21.1689221, "wattage": 40},
    {"sl_id": "AM028", "mac": "00124B001CE32649", "latitude": 38.8646825, "longitude": 21.1690144, "wattage": 40},
    {"sl_id": "AM029", "mac": "00124B001CE32667", "latitude": 38.8647283, "longitude": 21.1691067, "wattage": 40},
    {"sl_id": "AM030", "mac": "00124B001CE325DB", "latitude": 38.8647741, "longitude": 21.169199, "wattage": 40},
    {"sl_id": "AM031", "mac": "00124B001CE32877", "latitude": 38.8648199, "longitude": 21.1692913, "wattage": 40},
    {"sl_id": "AM032", "mac": "00124B00193F3FB0", "latitude": 38.8648657, "longitude": 21.1693836, "wattage": 40},
    {"sl_id": "AM033", "mac": "00124B001CE325CF", "latitude": 38.8649115, "longitude": 21.1694759, "wattage": 40},
    {"sl_id": "AM034", "mac": "00124B001CDE95A1", "latitude": 38.8649573, "longitude": 21.1695682, "wattage": 40},
    {"sl_id": "AM035", "mac": "00124B001CE32790", "latitude": 38.865003, "longitude": 21.1696606, "wattage": 40},
    {"sl_id": "AM036", "mac": "00124B001CE3261E", "latitude": 38.8650488, "longitude": 21.1697529, "wattage": 40},
    {"sl_id": "AM037", "mac": "00124B001CE3266C", "latitude": 38.8650946, "longitude": 21.1698452, "wattage": 40},
    {"sl_id": "AM038", "mac": "00124B001CE32772", "latitude": 38.8651404, "longitude": 21.1699375, "wattage": 40},
    {"sl_id": "AM039", "mac": "00124B001CE32597", "latitude": 38.8651862, "longitude": 21.1700298, "wattage": 40},
    {"sl_id": "AM040", "mac": "00124B001CE3274B", "latitude": 38.865232, "longitude": 21.1701221, "wattage": 40},
    {"sl_id": "AM041", "mac": "00124B001CE32657", "latitude": 38.8652778, "longitude": 21.1702144, "wattage": 40},
    {"sl_id": "AM042", "mac": "00124B001CE3267E", "latitude": 38.8653236, "longitude": 21.1703067, "wattage": 40},
    {"sl_id": "AM043", "mac": "00124B001CE32738", "latitude": 38.8653694, "longitude": 21.170399, "wattage": 40},
    {"sl_id": "AM044", "mac": "00124B001CE326B8", "latitude": 38.8654152, "longitude": 21.1704913, "wattage": 40},
    {"sl_id": "AM045", "mac": "00124B001CE32609", "latitude": 38.865461, "longitude": 21.1705836, "wattage": 40},
    {"sl_id": "AM046", "mac": "00124B001CE325C8", "latitude": 38.8655068, "longitude": 21.1706759, "wattage": 40},
    {"sl_id": "AM047", "mac": "00124B001CE3263B", "latitude": 38.8655526, "longitude": 21.1707683, "wattage": 40},
    {"sl_id": "AM048", "mac": "00124B00PLACEHOLDER0048", "latitude": 38.8655984, "longitude": 21.1708606, "wattage": 40},
    {"sl_id": "AM049", "mac": "00124B00PLACEHOLDER0049", "latitude": 38.8656442, "longitude": 21.1709529, "wattage": 40},
    {"sl_id": "AM050", "mac": "00124B00PLACEHOLDER0050", "latitude": 38.86569, "longitude": 21.1710452, "wattage": 40},
    {"sl_id": "AM051", "mac": "00124B00PLACEHOLDER0051", "latitude": 38.8657358, "longitude": 21.1711375, "wattage": 40},
    {"sl_id": "AM052", "mac": "00124B00PLACEHOLDER0052", "latitude": 38.8657816, "longitude": 21.1712298, "wattage": 40},
    {"sl_id": "AM053", "mac": "00124B00PLACEHOLDER0053", "latitude": 38.8658274, "longitude": 21.1713221, "wattage": 40},
    {"sl_id": "AM054", "mac": "00124B00PLACEHOLDER0054", "latitude": 38.8658732, "longitude": 21.1714144, "wattage": 40},
    {"sl_id": "AM055", "mac": "00124B00PLACEHOLDER0055", "latitude": 38.8659189, "longitude": 21.1715067, "wattage": 40},
    {"sl_id": "AM056", "mac": "00124B00193F3F88", "latitude": 38.8659647, "longitude": 21.171599, "wattage": 40},
    {"sl_id": "AM057", "mac": "00124B00193F3FB7", "latitude": 38.8660105, "longitude": 21.1716913, "wattage": 40},
    {"sl_id": "AM058", "mac": "00124B001CDE966D", "latitude": 38.8660563, "longitude": 21.1717836, "wattage": 40},
    {"sl_id": "AM059", "mac": "00124B001CE327D8", "latitude": 38.8661021, "longitude": 21.171876, "wattage": 40},
    {"sl_id": "AM060", "mac": "00124B001CE325ED", "latitude": 38.8661479, "longitude": 21.1719683, "wattage": 40},
    {"sl_id": "AM061", "mac": "00124B001CDE95CE", "latitude": 38.8661937, "longitude": 21.1720606, "wattage": 40},
    {"sl_id": "AM062", "mac": "00124B001CE32799", "latitude": 38.8662395, "longitude": 21.1721529, "wattage": 40},
    {"sl_id": "AM063", "mac": "00124B001CE324CC", "latitude": 38.8662853, "longitude": 21.1722452, "wattage": 40},
    {"sl_id": "AM064", "mac": "00124B001CE32684", "latitude": 38.8663311, "longitude": 21.1723375, "wattage": 40},
    {"sl_id": "AM065", "mac": "00124B001CE32665", "latitude": 38.8663769, "longitude": 21.1724298, "wattage": 40},
    {"sl_id": "AM066", "mac": "00124B001CE326E8", "latitude": 38.8664227, "longitude": 21.1725221, "wattage": 40},
    {"sl_id": "AM067", "mac": "00124B001CE32545", "latitude": 38.8664685, "longitude": 21.1726144, "wattage": 40},
    {"sl_id": "AM068", "mac": "00124B001CE32661", "latitude": 38.8665143, "longitude": 21.1727067, "wattage": 40},
    {"sl_id": "AM069", "mac": "00124B001CDE967C", "latitude": 38.8665601, "longitude": 21.172799, "wattage": 40},
    {"sl_id": "AM070", "mac": "00124B001CDE967D", "latitude": 38.8666059, "longitude": 21.1728913, "wattage": 40},
    {"sl_id": "AM071", "mac": "00124B001CE32566", "latitude": 38.8666517, "longitude": 21.1729837, "wattage": 40},
    {"sl_id": "AM072", "mac": "00124B001CE3277C", "latitude": 38.8666975, "longitude": 21.173076, "wattage": 40},
    {"sl_id": "AM073", "mac": "00124B001CE327CE", "latitude": 38.8667433, "longitude": 21.1731683, "wattage": 40},
    {"sl_id": "AM074", "mac": "00124B001CDE962E", "latitude": 38.8667891, "longitude": 21.1732606, "wattage": 40},
    {"sl_id": "AM075", "mac": "00124B001CDE9595", "latitude": 38.8668348, "longitude": 21.1733529, "wattage": 40},
    {"sl_id": "AM076", "mac": "00124B001CE32506", "latitude": 38.8668806, "longitude": 21.1734452, "wattage": 40},
    {"sl_id": "AM077", "mac": "00124B00193F3FAD", "latitude": 38.8669264, "longitude": 21.1735375, "wattage": 40},
    {"sl_id": "AM078", "mac": "00124B001CE32535", "latitude": 38.8669722, "longitude": 21.1736298, "wattage": 40},
    {"sl_id": "AM079", "mac": "00124B001CDE9648", "latitude": 38.867018, "longitude": 21.1737221, "wattage": 40},
    {"sl_id": "AM080", "mac": "00124B001CE32516", "latitude": 38.8670638, "longitude": 21.1738144, "wattage": 40},
    {"sl_id": "AM081", "mac": "00124B001CE32519", "latitude": 38.8671096, "longitude": 21.1739067, "wattage": 40},
    {"sl_id": "AM082", "mac": "00124B001CE32550", "latitude": 38.8671554, "longitude": 21.173999, "wattage": 40},
    {"sl_id": "AM083", "mac": "00124B001CDE961F", "latitude": 38.8672012, "longitude": 21.1740914, "wattage": 40},
    {"sl_id": "AM084", "mac": "00124B001CDE9641", "latitude": 38.867247, "longitude": 21.1741837, "wattage": 40},
    {"sl_id": "AM085", "mac": "00124B001CDE9664", "latitude": 38.8672928, "longitude": 21.174276, "wattage": 40},
    {"sl_id": "AM086", "mac": "00124B001CDE95B8", "latitude": 38.8673386, "longitude": 21.1743683, "wattage": 40},
    {"sl_id": "AM087", "mac": "00124B001CDE95C9", "latitude": 38.8673844, "longitude": 21.1744606, "wattage": 40},
    {"sl_id": "AM088", "mac": "00124B001CE32531", "latitude": 38.8674302, "longitude": 21.1745529, "wattage": 40},
    {"sl_id": "AM089", "mac": "00124B001CDE95D1", "latitude": 38.867476, "longitude": 21.1746452, "wattage": 40},
    {"sl_id": "AM090", "mac": "00124B001CE324E7", "latitude": 38.8675218, "longitude": 21.1747375, "wattage": 40},
    {"sl_id": "AM091", "mac": "00124B001CE32555", "latitude": 38.8675676, "longitude": 21.1748298, "wattage": 40},
    {"sl_id": "AM092", "mac": "00124B001CE32515", "latitude": 38.8676134, "longitude": 21.1749221, "wattage": 40},
    {"sl_id": "AM093", "mac": "00124B001CE3268A", "latitude": 38.8676592, "longitude": 21.1750144, "wattage": 40},
    {"sl_id": "AM094", "mac": "00124B001CE32641", "latitude": 38.8677049, "longitude": 21.1751067, "wattage": 40},
    {"sl_id": "AM095", "mac": "00124B001CDE9597", "latitude": 38.8677507, "longitude": 21.1751991, "wattage": 40},
    {"sl_id": "AM096", "mac": "00124B001CE3265A", "latitude": 38.8677965, "longitude": 21.1752914, "wattage": 40},
    {"sl_id": "AM097", "mac": "00124B001CE32574", "latitude": 38.8678423, "longitude": 21.1753837, "wattage": 40},
    {"sl_id": "AM098", "mac": "00124B00193F3FBD", "latitude": 38.8678881, "longitude": 21.175476, "wattage": 40},
    {"sl_id": "AM099", "mac": "00124B001CE3262E", "latitude": 38.8679339, "longitude": 21.1755683, "wattage": 40},
    {"sl_id": "AM100", "mac": "00124B001CE325D2", "latitude": 38.8679797, "longitude": 21.1756606, "wattage": 40},
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
