#!/bin/sh
set -euo pipefail

# Make layer deps visible
export PYTHONPATH="/opt/python:${PYTHONPATH:-}"
export PATH="/opt/python/bin:${PATH}"

PORT="${AWS_LWA_PORT:-8000}"

# mcp_server:app -> the "app" defined in mcp_server.py
exec uvicorn mcp_server:app --host 0.0.0.0 --port "$PORT"
