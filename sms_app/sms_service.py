"""
Thin wrapper around the TextBee SMS API (https://textbee.dev).

TextBee sends through your own Android phone and SIM. Credentials come from
Django settings (read from environment variables), so no secret is hardcoded.
Every failure mode is caught and returned as a plain result object, so the view
never crashes and never leaks details.

TextBee request:  POST https://api.textbee.dev/api/v1/gateway/send-sms
                  header x-api-key, JSON body {recipients, message, deviceId?}
TextBee response: {"data": {"success": true, "smsBatchId": "...", ...}}
"""

import json
import urllib.error
import urllib.request

from django.conf import settings

TEXTBEE_URL = "https://api.textbee.dev/api/v1/gateway/send-sms"


class SMSResult:
    def __init__(self, success, sid="", error=""):
        self.success = success
        self.sid = sid
        self.error = error


def send_sms(recipient, body):
    """Attempt to send an SMS through TextBee. Returns an SMSResult, never raises."""

    # Guard: missing API key.
    if not settings.TEXTBEE_API_KEY:
        return SMSResult(
            success=False,
            error="SMS service is not configured. Set TEXTBEE_API_KEY in the "
                  ".env file before sending.",
        )

    payload = {"recipients": [recipient], "message": body}
    if settings.TEXTBEE_DEVICE_ID:
        payload["deviceId"] = settings.TEXTBEE_DEVICE_ID

    data = json.dumps(payload).encode()
    headers = {
        "x-api-key": settings.TEXTBEE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        request = urllib.request.Request(TEXTBEE_URL, data=data, headers=headers)
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        # Provider rejected the request (no online device, out of quota, bad key).
        return SMSResult(success=False, error=_extract_error(exc))
    except Exception:
        # Network error, timeout, or an unreadable response.
        return SMSResult(
            success=False,
            error="Could not reach the SMS provider. Check your connection "
                  "and try again.",
        )

    # Success response nests the result under "data".
    details = result.get("data", {}) if isinstance(result, dict) else {}
    if details.get("success"):
        # Accepted for delivery (submission, not confirmed delivery).
        return SMSResult(success=True, sid=str(details.get("smsBatchId", "")))

    return SMSResult(
        success=False,
        error=details.get("message") or details.get("error") or "message rejected",
    )


def _extract_error(http_error):
    """Pull a readable message out of an HTTP error body, no secrets exposed."""
    try:
        body = json.loads(http_error.read().decode())
        msg = body.get("error") or body.get("message")
        if msg:
            return f"Provider error: {msg}"
    except Exception:
        pass
    return f"Provider error (HTTP {http_error.code})."
