import anthropic
import hashlib
from cities import LANGUAGE_NAMES


SYSTEM = """You are an expert web designer. Continue writing a single-file HTML website for a local business. The <!DOCTYPE html>, <head>, and CSS color variables are already written — do NOT rewrite them, just continue from where the file left off.

Requirements:
- Modern, beautiful design using the CSS variables --clr-dark and --clr-light already defined in :root
- Use var(--clr-dark) for hero, nav, footer backgrounds. Use var(--clr-light) for body/section backgrounds. Never hardcode color hex values.
- Mobile responsive
- Sections: sticky nav, full-width hero, about, services/specialties, hours & contact with Google Maps link, footer
- Real content only — use the actual business name, address, phone, hours, and reviews provided
- Output ONLY the continuation of the HTML (from where the prefill ended). No markdown fences, no explanation.

Critical: Write concise CSS (combine selectors, use shorthand). You must complete the entire file."""


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

    reviews  = [r for r in business.get("reviews", []) if r]
    hours    = business.get("hours", [])
    tagline  = business.get("tagline", "")
    desc     = business.get("description", "")
    logo     = business.get("logo_b64", "")
    photos   = business.get("photos_b64", [])

    hours_txt    = "\n".join(hours) if hours else "Call for hours"
    reviews_txt  = "\n".join(f'- "{r}"' for r in reviews[:3]) if reviews else ""
    logo_txt     = f"\nEmbed this base64 logo as <img> in the nav (max-height:48px): {logo[:80]}..." if logo else ""
    photos_txt   = f"\nEmbed these {len(photos)} base64 photos as <img> tags in a gallery section: {photos[0][:60]}..." if photos else ""
    tagline_txt  = f"\nTagline: {tagline}" if tagline else ""
    desc_txt     = f"\nDescription: {desc}" if desc else ""
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

Make it feel authentic and specific to this exact business. Continue the HTML file from where it starts below."""

    # Prefill the start of Claude's response with the exact colors already locked in.
    # Claude cannot override colors it didn't write — it just continues from here.
    prefill = (
        f'<!DOCTYPE html>\n<html lang="{language}">\n<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{business["name"]}</title>\n'
        f'<style>\n'
        f':root {{\n'
        f'  --clr-dark: {dark};\n'
        f'  --clr-light: {light};\n'
        f'  --clr-accent: {dark};\n'
        f'}}\n'
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM,
        messages=[
            {"role": "user",      "content": prompt},
            {"role": "assistant", "content": prefill},
        ],
    )
    # Claude continues from the prefill — stitch them back together
    html = prefill + msg.content[0].text.strip()
    if "```" in html:
        html = html.split("```", 1)[0]
    return html
