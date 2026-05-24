#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"
CHECK_HOST="${CHECK_HOST:-127.0.0.1}"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=10
MAX_PYTHON_MAJOR=3
MAX_PYTHON_MINOR=13
RUNTIME_DIR="$PROJECT_DIR/.runtime"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$LOG_DIR/gunicorn.pid"

mkdir -p "$LOG_DIR" "$PROJECT_DIR/templates_packages" "$PROJECT_DIR/project_files"

log() {
  printf '[deploy] %s\n' "$*" >&2
}

python_is_compatible() {
  local python_bin="$1"
  "$python_bin" - "$MIN_PYTHON_MAJOR" "$MIN_PYTHON_MINOR" "$MAX_PYTHON_MAJOR" "$MAX_PYTHON_MINOR" <<'PY'
import sys
minimum = (int(sys.argv[1]), int(sys.argv[2]))
maximum = (int(sys.argv[3]), int(sys.argv[4]))
current = sys.version_info[:2]
raise SystemExit(0 if minimum <= current <= maximum else 1)
PY
}

find_python() {
  local candidate
  for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && python_is_compatible "$candidate"; then
      command -v "$candidate"
      return 0
    fi
  done
  return 1
}

detect_platform() {
  local os_name arch_name
  os_name="$(uname -s)"
  arch_name="$(uname -m)"

  case "$os_name" in
    Linux)
      os_name="Linux"
      case "$arch_name" in
        x86_64|amd64) arch_name="x86_64" ;;
        aarch64|arm64) arch_name="aarch64" ;;
        *) log "不支持的 CPU 架构：$arch_name"; exit 1 ;;
      esac
      ;;
    Darwin)
      os_name="MacOSX"
      case "$arch_name" in
        x86_64|amd64) arch_name="x86_64" ;;
        aarch64|arm64) arch_name="arm64" ;;
        *) log "不支持的 CPU 架构：$arch_name"; exit 1 ;;
      esac
      ;;
    *) log "不支持的系统：$os_name"; exit 1 ;;
  esac

  printf '%s-%s' "$os_name" "$arch_name"
}

install_project_python() {
  local platform installer installer_url conda_python
  platform="$(detect_platform)"
  installer="$RUNTIME_DIR/miniforge.sh"
  conda_python="$RUNTIME_DIR/miniforge/bin/python"

  if [ -x "$conda_python" ] && python_is_compatible "$conda_python"; then
    printf '%s' "$conda_python"
    return 0
  fi

  mkdir -p "$RUNTIME_DIR"
  installer_url="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-${platform}.sh"
  log "当前 Python 版本过低，开始安装项目内 Python ${PYTHON_VERSION}：$installer_url"

  if command -v curl >/dev/null 2>&1; then
    curl -L "$installer_url" -o "$installer" >&2
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$installer" "$installer_url" >&2
  else
    log "服务器缺少 curl/wget，无法自动下载 Python 安装器"
    exit 1
  fi

  bash "$installer" -b -p "$RUNTIME_DIR/miniforge" >&2
  "$RUNTIME_DIR/miniforge/bin/conda" install -y "python=${PYTHON_VERSION}" pip >&2
  printf '%s' "$conda_python"
}

create_venv() {
  local python_bin="$1"
  if "$python_bin" -m venv "$VENV_DIR"; then
    return 0
  fi

  log "当前 Python 无法创建 venv，改用项目内 Python 运行时"
  PYTHON_BIN="$(install_project_python)"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
}

port_is_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -lnt 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]${port}$"
  elif command -v netstat >/dev/null 2>&1; then
    netstat -lnt 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]${port}$"
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
  else
    return 1
  fi
}

check_health() {
  local url response
  url="http://${CHECK_HOST}:${APP_PORT}/api/health/"
  if command -v curl >/dev/null 2>&1; then
    response="$(curl -fsS "$url" 2>/dev/null || true)"
  elif command -v wget >/dev/null 2>&1; then
    response="$(wget -qO- "$url" 2>/dev/null || true)"
  else
    log "服务器缺少 curl/wget，跳过健康检查：$url"
    return 0
  fi

  if printf '%s' "$response" | grep -q "project-management-api"; then
    log "健康检查通过：$url"
    return 0
  fi

  log "健康检查失败：$url"
  log "当前端口返回内容不是本项目，请检查端口是否被其他服务占用"
  return 1
}

ensure_compatible_venv() {
  if [ ! -x "$VENV_DIR/bin/python" ]; then
    return 0
  fi

  if python_is_compatible "$VENV_DIR/bin/python"; then
    return 0
  fi

  log "发现旧虚拟环境 Python 版本不兼容，重建：$VENV_DIR"
  rm -rf "$VENV_DIR"
}

PYTHON_BIN="$(find_python || true)"
if [ -z "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(install_project_python)"
else
  log "使用系统 Python：$PYTHON_BIN"
fi

ensure_compatible_venv

if [ ! -x "$VENV_DIR/bin/python" ]; then
  log "创建虚拟环境：$VENV_DIR"
  create_venv "$PYTHON_BIN"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
log "升级 pip/setuptools/wheel"
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

log "安装项目依赖"
"$VENV_PYTHON" -m pip install -r requirements.txt

export DJANGO_DEBUG="${DJANGO_DEBUG:-0}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-*}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-django-insecure-change-me-before-deploying}"

log "执行数据库迁移"
"$VENV_PYTHON" manage.py migrate --noinput

log "收集静态文件"
"$VENV_PYTHON" manage.py collectstatic --noinput

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" >/dev/null 2>&1; then
  log "停止旧服务进程：$(cat "$PID_FILE")"
  kill "$(cat "$PID_FILE")"
  sleep 2
fi

if port_is_in_use "$APP_PORT"; then
  log "端口 ${APP_PORT} 已被占用。请换端口启动，例如：APP_PORT=8010 ./scripts/run_server.sh"
  exit 1
fi

log "启动服务：http://${APP_HOST}:${APP_PORT}"
"$VENV_DIR/bin/gunicorn" codex_hhh.wsgi:application \
  --bind "${APP_HOST}:${APP_PORT}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --pid "$PID_FILE" \
  --access-logfile "$LOG_DIR/access.log" \
  --error-logfile "$LOG_DIR/error.log" \
  --daemon

sleep 2
check_health

log "启动完成。日志：$LOG_DIR/access.log / $LOG_DIR/error.log"
