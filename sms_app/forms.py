import re

from django import forms

MAX_SMS_LENGTH = 320


def normalize_ph_number(raw):
    """
    Accept a Philippine mobile number in common forms and return it in
    international E.164 format (+639XXXXXXXXX, which TextBee recommends),
    or None if invalid.
    Accepts: 09171234567, +639171234567, 639171234567, 9171234567.
    """
    digits = re.sub(r"[^\d]", "", raw)  # strip +, spaces, dashes
    if digits.startswith("0") and len(digits) == 11:
        digits = "63" + digits[1:]
    elif len(digits) == 10 and digits.startswith("9"):
        digits = "63" + digits
    if re.fullmatch(r"639\d{9}", digits):
        return "+" + digits
    return None


class SMSForm(forms.Form):
    recipient = forms.CharField(
        label="Recipient phone number",
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "09171234567",
            "class": "form-control",
        }),
    )
    message = forms.CharField(
        label="Message",
        max_length=MAX_SMS_LENGTH,
        widget=forms.Textarea(attrs={
            "placeholder": "Type your message here...",
            "class": "form-control",
            "rows": 4,
            "id": "id_message",
        }),
    )

    def clean_recipient(self):
        value = self.cleaned_data["recipient"].strip()
        if not value:
            raise forms.ValidationError("Please enter a recipient phone number.")
        normalized = normalize_ph_number(value)
        if normalized is None:
            raise forms.ValidationError(
                "Enter a valid Philippine mobile number, "
                "for example 09171234567 or +639171234567."
            )
        return normalized

    def clean_message(self):
        value = self.cleaned_data["message"].strip()
        if not value:
            raise forms.ValidationError("The message cannot be empty.")
        return value
