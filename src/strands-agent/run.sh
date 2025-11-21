#!/bin/sh
set -euo pipefail

# Make layer deps visible
export PYTHONPATH="/opt/python:${PYTHONPATH:-}"
export PATH="/opt/python/bin:${PATH}"

PORT="${AWS_LWA_PORT:-8000}"

# entrypoint:app -> the "app" defined in entrypoint.py
exec uvicorn entrypoint:app --host 0.0.0.0 --port "$PORT"
