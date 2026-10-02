#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

PYTHON_BIN=""
if [ -f .runtime ]; then
  . ./.runtime
fi
if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3 || command -v python)"
fi

if [ -n "$TERMUX_VERSION" ] && command -v termux-wake-lock >/dev/null 2>&1; then
  termux-wake-lock
fi

exec "$PYTHON_BIN" -m mrbeast
