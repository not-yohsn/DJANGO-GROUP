# Django SMS Sender

A web application built with the Django framework that sends SMS messages through the TextBee SMS API (which uses your own Android phone and SIM as the gateway). A user enters a recipient phone number and a message, the application validates the input, submits it to the provider, and displays a success or failure result. Every attempt is recorded in a message history.

**Course:** IT 120 - Integrative Programming and Technologies
**Activity:** Group Assignment
**Section:** HPNO1

## Group Members and Responsibilities

| Member | Responsibility |
|--------|----------------|
| John Joseph Perez | Django project setup, views, URLs, application logic, User interface, forms, validation, user feedback, SMS provider integration, testing, documentation, demo |

## Main Features

- SMS composition form: recipient phone number field, message field, and a Send button.
- Input validation: rejects empty fields and invalid phone-number formats (Philippine mobile numbers such as `09171234567` or `+639171234567`, normalized before sending).
- Error handling: missing or wrong credentials, invalid numbers, provider errors, and network errors are all caught and shown as readable messages without exposing secrets.
- Secure configuration: the SMS provider API key is read from an environment variable (`.env`), never hardcoded.
- CSRF protection on the form (Django built-in).
- **Extra features:** a live character counter on the message field, and a message-history page that lists every send attempt with its status.

## Technologies and Dependencies

- Python 3
- Django 6.1.2
- TextBee SMS API (called over HTTPS with Python's standard library, no extra SDK)
- python-dotenv 1.2.2 (loads the `.env` file)
- Bootstrap 5 (via CDN, for the user interface)

See `requirements.txt` for exact versions.

## Installation and Setup

1. Clone the repository and enter the project folder.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS / Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply the database migrations:
   ```bash
   python manage.py migrate
   ```

## Configuring the SMS Provider (TextBee)

> **Why TextBee:** Twilio no longer offers free trial accounts in the Philippines
> ("Trials are currently unavailable in Philippines"). We use TextBee instead, which
> turns your own Android phone and SIM into the SMS gateway. It is free (50 messages
> per day, 300 per month), needs no credits or card, and the SMS is sent from your
> real number. The brief allows any SMS provider ("such as Twilio").

1. Sign up free at <https://app.textbee.dev/register> and verify your email.
2. Install the **TextBee app** on an Android phone (download from
   <https://textbee.dev/download>), log in, and keep the phone charged and online.
3. In the dashboard (<https://app.textbee.dev/dashboard>) **register your device**
   (scan the code / enable the gateway) and **generate an API key**. Copy the API key
   and the **Device ID** from the Devices panel.
4. Copy `.env.example` to `.env` and set your values:
   ```bash
   copy .env.example .env        # Windows
   # cp .env.example .env        # macOS / Linux
   ```
   ```
   TEXTBEE_API_KEY=your_api_key_here
   TEXTBEE_DEVICE_ID=your_device_id   # optional; blank uses your default device
   ```
   The `.env` file is listed in `.gitignore` and must never be committed.
5. Enter the recipient as a Philippine mobile number, for example `09171234567`
   (the app accepts `+639171234567` too and normalizes to international format).

> **Note:** the TextBee phone must stay online for the message to go out; if it is
> offline, the message waits until the phone reconnects.

## Running the Application

```bash
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

- `/` - the SMS send form
- `/history/` - the message history
- `/admin/` - Django admin (run `python manage.py createsuperuser` first)

## Testing Procedures and Results

Run the automated test suite:

```bash
python manage.py test
```

Result: **9 tests pass.** They cover form validation (valid input, empty recipient, empty message, invalid phone format), the send view (form renders, successful send is logged, failed send is logged as failed, invalid input creates no record), and the SMS service (missing credentials returns a graceful failure).

Manual test cases (from the assignment brief):

| Test case | Expected result | Status |
|-----------|-----------------|--------|
| Valid phone number and message | Attempts to send and shows the provider response | Pass |
| Empty phone number | Submission rejected with a validation message | Pass |
| Empty message | Submission rejected with a validation message | Pass |
| Invalid phone number | Validation error shown | Pass |
| Missing / incorrect credentials | Handled without exposing sensitive information | Pass |
| Provider or network error | Understandable failure message shown | Pass |

The application reports **submission**, not confirmed delivery: a successful TextBee API response (HTTP 200, "added to queue") means the message was accepted for the phone to send, not necessarily delivered.

## Known Limitations

- **Twilio was not usable from the Philippines.** Twilio shows "Trials are currently unavailable in Philippines" and only lets a PH account Upgrade (pay) or switch accounts, so we switched to TextBee. The brief allows any SMS provider ("such as Twilio"), and only the `send_sms` function in `sms_app/sms_service.py` is provider-specific.
- **TextBee needs an Android phone as the gateway.** The phone (Android 7+) must have the TextBee app installed and stay online; if it is offline, the message waits.
- **Free plan limits:** 50 messages per day and 300 per month (sent and received combined).
- **The gateway SIM cannot reliably text its own number.** Sending to the same SIM that runs the TextBee gateway tends to fail with "the phone could not send the SMS (Android gave no exact reason)." Always send to a different number.
- **The gateway SIM must have SMS load/credit and signal.** If the SIM has no balance or no signal, the send fails at the phone even though the app and TextBee report the message as submitted.
- The app confirms submission to the provider, not final delivery to the handset.
- SQLite is used for simplicity (development database).
