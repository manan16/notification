"""Daily GBP to INR alert sender using Twilio SMS or WhatsApp."""

from __future__ import annotations

import logging
import os
import sys
from typing import Dict

import requests
from dotenv import load_dotenv
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

API_URL = "https://api.frankfurter.dev/v1/latest?base=GBP&symbols=INR"
DEFAULT_CHANNEL = "sms"
SUPPORTED_CHANNELS = {"sms", "whatsapp"}


class ConfigurationError(Exception):
    """Raised when required environment variables are missing or invalid."""


class ExchangeRateError(Exception):
    """Raised when the exchange rate cannot be fetched or parsed."""


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_config() -> Dict[str, str]:
    load_dotenv()

    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_NUMBER",
        "ALERT_TO_NUMBER",
    ]
    config = {key: os.getenv(key, "").strip() for key in required_vars}
    channel = os.getenv("CHANNEL", DEFAULT_CHANNEL).strip().lower() or DEFAULT_CHANNEL
    config["CHANNEL"] = channel

    missing = [key for key, value in config.items() if key != "CHANNEL" and not value]
    if missing:
        raise ConfigurationError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    if channel not in SUPPORTED_CHANNELS:
        raise ConfigurationError(
            f"Invalid CHANNEL '{channel}'. Supported values: sms, whatsapp."
        )

    return config


def fetch_gbp_inr_rate() -> tuple[float, str]:
    logging.info("Fetching latest GBP/INR exchange rate from Frankfurter API.")

    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ExchangeRateError(f"Failed to fetch exchange rate data: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise ExchangeRateError("Received a non-JSON response from the exchange API.") from exc

    rate = payload.get("rates", {}).get("INR")
    date = payload.get("date")

    if rate is None or date is None:
        raise ExchangeRateError("Exchange API response is missing INR rate or date.")

    try:
        parsed_rate = float(rate)
    except (TypeError, ValueError) as exc:
        raise ExchangeRateError("Exchange API returned an invalid INR rate.") from exc

    return parsed_rate, str(date)


def format_alert_message(rate: float, rate_date: str) -> str:
    return f"GBP/INR Daily Alert:\n£1 = ₹{rate:.2f}\nDate: {rate_date}"


def normalize_for_channel(phone_number: str, channel: str) -> str:
    if channel == "whatsapp":
        return phone_number if phone_number.startswith("whatsapp:") else f"whatsapp:{phone_number}"
    return phone_number


def send_alert(config: Dict[str, str], message_body: str) -> str:
    channel = config["CHANNEL"]
    from_number = normalize_for_channel(config["TWILIO_FROM_NUMBER"], channel)
    to_number = normalize_for_channel(config["ALERT_TO_NUMBER"], channel)

    logging.info("Sending %s alert via Twilio.", channel)
    logging.info("Sender: %s | Recipient: %s", from_number, to_number)

    client = Client(config["TWILIO_ACCOUNT_SID"], config["TWILIO_AUTH_TOKEN"])

    try:
        twilio_message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number,
        )
    except TwilioException as exc:
        raise RuntimeError(f"Twilio failed to send the alert: {exc}") from exc
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise RuntimeError(f"Unexpected error while sending the alert: {exc}") from exc

    logging.info("Alert sent successfully. Message SID: %s", twilio_message.sid)
    return twilio_message.sid


def main() -> int:
    configure_logging()

    try:
        config = load_config()
        rate, rate_date = fetch_gbp_inr_rate()
        message_body = format_alert_message(rate, rate_date)

        logging.info("Formatted alert message:\n%s", message_body)
        send_alert(config, message_body)
        logging.info("Forex alert pipeline completed successfully.")
        return 0

    except ConfigurationError as exc:
        logging.error("Configuration error: %s", exc)
    except ExchangeRateError as exc:
        logging.error("Exchange rate error: %s", exc)
    except RuntimeError as exc:
        logging.error("Delivery error: %s", exc)
    except Exception as exc:  # pragma: no cover - top-level safety net
        logging.exception("Unexpected fatal error: %s", exc)

    return 1


if __name__ == "__main__":
    sys.exit(main())
