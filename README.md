# Django SMS Sender

A web application built with the Django framework that sends SMS messages through the Twilio API. A user enters a recipient phone number and a message, the application validates the input, submits it to Twilio, and displays a success or failure result. Every attempt is recorded in a message history.

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
- Secure configuration: Twilio credentials are read from environment variables (`.env`), never hardcoded.
- CSRF protection on the form (Django built-in).
- **Extra features:** a live character counter on the message field, and a message-history page that lists every send attempt with its status.

## Technologies and Dependencies

- Python 3
- Django 6.1.2
- twilio 9.13.0 (SMS provider SDK)
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

## Configuring the SMS Provider (Twilio)

> **Known issue - Twilio trials in the Philippines:** As of this submission, Twilio
> no longer offers free trial accounts in the Philippines ("Trials are currently
> unavailable in Philippines. Twilio doesn't offer free trials in your region.").
> A PH-registered account must either **Upgrade** (add a paid balance) or send from
> a Twilio account created in a supported region. See **Known Limitations** below for
> the workarounds we considered. The application code is complete and works with any
> valid Twilio credentials; only obtaining the trial is blocked by region.

1. Create a free account at <https://www.twilio.com> and open the Console.
2. From the dashboard, copy your **Account SID**, **Auth Token**, and a **Twilio phone number** (get a trial number if needed).
3. On a trial account, verify the recipient number you will text under **Phone Numbers > Verified Caller IDs**.
4. Copy `.env.example` to `.env` and fill in your real values:
   ```bash
   copy .env.example .env        # Windows
   # cp .env.example .env        # macOS / Linux
   ```
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_NUMBER=+1234567890
   ```
   The `.env` file is listed in `.gitignore` and must never be committed.

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

The application reports **submission**, not confirmed delivery: a successful Twilio API response means the message was accepted, not necessarily delivered.

## Known Limitations

- **Twilio free trials are not available in the Philippines.** Twilio shows "Trials are currently unavailable in Philippines" and only lets a PH account Upgrade (pay) or switch accounts. This affects only how we obtain credentials; the application itself works with any valid Twilio account. Workarounds we considered:
  1. **Upgrade the Twilio account** by adding a small paid balance, then use a purchased number.
  2. **Use a Twilio account created in a supported region** (for example a groupmate's account registered elsewhere).
  3. **Swap the provider** for a Philippine SMS gateway such as Semaphore (<https://semaphore.co>). The brief allows any SMS provider ("such as Twilio"); only the `send_sms` function in `sms_app/sms_service.py` would change, the rest of the app stays the same.
- On a Twilio trial account (where available), messages can only be sent to verified numbers and include a trial prefix.
- The app confirms submission to the provider, not final delivery to the handset.
- SQLite is used for simplicity (development database).
