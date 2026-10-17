# Cloudflare Workers AI provider

Cloudflare runs open models on its own GPU infra, so the platform gets real
cloud image generation / editing with **no local GPU and no separate model
downloads**. The provider is additive: everything keeps working with zero
Cloudflare credentials, and the models only appear once configured.

## Enable

Add to the environment (`.env` / Coolify):

```dotenv
CLDFLARE_ACCOUNT_ID=<your account id>
CLDFLARE_API_TOKEN=<API token with "Workers AI: Run" permission>
```

Aliases `CF_ACCOUNT_ID` / `CF_API_TOKEN` are also accepted. Optional:

```dotenv
CLDFLARE_BASE_URL=https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/
CLDFLARE_TIMEOUT=120
```

## Operations & models

| Operation | Default Cloudflare model | Notes |
| --- | --- | --- |
| `text-to-image` | `@cf/stabilityai/stable-diffusion-xl-base-1.0` | also offer FLUX.2 klein |
| `generative-fill` / `background-generate` / `product-edit` / `mockup-generate` | `@cf/black-forest-labs/flux-2-klein-4b` | prompt-driven editing/restyle (reference image) |
| `inpaint` / `object-remove` | `@cf/runwayml/stable-diffusion-v1-5-inpainting` | mask + prompt inpainting; falls back to FLUX edit if the account can't access RunwayML models |
| editing with reference image | `@cf/black-forest-labs/flux-2-klein-4b` / `-9b` | multipart (`input_image_0`) → multi-reference edit |

> **Note (verified live)**: FLUX.2 klein generation + editing work on this
> account. `@cf/runwayml/stable-diffusion-v1-5-img2img` and
> `…-inpainting` may be restricted on some tokens/accounts
> ("This account is not allowed to access …"); the provider automatically
> falls back to the FLUX edit path in that case so requests still complete.
> Mask-based inpainting without a permitted SD model is best served by the
> local ComfyUI provider (`comfyui-local-inpaint`).

Registry models (visible only when credentials exist):

- `cf-flux-klein-9b`, `cf-flux-klein-4b` — generate + edit, fastest quality
- `cf-sdxl-base` — plain text-to-image (SDXL 1.0)
- `cf-sd15-img2img` — editing restyle
- `cf-sd15-inpaint` — mask-based inpainting (same skill as local LaMa/MAT,
  but runs in the cloud so it is not CPU-bound)

## Routing / selection

- Added to `IMAGE_MODELS` with `provider: "cloudflare"`.
- `get_image_models()` only returns cloudflare entries when
  `CLDFLARE_ACCOUNT_ID` + `CLDFLARE_API_TOKEN` are set (new provider-config
  filter; this also hides un-configured hf/openai/stability entries).
- `_PROVIDER_RANK`: `huggingface → cloudflare → openai → stability →
  comfyui_local → local → mock`, so a real configured provider is preferred
  over local/mock fallbacks.
- All Cloudflare jobs flow through the existing job pipeline / credits /
  entitlement checks unchanged.

## Code pointers

- Provider: `backend/apps/ai_tools/providers/cloudflare.py`
- Registry entries: `backend/apps/ai_tools/registry.py`
- Env settings: `backend/config/settings/base.py`
- Tests: `backend/tests/unit/apps/ai_tools/test_cloudflare_provider.py`

## Model catalog (2026, partial)

Current useful Workers AI model ids (may be deprecated by Cloudflare over
time): `@cf/black-forest-labs/flux-2-klein-{4b,9b}`, `flux-2-dev`,
`@cf/stabilityai/stable-diffusion-xl-base-1.0`,
`@cf/stabilityai/stable-diffusion-xl-lightning`,
`@cf/runwayml/stable-diffusion-v1-5-img2img`,
`@cf/runwayml/stable-diffusion-v1-5-inpainting`,
`@cf/lykon/dreamshaper-8-lcm`. Chat/vision (not yet integrated):
`@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/qwen/qwen2.5-coder-32b-instruct`,
`@cf/meta/llama-3.2-11b-vision-instruct`, `@cf/meta/llama-4-scout-17b-16e-instruct`.