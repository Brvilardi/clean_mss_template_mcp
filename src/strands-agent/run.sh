#!/bin/sh
set -euo pipefail

# IMPORTANT: Prepend /opt/python to PYTHONPATH so agent dependencies layer takes precedence
# This ensures we use the correct Pydantic v2 from the agent layer, not older versions from other layers
export PYTHONPATH="/opt/python:${PYTHONPATH:-}"
export PATH="/opt/python/bin:${PATH}"

PORT="${AWS_LWA_PORT:-8000}"

# entrypoint:app -> the "app" defined in entrypoint.py
exec uvicorn entrypoint:app --host 0.0.0.0 --port "$PORT"
