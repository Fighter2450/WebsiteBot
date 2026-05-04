"""
World cities list with coordinates and language.
Format: "City, Country" -> {lat, lng, lang, country}
"""

WORLD_CITIES = {
    # ══ TIER 1 — Highest opportunity (low website penetration, large populations) ══

    # ── AFRICA ────────────────────────────────────────────────────────
    "Lagos, Nigeria":             {"lat": 6.5244,   "lng": 3.3792,     "lang": "en", "country": "NG"},
    "Nairobi, Kenya":             {"lat": -1.2921,  "lng": 36.8219,    "lang": "en", "country": "KE"},
    "Johannesburg, South Africa": {"lat": -26.2041, "lng": 28.0473,    "lang": "en", "country": "ZA"},
    "Cape Town, South Africa":    {"lat": -33.9249, "lng": 18.4241,    "lang": "en", "country": "ZA"},
    "Cairo, Egypt":               {"lat": 30.0444,  "lng": 31.2357,    "lang": "ar", "country": "EG"},

    # ── SOUTHEAST ASIA ────────────────────────────────────────────────
    "Jakarta, Indonesia":     {"lat": -6.2088,  "lng": 106.8456,   "lang": "id", "country": "ID"},
    "Bali, Indonesia":        {"lat": -8.3405,  "lng": 115.0920,   "lang": "id", "country": "ID"},
    "Manila, Philippines":    {"lat": 14.5995,  "lng": 120.9842,   "lang": "en", "country": "PH"},
    "Cebu, Philippines":      {"lat": 10.3157,  "lng": 123.8854,   "lang": "en", "country": "PH"},
    "Bangkok, Thailand":      {"lat": 13.7563,  "lng": 100.5018,   "lang": "th", "country": "TH"},
    "Chiang Mai, Thailand":   {"lat": 18.7883,  "lng": 98.9853,    "lang": "th", "country": "TH"},
    "Kuala Lumpur, Malaysia": {"lat": 3.1390,   "lng": 101.6869,   "lang": "en", "country": "MY"},

    # ── INDIA ─────────────────────────────────────────────────────────
    "Mumbai, India":          {"lat": 19.0760,  "lng": 72.8777,    "lang": "en", "country": "IN"},
    "Delhi, India":           {"lat": 28.7041,  "lng": 77.1025,    "lang": "en", "country": "IN"},
    "Bangalore, India":       {"lat": 12.9716,  "lng": 77.5946,    "lang": "en", "country": "IN"},
    "Hyderabad, India":       {"lat": 17.3850,  "lng": 78.4867,    "lang": "en", "country": "IN"},
    "Chennai, India":         {"lat": 13.0827,  "lng": 80.2707,    "lang": "en", "country": "IN"},
    "Pune, India":            {"lat": 18.5204,  "lng": 73.8567,    "lang": "en", "country": "IN"},

    # ── LATIN AMERICA ─────────────────────────────────────────────────
    "Mexico City, Mexico":    {"lat": 19.4326,  "lng": -99.1332,   "lang": "es", "country": "MX"},
    "Guadalajara, Mexico":    {"lat": 20.6597,  "lng": -103.3496,  "lang": "es", "country": "MX"},
    "Monterrey, Mexico":      {"lat": 25.6866,  "lng": -100.3161,  "lang": "es", "country": "MX"},
    "Tijuana, Mexico":        {"lat": 32.5149,  "lng": -117.0382,  "lang": "es", "country": "MX"},
    "Cancun, Mexico":         {"lat": 21.1619,  "lng": -86.8515,   "lang": "es", "country": "MX"},
    "Bogota, Colombia":       {"lat": 4.7110,   "lng": -74.0721,   "lang": "es", "country": "CO"},
    "Medellin, Colombia":     {"lat": 6.2442,   "lng": -75.5812,   "lang": "es", "country": "CO"},
    "Lima, Peru":             {"lat": -12.0464, "lng": -77.0428,   "lang": "es", "country": "PE"},
    "Buenos Aires, Argentina":{"lat": -34.6037, "lng": -58.3816,   "lang": "es", "country": "AR"},
    "Cordoba, Argentina":     {"lat": -31.4201, "lng": -64.1888,   "lang": "es", "country": "AR"},
    "Santiago, Chile":        {"lat": -33.4489, "lng": -70.6693,   "lang": "es", "country": "CL"},
    "Sao Paulo, Brazil":      {"lat": -23.5505, "lng": -46.6333,   "lang": "pt", "country": "BR"},
    "Rio de Janeiro, Brazil": {"lat": -22.9068, "lng": -43.1729,   "lang": "pt", "country": "BR"},
    "Brasilia, Brazil":       {"lat": -15.8267, "lng": -47.9218,   "lang": "pt", "country": "BR"},
    "Salvador, Brazil":       {"lat": -12.9714, "lng": -38.5014,   "lang": "pt", "country": "BR"},
    "Fortaleza, Brazil":      {"lat": -3.7172,  "lng": -38.5434,   "lang": "pt", "country": "BR"},

    # ── MIDDLE EAST ───────────────────────────────────────────────────
    "Riyadh, Saudi Arabia":   {"lat": 24.7136,  "lng": 46.6753,    "lang": "ar", "country": "SA"},
    "Jeddah, Saudi Arabia":   {"lat": 21.4858,  "lng": 39.1925,    "lang": "ar", "country": "SA"},
    "Dubai, UAE":             {"lat": 25.2048,  "lng": 55.2708,    "lang": "ar", "country": "AE"},
    "Abu Dhabi, UAE":         {"lat": 24.4539,  "lng": 54.3773,    "lang": "ar", "country": "AE"},
    "Istanbul, Turkey":       {"lat": 41.0082,  "lng": 28.9784,    "lang": "tr", "country": "TR"},
    "Ankara, Turkey":         {"lat": 39.9334,  "lng": 32.8597,    "lang": "tr", "country": "TR"},
    "Izmir, Turkey":          {"lat": 38.4192,  "lng": 27.1287,    "lang": "tr", "country": "TR"},

    # ══ TIER 2 — Medium opportunity ══════════════════════════════════

    # ── SOUTHERN / EASTERN EUROPE ─────────────────────────────────────
    "Rome, Italy":            {"lat": 41.9028,  "lng": 12.4964,    "lang": "it", "country": "IT"},
    "Milan, Italy":           {"lat": 45.4654,  "lng": 9.1859,     "lang": "it", "country": "IT"},
    "Naples, Italy":          {"lat": 40.8518,  "lng": 14.2681,    "lang": "it", "country": "IT"},
    "Turin, Italy":           {"lat": 45.0703,  "lng": 7.6869,     "lang": "it", "country": "IT"},
    "Florence, Italy":        {"lat": 43.7696,  "lng": 11.2558,    "lang": "it", "country": "IT"},
    "Madrid, Spain":          {"lat": 40.4168,  "lng": -3.7038,    "lang": "es", "country": "ES"},
    "Barcelona, Spain":       {"lat": 41.3851,  "lng": 2.1734,     "lang": "es", "country": "ES"},
    "Valencia, Spain":        {"lat": 39.4699,  "lng": -0.3763,    "lang": "es", "country": "ES"},
    "Seville, Spain":         {"lat": 37.3891,  "lng": -5.9845,    "lang": "es", "country": "ES"},
    "Lisbon, Portugal":       {"lat": 38.7223,  "lng": -9.1393,    "lang": "pt", "country": "PT"},
    "Porto, Portugal":        {"lat": 41.1579,  "lng": -8.6291,    "lang": "pt", "country": "PT"},
    "Athens, Greece":         {"lat": 37.9838,  "lng": 23.7275,    "lang": "el", "country": "GR"},
    "Warsaw, Poland":         {"lat": 52.2297,  "lng": 21.0122,    "lang": "pl", "country": "PL"},
    "Krakow, Poland":         {"lat": 50.0647,  "lng": 19.9450,    "lang": "pl", "country": "PL"},
    "Budapest, Hungary":      {"lat": 47.4979,  "lng": 19.0402,    "lang": "hu", "country": "HU"},
    "Bucharest, Romania":     {"lat": 44.4268,  "lng": 26.1025,    "lang": "ro", "country": "RO"},
    "Prague, Czech Republic": {"lat": 50.0755,  "lng": 14.4378,    "lang": "cs", "country": "CZ"},
    "Moscow, Russia":         {"lat": 55.7558,  "lng": 37.6173,    "lang": "ru", "country": "RU"},
    "Saint Petersburg, Russia":{"lat": 59.9311, "lng": 30.3609,    "lang": "ru", "country": "RU"},

    # ── WESTERN EUROPE ────────────────────────────────────────────────
    "Paris, France":          {"lat": 48.8566,  "lng": 2.3522,     "lang": "fr", "country": "FR"},
    "Lyon, France":           {"lat": 45.7640,  "lng": 4.8357,     "lang": "fr", "country": "FR"},
    "Marseille, France":      {"lat": 43.2965,  "lng": 5.3698,     "lang": "fr", "country": "FR"},
    "Toulouse, France":       {"lat": 43.6047,  "lng": 1.4442,     "lang": "fr", "country": "FR"},
    "Nice, France":           {"lat": 43.7102,  "lng": 7.2620,     "lang": "fr", "country": "FR"},
    "Brussels, Belgium":      {"lat": 50.8503,  "lng": 4.3517,     "lang": "fr", "country": "BE"},
    "Berlin, Germany":        {"lat": 52.5200,  "lng": 13.4050,    "lang": "de", "country": "DE"},
    "Munich, Germany":        {"lat": 48.1351,  "lng": 11.5820,    "lang": "de", "country": "DE"},
    "Hamburg, Germany":       {"lat": 53.5753,  "lng": 10.0153,    "lang": "de", "country": "DE"},
    "Frankfurt, Germany":     {"lat": 50.1109,  "lng": 8.6821,     "lang": "de", "country": "DE"},
    "Cologne, Germany":       {"lat": 50.9333,  "lng": 6.9500,     "lang": "de", "country": "DE"},
    "Stuttgart, Germany":     {"lat": 48.7758,  "lng": 9.1829,     "lang": "de", "country": "DE"},
    "Vienna, Austria":        {"lat": 48.2082,  "lng": 16.3738,    "lang": "de", "country": "AT"},
    "Salzburg, Austria":      {"lat": 47.8095,  "lng": 13.0550,    "lang": "de", "country": "AT"},
    "Zurich, Switzerland":    {"lat": 47.3769,  "lng": 8.5417,     "lang": "de", "country": "CH"},
    "Geneva, Switzerland":    {"lat": 46.2044,  "lng": 6.1432,     "lang": "fr", "country": "CH"},
    "Amsterdam, Netherlands": {"lat": 52.3676,  "lng": 4.9041,     "lang": "nl", "country": "NL"},
    "Rotterdam, Netherlands": {"lat": 51.9244,  "lng": 4.4777,     "lang": "nl", "country": "NL"},
    "The Hague, Netherlands": {"lat": 52.0705,  "lng": 4.3007,     "lang": "nl", "country": "NL"},
    "Stockholm, Sweden":      {"lat": 59.3293,  "lng": 18.0686,    "lang": "sv", "country": "SE"},
    "Gothenburg, Sweden":     {"lat": 57.7089,  "lng": 11.9746,    "lang": "sv", "country": "SE"},
    "Oslo, Norway":           {"lat": 59.9139,  "lng": 10.7522,    "lang": "no", "country": "NO"},
    "Copenhagen, Denmark":    {"lat": 55.6761,  "lng": 12.5683,    "lang": "da", "country": "DK"},
    "Tel Aviv, Israel":       {"lat": 32.0853,  "lng": 34.7818,    "lang": "he", "country": "IL"},

    # ── EAST ASIA ─────────────────────────────────────────────────────
    "Tokyo, Japan":           {"lat": 35.6762,  "lng": 139.6503,   "lang": "ja", "country": "JP"},
    "Osaka, Japan":           {"lat": 34.6937,  "lng": 135.5023,   "lang": "ja", "country": "JP"},
    "Kyoto, Japan":           {"lat": 35.0116,  "lng": 135.7681,   "lang": "ja", "country": "JP"},
    "Yokohama, Japan":        {"lat": 35.4437,  "lng": 139.6380,   "lang": "ja", "country": "JP"},
    "Nagoya, Japan":          {"lat": 35.1815,  "lng": 136.9066,   "lang": "ja", "country": "JP"},
    "Seoul, South Korea":     {"lat": 37.5665,  "lng": 126.9780,   "lang": "ko", "country": "KR"},
    "Busan, South Korea":     {"lat": 35.1796,  "lng": 129.0756,   "lang": "ko", "country": "KR"},
    "Incheon, South Korea":   {"lat": 37.4563,  "lng": 126.7052,   "lang": "ko", "country": "KR"},
    "Shanghai, China":        {"lat": 31.2304,  "lng": 121.4737,   "lang": "zh", "country": "CN"},
    "Beijing, China":         {"lat": 39.9042,  "lng": 116.4074,   "lang": "zh", "country": "CN"},
    "Shenzhen, China":        {"lat": 22.5431,  "lng": 114.0579,   "lang": "zh", "country": "CN"},
    "Guangzhou, China":       {"lat": 23.1291,  "lng": 113.2644,   "lang": "zh", "country": "CN"},
    "Chengdu, China":         {"lat": 30.5728,  "lng": 104.0668,   "lang": "zh", "country": "CN"},
    "Hong Kong":              {"lat": 22.3193,  "lng": 114.1694,   "lang": "zh", "country": "HK"},
    "Taipei, Taiwan":         {"lat": 25.0330,  "lng": 121.5654,   "lang": "zh", "country": "TW"},
    "Singapore":              {"lat": 1.3521,   "lng": 103.8198,   "lang": "en", "country": "SG"},

    # ══ TIER 3 — English-speaking developed (lowest opportunity) ══════

    # ── UNITED KINGDOM ────────────────────────────────────────────────
    "London, UK":             {"lat": 51.5074,  "lng": -0.1278,    "lang": "en", "country": "GB"},
    "Manchester, UK":         {"lat": 53.4808,  "lng": -2.2426,    "lang": "en", "country": "GB"},
    "Birmingham, UK":         {"lat": 52.4862,  "lng": -1.8904,    "lang": "en", "country": "GB"},
    "Glasgow, UK":            {"lat": 55.8642,  "lng": -4.2518,    "lang": "en", "country": "GB"},
    "Edinburgh, UK":          {"lat": 55.9533,  "lng": -3.1883,    "lang": "en", "country": "GB"},
    "Liverpool, UK":          {"lat": 53.4084,  "lng": -2.9916,    "lang": "en", "country": "GB"},

    # ── CANADA ────────────────────────────────────────────────────────
    "Toronto, Canada":        {"lat": 43.6532,  "lng": -79.3832,   "lang": "en", "country": "CA"},
    "Vancouver, Canada":      {"lat": 49.2827,  "lng": -123.1207,  "lang": "en", "country": "CA"},
    "Calgary, Canada":        {"lat": 51.0447,  "lng": -114.0719,  "lang": "en", "country": "CA"},
    "Montreal, Canada":       {"lat": 45.5017,  "lng": -73.5673,   "lang": "fr", "country": "CA"},
    "Ottawa, Canada":         {"lat": 45.4215,  "lng": -75.6972,   "lang": "en", "country": "CA"},

    # ── AUSTRALIA / NZ ────────────────────────────────────────────────
    "Sydney, Australia":      {"lat": -33.8688, "lng": 151.2093,   "lang": "en", "country": "AU"},
    "Melbourne, Australia":   {"lat": -37.8136, "lng": 144.9631,   "lang": "en", "country": "AU"},
    "Brisbane, Australia":    {"lat": -27.4698, "lng": 153.0251,   "lang": "en", "country": "AU"},
    "Perth, Australia":       {"lat": -31.9505, "lng": 115.8605,   "lang": "en", "country": "AU"},
    "Adelaide, Australia":    {"lat": -34.9285, "lng": 138.6007,   "lang": "en", "country": "AU"},
    "Auckland, New Zealand":  {"lat": -36.8509, "lng": 174.7645,   "lang": "en", "country": "NZ"},
    "Wellington, New Zealand":{"lat": -41.2865, "lng": 174.7762,   "lang": "en", "country": "NZ"},

    # ── UNITED STATES (last — most saturated market) ──────────────────
    "New York City, USA":     {"lat": 40.7128,  "lng": -74.0060,   "lang": "en", "country": "US"},
    "Los Angeles, USA":       {"lat": 34.0522,  "lng": -118.2437,  "lang": "en", "country": "US"},
    "Chicago, USA":           {"lat": 41.8781,  "lng": -87.6298,   "lang": "en", "country": "US"},
    "Houston, USA":           {"lat": 29.7604,  "lng": -95.3698,   "lang": "en", "country": "US"},
    "Phoenix, USA":           {"lat": 33.4484,  "lng": -112.0740,  "lang": "en", "country": "US"},
    "Philadelphia, USA":      {"lat": 39.9526,  "lng": -75.1652,   "lang": "en", "country": "US"},
    "San Antonio, USA":       {"lat": 29.4241,  "lng": -98.4936,   "lang": "en", "country": "US"},
    "San Diego, USA":         {"lat": 32.7157,  "lng": -117.1611,  "lang": "en", "country": "US"},
    "Dallas, USA":            {"lat": 32.7767,  "lng": -96.7970,   "lang": "en", "country": "US"},
    "San Jose, USA":          {"lat": 37.3382,  "lng": -121.8863,  "lang": "en", "country": "US"},
    "Austin, USA":            {"lat": 30.2672,  "lng": -97.7431,   "lang": "en", "country": "US"},
    "Jacksonville, USA":      {"lat": 30.3322,  "lng": -81.6557,   "lang": "en", "country": "US"},
    "Fort Worth, USA":        {"lat": 32.7555,  "lng": -97.3308,   "lang": "en", "country": "US"},
    "Columbus, USA":          {"lat": 39.9612,  "lng": -82.9988,   "lang": "en", "country": "US"},
    "Charlotte, USA":         {"lat": 35.2271,  "lng": -80.8431,   "lang": "en", "country": "US"},
    "Indianapolis, USA":      {"lat": 39.7684,  "lng": -86.1581,   "lang": "en", "country": "US"},
    "San Francisco, USA":     {"lat": 37.7749,  "lng": -122.4194,  "lang": "en", "country": "US"},
    "Seattle, USA":           {"lat": 47.6062,  "lng": -122.3321,  "lang": "en", "country": "US"},
    "Denver, USA":            {"lat": 39.7392,  "lng": -104.9903,  "lang": "en", "country": "US"},
    "Nashville, USA":         {"lat": 36.1627,  "lng": -86.7816,   "lang": "en", "country": "US"},
    "Las Vegas, USA":         {"lat": 36.1699,  "lng": -115.1398,  "lang": "en", "country": "US"},
    "Washington DC, USA":     {"lat": 38.9072,  "lng": -77.0369,   "lang": "en", "country": "US"},
    "Miami, USA":             {"lat": 25.7617,  "lng": -80.1918,   "lang": "en", "country": "US"},
    "Atlanta, USA":           {"lat": 33.7490,  "lng": -84.3880,   "lang": "en", "country": "US"},
    "Boston, USA":            {"lat": 42.3601,  "lng": -71.0589,   "lang": "en", "country": "US"},
    "Portland, USA":          {"lat": 45.5051,  "lng": -122.6750,  "lang": "en", "country": "US"},
    "Minneapolis, USA":       {"lat": 44.9778,  "lng": -93.2650,   "lang": "en", "country": "US"},
    "Tampa, USA":             {"lat": 27.9506,  "lng": -82.4572,   "lang": "en", "country": "US"},
    "New Orleans, USA":       {"lat": 29.9511,  "lng": -90.0715,   "lang": "en", "country": "US"},
    "Detroit, USA":           {"lat": 42.3314,  "lng": -83.0458,   "lang": "en", "country": "US"},
}

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "pt": "Portuguese",
    "de": "German",
    "it": "Italian",
    "nl": "Dutch",
    "ru": "Russian",
    "tr": "Turkish",
    "pl": "Polish",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
    "th": "Thai",
    "id": "Indonesian",
    "el": "Greek",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "he": "Hebrew",
}

# All city names as a flat list for the scheduler
ALL_CITIES = list(WORLD_CITIES.keys())

def get_city_info(city: str) -> dict:
    return WORLD_CITIES.get(city, {"lat": 0, "lng": 0, "lang": "en", "country": "US"})
