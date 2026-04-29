#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_ROOT"

echo "Creating virtual environment in .venv/"
python3 -m venv .venv

echo "Activating virtual environment"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Python dependencies"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  echo ".env already exists; leaving it unchanged"
fi

cat <<'EOF'

Setup complete.

Next steps:
1. Edit .env and add your Twilio credentials and destination number.
2. For WhatsApp, set CHANNEL=whatsapp and use Twilio WhatsApp-enabled numbers.
3. Activate the virtual environment with:
   source .venv/bin/activate
4. Run the alert locally with:
   python src/forex_alert.py

EOF
