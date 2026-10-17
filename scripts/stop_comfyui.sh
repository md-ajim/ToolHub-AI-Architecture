#!/usr/bin/env bash
# Stop the background ComfyUI service started by start_comfyui.sh --daemon
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${COMFYUI_PORT:-8188}"

PID="$(lsof -ti tcp:$PORT 2>/dev/null || true)"
if [[ -z "$PID" ]]; then
  echo "ComfyUI is not running on port $PORT."
  exit 0
fi

kill "$PID"
echo "Stopped ComfyUI (PID $PID)."