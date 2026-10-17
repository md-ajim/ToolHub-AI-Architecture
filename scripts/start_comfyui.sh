#!/usr/bin/env bash
# Start ComfyUI as a local CPU-only inference service for ToolHub.
#
# Docker containers reach the host through host.docker.internal, so ComfyUI
# must listen on the host bridge. Restrict port 8188 with the host firewall.
#
# Usage:
#   scripts/start_comfyui.sh            # start in foreground
#   scripts/start_comfyui.sh --daemon   # start in background
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMFY_DIR="${COMFYUI_DIR:-$REPO_DIR/comfyui}"
VENV_PY="$COMFY_DIR/.venv/bin/python"
PORT="${COMFYUI_PORT:-8188}"
LISTEN="${COMFYUI_LISTEN:-0.0.0.0}"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: ComfyUI venv not found at $VENV_PY" >&2
  echo "Run: cd $COMFY_DIR && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

if [[ ! -d "$COMFY_DIR/models" ]]; then
  mkdir -p "$COMFY_DIR/models"
fi

ARGS=(--listen "$LISTEN" --port "$PORT" --cpu --disable-auto-launch)

if [[ "${1:-}" == "--daemon" ]]; then
  nohup "$VENV_PY" "$COMFY_DIR/main.py" "${ARGS[@]}" \
    > "$REPO_DIR/logs/comfyui.log" 2>&1 &
  echo "ComfyUI starting in background on http://$LISTEN:$PORT"
  echo "Log: $REPO_DIR/logs/comfyui.log"
  echo "PID: $!"
else
  exec "$VENV_PY" "$COMFY_DIR/main.py" "${ARGS[@]}"
fi