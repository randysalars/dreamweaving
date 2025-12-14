"""
GA4 Measurement Protocol helper for Dreamweaving donation events.

Configure env vars:
  GA4_MEASUREMENT_ID=G-XXXXXXX
  GA4_API_SECRET=your_secret

Usage:
  from server_mp import send_donation_success
  send_donation_success(client_id, session_id, amount=25.0, currency="USD", ...)
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

import requests

MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID")
API_SECRET = os.getenv("GA4_API_SECRET")
GA4_ENDPOINT = "https://www.google-analytics.com/mp/collect"


class GA4ConfigError(RuntimeError):
    pass


def _require_config() -> None:
    if not MEASUREMENT_ID or not API_SECRET:
        raise GA4ConfigError("Set GA4_MEASUREMENT_ID and GA4_API_SECRET environment variables.")


def _post_event(client_id: str, events: list[Dict[str, Any]], session_id: Optional[str] = None) -> None:
    _require_config()
    payload: Dict[str, Any] = {
        "client_id": client_id,
        "events": events,
        "timestamp_micros": int(time.time() * 1_000_000),
    }
    if session_id:
        payload["user_id"] = session_id

    resp = requests.post(
        GA4_ENDPOINT,
        params={"measurement_id": MEASUREMENT_ID, "api_secret": API_SECRET},
        json=payload,
        timeout=5,
    )
    if not resp.ok:
        raise RuntimeError(f"GA4 MP error {resp.status_code}: {resp.text}")


def send_donation_success(
    *,
    client_id: str,
    session_id: Optional[str],
    amount: float,
    currency: str = "USD",
    transaction_id: Optional[str] = None,
    cta_label: Optional[str] = None,
    message_type: Optional[str] = None,
    source_medium_campaign: Optional[str] = None,
) -> None:
    """Send donation_success conversion to GA4."""
    event: Dict[str, Any] = {
        "name": "donation_success",
        "params": {
            "stage": "conversion",
            "value": amount,
            "currency": currency,
            "transaction_id": transaction_id or str(uuid.uuid4()),
        },
    }
    if cta_label:
        event["params"]["cta_label"] = cta_label
    if message_type:
        event["params"]["message_type"] = message_type
    if source_medium_campaign:
        event["params"]["source_medium_campaign"] = source_medium_campaign

    _post_event(client_id=client_id, events=[event], session_id=session_id)


def send_donation_abandon(
    *,
    client_id: str,
    session_id: Optional[str],
    transaction_id: Optional[str] = None,
) -> None:
    """Emit donation_abandon when PayPal was opened but no success within SLA."""
    event: Dict[str, Any] = {
        "name": "donation_abandon",
        "params": {
            "stage": "intent",
            "transaction_id": transaction_id or str(uuid.uuid4()),
        },
    }
    _post_event(client_id=client_id, events=[event], session_id=session_id)


if __name__ == "__main__":
    # Simple manual test; set env vars before running.
    cid = str(uuid.uuid4())
    try:
        send_donation_success(
            client_id=cid,
            session_id=None,
            amount=1.23,
            currency="USD",
            cta_label="blessing_cta_top",
            message_type="christ_centered",
            source_medium_campaign="facebook_post|dreamweaving_christmas_2024",
        )
        print("Sent donation_success test event.")
    except Exception as exc:  # pragma: no cover
        print(f"Failed to send GA4 MP event: {exc}")
