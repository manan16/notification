# forex-alert

`forex-alert` is a Python 3.10 project that fetches the latest GBP to INR exchange rate from the Frankfurter API and sends a daily notification through Twilio. It supports standard SMS delivery and optional WhatsApp delivery through Twilio WhatsApp or the WhatsApp Sandbox.

## Project overview

- Fetches the latest `GBP -> INR` rate from `https://api.frankfurter.dev/v1/latest?base=GBP&symbols=INR`
- Formats a daily alert message with the rate and API date
- Sends the message using Twilio SMS by default
- Supports WhatsApp delivery when `CHANNEL=whatsapp`
- Runs automatically every day with GitHub Actions at `07:00 UTC`

## Repo structure

```text
forex-alert/
├── .github/
│   └── workflows/
│       └── daily-forex-alert.yml
├── src/
│   └── forex_alert.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── setup.sh
```

## Twilio setup

1. Create or sign in to your Twilio account.
2. Copy your `Account SID` and `Auth Token` from the Twilio Console.
3. Buy or configure a Twilio phone number that can send SMS.
4. Set your recipient phone number in E.164 format, for example `+447700900123`.

## SMS setup

Use your Twilio SMS-enabled number as `TWILIO_FROM_NUMBER`, for example:

```env
TWILIO_FROM_NUMBER=+15005550006
ALERT_TO_NUMBER=+447700900123
CHANNEL=sms
```

## WhatsApp sandbox setup

If you want WhatsApp delivery:

1. Open the Twilio Console and navigate to WhatsApp Sandbox.
2. Complete the sandbox join flow on your mobile number.
3. Use the Twilio WhatsApp-enabled sender number shown in the sandbox.
4. Set `CHANNEL=whatsapp`.

Example:

```env
TWILIO_FROM_NUMBER=+14155238886
ALERT_TO_NUMBER=+447700900123
CHANNEL=whatsapp
```

When `CHANNEL=whatsapp`, the app automatically converts the sender and recipient into Twilio's required `whatsapp:+<number>` format.

## Local setup

### Option 1: use the helper script

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and add your real Twilio credentials and phone numbers.

## GitHub Secrets setup

Add the following repository secrets in GitHub:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`
- `ALERT_TO_NUMBER`
- `CHANNEL`

To add them:

1. Open your GitHub repository.
2. Go to `Settings`.
3. Open `Secrets and variables` -> `Actions`.
4. Create each secret listed above.

If you want SMS delivery, set `CHANNEL` to `sms`.
If you want WhatsApp delivery, set `CHANNEL` to `whatsapp`.

## GitHub Actions schedule

The workflow file is:

```text
.github/workflows/daily-forex-alert.yml
```

It runs:

- Automatically every day at `07:00 UTC`
- Manually with `workflow_dispatch`

GitHub Actions cron uses UTC, so the configured `07:00 UTC` schedule is intended to match `08:00 AM UK time` for the requested setup. Be aware that UK daylight saving changes can affect the local equivalent over the year.

## How to test locally

1. Activate your virtual environment.
2. Make sure `.env` is populated.
3. Run:

```bash
python src/forex_alert.py
```

If the API request succeeds and Twilio is configured correctly, you should receive a message like:

```text
GBP/INR Daily Alert:
£1 = ₹127.85
Date: 2026-04-29
```

## How to switch from SMS to WhatsApp

Update `CHANNEL` in `.env` or in your GitHub secret:

```env
CHANNEL=whatsapp
```

No code changes are needed. The script will automatically prefix both Twilio numbers with `whatsapp:` when that channel is selected.

## Troubleshooting

- If you see a configuration error, check that all required environment variables are set.
- If the API fetch fails, verify network access and confirm the Frankfurter endpoint is reachable.
- If Twilio delivery fails, confirm the sender number is enabled for the selected channel.
- If WhatsApp does not send, make sure your destination number has joined the Twilio WhatsApp Sandbox or that your account is approved for WhatsApp messaging.
- If GitHub Actions runs but sends nothing, review the workflow logs and verify that all repository secrets are present and spelled exactly correctly.
