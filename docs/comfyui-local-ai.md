# Local AI via ComfyUI

This documents the on-premise, CPU-only ComfyUI integration that powers the
`comfyui_local` provider for ToolHub-AI image tools.

## Overview

| Item | Value |
| --- | --- |
| Provider name | `comfyui_local` |
| Inference engine | ComfyUI (Python desktop tool) |
| Install location | `<repo>/comfyui/` (gitignored) |
| Listener | `http://0.0.0.0:8188` (Docker host bridge; firewall-restricted) |
| Models dir | `<repo>/comfyui/models/` |
| Model cache (RMBG) | `<repo>/models_cache/` (gitignored, mounted into Docker) |
| Startup script | `scripts/start_comfyui.sh` |
| Shutdown script | `scripts/stop_comfyui.sh` |
| Service log | `logs/comfyui.log` |
| Env gate | `COMFYUI_ENABLED` (default `false`) |

## Start / stop

```bash
# foreground (with logs on screen)
./scripts/start_comfyui.sh

# detached daemon (default)
./scripts/start_comfyui.sh --daemon

# stop
./scripts/stop_comfyui.sh

# health check
curl -s http://127.0.0.1:8188/system_stats
```

The daemon runs with:
`--listen 0.0.0.0 --port 8188 --cpu --disable-auto-launch`

Because the host has no NVIDIA GPU and only ~9 GB RAM, ComfyUI runs in CPU mode.

## Architecture (backend)

```
backend/apps/ai_tools/comfyui/
  client.py             ComfyUIClient: upload -> prompt -> poll -> download
  errors.py             ComfyError hierarchy + SAFE_ERROR_MAP for user messages
  routing.py            ImageTaskRouter + CAPABILITY_REGISTRY
  workflows_registry.py WorkflowRegistry: loads workflow JSON templates
  workflows/            upscale.json, background_remove.json,
                        face_restore.json, inpaint.json
backend/apps/ai_tools/providers/comfyui_provider.py   ComfyUILocalImageProvider
backend/apps/ai_tools/health.py                        ComfyUIHealthService
```

Flow for a user job:

1. `enqueue_ai_job()` (services.py) picks `comfyui_local`, reserves credits, and
   dispatches to Celery task `apps.ai_tools.tasks.process_comfyui_job`
   (queue `image_local_ai`, Redis lock `comfyui:job:inference_lock`).
2. The provider resolves the operation -> workflow template -> model file.
3. `ComfyUIClient` uploads the input image, submits the prompt, polls
   `/history/{prompt_id}`, downloads the first rendered image.
4. Output is saved via Django `ContentFile` and the job marked complete.

## Workflows

| Operation | Workflow | Status on current box |
| --- | --- | --- |
| Upscale (4x Real-ESRGAN UltraSharp) | `upscale.json` | Functioning (model installed) |
| Background removal | `background_remove.json` | Functioning with native ComfyUI BiRefNet nodes |
| Object remove / inpaint | `inpaint.json` | **Functioning** — LaMa/MAT via `comfyui-inpaint-nodes` (mask-driven, CPU-fast) |
| Face restore | `face_restore.json` | **Functioning** — CodeFormer via `facerestore_cf` |

Custom nodes installed under `comfyui/custom_nodes/`:

- `comfyui-inpaint-nodes` (Acly) — `INPAINT_LoadInpaintModel`, `INPAINT_InpaintWithModel`, mask helpers. Model files in `comfyui/models/inpaint/`.
- `facerestore_cf` (mav-rik) — `FaceRestoreModelLoader`, `FaceRestoreCFWithModel`. Weights in `comfyui/models/facerestore_models/` + `comfyui/models/facedetection/`.

> GPU upgrade: installing an SDXL checkpoint + the Fooocus inpaint head lets the
> same `inpaint.json` path do prompted generative fill; no provider or workflow
> code changes needed.

## Configuration (env vars)

| Variable | Default | Meaning |
| --- | --- | --- |
| `COMFYUI_ENABLED` | `false` | Master switch; hides comfyui models from registry when off |
| `COMFYUI_BASE_URL` | `http://127.0.0.1:8188` | ComfyUI endpoint |
| `COMFYUI_TIMEOUT` | `5` | Request timeout (s) |
| `COMFYUI_EXECUTION_TIMEOUT` | `600` | Workflow run timeout (s) |
| `COMFYUI_MODELS_DIR` | absolute path | Where ComfyUI model binaries live |
| `COMFYUI_STRICT_WORKFLOW_VALIDATION` | `true` | Validate workflow payloads strictly |
| `COMFYUI_QA_ACCESSIBLE` | `true` | Allow `qa-test@toolhub.local` local inference |
| `COMFYUI_JOB_CONCURRENCY` | `1` | Serialized CPU inference (Redis lock) |

Docker: `docker-compose.yml` passes the `COMFYUI_*` variables to the `backend`
and `celery-worker` services and adds
`extra_hosts: host.docker.internal:host-gateway` so containers reach the host.

## Access control

- QA user (`qa-test@toolhub.local`) can use local models without a subscription
  (existing `is_qa` entitlement path).
- Normal free users keep the existing "No active subscription plan" gate.
- Subscriptions and credit accounting are unchanged for all providers.

## Health endpoint

`GET /api/v1/ai/local-ai/health/` returns `{enabled, base_url, status, latency, ...}`.
Status values: `enabled` / `unavailable` / `disabled` (when feature gate is off).

## GPU upgrade path

To move off CPU: install NVIDIA driver + CUDA, replace the ComfyUI venv's torch
with the matching `torch/torchvision` CUDA wheels, then start with
`--listen 0.0.0.0 --port 8188` (or keep loopback). No code changes required.