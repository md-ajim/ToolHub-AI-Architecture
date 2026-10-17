# Local AI Model Matrix

All local models used by the `comfyui_local` provider (and the legacy local RMBG
provider). Rated for the current CPU-only host (Intel Core i5-4460, 4 cores,
~9 GB RAM, no NVIDIA GPU).

## RMBG background removal (local models)

| Model | Source | Files | Size | Status |
| --- | --- | --- | --- | --- |
| RMBG-1.4 | `briaai/RMBG-1.4` (gated) | `models_cache/RMBG-1.4/{model.pth,model.safetensors,pytorch_model.bin,onnx/*}` | ~168 MB (pth/safetensors) | Installed; retained for local non-Comfy inference paths |
| RMBG-2.0 | `briaai/RMBG-2.0` (gated) | — | — | **Blocked** — HF token lacked gated-repo permission (HTTP 403), download failed |

> The HF token is scoped to a fine-grained "toolhub-ai-inference" token. For
> RMBG-2.0 the "Access public gated repos" permission must be granted on the
> token before the repo can be downloaded.

## ComfyUI background removal model

| Model | File | Size | Status |
| --- | --- | --- | --- |
| BiRefNet | `comfyui/models/background_removal/birefnet.safetensors` | ~424 MB | Installed; native ComfyUI `background_remove` workflow functional |

## ComfyUI upscale models

| Model | File | Kind | Size | Status |
| --- | --- | --- | --- | --- |
| 4x-UltraSharp | `comfyui/models/upscale_models/4x-UltraSharp.pth` | Real-ESRGAN x4 upscaler | ~67 MB | Installed; `upscale` workflow functional |

## ComfyUI inpainting / editing models (LaMa + MAT via `comfyui-inpaint-nodes`)

| Model | File | Kind | Size | Status |
| --- | --- | --- | --- | --- |
| MAT (fp16) | `comfyui/models/inpaint/MAT_Places512_G_fp16.safetensors` | MAT inpaint (512px) | ~120 MB | Installed; default `inpaint`/`object-remove` model — higher quality |
| LaMa | `comfyui/models/inpaint/big-lama.pt` | LaMa inpaint (256px) | ~196 MB | Installed; lighter/CPU-faster alternative |

Both run through `INPAINT_LoadInpaintModel` + `INPAINT_InpaintWithModel`
(e.g. object removal / mask-based editing / local outpainting-capable). No SD
checkpoint required. For prompted generative fill a Fooocus/SDXL checkpoint
can be added later (see `docs/comfyui-local-ai.md`).

## ComfyUI face restoration models (CodeFormer via `facerestore_cf`)

| Model | File | Kind | Size | Status |
| --- | --- | --- | --- | --- |
| CodeFormer | `comfyui/models/facerestore_models/codeformer.pth` | face restoration | ~376 MB | Installed; `face_restore` workflow functional |
| RetinaFace ResNet50 | `comfyui/models/facedetection/detection_Resnet50_Final.pth` | face detection | ~104 MB | Installed; used by the restore node |

## ComfyUI support models (not yet installed)

| Model | Purpose | Where it would live | Status |
| --- | --- | --- | --- |
| SDXL + Fooocus inpaint head | prompted generative fill / high-quality editing | `comfyui/models/checkpoints` + `inpaint` | Deferred — GPU upgrade target (CPU-impractical) |

## Profile

| Operation | Profile | Expected on this box |
| --- | --- | --- |
| Upscale 4x | `cpu-light` | Functional, slower on large inputs |
| Background remove | `cpu-light` | Functional via `LocalRMBGImageProvider` (rembg+onnxruntime) |
| Object remove / inpaint | `cpu-light` | Functional via LaMa/MAT (seconds) |
| Face restore | `cpu-light` | Functional via CodeFormer (slower, low-Fi works) |

All ComfyUI jobs are serialized via the `comfyui:job:inference_lock` Redis lock
(`COMFYUI_JOB_CONCURRENCY=1`) so concurrent CPU jobs do not thrash the host.