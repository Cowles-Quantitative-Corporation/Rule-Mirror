"""Fail-closed CQC product access lookup with an opaque member subject."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request

from app.core.config import get_settings


def _subject(secret: str, email: str) -> str:
    return hmac.new(secret.encode("utf-8"), email.strip().lower().encode("utf-8"), hashlib.sha256).hexdigest()


def _signature(secret: str, timestamp: str, subject: str) -> str:
    message = f"GET\n/api/cqc/entitlement\n{timestamp}\n{subject}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def cqc_entitlements_for_email(email: str) -> dict:
    """Return effective products. Any bad response or outage grants nothing."""
    settings = get_settings()
    url = settings.cqc_entitlement_api_url.strip().rstrip("/")
    secret = settings.cqc_entitlement_shared_secret.strip()
    if not url or len(secret) < 32 or "@" not in email:
        return {"products": [], "active": False, "source": "not_configured"}
    timestamp = str(int(time.time()))
    subject = _subject(secret, email)
    request = urllib.request.Request(
        f"{url}/api/cqc/entitlement",
        headers={
            "Accept": "application/json",
            "X-CQC-Subject": subject,
            "X-CQC-Timestamp": timestamp,
            "X-CQC-Signature": _signature(secret, timestamp, subject),
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=max(0.5, min(settings.cqc_entitlement_timeout_seconds, 10.0))) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, urllib.error.HTTPError, urllib.error.URLError):
        return {"products": [], "active": False, "source": "unavailable"}
    raw_products = payload.get("products")
    products = sorted({item for item in raw_products if item in {"cqc_max", "oryntra_pro", "rulemirror_pro"}}) if isinstance(raw_products, list) else []
    return {
        "products": products,
        "active": bool(products),
        "rulemirror_pro": "rulemirror_pro" in products,
        "expires_at": payload.get("expires_at") if products else None,
        "source": "cqc_entitlement_service" if products else "not_entitled",
    }
