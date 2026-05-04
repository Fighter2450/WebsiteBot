import googlemaps
import time
import re

CHAIN_KEYWORDS = {
    "mcdonald", "subway", "starbucks", "burger king", "wendy", "taco bell",
    "chick-fil-a", "chickfila", "dunkin", "domino", "pizza hut", "kfc",
    "popeyes", "chipotle", "panda express", "five guys", "shake shack",
    "in-n-out", "whataburger", "sonic", "dairy queen", "hardee", "carl's jr",
    "jack in the box", "panera", "olive garden", "applebee", "chili's",
    "ihop", "denny", "waffle house", "cracker barrel", "red lobster",
    "outback", "longhorn", "texas roadhouse", "buffalo wild", "hooters",
    "jersey mike", "jimmy john", "firehouse", "potbelly", "wingstop",
    "raising cane", "culver", "del taco", "el pollo", "little caesar",
    "papa john", "papa murphy", "round table", "cicis", "moe's", "qdoba",
    "noodles", "zaxby", "church's chicken", "bojangles", "golden corral",
}


def _is_chain(name: str) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in CHAIN_KEYWORDS)


# Residential neighborhood coordinates per city — avoids downtown chains
CITY_NEIGHBORHOODS = {
    "New York City, NY":  [(40.6782, -73.9442), (40.7282, -73.7949), (40.8448, -73.8648)],
    "Los Angeles, CA":    [(34.0195, -118.4912), (34.0736, -118.2387), (33.9731, -118.2479)],
    "Chicago, IL":        [(41.9484, -87.6553), (41.8369, -87.6234), (41.7508, -87.5940)],
    "Houston, TX":        [(29.7372, -95.4739), (29.8047, -95.3677), (29.6697, -95.2770)],
    "Phoenix, AZ":        [(33.5722, -112.0901), (33.4152, -111.9318), (33.4942, -112.1420)],
    "Philadelphia, PA":   [(39.9284, -75.1520), (40.0379, -75.1180), (39.9181, -75.2271)],
    "San Antonio, TX":    [(29.4813, -98.5144), (29.3697, -98.4592), (29.5266, -98.3779)],
    "San Diego, CA":      [(32.7474, -117.1198), (32.6780, -117.0827), (32.8025, -117.1490)],
    "Dallas, TX":         [(32.8208, -96.8714), (32.7373, -96.9934), (32.7068, -96.7906)],
    "San Jose, CA":       [(37.3688, -121.9249), (37.2967, -121.8286), (37.3861, -121.8353)],
    "Austin, TX":         [(30.2500, -97.7665), (30.3077, -97.7431), (30.2135, -97.8450)],
    "Jacksonville, FL":   [(30.3322, -81.6557), (30.2969, -81.7226), (30.3961, -81.5678)],
    "Fort Worth, TX":     [(32.7555, -97.3308), (32.7041, -97.4315), (32.8180, -97.2697)],
    "Columbus, OH":       [(39.9612, -82.9988), (39.9848, -82.8937), (39.9154, -83.0632)],
    "Charlotte, NC":      [(35.2271, -80.8431), (35.1796, -80.8692), (35.3078, -80.7470)],
    "Indianapolis, IN":   [(39.7684, -86.1581), (39.8234, -86.1527), (39.7133, -86.2317)],
    "San Francisco, CA":  [(37.7594, -122.4869), (37.7282, -122.4752), (37.7880, -122.4184)],
    "Seattle, WA":        [(47.6062, -122.3321), (47.6588, -122.3680), (47.5480, -122.3865)],
    "Denver, CO":         [(39.7392, -104.9903), (39.7621, -104.9391), (39.6966, -105.0252)],
    "Nashville, TN":      [(36.1627, -86.7816), (36.1189, -86.8553), (36.2134, -86.7290)],
    "Oklahoma City, OK":  [(35.4676, -97.5164), (35.5246, -97.4707), (35.4098, -97.5942)],
    "El Paso, TX":        [(31.7619, -106.4850), (31.8257, -106.5685), (31.6950, -106.3776)],
    "Washington, DC":     [(38.9072, -77.0369), (38.8951, -77.0268), (38.9340, -77.0629)],
    "Las Vegas, NV":      [(36.1699, -115.1398), (36.2120, -115.2357), (36.0974, -115.1722)],
    "Louisville, KY":     [(38.2527, -85.7585), (38.2934, -85.6629), (38.1974, -85.8143)],
}

DETAIL_FIELDS = [
    "name", "place_id", "formatted_address", "formatted_phone_number",
    "website", "opening_hours", "rating", "user_ratings_total", "reviews", "type"
]


def _offset_coords(lat: float, lng: float, km: float) -> list[tuple]:
    """Return 8 points evenly spread ~km kilometres from the centre.
    Avoids the tourist/commercial city centre where every business has a website."""
    import math
    delta_lat = km / 111.0
    delta_lng = km / (111.0 * math.cos(math.radians(lat)))
    offsets = [
        ( delta_lat,  0),           # N
        (-delta_lat,  0),           # S
        ( 0,          delta_lng),   # E
        ( 0,         -delta_lng),   # W
        ( delta_lat * 0.7,  delta_lng * 0.7),   # NE
        (-delta_lat * 0.7,  delta_lng * 0.7),   # SE
        (-delta_lat * 0.7, -delta_lng * 0.7),   # SW
        ( delta_lat * 0.7, -delta_lng * 0.7),   # NW
    ]
    return [(lat + dlat, lng + dlng) for dlat, dlng in offsets]


def find_businesses_without_websites(api_key: str, city: str, business_type: str, limit: int = 60) -> list[dict]:
    """Search residential neighbourhoods for businesses with no website."""
    gmaps = googlemaps.Client(key=api_key)

    # Use hardcoded residential coords where available, otherwise spread 8
    # points ~5 km from city centre to avoid the saturated downtown core.
    if city in CITY_NEIGHBORHOODS:
        neighborhoods = CITY_NEIGHBORHOODS[city]
    else:
        geo = gmaps.geocode(city)
        if not geo:
            print(f"  [warn] Could not geocode {city} — skipping")
            return []
        loc = geo[0]["geometry"]["location"]
        center_lat, center_lng = loc["lat"], loc["lng"]
        # Search centre + 8 points at 5 km (residential ring).
        # 9 points is enough to find no-website businesses without timing out.
        neighborhoods = (
            [(center_lat, center_lng)] +
            _offset_coords(center_lat, center_lng, 5)
        )

    results = []
    seen_ids = set()
    deadline = time.time() + 90  # hard cap: stop searching after 90 seconds

    for lat, lng in neighborhoods:
        if len(results) >= limit or time.time() > deadline:
            break

        try:
            response = gmaps.places_nearby(
                location=(lat, lng),
                rank_by="distance",
                type=business_type,
            )
        except Exception as e:
            print(f"  [warn] places_nearby failed: {e}")
            continue

        candidates = response.get("results", [])
        if not candidates:
            continue

        for place in candidates:
            if len(results) >= limit or time.time() > deadline:
                break

            place_id = place["place_id"]
            if place_id in seen_ids:
                continue
            seen_ids.add(place_id)

            # Quick check — skip if the summary already shows a website
            if place.get("website"):
                continue

            try:
                detail = gmaps.place(place_id=place_id, fields=DETAIL_FIELDS).get("result", {})
            except Exception as e:
                print(f"  [warn] Could not fetch details for {place.get('name')}: {e}")
                continue

            if detail.get("website"):
                continue

            if _is_chain(detail.get("name", place.get("name", ""))):
                continue

            name = detail.get("name", place.get("name", ""))
            print(f"  [found] {name} — no website")
            results.append({
                "place_id": place_id,
                "name": name,
                "address": detail.get("formatted_address", ""),
                "phone": detail.get("formatted_phone_number", ""),
                "hours": detail.get("opening_hours", {}).get("weekday_text", []),
                "rating": detail.get("rating"),
                "review_count": detail.get("user_ratings_total", 0),
                "reviews": [r.get("text", "") for r in detail.get("reviews", [])[:3]],
                "category": business_type,
                "city": city,
            })

    if time.time() > deadline:
        print(f"  [warn] Search hit 90s deadline — returning {len(results)} results")
    return results
