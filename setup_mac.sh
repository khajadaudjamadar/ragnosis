#!/usr/bin/env bash
# One-time setup for macOS / Linux. Run: bash setup_mac.sh
set -e
cd "$(dirname "$0")/backend"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
cd ../frontend
npm install
echo "Setup done. Edit backend/.env, then see README.md section 4 to run."
