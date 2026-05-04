"""
Free SMS via carrier email gateways.
Sends to all major carriers — the right one delivers, others bounce silently.
Uses the existing Gmail SMTP account, zero cost.
"""
import re
import smtplib
from email.mime.text import MIMEText

# Top 3 US carriers only — covers ~80% of numbers, keeps bounce spam low
CARRIER_GATEWAYS = [
    "txt.att.net",    # AT&T    ~40% market share
    "vtext.com",      # Verizon ~28%
    "tmomail.net",    # T-Mobile ~27%
]

SMS_BODY = (
    "Hi {name}! I noticed you don't have a website so I built one for you — free. "
    "Take a look: {preview_url} "
    "Want it live on your own domain? $99/mo, I handle everything. "
    "-{from_name} (reply STOP to opt out)"
)


def _clean_phone(phone: str) -> str | None:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return digits
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:]
    return None


def send_sms(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    from_name: str,
    business: dict,
    preview_url: str,
) -> bool:
    phone_raw = business.get("phone", "")
    if not phone_raw:
        return False

    digits = _clean_phone(phone_raw)
    if not digits:
        return False

    body = SMS_BODY.format(
        name=business["name"],
        preview_url=preview_url,
        from_name=from_name,
    )[:300]

    sent = False
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            for gateway in CARRIER_GATEWAYS:
                to = f"{digits}@{gateway}"
                msg = MIMEText(body)
                msg["From"]    = smtp_user
                msg["To"]      = to
                msg["Subject"] = ""
                try:
                    server.sendmail(smtp_user, to, msg.as_string())
                    sent = True
                except Exception:
                    pass
    except Exception as e:
        print(f"  [sms] SMTP error: {e}")
        return False

    return sent
