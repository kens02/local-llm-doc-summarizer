#!/bin/sh
set -e

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r src/backend/requirements.txt

if command -v npm >/dev/null 2>&1; then
  (cd src/frontend && npm install)
fi

echo "Setup complete. Activate venv with: . .venv/bin/activate"
