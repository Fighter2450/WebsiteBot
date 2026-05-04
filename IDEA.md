# Website Bot — Business Outreach Automation

## The Idea

Search Google Maps for local businesses that have no website.
For each one found, auto-generate a professional website tailored to their business type,
deploy it as a live preview, then email the owner with a link and a short pitch.
Repeat indefinitely.

## Pipeline

1. **Find** — Query Google Places API by city + business category, filter where `website` is missing
2. **Generate** — Feed business data (name, address, hours, reviews, category) into Claude API → get back a full single-page HTML/CSS site
3. **Deploy** — Push the HTML to a GitHub Gist → render via htmlpreview.github.io for a free live URL
4. **Email** — Search for owner's email (Places API, web search, social scrape fallback) → send pitch with live preview link
5. **Track** — SQLite database so you never contact the same business twice

## Value Prop to Business Owner

"I noticed you don't have a website — I already built one for you. Here's a live preview.
If you like it, let's talk."

## Tech Stack

- `googlemaps` — Places API (find + enrich)
- `anthropic` — Claude generates the HTML per business type
- `PyGithub` — deploy preview via Gist
- `smtplib` / SendGrid — outreach email
- `sqlite3` — dedup tracking
- `requests` / `re` — email scraping fallback

## Required Env Vars

```
GOOGLE_PLACES_API_KEY=
ANTHROPIC_API_KEY=
GITHUB_TOKEN=
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=your-app-password
FROM_NAME=Your Name
```

## Usage

```bash
python website_bot/main.py --city "Austin, TX" --type restaurant --limit 10
```
