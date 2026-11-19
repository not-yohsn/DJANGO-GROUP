import re

from django import forms

# E.164 format: a leading + and 8 to 15 digits, e.g. +639171234567
E164_PATTERN = re.compile(r"^\+\d{8,15}$")

MAX_SMS_LENGTH = 320


class SMSForm(forms.Form):
    recipient = forms.CharField(
        label="Recipient phone number",
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "+639171234567",
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
        value = self.cleaned_data["recipient"].strip().replace(" ", "")
        if not value:
            raise forms.ValidationError("Please enter a recipient phone number.")
        if not E164_PATTERN.match(value):
            raise forms.ValidationError(
                "Enter a valid phone number in international format, "
                "for example +639171234567."
            )
        return value

    def clean_message(self):
        value = self.cleaned_data["message"].strip()
        if not value:
            raise forms.ValidationError("The message cannot be empty.")
        return value
