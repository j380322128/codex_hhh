#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$PROJECT_DIR/logs/gunicorn.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "[deploy] 服务未运行：找不到 $PID_FILE"
  exit 0
fi

PID="$(cat "$PID_FILE")"
if kill -0 "$PID" >/dev/null 2>&1; then
  echo "[deploy] 停止服务进程：$PID"
  kill "$PID"
else
  echo "[deploy] 进程不存在：$PID"
fi

rm -f "$PID_FILE"
