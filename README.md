# Django SMS Sender

A web application built with the Django framework that sends SMS messages through the Textbelt SMS API. A user enters a recipient phone number and a message, the application validates the input, submits it to the provider, and displays a success or failure result. Every attempt is recorded in a message history.

**Course:** IT 120 - Integrative Programming and Technologies
**Activity:** Group Assignment
**Section:** HPNO1

## Group Members and Responsibilities

| Member | Responsibility |
|--------|----------------|
| John Joseph Perez | Django project setup, views, URLs, application logic, User interface, forms, validation, user feedback, SMS provider integration, testing, documentation, demo |

## Main Features

- SMS composition form: recipient phone number field, message field, and a Send button.
- Input validation: rejects empty fields and invalid phone-number formats (international E.164, for example `+639171234567`).
- Error handling: missing or wrong credentials, invalid numbers, provider errors, and network errors are all caught and shown as readable messages without exposing secrets.
- Secure configuration: the SMS provider API key is read from an environment variable (`.env`), never hardcoded.
- CSRF protection on the form (Django built-in).
- **Extra features:** a live character counter on the message field, and a message-history page that lists every send attempt with its status.

## Technologies and Dependencies

- Python 3
- Django 6.1.2
- Textbelt SMS API (called over HTTPS with Python's standard library, no extra SDK)
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

## Configuring the SMS Provider (Textbelt)

> **Why Textbelt:** Twilio no longer offers free trial accounts in the Philippines
> ("Trials are currently unavailable in Philippines"). We use Textbelt instead, which
> provides a free tier (1 SMS per day) with no account required, and an inexpensive
> paid key for reliable sending. The brief allows any SMS provider ("such as Twilio").

1. For a quick demo, no account is needed: the free key is the literal word `textbelt`
   (limited to 1 SMS per day). This is already the default in `.env.example`.
2. For reliable sending, buy a paid key at <https://textbelt.com> (cheap, a few dollars
   covers hundreds of texts).
3. Copy `.env.example` to `.env` and set your key:
   ```bash
   copy .env.example .env        # Windows
   # cp .env.example .env        # macOS / Linux
   ```
   ```
   TEXTBELT_KEY=textbelt         # free tier, 1 SMS/day; replace with a paid key
   ```
   The `.env` file is listed in `.gitignore` and must never be committed.
4. Enter the recipient number in international format, for example `+639171234567`.

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

The application reports **submission**, not confirmed delivery: a successful Textbelt API response means the message was accepted, not necessarily delivered.

## Known Limitations

- **Twilio was not usable from the Philippines.** Twilio shows "Trials are currently unavailable in Philippines" and only lets a PH account Upgrade (pay) or switch accounts, so we switched to Textbelt. The brief allows any SMS provider ("such as Twilio"), and only the `send_sms` function in `sms_app/sms_service.py` is provider-specific.
- **Textbelt free tier is limited to 1 SMS per day.** The shared free key (`textbelt`) can also be exhausted globally; for reliable or repeated sending, use a paid Textbelt key.
- The app confirms submission to the provider, not final delivery to the handset.
- SQLite is used for simplicity (development database).
