#!/usr/bin/env bash
set -e

export DEBIAN_FRONTEND=noninteractive
export GIT_TERMINAL_PROMPT=0
export PIP_NO_INPUT=1

REPO_URL="https://github.com/BigFloppa9/MrBeast-GTFO.git"
SELF="${BASH_SOURCE[0]:-}"
DIR=""

if [ -n "$SELF" ] && [ -f "$(dirname "$SELF")/main.py" ]; then
  DIR="$(cd "$(dirname "$SELF")" && pwd)"
fi

if [ -z "$DIR" ]; then
  DIR="$HOME/MrBeast-GTFO"
fi

if [ -n "$TERMUX_VERSION" ] || [ -d /data/data/com.termux/files/usr ]; then
  ENV_KIND="termux"
elif [ -f /.dockerenv ] || grep -qE "docker|containerd|kubepods" /proc/1/cgroup 2>/dev/null; then
  ENV_KIND="docker"
else
  ENV_KIND="linux"
fi

echo "Environment: $ENV_KIND"

APT_FLAGS=(-y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold)

sudo_cmd() {
  if [ "$(id -u)" -eq 0 ]; then "$@"; elif command -v sudo >/dev/null 2>&1; then sudo "$@"; else "$@"; fi
}

install_system_packages() {
  case "$ENV_KIND" in
    termux)
      apt-get update || true
      apt-get "${APT_FLAGS[@]}" full-upgrade
      apt-get "${APT_FLAGS[@]}" install git python clang make libffi openssl python-cryptography
      ;;
    *)
      if command -v apt-get >/dev/null 2>&1; then
        sudo_cmd apt-get update || true
        sudo_cmd apt-get "${APT_FLAGS[@]}" install git python3 python3-venv python3-pip
      elif command -v dnf >/dev/null 2>&1; then
        sudo_cmd dnf install -y git python3 python3-pip
      elif command -v pacman >/dev/null 2>&1; then
        sudo_cmd pacman -S --noconfirm --needed git python python-pip
      elif command -v apk >/dev/null 2>&1; then
        sudo_cmd apk add --no-cache git python3 py3-pip
      fi
      ;;
  esac
}

install_system_packages

command -v git >/dev/null 2>&1 || { echo "git is required"; exit 1; }
PYTHON="$(command -v python3 || command -v python || true)"
[ -n "$PYTHON" ] || { echo "python3 is required"; exit 1; }

if [ ! -f "$DIR/main.py" ]; then
  git clone "$REPO_URL" "$DIR"
fi

cd "$DIR"

if [ "$ENV_KIND" = "termux" ]; then
  export AIOHTTP_NO_EXTENSIONS=1 MULTIDICT_NO_EXTENSIONS=1 YARL_NO_EXTENSIONS=1 FROZENLIST_NO_EXTENSIONS=1
  "$PYTHON" -m pip install --upgrade setuptools wheel || true
  "$PYTHON" -m pip install "discord.py>=2.4.0"
  "$PYTHON" -c "import cryptography" 2>/dev/null || "$PYTHON" -m pip install cryptography
  echo "PYTHON_BIN=$PYTHON" > .runtime
elif [ "$ENV_KIND" = "docker" ]; then
  "$PYTHON" -m pip install --break-system-packages -r requirements.txt 2>/dev/null || "$PYTHON" -m pip install -r requirements.txt
  echo "PYTHON_BIN=$PYTHON" > .runtime
else
  "$PYTHON" -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
  echo "PYTHON_BIN=$DIR/.venv/bin/python" > .runtime
fi

echo
echo "Installed in: $DIR"
echo "Starting. Next time use: cd \"$DIR\" && bash start.sh"
echo

exec bash "$DIR/start.sh"
