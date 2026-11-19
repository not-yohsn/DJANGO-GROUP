from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import SMSForm
from .models import SentMessage
from .sms_service import send_sms


def send_sms_view(request):
    """Display the SMS form and process submissions."""
    if request.method == "POST":
        form = SMSForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data["recipient"]
            body = form.cleaned_data["message"]

            result = send_sms(recipient, body)

            if result.success:
                SentMessage.objects.create(
                    recipient=recipient,
                    body=body,
                    status=SentMessage.STATUS_SENT,
                    provider_sid=result.sid,
                )
                messages.success(
                    request,
                    "Message submitted to the provider "
                    "(submission confirmed, delivery not guaranteed).",
                )
                return redirect("send_sms")
            else:
                SentMessage.objects.create(
                    recipient=recipient,
                    body=body,
                    status=SentMessage.STATUS_FAILED,
                    error_detail=result.error[:255],
                )
                messages.error(request, result.error)
        # If the form is invalid, fall through and re-render with errors.
    else:
        form = SMSForm()

    return render(request, "sms_app/send.html", {"form": form})


def history_view(request):
    """Show previous send attempts (the message-history feature)."""
    sent_messages = SentMessage.objects.all()
    return render(request, "sms_app/history.html", {"messages_list": sent_messages})
