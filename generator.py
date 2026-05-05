import anthropic
import hashlib
import re
from cities import LANGUAGE_NAMES


SYSTEM = """You are a senior web designer. Generate a complete, polished, single-file HTML website for a local business.

Design standards:
- Clean, modern layout with generous whitespace — no clutter
- Typography: large bold headings, readable body text (1.6 line-height), clear hierarchy
- ABSOLUTELY NO EMOJIS — not in headings, nav, buttons, icons, body text, or anywhere else. Zero. None.
- Use CSS shapes, borders, or Unicode symbols like ★ (U+2605) for ratings ONLY — no emoji substitutes
- Hero: full-width, min-height 85vh, business name large and centered, subtle overlay on photo if one is provided
- If photo URLs are provided, use them as real <img> tags (object-fit:cover) — do NOT use placeholder or emoji images
- If no photos, use a solid color hero with no fake image placeholders
- Sections: sticky nav, hero, about, services (card grid), hours & contact, footer
- Hours in a clean table or list — plain text labels only, no icons
- Google Maps link using the business address — text link only, no emoji pin
- Reviews as elegant blockquotes with a subtle left border — plain text or CSS stars, no emoji
- Mobile responsive with a hamburger-free nav (links stack on small screens)
- No external dependencies except Google Fonts

Code quality:
- Output ONLY raw HTML from <!DOCTYPE html> to </html>. No markdown, no explanation.
- Concise CSS: combine selectors, use shorthand, no redundant rules
- Complete the entire file — an unfinished file renders blank"""


PALETTES = {
    # ── Food & Drink ─────────────────────────────────────────────────────────
    "restaurant":         ("#7f1d1d", "#fef2f2", "Playfair Display"),   # deep burgundy / warm cream
    "cafe":               ("#78350f", "#fffbeb", "Fraunces"),            # espresso / warm ivory
    "bar":                ("#0c0a09", "#fef3c7", "Space Grotesk"),       # near-black / warm amber glow
    "bakery":             ("#92400e", "#fdf8f2", "Fraunces"),            # amber brown / cream
    # ── Home Trades ──────────────────────────────────────────────────────────
    "plumber":            ("#1e3a8a", "#eff6ff", "Space Grotesk"),       # navy / light blue
    "electrician":        ("#713f12", "#fffbeb", "Space Grotesk"),       # dark amber / pale yellow
    "locksmith":          ("#374151", "#f3f4f6", "Space Grotesk"),       # slate gray / light gray
    "painter":            ("#0f766e", "#f0fdfa", "DM Sans"),             # rich teal / mint
    # ── Beauty & Wellness ────────────────────────────────────────────────────
    "hair_care":          ("#4c1d95", "#faf5ff", "Fraunces"),            # deep violet / soft lavender
    "beauty_salon":       ("#831843", "#fdf2f8", "Playfair Display"),    # deep magenta / blush
    "spa":                ("#166534", "#f0fdf4", "Playfair Display"),    # forest green / mint
    "nail_salon":         ("#9d174d", "#fff1f2", "Fraunces"),            # rose / blush
    # ── Fitness & Practical ──────────────────────────────────────────────────
    "gym":                ("#7c2d12", "#fff7ed", "Space Grotesk"),       # burnt orange / warm light
    "laundry":            ("#075985", "#e0f2fe", "DM Sans"),             # ocean blue / ice blue
    "car_repair":         ("#292524", "#fafaf9", "Space Grotesk"),       # dark charcoal / off-white
    "car_wash":           ("#0284c7", "#e0f2fe", "Space Grotesk"),       # bright blue / ice blue
    # ── Medical / Health ─────────────────────────────────────────────────────
    "dentist":            ("#0e7490", "#ecfeff", "DM Sans"),             # cool teal / clean white
    "doctor":             ("#1e40af", "#eff6ff", "DM Sans"),             # medical blue / light blue
    "physiotherapist":    ("#065f46", "#ecfdf5", "DM Sans"),             # healing dark green / mint
    "veterinary_care":    ("#2d4a1e", "#f7fee7", "Fraunces"),            # earthy green / pale lime
    # ── Retail ───────────────────────────────────────────────────────────────
    "florist":            ("#881337", "#fff1f2", "Playfair Display"),    # deep rose / blush
    "jewelry_store":      ("#1a1209", "#fef9c3", "Playfair Display"),    # rich dark / champagne gold
    "clothing_store":     ("#312e81", "#eef2ff", "Fraunces"),            # deep indigo / soft white
    "shoe_store":         ("#44403c", "#fafaf9", "Space Grotesk"),       # warm leather / off-white
    # ── Professional Services ─────────────────────────────────────────────────
    "lawyer":             ("#1e293b", "#f8fafc", "Playfair Display"),    # deep slate / cool white
    "accounting":         ("#0f172a", "#f1f5f9", "Space Grotesk"),       # near-black navy / cool white
    "real_estate_agency": ("#3f6212", "#f7fee7", "Playfair Display"),   # olive / pale lime
    "insurance_agency":   ("#1e3a5f", "#dbeafe", "Space Grotesk"),      # deep steel blue / ice
}


# Keyword → palette override. Checked against business name + description before
# falling back to category. Add tuples in priority order (first match wins).
NAME_OVERRIDES = [
    # ── Golf / Country Club ────────────────────────────────────────────────
    ({"golf", "country club", "links", "fairway", "clubhouse", "pga", "lpga"},
     "#14532d", "#f0fdf4", "Playfair Display"),   # golf green / light mint

    # ── Beach / Coastal ────────────────────────────────────────────────────
    ({"beach", "surf", "coastal", "ocean", "sea", "bay", "shore", "island",
      "tiki", "caribbean", "tropical", "lagoon"},
     "#0369a1", "#e0f9ff", "Space Grotesk"),       # ocean blue / sky

    # ── BBQ / Smokehouse ──────────────────────────────────────────────────
    ({"bbq", "barbecue", "smokehouse", "smoke", "pit", "grill", "grille",
      "roadhouse"},
     "#292524", "#fef3c7", "Space Grotesk"),       # charcoal / amber

    # ── Italian / Pizza ───────────────────────────────────────────────────
    ({"italian", "trattoria", "osteria", "pizzeria", "pizza", "pasta",
      "ristorante", "gelato"},
     "#9a3412", "#fff7ed", "Playfair Display"),    # terracotta / warm white

    # ── Mexican / Latin ───────────────────────────────────────────────────
    ({"mexican", "taco", "cantina", "burrito", "guacamole", "salsa",
      "tacos", "tex-mex", "latina", "latino"},
     "#b45309", "#fffbeb", "Fraunces"),            # warm amber / ivory

    # ── Steakhouse ────────────────────────────────────────────────────────
    ({"steakhouse", "steak", "chophouse", "chop house", "prime", "ribeye",
      "wagyu"},
     "#450a0a", "#fef2f2", "Playfair Display"),    # deep blood red / cream

    # ── Asian / Japanese / Sushi ──────────────────────────────────────────
    ({"sushi", "ramen", "japanese", "izakaya", "yakitori", "tempura",
      "sake", "noodle", "pho", "vietnamese", "thai", "korean", "dim sum",
      "chinese", "wonton", "boba"},
     "#1c1917", "#f5f5f4", "Space Grotesk"),       # minimal dark / off-white

    # ── Indian / Middle Eastern ───────────────────────────────────────────
    ({"indian", "curry", "tandoor", "biryani", "masala", "chai",
      "mediterranean", "greek", "lebanese", "persian", "falafel",
      "hummus", "shawarma", "kebab"},
     "#92400e", "#fffbeb", "Fraunces"),            # saffron / ivory

    # ── French / European Fine Dining ─────────────────────────────────────
    ({"french", "bistro", "brasserie", "patisserie", "croissant",
      "boulangerie", "wine bar", "winery"},
     "#1e293b", "#fffbeb", "Playfair Display"),    # deep slate / warm parchment

    # ── Sports Bar ────────────────────────────────────────────────────────
    ({"sports bar", "sports grill", "sports lounge", "game day",
      "tailgate", "stadium"},
     "#1e3a8a", "#fef3c7", "Space Grotesk"),       # team navy / warm amber

    # ── Kids / Family ─────────────────────────────────────────────────────
    ({"kids", "children", "family", "playground", "bounce", "toddler",
      "nursery", "daycare", "preschool"},
     "#0369a1", "#fef9c3", "Fraunces"),            # bright blue / sunny yellow

    # ── Bridal / Wedding ──────────────────────────────────────────────────
    ({"bridal", "wedding", "bride", "groom", "floral design",
      "event planner", "wedding planner"},
     "#831843", "#fdf2f8", "Playfair Display"),    # deep rose / blush

    # ── Vegan / Health Food ───────────────────────────────────────────────
    ({"vegan", "vegetarian", "plant-based", "organic", "superfood",
      "juice bar", "smoothie", "wellness"},
     "#166534", "#f0fdf4", "DM Sans"),             # fresh green / mint
]


# Multiple palette variants per category — name hash picks one so each
# business gets a consistent but varied look.
CATEGORY_VARIANTS: dict[str, list[tuple]] = {
    "restaurant": [
        ("#7f1d1d", "#fef2f2", "Playfair Display"),   # deep burgundy / cream
        ("#14532d", "#f0fdf4", "Playfair Display"),   # forest green / mint
        ("#1e3a8a", "#eff6ff", "Playfair Display"),   # deep navy / light blue
        ("#3b0764", "#faf5ff", "Playfair Display"),   # deep violet / soft lavender
        ("#0c4a6e", "#e0f2fe", "Fraunces"),           # deep ocean / sky
        ("#365314", "#f7fee7", "Fraunces"),           # olive / pale lime
        ("#4a1942", "#fdf4ff", "Playfair Display"),   # dark plum / blush
        ("#292524", "#fef9c3", "Fraunces"),           # near-black / warm gold
        ("#7c2d12", "#fff7ed", "Playfair Display"),   # burnt sienna / ivory
        ("#064e3b", "#ecfdf5", "Playfair Display"),   # deep emerald / mint
        ("#1c1917", "#fef3c7", "Space Grotesk"),      # charcoal / amber
        ("#4c1d95", "#faf5ff", "Fraunces"),           # indigo / lavender
    ],
    "cafe": [
        ("#78350f", "#fffbeb", "Fraunces"),           # espresso / warm ivory
        ("#292524", "#fef9c3", "Space Grotesk"),      # near-black / amber
        ("#14532d", "#f0fdf4", "Fraunces"),           # forest green / mint
        ("#1e3a8a", "#fef9c3", "Fraunces"),           # navy / golden
        ("#713f12", "#fdf8f2", "Fraunces"),           # amber brown / cream
        ("#4c1d95", "#faf5ff", "Fraunces"),           # deep violet / lavender
    ],
    "bar": [
        ("#0c0a09", "#fef3c7", "Space Grotesk"),      # near-black / warm amber glow
        ("#1e3a8a", "#fef3c7", "Space Grotesk"),      # navy / amber
        ("#3b0764", "#fef9c3", "Space Grotesk"),      # deep violet / gold
        ("#292524", "#ecfdf5", "Space Grotesk"),      # charcoal / pale mint
        ("#450a0a", "#fef2f2", "Space Grotesk"),      # blood red / cream
        ("#064e3b", "#fef3c7", "Space Grotesk"),      # dark green / amber
    ],
    "bakery": [
        ("#92400e", "#fdf8f2", "Fraunces"),           # amber brown / cream
        ("#78350f", "#fffbeb", "Fraunces"),           # espresso / ivory
        ("#831843", "#fdf2f8", "Playfair Display"),   # deep rose / blush
        ("#166534", "#f0fdf4", "Fraunces"),           # forest green / mint
        ("#4c1d95", "#faf5ff", "Fraunces"),           # violet / lavender
        ("#1e3a8a", "#eff6ff", "Fraunces"),           # navy / pale blue
    ],
    "hair_care": [
        ("#4c1d95", "#faf5ff", "Fraunces"),           # deep violet / soft lavender
        ("#831843", "#fdf2f8", "Playfair Display"),   # magenta / blush
        ("#1e3a8a", "#eff6ff", "Fraunces"),           # navy / pale blue
        ("#065f46", "#ecfdf5", "Fraunces"),           # dark teal / mint
        ("#292524", "#fef9c3", "Fraunces"),           # charcoal / warm gold
    ],
    "beauty_salon": [
        ("#831843", "#fdf2f8", "Playfair Display"),   # deep magenta / blush
        ("#4c1d95", "#faf5ff", "Playfair Display"),   # violet / lavender
        ("#9d174d", "#fff1f2", "Playfair Display"),   # rose / blush
        ("#1e3a8a", "#fdf2f8", "Playfair Display"),   # navy / blush
        ("#166534", "#f0fdf4", "Playfair Display"),   # green / mint
    ],
    "gym": [
        ("#7c2d12", "#fff7ed", "Space Grotesk"),      # burnt orange / warm light
        ("#292524", "#fafaf9", "Space Grotesk"),      # charcoal / off-white
        ("#1e3a8a", "#eff6ff", "Space Grotesk"),      # bold navy / light blue
        ("#14532d", "#f0fdf4", "Space Grotesk"),      # dark green / mint
        ("#450a0a", "#fef2f2", "Space Grotesk"),      # deep red / light
        ("#1c1917", "#fef9c3", "Space Grotesk"),      # near-black / gold
    ],
    "spa": [
        ("#166534", "#f0fdf4", "Playfair Display"),   # forest green / mint
        ("#0e7490", "#ecfeff", "Playfair Display"),   # teal / pale cyan
        ("#4c1d95", "#faf5ff", "Playfair Display"),   # violet / lavender
        ("#831843", "#fdf2f8", "Playfair Display"),   # rose / blush
        ("#1e3a8a", "#eff6ff", "Playfair Display"),   # navy / pale blue
    ],
    "florist": [
        ("#881337", "#fff1f2", "Playfair Display"),   # deep rose / blush
        ("#166534", "#f0fdf4", "Playfair Display"),   # forest green / mint
        ("#4c1d95", "#faf5ff", "Playfair Display"),   # violet / lavender
        ("#9a3412", "#fff7ed", "Playfair Display"),   # terracotta / warm white
        ("#1e3a8a", "#eff6ff", "Playfair Display"),   # navy / pale blue
    ],
    "clothing_store": [
        ("#312e81", "#eef2ff", "Fraunces"),           # deep indigo / soft white
        ("#1c1917", "#fef9c3", "Fraunces"),           # near-black / gold
        ("#831843", "#fdf2f8", "Fraunces"),           # rose / blush
        ("#14532d", "#f0fdf4", "Fraunces"),           # green / mint
        ("#292524", "#fafaf9", "Space Grotesk"),      # charcoal / off-white
        ("#0c4a6e", "#e0f2fe", "Fraunces"),           # dark ocean / ice
    ],
}


def _name_hash(name: str) -> int:
    """Stable hash of the business name — same name always gets same palette."""
    return int(hashlib.md5(name.lower().encode()).hexdigest(), 16)


def _category_palette(category: str, name: str) -> tuple:
    """Pick a palette for this category. Uses name hash for variety so two
    restaurants don't always look identical, while staying thematically coherent."""
    variants = CATEGORY_VARIANTS.get(category)
    if variants:
        return variants[_name_hash(name) % len(variants)]
    # Fallback: single palette from PALETTES, or a neutral dark default
    return PALETTES.get(category, ("#1e293b", "#f8fafc", "DM Sans"))


def _theme_override(name: str, description: str) -> tuple | None:
    """Return (dark, light, font) if the business name/description matches a theme."""
    text = (name + " " + description).lower()
    for keywords, dark, light, font in NAME_OVERRIDES:
        if any(kw in text for kw in keywords):
            return dark, light, font
    return None


def generate_website(client: anthropic.Anthropic, business: dict, existing_html: str = "", language: str = "en") -> str:
    category      = business.get("category", "restaurant")
    name          = business.get("name", "")
    description   = business.get("description", "") or ""

    # Name/description theme takes priority over category palette
    override = _theme_override(name, description)
    if override:
        dark, light, font = override
    else:
        dark, light, font = _category_palette(category, name)
    language_name = LANGUAGE_NAMES.get(language, "English")

    reviews   = [r for r in business.get("reviews", []) if r]
    hours     = business.get("hours", [])
    tagline   = business.get("tagline", "")
    desc      = business.get("description", "")
    logo      = business.get("logo_b64", "")
    photo_urls = business.get("photo_urls", [])

    hours_txt   = "\n".join(hours) if hours else "Call for hours"
    reviews_txt = "\n".join(f'- "{r}"' for r in reviews[:3]) if reviews else ""
    logo_txt    = f"\nEmbed this base64 logo as <img> in the nav (max-height:48px): {logo[:80]}..." if logo else ""
    tagline_txt = f"\nTagline: {tagline}" if tagline else ""
    desc_txt    = f"\nDescription: {desc}" if desc else ""

    if photo_urls:
        photos_txt = "\nReal business photos — use these as <img src='URL'> tags (object-fit:cover):\n" + "\n".join(
            f"  Photo {i+1}: {url}" for i, url in enumerate(photo_urls)
        )
    else:
        photos_txt = "\nNo photos available — use a solid color hero, no placeholder images."
    rating       = business.get("rating")
    rating_txt   = f"\nGoogle Rating: {rating} stars ({business.get('review_count', 0)} reviews)" if rating else ""

    prompt = f"""Generate a website for this business:

Name: {business["name"]}
Type: {business.get("category", "")}
City: {business.get("city", "")}
Address: {business.get("address", "")}
Phone: {business.get("phone", "")}{rating_txt}{tagline_txt}{desc_txt}
Hours:
{hours_txt}
{f"Customer reviews to use as testimonials:{chr(10)}{reviews_txt}" if reviews_txt else ""}
{logo_txt}{photos_txt}

Headline font: {font} — load from Google Fonts.
Language: Write ALL text in {language_name}. Every heading, paragraph, button, nav link, and footer must be in {language_name}.

Make it feel authentic and specific to this exact business."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    html = msg.content[0].text.strip()
    if html.startswith("```"):
        html = html.split("\n", 1)[1]
        html = html.rsplit("```", 1)[0]

    # Lock palette: replace background hex colors inside <style> blocks
    # so Claude's chosen reds/yellows become our actual palette colors.
    html = _lock_palette(html, dark, light, font)

    # Strip any emojis Claude snuck in despite instructions
    html = _strip_emojis(html)

    return html


def _strip_emojis(html: str) -> str:
    """Remove Unicode emoji characters from the generated HTML.
    Operates on the raw string so it catches emojis in any context."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"   # emoticons
        "\U0001F300-\U0001F5FF"   # symbols & pictographs
        "\U0001F680-\U0001F6FF"   # transport & map
        "\U0001F700-\U0001F77F"   # alchemical symbols
        "\U0001F780-\U0001F7FF"   # geometric extended
        "\U0001F800-\U0001F8FF"   # supplemental arrows
        "\U0001F900-\U0001F9FF"   # supplemental symbols & pictographs
        "\U0001FA00-\U0001FA6F"   # chess symbols
        "\U0001FA70-\U0001FAFF"   # symbols & pictographs extended-A
        "\U00002702-\U000027B0"   # dingbats
        "\U000024C2-\U0001F251"   # enclosed chars
        "\U0001F004"              # mahjong tile
        "\U0001F0CF"              # playing card
        "\U0001F170-\U0001F171"   # A/B buttons
        "\U0001F17E-\U0001F17F"   # O/P buttons
        "\U0001F18E"              # AB button
        "\U000023E9-\U000023F3"   # transport symbols
        "\U000023F8-\U000023FA"   # pause/stop
        "\U0000200D"              # zero-width joiner
        "\U0000FE0F"              # variation selector-16
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", html)


def _luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    except Exception:
        return 0.5


def _lock_palette(html: str, dark: str, light: str, font: str) -> str:
    """Replace background/border hex colors inside <style> blocks with our palette,
    then inject safety-net !important overrides for nav/footer/body."""

    # Step 1: regex-replace background colors in CSS
    bg_prop = re.compile(
        r'((?:background(?:-color)?|border(?:-color)?)\s*:\s*)(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})',
        re.IGNORECASE,
    )

    def swap(m: re.Match) -> str:
        lum = _luminance(m.group(2))
        return m.group(1) + (dark if lum < 0.45 else light)

    style_block = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.DOTALL | re.IGNORECASE)

    def fix_styles(m: re.Match) -> str:
        return m.group(1) + bg_prop.sub(swap, m.group(2)) + m.group(3)

    html = style_block.sub(fix_styles, html)

    # Step 2: safety-net !important block — catches inline styles and missed selectors
    overrides = (
        f'<style id="palette-lock">'
        f'nav,nav *,header{{background:{dark}!important}}'
        f'nav a,nav *{{color:#fff!important}}'
        f'footer,footer *{{background:{dark}!important;color:#fff!important}}'
        f'body{{background:{light}!important}}'
        f'h1,h2,h3,h4{{font-family:"{font}",Georgia,serif!important}}'
        f'</style>'
    )
    if '</head>' in html:
        html = html.replace('</head>', overrides + '</head>', 1)
    elif '<body' in html:
        html = html.replace('<body', overrides + '<body', 1)

    return html
