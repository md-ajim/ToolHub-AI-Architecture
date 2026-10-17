# Third-Party Integration Backlog (prioritized by capability gap)

Rule: integrate ONLY after credential-backed `verify_models --live` passes
for the exact capability. No placeholders, no generic reuse.

> STATUS 2026-09-26 (pm): **VERIFIED LIVE: cf-flux-klein-4b, cf-flux-klein-9b,
> local-rmbg-u2net.** fal provider code-complete (6 models incl. relight);
> PhotoRoom code-complete (ghost/flat-lay); **OpenRouter code-complete**
> (`or-gemini-flash-image`, path proven, balance exhausted — top up to
> promote). xKiro stays chat-only (403 bot-block, no image endpoints
> documented). Remaining steps are OWNER-side (fund/top-up + `--live`).

## ✅ INTEGRATED (pending owner payment + key only)

| Gap | Model | Endpoint (schema-verified) | Key needed | Verify command |
|---|---|---|---|---|
| upscale (cloud) | `fal-esrgan-upscale` (free-tier, 2cr) | `fal-ai/esrgan` | FAL_KEY | `verify_models --live --models fal-esrgan-upscale` |
| fashion-model | `fal-fashn-tryon` (max-tier, 8cr, garment ref required) | `fal-ai/fashn/tryon/v1.6` | FAL_KEY | `verify_models --live --models fal-fashn-tryon` |
| background-generate / product-edit / mockup-generate | `fal-flux-kontext-edit` (pro, 3cr) | `fal-ai/flux-kontext` | FAL_KEY | `verify_models --live --models fal-flux-kontext-edit` |
| text-to-image | `fal-flux-schnell-t2i` (pro, 2cr) | `fal-ai/flux/schnell` | FAL_KEY | `verify_models --live --models fal-flux-schnell-t2i` |
| product-photography / product-staging | `fal-product-photography` (pro, 5cr) | `fal-ai/image-apps-v2/product-photography` | FAL_KEY | `verify_models --live --models fal-product-photography` |
| **relight** | `fal-relight` (pro, 5cr, style presets) | `fal-ai/image-apps-v2/relighting` | FAL_KEY | `verify_models --live --models fal-relight` |
| **ghost-mannequin** | `photoroom-ghost-mannequin` (max-tier, 11cr, dedicated endpoint) | PhotoRoom `v2/edit` + `ghostMannequin.mode=ai.auto` | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-ghost-mannequin` |
| **flat-lay** | `photoroom-flat-lay` (pro, 11cr, dedicated endpoint) | PhotoRoom `v2/edit` + `flatLay.mode=ai.auto` | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-flat-lay` |
| **shadow** | `photoroom-shadow` (pro, 11cr, dedicated shadows model + overrides) | PhotoRoom `v2/edit` + `shadow.mode=ai.auto-with-overrides` (+ intensity/softness/spread/direction from editor sliders) | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-shadow` |
| **retouch / fashion-retouch** | `photoroom-beautify` (pro, 11cr, `beautify.mode=ai.auto`, documented re-imagining caveat) | PhotoRoom `v2/edit` + `beautify.mode` | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-beautify` |
| **enhance** | `fal-clarity-enhance` (free-tier, 2cr floor, 1x = detail regen without resizing) | `fal-ai/clarity-upscaler` (`upscale_factor=1`) | FAL_KEY | `verify_models --live --models fal-clarity-enhance` |
| **object-remove / inpaint / generative-fill (masked)** | `fal-qwen-inpaint` (pro, 3cr floor) | `fal-ai/qwen-image-edit/inpaint` (mask required, fails clearly without) | FAL_KEY | `verify_models --live --models fal-qwen-inpaint` |
| **expand / expand-image** | `fal-outpaint` (pro, 4cr, directional px→endpoint mapping) | `fal-ai/image-apps-v2/outpaint` | FAL_KEY | `verify_models --live --models fal-outpaint` |
| **recolor** | `fal-flux-kontext-edit` (pro, 3cr, whole-image instruction edit) | `fal-ai/flux-kontext` (no mask in recolor contract) | FAL_KEY | covered by kontext live run |

Deliberately NOT mapped (honesty): masked generative-fill via Kontext
(whole-image editor, no mask input — dedicated inpainting still via
ComfyUI/CF sd15-inpaint); FASHN never synthesizes garments (reference
required); PhotoRoom sandbox never used (watermark risk).

## P1 — Upscale (cloud, no local GPU dependency)

- Provider / Model: fal `topaz/upscale/image` (Precision) or `fal-ai/esrgan`
- Exact capability: `image_upscaling`
- Official API: `POST https://fal.run/<endpoint>` (`FAL_KEY`), image URL in,
  PNG/JPEG out, `upscale_factor` param (fal model pages, verified 2026-09-26)
- Input: JPG/PNG/WEBP URL; Output: upscaled image (Topaz bills per 24 MP out)
- Pricing: Topaz Precision ~$0.08/24MP; ESRGAN-class ~$0.003–0.01/run
- Expected credits: ESRGAN 1–2 cr; Topaz ~9 cr/MP @ $0.0094 budget
- Resolution: up to 4x+ (Topaz), 2–4x (ESRGAN)
- Commercial: fal partner models carry commercial-use badge (verify per model)
- Reliability: fal per-output billing (fixed price regardless of GPU time)
- Why insufficient now: only local ComfyUI Real-ESRGAN exists (needs GPU host)

## P1 — Fashion (model)

- Provider / Model: FASHN API (`tryon-max`, `tryon-v1.6`) directly or via
  fal (`fal-ai/fashn/tryon/v1.6`) — INTEGRATED as `fal-fashn-tryon`.
- Exact capability: `fashion_model_generation` (product→model).
  `ghost_mannequin` / `flat_lay` are NOT covered by try-on (input ≠
  generation) — they use dedicated PhotoRoom endpoints instead (below).

- Fallback: `fal-ai/image-apps-v2/virtual-try-on` ($0.04/image).
- Official API: `POST https://api.fashn.ai/v1/...` or `https://fal.run/...`
  (fashn.ai/products/api + fal model pages, verified 2026-09-26)
- Input: person/model image + garment image URLs; Output: on-model photo ≤4K
- Pricing: ~$0.04–0.075/generation; credits from $7.50, no subscription
- Expected credits: ~5–8 cr
- Commercial: explicitly commercial-use allowed
- Reliability: 5–55s per generation (async queue)
- Why insufficient now: zero fashion models in-repo; Qwen/FLUX are generic
  edits, NOT garment-accurate try-on — must NOT substitute

## P2 — Background generation / product staging / product photography (cloud)

- Provider / Model: fal `flux-kontext-pro` ($0.04/img), Seedream V4 ($0.03/img)
- Exact capabilities: `background_generation`, `product_staging`,
  `product_photography` (each verified separately — staging needs
  composition fidelity, not just any edit)
- Official API: fal model endpoints (pricing page verified 2026-09-26)
- Expected credits: ~4–5 cr
- Why insufficient now: bg-generation is Cloudflare-Flux-only (unverified
  token); no staging-specific model exists

## P2 — Text-to-image (second source)

- Status: Cloudflare FLUX assessed but token invalid. Before adding a new
  vendor, retry CF with a valid token (cheapest path: $0.0012–0.015/img).
- Alternative: fal Seedream/FLUX-Kontext (~$0.03–0.04/img, ~4 cr).

## P3 — face-restore-cloud (remaining research)

- Candidates: fal GFPGAN/CodeFormer endpoints, Magnific — all TO VERIFY
  (model-page verification required before integration).
- enhance/recolor/retouch/shadow/expand: INTEGRATED (see table above).
- infographic/creative-suite: deterministic `local-creative-compose`
  (no AI needed) — INTEGRATED + unit-tested.

## Per-tool gap sheet (all 18 unavailable AI capabilities)

| Tool | Required capability | Current gap | Candidates | Credential needed | Integration required |
|---|---|---|---|---|---|
| upscale | image_upscaling | cloud upscaler missing (local Comfy unverified) | fal Topaz/ESRGAN (P1) | FAL_KEY | new `fal` provider adapter |
| text-to-image | text_to_image | CF token invalid | valid CF token (retry) else fal Seedream (P2) | CLOUDFLARE_* or FAL_KEY | verify first; adapter exists for CF |
| object-remove/inpaint | object_removal+inpainting | Comfy unreachable | reachable ComfyUI (first) else CF sd15-inpaint (BETA→verify) | COMFYUI service / CF token | verify first |
| face-restore | face_restoration | Comfy unreachable | reachable ComfyUI else fal GFPGAN (P3) | COMFYUI service / FAL_KEY | verify first |
| generative-fill/background-generate/product-edit/mockup | generative editing stack | HF flag OFF+token invalid; CF invalid | valid HF token (Qwen) or CF token (Flux) (P2) | HF_API_TOKEN / CLOUDFLARE_* | verify first; adapters exist |
| enhance | image_enhancement | `fal-clarity-enhance` INTEGRATED (1x detail regen) | FAL_KEY | `verify_models --live --models fal-clarity-enhance` |
| retouch / fashion-retouch | retouching | `photoroom-beautify` INTEGRATED (re-imagining caveat documented) | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-beautify` |
| infographic / size-chart / carousel / social-creative / ad-creative | layout contracts | NO AI model needed — `local-creative-compose` deterministic Pillow pipelines (title/bullets, table, cards, formats, offer layout), TEST-ONLY + per-op allowlist, no AI selector, 1cr utility pricing | — | unit-tested, no live run needed |
| relight | relighting | `fal-relight` INTEGRATED (dedicated endpoint) | FAL_KEY | `verify_models --live --models fal-relight` |
| shadow | shadow_generation | `photoroom-shadow` INTEGRATED (dedicated) | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-shadow` |
| recolor | recoloring | `fal-flux-kontext-edit` INTEGRATED (instruction edit) | FAL_KEY | covered by kontext live run |
| enhance | image_enhancement | `fal-clarity-enhance` INTEGRATED (1x) | FAL_KEY | `verify_models --live --models fal-clarity-enhance` |
| product-staging/product-photography | own contracts | `fal-product-photography` INTEGRATED (dedicated) | FAL_KEY | `verify_models --live --models fal-product-photography` |
| fashion-model | fashion_model_generation | `fal-fashn-tryon` INTEGRATED | FAL_KEY | `verify_models --live --models fal-fashn-tryon` |
| ghost-mannequin | ghost_mannequin | `photoroom-ghost-mannequin` INTEGRATED (dedicated) | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-ghost-mannequin` |
| flat-lay | flat_lay_generation | `photoroom-flat-lay` INTEGRATED (dedicated) | PHOTOROOM_API_KEY | `verify_models --live --models photoroom-flat-lay` |
| infographic/size-chart/carousel/social-creative/ad-creative | layout contracts | `local-creative-compose` INTEGRATED (deterministic, 1cr, no AI selector) | — | unit-tested |

## Product/Fashion requirements (separate capabilities)

- product-staging: staged scene composition (product + generated set).
  Best: fal Kontext/Seedream (P2). Fallback: none. Status: UNAVAILABLE.
- product-photography: studio-grade packshot. Best: fal Kontext (P2) /
  FASHN product-to-model. Status: UNAVAILABLE.
- fashion-model: garment→on-model. `fal-fashn-tryon` INTEGRATED.
  Status: key + live-verify pending.
- ghost-mannequin: invisible-mannequin garment shots.
  `photoroom-ghost-mannequin` INTEGRATED (dedicated endpoint).
  Status: key + live-verify pending.
- flat-lay: styled flat arrangement. `photoroom-flat-lay` INTEGRATED
  (dedicated endpoint). Status: key + live-verify pending.
- fashion-retouch: garment-aware retouch. `photoroom-beautify` INTEGRATED.
  Status: key + live-verify pending.

## AI Product Studio workflow → operation mapping (no single fake selector)

`ai-product-studio` is a multi-step workflow (`AIProductStudio.tsx`);
each step resolves its own production model independently:

| Step | Operation | Capability | Compatible today | Behavior if empty |
|---|---|---|---|---|
| clean (bg remove) | background-remove | background_removal | local-rmbg-u2net | step blocked, clear error |
| enhance | enhance | image_enhancement | none | step skipped as unavailable |
| light | relight | relighting | none | step skipped as unavailable |
| shadow | shadow | shadow_generation | none | step skipped as unavailable |
| background | background-generate | background_generation | none (CF pending) | step skipped as unavailable |
| marketplace size | marketplace-resize | marketplace_resize (non-AI) | local-deterministic utility | always available |
| export | export (non-AI) | n/a | n/a | always available |

Multi-model workflows are acceptable. Steps without a production model
report unavailable instead of faking output.
