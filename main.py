#!/usr/bin/env python3
"""
Website Bot — find businesses without websites, generate one, email them.

Usage:
    python website_bot/main.py --city "Austin, TX" --type restaurant --limit 10
    python website_bot/main.py --all-cities --type restaurant --limit 10
    python website_bot/main.py --list   # show all tracked businesses
"""
import argparse
import os
import sys

import anthropic
from dotenv import load_dotenv

from finder import find_businesses_without_websites
from generator import generate_website
from deployer import deploy_to_gist
from email_finder import find_email
from emailer import send_pitch
from sms_sender import send_sms
from tracker import init_db, already_processed, mark_processed, list_all
from cities import ALL_CITIES, get_city_info

load_dotenv()

TOP_10_CITIES = TOP_25_CITIES = ALL_CITIES  # now all world cities

REMOVED_CITIES = [
    "New York City, NY",
    "Los Angeles, CA",
    "Chicago, IL",
    "Houston, TX",
    "Phoenix, AZ",
    "Philadelphia, PA",
    "San Antonio, TX",
    "San Diego, CA",
    "Dallas, TX",
    "San Jose, CA",
    "Austin, TX",
    "Jacksonville, FL",
    "Fort Worth, TX",
    "Columbus, OH",
    "Charlotte, NC",
    "Indianapolis, IN",
    "San Francisco, CA",
    "Seattle, WA",
    "Denver, CO",
    "Nashville, TN",
    "Oklahoma City, OK",
    "El Paso, TX",
    "Washington, DC",
    "Las Vegas, NV",
    "Louisville, KY",
]

REQUIRED_VARS = ["GOOGLE_PLACES_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN",
                 "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "FROM_NAME"]


def check_env():
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print(f"[error] Missing env vars: {', '.join(missing)}")
        print("Add them to your .env file. See website_bot/IDEA.md for the full list.")
        sys.exit(1)


def run(city: str, business_type: str, limit: int, dry_run: bool):
    check_env()
    init_db()

    city_info = get_city_info(city)
    language  = city_info.get("lang", "en")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"\n[find] Searching for {business_type} in {city} (lang={language})...")
    businesses = find_businesses_without_websites(
        api_key=os.environ["GOOGLE_PLACES_API_KEY"],
        city=city,
        business_type=business_type,
        limit=limit,
    )
    print(f"[find] Found {len(businesses)} candidates")

    for biz in businesses:
        place_id = biz["place_id"]
        name = biz["name"]

        if already_processed(place_id):
            print(f"[skip] {name} — already processed")
            continue

        print(f"\n[generate] Building website for: {name}")
        try:
            html = generate_website(client, biz, language=language)
            print(f"[generate] Done ({len(html):,} chars)")
        except Exception as e:
            print(f"[generate] Failed: {e} — will retry next cycle")
            continue

        if dry_run:
            out = os.path.join(os.path.dirname(__file__), f"preview_{place_id[:8]}.html")
            with open(out, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[dry-run] Saved to {out} — skipping deploy + email")
            mark_processed(place_id, name, city, business_type, "", out, "dry_run", html=html)
            continue

        print(f"[deploy] Uploading to GitHub Gist...")
        try:
            preview_url = deploy_to_gist(os.environ["GITHUB_TOKEN"], name, html)
            print(f"[deploy] Preview: {preview_url}")
        except Exception as e:
            print(f"[deploy] Gist failed: {e} — saving locally")
            # Still save to DB so it appears on the globe; no public URL
            mark_processed(place_id, name, city, business_type, "", "", "deploy_failed", html=html)
            continue

        # Save HTML + generate token before emailing
        token = mark_processed(place_id, name, city, business_type, "", preview_url, "no_email", html=html)
        # Also make the site accessible directly via Railway (no Gist dependency)
        _railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
        _base = (os.environ.get("PUBLIC_URL", "").rstrip("/")
                 or (f"https://{_railway_domain}" if _railway_domain else "")
                 or "http://localhost:5050")
        if token and not preview_url.startswith("http"):
            preview_url = f"{_base}/preview/{token}"
        # Auto-detect public URL: Railway sets RAILWAY_PUBLIC_DOMAIN automatically
        _railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
        base_url = (
            os.environ.get("PUBLIC_URL", "").rstrip("/")
            or (f"https://{_railway_domain}" if _railway_domain else "")
            or "http://localhost:5050"
        )
        customize_url = f"{base_url}/customize/{token}"

        print(f"[email] Searching for contact email...")
        email = find_email(biz)

        if email:
            print(f"[email] Sending to {email}")
            try:
                send_pitch(
                    smtp_host=os.environ["SMTP_HOST"],
                    smtp_port=int(os.environ["SMTP_PORT"]),
                    smtp_user=os.environ["SMTP_USER"],
                    smtp_pass=os.environ["SMTP_PASS"],
                    from_name=os.environ["FROM_NAME"],
                    to_email=email,
                    business=biz,
                    preview_url=preview_url,
                    customize_url=customize_url,
                    language=language,
                )
                mark_processed(place_id, name, city, business_type, email, preview_url, "sent", html=html, token=token)
                print(f"[email] Sent!")
            except Exception as e:
                print(f"[email] Failed: {e}")
                mark_processed(place_id, name, city, business_type, email, preview_url, "email_failed", html=html, token=token)
        else:
            print(f"[email] No email found — trying SMS fallback...")
            if biz.get("phone"):
                ok = send_sms(
                    smtp_host=os.environ["SMTP_HOST"],
                    smtp_port=int(os.environ["SMTP_PORT"]),
                    smtp_user=os.environ["SMTP_USER"],
                    smtp_pass=os.environ["SMTP_PASS"],
                    from_name=os.environ.get("FROM_NAME", ""),
                    business=biz,
                    preview_url=preview_url,
                )
                status = "sms_sent" if ok else "no_contact"
                mark_processed(place_id, name, city, business_type, biz.get("phone",""), preview_url, status, html=html, token=token)
                print(f"[sms] {'Sent!' if ok else 'Failed — no phone or bad number'}")
            else:
                print(f"[sms] No phone number — skipping")
                mark_processed(place_id, name, city, business_type, "", preview_url, "no_contact", html=html, token=token)

    print("\n[done] Run complete.")


def show_list():
    init_db()
    rows = list_all()
    if not rows:
        print("No businesses tracked yet.")
        return
    print(f"\n{'Name':<30} {'City':<15} {'Status':<14} {'Email':<30} {'Date'}")
    print("-" * 110)
    for name, city, email, url, status, created in rows:
        print(f"{name:<30} {city:<15} {status:<14} {(email or ''):<30} {created[:10]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Website bot for businesses without sites")
    parser.add_argument("--city", type=str, help="City to search, e.g. 'Austin, TX'")
    parser.add_argument("--type", dest="btype", type=str, default="restaurant",
                        help="Business type (restaurant, plumber, salon, etc.)")
    parser.add_argument("--limit", type=int, default=10, help="Max businesses to process")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate HTML locally, skip deploy and email")
    parser.add_argument("--all-cities", action="store_true",
                        help="Run across all top 10 most populated US cities")
    parser.add_argument("--list", action="store_true", help="Show all tracked businesses")
    args = parser.parse_args()

    if args.list:
        show_list()
    elif args.all_cities:
        for i, city in enumerate(TOP_10_CITIES, 1):
            print(f"\n{'='*60}")
            print(f"  City {i}/10: {city}")
            print(f"{'='*60}")
            run(city, args.btype, args.limit, args.dry_run)
    elif not args.city:
        parser.print_help()
        sys.exit(1)
    else:
        run(args.city, args.btype, args.limit, args.dry_run)
