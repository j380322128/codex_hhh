#!/usr/bin/env bash
set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "== System =="
uname -a
echo

echo "== Python =="
for candidate in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    printf '%s -> ' "$candidate"
    "$candidate" --version
  fi
done
echo

echo "== Project files =="
pwd
ls -la
echo

echo "== Virtualenv =="
if [ -x .venv/bin/python ]; then
  .venv/bin/python --version
  .venv/bin/python -m pip --version
else
  echo ".venv not found"
fi
echo

echo "== Django check =="
if [ -x .venv/bin/python ]; then
  .venv/bin/python -m django --version 2>&1 || true
  .venv/bin/python manage.py check 2>&1 || true
else
  echo "skip: .venv not found"
fi
echo

echo "== Gunicorn process =="
if [ -f logs/gunicorn.pid ]; then
  PID="$(cat logs/gunicorn.pid)"
  echo "pid file: $PID"
  ps -p "$PID" -f 2>/dev/null || true
else
  echo "pid file not found"
fi
echo

echo "== Ports =="
if command -v ss >/dev/null 2>&1; then
  ss -lntp 2>/dev/null | grep -E ':8000|:9000' || true
elif command -v netstat >/dev/null 2>&1; then
  netstat -lntp 2>/dev/null | grep -E ':8000|:9000' || true
else
  echo "ss/netstat not found"
fi
echo

echo "== Recent error log =="
if [ -f logs/error.log ]; then
  tail -n 80 logs/error.log
else
  echo "logs/error.log not found"
fi
