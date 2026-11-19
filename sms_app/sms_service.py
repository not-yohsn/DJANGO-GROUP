"""
Thin wrapper around the Textbelt SMS API (https://textbelt.com).

The API key comes from Django settings (read from an environment variable),
so no secret is ever hardcoded here. Every failure mode is caught and returned
as a plain result object, so the view never crashes and never leaks details.

Textbelt request:  POST https://textbelt.com/text  with phone, message, key
Textbelt response: {"success": true, "textId": "...", "quotaRemaining": N}
               or  {"success": false, "error": "..."}
"""

import json
import urllib.parse
import urllib.request

from django.conf import settings

TEXTBELT_URL = "https://textbelt.com/text"


class SMSResult:
    def __init__(self, success, sid="", error=""):
        self.success = success
        self.sid = sid
        self.error = error


def send_sms(recipient, body):
    """Attempt to send an SMS through Textbelt. Returns an SMSResult, never raises."""

    # Guard: missing API key.
    if not settings.TEXTBELT_KEY:
        return SMSResult(
            success=False,
            error="SMS service is not configured. Set TEXTBELT_KEY in the .env "
                  "file before sending.",
        )

    data = urllib.parse.urlencode({
        "phone": recipient,
        "message": body,
        "key": settings.TEXTBELT_KEY,
    }).encode()

    try:
        request = urllib.request.Request(TEXTBELT_URL, data=data)
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode())
    except Exception:
        # Network error, timeout, or an unreadable response.
        return SMSResult(
            success=False,
            error="Could not reach the SMS provider. Check your connection "
                  "and try again.",
        )

    # A successful API call means the message was accepted for delivery,
    # not that it was delivered. We report submission, not delivery.
    if payload.get("success"):
        return SMSResult(success=True, sid=str(payload.get("textId", "")))

    # Provider rejected the request (bad number, out of quota, bad key, etc.).
    return SMSResult(
        success=False,
        error=f"Provider error: {payload.get('error', 'message rejected')}",
    )
