"""
Thin wrapper around the Twilio API.

All credentials come from Django settings (which read them from environment
variables), so no secret is ever hardcoded here. Every failure mode is caught
and returned as a plain result object, so the view never crashes and never
leaks sensitive details to the user.
"""

from django.conf import settings


class SMSResult:
    def __init__(self, success, sid="", error=""):
        self.success = success
        self.sid = sid
        self.error = error


def send_sms(recipient, body):
    """Attempt to send an SMS. Returns an SMSResult, never raises."""

    # Guard: missing or incomplete credentials.
    if not (settings.TWILIO_ACCOUNT_SID
            and settings.TWILIO_AUTH_TOKEN
            and settings.TWILIO_FROM_NUMBER):
        return SMSResult(
            success=False,
            error="SMS service is not configured. Set the Twilio credentials "
                  "in the .env file before sending.",
        )

    # Import here so the app still loads even if the package is missing.
    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException
    except ImportError:
        return SMSResult(
            success=False,
            error="The twilio package is not installed. Run: pip install twilio",
        )

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_FROM_NUMBER,
            to=recipient,
        )
        # A successful API call means the message was accepted for delivery,
        # not that it was delivered. We report submission, not delivery.
        return SMSResult(success=True, sid=message.sid)
    except TwilioRestException as exc:
        # Provider rejected the request (bad number, unverified recipient,
        # wrong credentials, etc.). Show a readable reason, no secrets.
        return SMSResult(success=False, error=f"Provider error: {exc.msg}")
    except Exception:
        # Network error or any other unexpected failure.
        return SMSResult(
            success=False,
            error="Could not reach the SMS provider. Check your connection "
                  "and try again.",
        )
