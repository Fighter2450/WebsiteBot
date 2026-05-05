#!/usr/bin/env python3
"""
Admin dashboard + auto-scheduler.
Double-click start.bat to launch everything.
"""
import sqlite3
import os
import sys
import threading
import time
import subprocess
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Add parent dir so we can import bot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tracker import get_by_token, save_custom_html
from generator import generate_website
import anthropic

# DB_PATH: use env var so Railway volume or local path can be set externally
DB_PATH   = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "tracker.db"))
STATIC    = os.path.dirname(__file__)
BOT_MAIN  = os.path.join(os.path.dirname(__file__), "..", "main.py")

# World cities + coords + language from cities.py
from cities import WORLD_CITIES, ALL_CITIES, get_city_info

app = Flask(__name__, static_folder=STATIC)
CORS(app)

# ── Scheduler state ──────────────────────────────────────────────
scheduler_state = {
    "running":        False,
    "enabled":        True,
    "interval_hours": 2,
    "last_run":       None,
    "next_run":       (datetime.now() + timedelta(seconds=5)).isoformat(),
    "current_city":   None,
    "current_category": None,
    "log":            [],
}

ALL_CATEGORIES = [
    "restaurant", "cafe", "bar", "bakery",
    "plumber", "electrician", "locksmith", "painter",
    "hair_care", "beauty_salon", "spa", "nail_salon",
    "gym", "laundry", "car_repair", "car_wash",
    "dentist", "doctor", "physiotherapist", "veterinary_care",
    "florist", "jewelry_store", "clothing_store", "shoe_store",
    "lawyer", "accounting", "real_estate_agency", "insurance_agency",
]

# All world cities — pulled from cities.py
CITIES = ALL_CITIES

# Build CITY_COORDS from WORLD_CITIES dict (lat/lng keyed by city name)
CITY_COORDS = {city: {"lat": info["lat"], "lng": info["lng"]} for city, info in WORLD_CITIES.items()}


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    scheduler_state["log"].insert(0, entry)
    scheduler_state["log"] = scheduler_state["log"][:100]
    print(entry)


MAX_PER_SEARCH = 5   # finder=90s + 5×(45s Claude + 30s email) = ~475s, fits in 600s timeout

def run_bot_cycle():
    scheduler_state["running"] = True
    scheduler_state["last_run"] = datetime.now().isoformat()
    log(f"🚀 Auto-run started — {len(CITIES)} world cities × {len(ALL_CATEGORIES)} categories (max {MAX_PER_SEARCH}/search)")

    for category in ALL_CATEGORIES:
        if not scheduler_state["enabled"]:
            log("⏹ Scheduler disabled — stopping")
            break
        for city in CITIES:
            if not scheduler_state["enabled"]:
                break
            scheduler_state["current_city"] = city
            scheduler_state["current_category"] = category
            city_info = get_city_info(city)
            lang      = city_info.get("lang", "en")
            log(f"📍 {city} ({lang}) — {category}")
            try:
                result = subprocess.run(
                    [sys.executable, BOT_MAIN,
                     "--city", city, "--type", category, "--limit", str(MAX_PER_SEARCH)],
                    cwd=os.path.join(os.path.dirname(__file__), ".."),
                    capture_output=True, text=True, timeout=600,   # 10 min; finder capped at 90s internally
                )
                found    = result.stdout.count("[found]")
                sent     = result.stdout.count("[email] Sent!")
                sms      = result.stdout.count("[sms] Sent!")
                no_email = result.stdout.count("No email found")
                err      = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
                summary  = f"{found} found, {sent} emailed, {sms} SMS, {no_email} no-email"
                if err:
                    summary += f" | ERR: {err[-120:]}"
                log(f"✅ {city}/{category}: {summary}")
            except subprocess.TimeoutExpired:
                log(f"⚠️ {city}/{category}: timed out")
            except Exception as e:
                log(f"❌ {city}/{category}: {e}")

    scheduler_state["running"] = False
    scheduler_state["current_city"] = None
    nxt = datetime.now() + timedelta(hours=scheduler_state["interval_hours"])
    scheduler_state["next_run"] = nxt.isoformat()
    log(f"💤 Cycle complete. Next run at {nxt.strftime('%I:%M %p')}")


def scheduler_loop():
    # Wait 5 seconds after startup, then kick off immediately
    time.sleep(5)
    log("🤖 Auto-scheduler initialized")

    while True:
        if scheduler_state["enabled"] and not scheduler_state["running"]:
            run_bot_cycle()

        # Sleep in 10-second ticks so we can react to interval changes
        target = datetime.now() + timedelta(hours=scheduler_state["interval_hours"])
        scheduler_state["next_run"] = target.isoformat()
        while datetime.now() < target:
            time.sleep(10)
            if not scheduler_state["enabled"]:
                break


# ── Flask routes ─────────────────────────────────────────────────
def get_db():
    if not os.path.exists(DB_PATH):
        return None
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


@app.route("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.route("/api/stats")
def stats():
    con = get_db()
    if not con:
        return jsonify({"total":0,"sent":0,"deployed":0,"no_email":0,"cities":0})
    rows = con.execute("SELECT status, COUNT(*) as n FROM businesses GROUP BY status").fetchall()
    city_count = con.execute("SELECT COUNT(DISTINCT city) FROM businesses").fetchone()[0]
    con.close()
    counts = {r["status"]: r["n"] for r in rows}
    total  = sum(counts.values())
    return jsonify({
        "total": total, "sent": counts.get("sent", 0),
        "deployed": total - counts.get("no_email",0) - counts.get("dry_run",0),
        "no_email": counts.get("no_email",0), "cities": city_count,
    })


@app.route("/api/cities")
def cities():
    con = get_db()
    if not con:
        return jsonify([])
    rows = con.execute("""
        SELECT city, COUNT(*) as total,
               SUM(CASE WHEN status='sent' THEN 1 ELSE 0 END) as sent
        FROM businesses GROUP BY city ORDER BY total DESC
    """).fetchall()
    con.close()
    result = []
    for r in rows:
        coords = CITY_COORDS.get(r["city"], {"lat":39.5,"lng":-98.35})
        result.append({"city":r["city"],"total":r["total"],"sent":r["sent"],**coords})
    return jsonify(result)


@app.route("/api/city/<path:city_name>")
def city_businesses(city_name):
    con = get_db()
    if not con:
        return jsonify([])
    rows = con.execute("""
        SELECT name, place_id, city, category, email, preview_url, status, token, created_at
        FROM businesses WHERE city=? ORDER BY created_at DESC
    """, (city_name,)).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/activity")
def activity():
    con = get_db()
    if not con:
        return jsonify([])
    rows = con.execute("""
        SELECT name, city, category, email, preview_url, status, created_at
        FROM businesses ORDER BY created_at DESC LIMIT 50
    """).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/arcs")
def arcs():
    con = get_db()
    if not con:
        return jsonify([])
    rows = con.execute("SELECT DISTINCT city FROM businesses WHERE status='sent'").fetchall()
    con.close()
    HQ = {"lat": 39.5, "lng": -98.35}
    result = []
    for r in rows:
        coords = CITY_COORDS.get(r["city"])
        if coords:
            result.append({"startLat":HQ["lat"],"startLng":HQ["lng"],
                           "endLat":coords["lat"],"endLng":coords["lng"],"city":r["city"]})
    return jsonify(result)


@app.route("/api/scheduler")
def scheduler_status():
    return jsonify({
        "running":          scheduler_state["running"],
        "enabled":          scheduler_state["enabled"],
        "interval_hours":   scheduler_state["interval_hours"],
        "last_run":         scheduler_state["last_run"],
        "next_run":         scheduler_state["next_run"],
        "current_city":     scheduler_state["current_city"],
        "current_category": scheduler_state["current_category"],
        "log":              scheduler_state["log"][:20],
        "limit_per_city":   MAX_PER_SEARCH,
        "total_categories": len(ALL_CATEGORIES),
        "total_cities":     len(CITIES),
        "total_countries":  len({WORLD_CITIES[c]["country"] for c in WORLD_CITIES}),
    })


@app.route("/api/scheduler/toggle", methods=["POST"])
def toggle_scheduler():
    scheduler_state["enabled"] = not scheduler_state["enabled"]
    log(f"Scheduler {'enabled' if scheduler_state['enabled'] else 'paused'} by user")
    return jsonify({"enabled": scheduler_state["enabled"]})


@app.route("/api/scheduler/run-now", methods=["POST"])
def run_now():
    if scheduler_state["running"]:
        return jsonify({"error": "Already running"}), 400
    # Force-enable so the cycle doesn't exit immediately if scheduler is paused
    scheduler_state["enabled"] = True
    threading.Thread(target=run_bot_cycle, daemon=True).start()
    return jsonify({"ok": True})


@app.route("/api/test-email", methods=["POST"])
def test_email():
    import smtplib
    from email.mime.text import MIMEText
    try:
        host  = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        port  = int(os.environ.get("SMTP_PORT", 587))
        user  = os.environ.get("SMTP_USER", "")
        pw    = os.environ.get("SMTP_PASS", "")
        fname = os.environ.get("FROM_NAME", "WebsiteBot")
        if not user or not pw:
            return jsonify({"error": "SMTP_USER or SMTP_PASS not set in .env"}), 400
        msg = MIMEText(f"Test email from WebsiteBot — SMTP is working!")
        msg["Subject"] = "WebsiteBot SMTP Test"
        msg["From"]    = f"{fname} <{user}>"
        msg["To"]      = user
        if port == 465:
            with smtplib.SMTP_SSL(host, port) as s:
                s.login(user, pw)
                s.sendmail(user, user, msg.as_string())
        else:
            with smtplib.SMTP(host, port) as s:
                s.ehlo(); s.starttls(); s.login(user, pw)
                s.sendmail(user, user, msg.as_string())
        log(f"📧 Test email sent to {user}")
        return jsonify({"ok": True, "sent_to": user})
    except Exception as e:
        log(f"❌ Test email failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/scheduler/settings", methods=["POST"])
def update_settings():
    data = request.json
    if "interval_hours" in data:
        scheduler_state["interval_hours"] = max(1, int(data["interval_hours"]))
    log(f"Settings updated: {data}")
    return jsonify({"ok": True})


@app.route("/api/regen", methods=["POST"])
def regen_site():
    try:
        data     = request.json or {}
        place_id = data.get("place_id", "")
        notes    = data.get("notes", "")

        if not place_id:
            return jsonify({"error": "No place_id provided"}), 400

        con = get_db()
        if not con:
            return jsonify({"error": "No database found"}), 500
        row = con.execute("SELECT * FROM businesses WHERE place_id=?", (place_id,)).fetchone()
        con.close()
        if not row:
            return jsonify({"error": f"Business not found for place_id: {place_id}"}), 404

        biz = dict(row)
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return jsonify({"error": "ANTHROPIC_API_KEY not set in .env"}), 500

        ai_client = anthropic.Anthropic(api_key=api_key)

        desc = biz.get("description") or ""
        if notes:
            desc = desc + f"\n\nAdmin notes: {notes}"

        city_name = biz.get("city", "")
        language  = get_city_info(city_name).get("lang", "en")

        business = {
            "place_id":     biz.get("place_id", ""),
            "name":         biz.get("name", ""),
            "address":      biz.get("address") or "",
            "phone":        biz.get("phone") or "",
            "hours":        [],
            "rating":       biz.get("rating"),
            "review_count": biz.get("review_count") or 0,
            "reviews":      [],
            "category":     biz.get("category", ""),
            "city":         city_name,
            "tagline":      biz.get("tagline") or "",
            "description":  desc,
            "logo_b64":     "",
            "photos_b64":   [],
        }

        # Always rebuild fresh — passing existing HTML caused Claude to preserve the old broken design
        html = generate_website(ai_client, business, existing_html="", language=language)

        token = biz.get("token", "")
        if token:
            save_custom_html(token, html)

        print(f"[regen] Done for {biz.get('name')}")
        return jsonify({"ok": True, "html": html, "preview_url": biz.get("preview_url", ""), "token": token})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/retry-failed-emails", methods=["POST"])
def retry_failed_emails():
    """Retry sending emails to all businesses with status=email_failed."""
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_name = os.environ.get("FROM_NAME", "")
    if not all([smtp_host, smtp_user, smtp_pass]):
        return jsonify({"error": "SMTP env vars not set"}), 500

    con = get_db()
    if not con:
        return jsonify({"error": "No database"}), 500
    rows = con.execute(
        "SELECT * FROM businesses WHERE status='email_failed' AND email IS NOT NULL AND email != ''"
    ).fetchall()
    con.close()
    total = len(rows)
    if total == 0:
        return jsonify({"ok": True, "retried": 0, "message": "No failed emails to retry"})

    from emailer import send_pitch

    def _run():
        sent = 0
        failed = 0
        for r in rows:
            biz = dict(r)
            try:
                railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
                base_url = (os.environ.get("PUBLIC_URL", "").rstrip("/")
                            or (f"https://{railway_domain}" if railway_domain else "")
                            or "http://localhost:5050")
                token = biz.get("token", "")
                customize_url = f"{base_url}/customize/{token}" if token else ""
                preview_url   = biz.get("preview_url", "")
                language      = get_city_info(biz.get("city", "")).get("lang", "en")

                business = {
                    "name":     biz["name"],
                    "category": biz.get("category", "restaurant"),
                    "city":     biz.get("city", ""),
                    "phone":    biz.get("phone", ""),
                }
                send_pitch(
                    smtp_host=smtp_host, smtp_port=smtp_port,
                    smtp_user=smtp_user, smtp_pass=smtp_pass,
                    from_name=from_name, to_email=biz["email"],
                    business=business, preview_url=preview_url,
                    customize_url=customize_url, language=language,
                )
                con2 = get_db()
                con2.execute("UPDATE businesses SET status='sent' WHERE place_id=?", (biz["place_id"],))
                con2.commit()
                con2.close()
                sent += 1
                log(f"📧 Retry sent → {biz['name']} ({biz['email']})")
            except Exception as e:
                failed += 1
                log(f"❌ Retry failed → {biz['name']}: {e}")
        log(f"✅ Retry complete: {sent} sent, {failed} still failing")

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"ok": True, "queued": total})


@app.route("/api/regen-all", methods=["POST"])
def regen_all():
    """Re-generate every site with the current palette logic (fixes old red/white sites)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"error": "ANTHROPIC_API_KEY not set"}), 500
    con = get_db()
    if not con:
        return jsonify({"error": "No database"}), 500
    rows = con.execute("SELECT place_id, name, city, category FROM businesses ORDER BY created_at DESC").fetchall()
    con.close()
    total = len(rows)
    if total == 0:
        return jsonify({"ok": True, "regenerated": 0})

    def _run():
        ai_client = anthropic.Anthropic(api_key=api_key)
        done = 0
        for r in rows:
            try:
                con2 = get_db()
                row = con2.execute("SELECT * FROM businesses WHERE place_id=?", (r["place_id"],)).fetchone()
                con2.close()
                if not row:
                    continue
                biz = dict(row)
                language = get_city_info(biz.get("city","")).get("lang","en")
                business = {
                    "place_id": biz.get("place_id",""), "name": biz.get("name",""),
                    "address": biz.get("address",""), "phone": biz.get("phone",""),
                    "hours": [], "rating": biz.get("rating"), "review_count": biz.get("review_count",0),
                    "reviews": [], "category": biz.get("category",""), "city": biz.get("city",""),
                    "tagline": biz.get("tagline",""), "description": biz.get("description",""),
                    "logo_b64": "", "photos_b64": [],
                }
                html = generate_website(ai_client, business, existing_html="", language=language)
                token = biz.get("token","")
                if token:
                    save_custom_html(token, html)
                con3 = get_db()
                con3.execute("UPDATE businesses SET html=? WHERE place_id=?", (html, biz["place_id"]))
                con3.commit()
                con3.close()
                done += 1
                log(f"🎨 Regen {done}/{total}: {biz.get('name')}")
            except Exception as e:
                log(f"⚠️ Regen failed for {r['name']}: {e}")
        log(f"✅ Regen-all complete: {done}/{total} sites updated")

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"ok": True, "queued": total})


@app.route("/api/business/<place_id>/html")
def business_html(place_id):
    con = get_db()
    if not con:
        return jsonify({"html": ""}), 200
    row = con.execute("SELECT html, custom_html FROM businesses WHERE place_id=?", (place_id,)).fetchone()
    con.close()
    if not row:
        return jsonify({"html": ""}), 200
    return jsonify({"html": row["custom_html"] or row["html"] or ""})


@app.route("/preview/<token>")
def preview_html(token):
    """Serve the latest HTML for a business directly as a webpage."""
    con = get_db()
    if not con:
        return "Not found", 404
    row = con.execute("SELECT html, custom_html FROM businesses WHERE token=?", (token,)).fetchone()
    con.close()
    if not row:
        return "Not found", 404
    html = row["custom_html"] or row["html"] or ""
    if not html:
        return "No HTML generated yet", 404
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/guide")
def guide():
    return send_from_directory(STATIC, "guide.html")


@app.route("/customize/<token>")
def customize_page(token):
    return send_from_directory(STATIC, "customize.html")


@app.route("/api/customize/<token>", methods=["GET"])
def customize_get(token):
    biz = get_by_token(token)
    if not biz:
        return jsonify({"error": "not found"}), 404
    # Parse stored hours back into list if they're a string
    hours = biz.get("hours") or []
    if isinstance(hours, str):
        import json
        try:
            hours = json.loads(hours)
        except Exception:
            hours = [h for h in hours.split("\n") if h]
    return jsonify({
        "name":        biz.get("name", ""),
        "city":        biz.get("city", ""),
        "category":    biz.get("category", ""),
        "phone":       biz.get("phone", ""),
        "address":     biz.get("address", ""),
        "hours":       hours,
        "tagline":     biz.get("tagline", ""),
        "description": biz.get("description", ""),
        "logo":        biz.get("logo", ""),
        "photos":      [],
        "preview_url": biz.get("preview_url", ""),
        "html":        biz.get("html", ""),
        "custom_html": biz.get("custom_html", ""),
    })


@app.route("/api/customize/<token>", methods=["POST"])
def customize_post(token):
    biz = get_by_token(token)
    if not biz:
        return jsonify({"error": "not found"}), 404

    data = request.json
    ai_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    city_name = biz.get("city", "")
    language  = get_city_info(city_name).get("lang", "en")

    # Build enriched business dict with user overrides
    business = {
        "place_id":     biz.get("place_id", ""),
        "name":         data.get("name") or biz.get("name", ""),
        "address":      data.get("address") or biz.get("address", ""),
        "phone":        data.get("phone") or biz.get("phone", ""),
        "hours":        data.get("hours") or [],
        "rating":       biz.get("rating"),
        "review_count": biz.get("review_count", 0),
        "reviews":      [],
        "category":     biz.get("category", ""),
        "city":         city_name,
        "tagline":      data.get("tagline", ""),
        "description":  data.get("description", ""),
        "logo_b64":     data.get("logo", ""),
        "photos_b64":   data.get("photos", []),
    }

    existing_html = biz.get("custom_html") or biz.get("html") or ""

    try:
        html = generate_website(ai_client, business, existing_html=existing_html, language=language)
        save_custom_html(token, html)
        return jsonify({"html": html, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Start scheduler in background thread
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5050))
    print("\n" + "="*50)
    print("  WebsiteBot Command Center")
    print(f"  http://localhost:{port}")
    print("  Bot will auto-run in 5 seconds...")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
