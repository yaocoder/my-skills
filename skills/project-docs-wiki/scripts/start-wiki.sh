#!/usr/bin/env bash
# One-click start/stop for a local VitePress wiki (docs/).
# Default port 5177 — VitePress default 5173 collides with typical Vite apps.
#
# Copy to the target repo root. Adjust PKG if the repo is not pnpm.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.local-run"
LOG_DIR="$RUN_DIR/logs"
PID_DIR="$RUN_DIR/pids"
PID_FILE="$PID_DIR/wiki.pid"
LOG_FILE="$LOG_DIR/wiki.log"
WIKI_PORT="${WIKI_PORT:-5177}"
WIKI_HOST="${WIKI_HOST:-127.0.0.1}"
DOCS_DIR="${WIKI_DOCS:-docs}"
URL="http://${WIKI_HOST}:${WIKI_PORT}/"

detect_pm() {
  if [[ -f "$ROOT_DIR/pnpm-lock.yaml" ]] || [[ -f "$ROOT_DIR/pnpm-workspace.yaml" ]]; then
    echo pnpm
  elif [[ -f "$ROOT_DIR/yarn.lock" ]]; then
    echo yarn
  else
    echo npm
  fi
}

PM="$(detect_pm)"

pm_exec() {
  case "$PM" in
    pnpm) pnpm exec "$@" ;;
    yarn) yarn exec "$@" ;;
    npm) npx "$@" ;;
  esac
}

pm_install() {
  case "$PM" in
    pnpm) pnpm install ;;
    yarn) yarn install ;;
    npm) npm install ;;
  esac
}

usage() {
  cat <<EOF
Usage: ./start-wiki.sh [--fg|--stop|--status|-h]

  (no args)   start in background; print URL; macOS may open browser
  --fg        foreground (Ctrl+C to stop)
  --stop      stop background wiki
  --status    print running or not

Env:
  WIKI_PORT    port (default 5177)
  WIKI_HOST    bind (default 127.0.0.1)
  WIKI_DOCS    docs dir (default docs)
  NO_OPEN=1    do not open browser

Needs: $PM install with vitepress at repo root.
EOF
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing command: $1" >&2
    exit 1
  }
}

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

port_in_use() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$WIKI_PORT" -sTCP:LISTEN >/dev/null 2>&1
  else
    return 1
  fi
}

stop_wiki() {
  if is_running; then
    local pid
    pid="$(cat "$PID_FILE")"
    echo "stopping wiki (pid=$pid)…"
    kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 20); do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.2
    done
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    echo "stopped."
  else
    rm -f "$PID_FILE"
    echo "wiki not running."
  fi
}

ensure_deps() {
  need_cmd "$PM"
  # Do not run `vitepress --version` — some versions start the dev server.
  if [[ ! -f "$ROOT_DIR/node_modules/vitepress/package.json" ]]; then
    echo "vitepress missing; running $PM install…"
    (cd "$ROOT_DIR" && pm_install)
  fi
  if [[ ! -f "$ROOT_DIR/node_modules/vitepress/package.json" ]]; then
    echo "vitepress still missing. From repo root: $PM add -D vitepress" >&2
    exit 1
  fi
  if [[ ! -d "$ROOT_DIR/$DOCS_DIR" ]]; then
    echo "docs dir not found: $ROOT_DIR/$DOCS_DIR" >&2
    exit 1
  fi
}

open_browser() {
  if [[ "${NO_OPEN:-0}" == "1" ]]; then
    return 0
  fi
  if [[ "$(uname -s)" == "Darwin" ]] && command -v open >/dev/null 2>&1; then
    open "$URL" >/dev/null 2>&1 || true
  fi
}

wait_ready() {
  local i
  for i in $(seq 1 60); do
    if command -v curl >/dev/null 2>&1; then
      if curl -sf "$URL" >/dev/null 2>&1; then
        return 0
      fi
    else
      sleep 1
      return 0
    fi
    sleep 0.5
  done
  return 1
}

start_fg() {
  ensure_deps
  if port_in_use; then
    echo "port $WIKI_PORT in use. Try: WIKI_PORT=5178 $0 --fg" >&2
    exit 1
  fi
  echo "wiki (fg) → $URL"
  echo "docs: $ROOT_DIR/$DOCS_DIR"
  cd "$ROOT_DIR"
  exec pm_exec vitepress dev "$DOCS_DIR" --host "$WIKI_HOST" --port "$WIKI_PORT"
}

start_bg() {
  ensure_deps
  if is_running; then
    echo "already running (pid=$(cat "$PID_FILE")) → $URL"
    open_browser
    exit 0
  fi
  if port_in_use; then
    echo "port $WIKI_PORT in use, no pid file from this script." >&2
    echo "Try: WIKI_PORT=5178 $0" >&2
    exit 1
  fi

  mkdir -p "$LOG_DIR" "$PID_DIR"
  echo "starting wiki (bg) → $URL"
  (
    cd "$ROOT_DIR"
    pm_exec vitepress dev "$DOCS_DIR" --host "$WIKI_HOST" --port "$WIKI_PORT" \
      >>"$LOG_FILE" 2>&1 &
    echo $! >"$PID_FILE"
  )

  if wait_ready; then
    echo "ready: $URL"
    echo "log: $LOG_FILE"
    echo "stop: ./start-wiki.sh --stop"
    open_browser
  else
    echo "timeout. log: $LOG_FILE" >&2
    stop_wiki
    exit 1
  fi
}

status_wiki() {
  if is_running; then
    echo "running pid=$(cat "$PID_FILE") → $URL"
    exit 0
  fi
  echo "not running."
  exit 1
}

main() {
  local mode=bg
  for arg in "$@"; do
    case "$arg" in
      --fg) mode=fg ;;
      --stop) mode=stop ;;
      --status) mode=status ;;
      -h|--help) usage; exit 0 ;;
      *)
        echo "unknown arg: $arg" >&2
        usage >&2
        exit 1
        ;;
    esac
  done

  case "$mode" in
    fg) start_fg ;;
    stop) stop_wiki ;;
    status) status_wiki ;;
    bg) start_bg ;;
  esac
}

main "$@"
