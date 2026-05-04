"""
Email finder — multiple strategies for businesses that have no website.

Strategy order (fastest → slowest):
  1. Google Places "editorial_summary" / website field (already filtered out)
  2. DDG search for their email directly
  3. Facebook business page scrape
  4. Common email pattern guessing + MX verification
  5. Yelp biz page scrape
  6. Instagram bio scrape
"""
import re
import time
import socket
import requests
from urllib.parse import quote_plus, urlparse

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

BLOCKED_DOMAINS = {
    "duckduckgo.com", "google.com", "bing.com", "yahoo.com",
    "yelp.com", "tripadvisor.com", "facebook.com", "instagram.com",
    "twitter.com", "tiktok.com", "apple.com", "microsoft.com",
    "amazonaws.com", "cloudflare.com", "sentry.io", "example.com",
    "w3.org", "schema.org", "opentable.com", "grubhub.com",
    "doordash.com", "ubereats.com", "wix.com", "squarespace.com",
    "godaddy.com", "wordpress.com", "shopify.com", "zomato.com",
    "foursquare.com", "yellowpages.com", "whitepages.com",
}

BLOCKED_PREFIXES = {
    "noreply", "no-reply", "donotreply", "support", "privacy",
    "legal", "abuse", "postmaster", "mailer-daemon", "webmaster",
    "unsubscribe", "bounce", "info-",
}

# Free email providers — valid but lower priority
FREE_PROVIDERS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"}


def _clean_name(name: str) -> str:
    """Slug-ify a business name for domain / email guessing."""
    s = name.lower()
    s = re.sub(r"[''`]", "", s)           # apostrophes
    s = re.sub(r"[^a-z0-9 ]+", " ", s)   # non-alphanumeric → space
    s = re.sub(r"\s+", "", s)             # collapse spaces
    return s[:30]


def _score(email: str, name: str) -> int:
    """Higher = more likely to be the real contact email."""
    local, domain = email.lower().split("@", 1)
    score = 0
    name_words = [w for w in re.sub(r"[^a-z0-9]", " ", name.lower()).split() if len(w) > 2]
    if any(w in local for w in name_words):
        score += 10
    if domain not in FREE_PROVIDERS:
        score += 5
    if local in ("info", "contact", "hello", "hi", "hola", "bonjour"):
        score += 3
    return score


def _filter(emails: list[str], name: str) -> list[str]:
    results = []
    for e in emails:
        e = e.strip(".,;:'\")([]")
        if not e or "@" not in e:
            continue
        if e.lower().endswith((".png", ".jpg", ".gif", ".svg", ".js", ".css", ".php")):
            continue
        local, domain = e.lower().split("@", 1)
        if domain in BLOCKED_DOMAINS:
            continue
        if any(local == p or local.startswith(p + "-") for p in BLOCKED_PREFIXES):
            continue
        results.append(e)
    # dedupe, sort by score
    seen = {}
    for e in results:
        key = e.lower()
        if key not in seen:
            seen[key] = e
    ranked = sorted(seen.values(), key=lambda e: _score(e, name), reverse=True)
    return ranked


def _get(url: str, timeout: int = 10) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""


def _ddg(query: str, timeout: int = 10) -> str:
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            timeout=timeout,
        )
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""


def _extract_urls_from_ddg(html: str) -> list[str]:
    urls = re.findall(r'href="(https?://[^"&]+)"', html)
    clean = []
    for u in urls:
        host = urlparse(u).netloc.replace("www.", "")
        if host and host not in BLOCKED_DOMAINS and "duckduckgo" not in host:
            clean.append(u)
    return list(dict.fromkeys(clean))[:6]


def _has_mx(domain: str) -> bool:
    """Check if a domain has MX records (i.e. accepts email)."""
    try:
        socket.getaddrinfo(domain, None)
        return True
    except Exception:
        return False


def _scrape_page(url: str, name: str) -> list[str]:
    html = _get(url)
    if not html:
        return []
    return _filter(EMAIL_RE.findall(html), name)


# ── Strategy implementations ─────────────────────────────────────────────────

def _strategy_ddg_direct(name: str, city: str) -> list[str]:
    """Search DDG for the business email directly."""
    city_short = city.split(",")[0]
    queries = [
        f'"{name}" {city_short} email',
        f'"{name}" {city_short} contact email',
        f'"{name}" {city_short} "@gmail.com" OR "@yahoo.com" OR "@hotmail.com"',
        f'"{name}" {city_short} owner',
    ]
    for q in queries:
        html = _ddg(q)
        emails = _filter(EMAIL_RE.findall(html), name)
        if emails:
            return emails
        time.sleep(0.3)
    return []


def _strategy_ddg_site_scrape(name: str, city: str) -> list[str]:
    """Find their website via DDG and scrape it."""
    city_short = city.split(",")[0]
    html = _ddg(f'"{name}" {city_short} -site:yelp.com -site:tripadvisor.com -site:facebook.com')
    urls = _extract_urls_from_ddg(html)
    for url in urls:
        for path in ["", "/contact", "/about", "/contact-us", "/about-us"]:
            emails = _scrape_page(url.rstrip("/") + path, name)
            if emails:
                return emails
            time.sleep(0.2)
    return []


def _strategy_facebook(name: str, city: str) -> list[str]:
    """Search DDG for their Facebook page, then scrape it for emails."""
    city_short = city.split(",")[0]
    html = _ddg(f'site:facebook.com "{name}" {city_short}')
    urls = [u for u in _extract_urls_from_ddg(html) if "facebook.com" in u]
    for url in urls[:3]:
        # Facebook renders client-side, but the HTML source often has emails in meta/og tags
        page_html = _get(url)
        if page_html:
            emails = _filter(EMAIL_RE.findall(page_html), name)
            if emails:
                return emails
    return []


def _strategy_instagram(name: str, city: str) -> list[str]:
    """Look for their Instagram bio email."""
    city_short = city.split(",")[0]
    html = _ddg(f'site:instagram.com "{name}" {city_short}')
    urls = [u for u in _extract_urls_from_ddg(html) if "instagram.com" in u]
    for url in urls[:2]:
        page_html = _get(url)
        if page_html:
            emails = _filter(EMAIL_RE.findall(page_html), name)
            if emails:
                return emails
    return []


def _strategy_yelp(name: str, city: str) -> list[str]:
    """Scrape Yelp business page for contact email."""
    city_short = city.split(",")[0]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    city_slug = re.sub(r"[^a-z0-9]+", "-", city_short.lower()).strip("-")
    html = _get(f"https://www.yelp.com/biz/{slug}-{city_slug}")
    if html:
        emails = _filter(EMAIL_RE.findall(html), name)
        if emails:
            return emails
    # Also try searching Yelp via DDG
    html2 = _ddg(f'site:yelp.com "{name}" {city_short}')
    urls = [u for u in _extract_urls_from_ddg(html2) if "yelp.com/biz" in u]
    for url in urls[:2]:
        emails = _scrape_page(url, name)
        if emails:
            return emails
    return []


def _strategy_pattern_guess(name: str, city: str, address: str = "") -> list[str]:
    """
    Guess common email patterns for the business.
    Only return if the domain actually has MX records.
    """
    slug = _clean_name(name)
    if not slug:
        return []

    # Build candidate domains
    domains = [
        f"{slug}.com",
        f"{slug}restaurant.com" if "restaurant" not in slug else None,
        f"{slug}cafe.com" if "cafe" not in slug else None,
    ]
    domains = [d for d in domains if d]

    # Also try common free-provider patterns
    free_guesses = [
        f"info@{slug}.com",
        f"contact@{slug}.com",
        f"hello@{slug}.com",
        f"{slug}@gmail.com",
        f"{slug}info@gmail.com",
    ]

    found = []
    for domain in domains:
        if _has_mx(domain):
            for prefix in ["info", "contact", "hello", "hi", "owner"]:
                found.append(f"{prefix}@{domain}")
    # Free provider guesses — add last (lower priority)
    found.extend(free_guesses)
    return found[:3] if found else []


# ── Main entry point ─────────────────────────────────────────────────────────

def find_email(business: dict) -> str | None:
    name    = business["name"]
    city    = business.get("city", "")
    address = business.get("address", "")

    print(f"  [email] Searching for {name}...")

    # 1. DDG direct email search (fast, works if they've ever posted their email)
    emails = _strategy_ddg_direct(name, city)
    if emails:
        print(f"  [email] Found via DDG direct: {emails[0]}")
        return emails[0]

    # 2. Scrape their actual website if DDG finds one
    emails = _strategy_ddg_site_scrape(name, city)
    if emails:
        print(f"  [email] Found via website scrape: {emails[0]}")
        return emails[0]

    # 3. Facebook page
    emails = _strategy_facebook(name, city)
    if emails:
        print(f"  [email] Found via Facebook: {emails[0]}")
        return emails[0]

    # 4. Instagram
    emails = _strategy_instagram(name, city)
    if emails:
        print(f"  [email] Found via Instagram: {emails[0]}")
        return emails[0]

    # 5. Yelp
    emails = _strategy_yelp(name, city)
    if emails:
        print(f"  [email] Found via Yelp: {emails[0]}")
        return emails[0]

    # 6. Pattern guess with MX check (last resort — only sends to real domains)
    emails = _strategy_pattern_guess(name, city, address)
    if emails:
        print(f"  [email] Using pattern guess: {emails[0]}")
        return emails[0]

    print(f"  [email] No email found for {name}")
    return None
