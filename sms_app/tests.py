from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .forms import SMSForm
from .models import SentMessage
from .sms_service import SMSResult


class SMSFormTests(TestCase):
    def test_valid_local_number_is_normalized(self):
        form = SMSForm(data={"recipient": "09171234567", "message": "Hello"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["recipient"], "+639171234567")

    def test_valid_international_number(self):
        form = SMSForm(data={"recipient": "+639171234567", "message": "Hello"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["recipient"], "+639171234567")

    def test_empty_recipient_is_rejected(self):
        form = SMSForm(data={"recipient": "", "message": "Hello"})
        self.assertFalse(form.is_valid())
        self.assertIn("recipient", form.errors)

    def test_empty_message_is_rejected(self):
        form = SMSForm(data={"recipient": "09171234567", "message": "   "})
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_invalid_phone_format_is_rejected(self):
        form = SMSForm(data={"recipient": "12345", "message": "Hi"})
        self.assertFalse(form.is_valid())
        self.assertIn("recipient", form.errors)


class SendViewTests(TestCase):
    def test_get_renders_form(self):
        response = self.client.get(reverse("send_sms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Send an SMS")

    @patch("sms_app.views.send_sms")
    def test_successful_send_is_logged(self, mock_send):
        mock_send.return_value = SMSResult(success=True, sid="SM123")
        response = self.client.post(reverse("send_sms"), {
            "recipient": "+639171234567",
            "message": "Hello there",
        })
        self.assertEqual(response.status_code, 302)  # redirect after success
        record = SentMessage.objects.get()
        self.assertEqual(record.status, SentMessage.STATUS_SENT)
        self.assertEqual(record.provider_sid, "SM123")

    @patch("sms_app.views.send_sms")
    def test_failed_send_is_logged_as_failed(self, mock_send):
        mock_send.return_value = SMSResult(success=False, error="Provider error")
        response = self.client.post(reverse("send_sms"), {
            "recipient": "+639171234567",
            "message": "Hello there",
        })
        self.assertEqual(response.status_code, 200)  # re-renders with error
        record = SentMessage.objects.get()
        self.assertEqual(record.status, SentMessage.STATUS_FAILED)

    def test_invalid_post_does_not_create_record(self):
        self.client.post(reverse("send_sms"), {"recipient": "", "message": ""})
        self.assertEqual(SentMessage.objects.count(), 0)


class SMSServiceTests(TestCase):
    def test_missing_credentials_returns_failure(self):
        from .sms_service import send_sms
        with self.settings(TEXTBEE_API_KEY=""):
            result = send_sms("+639171234567", "Hi")
        self.assertFalse(result.success)
        self.assertIn("not configured", result.error)
