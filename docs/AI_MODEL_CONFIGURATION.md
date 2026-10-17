# AI Model Configuration — layers, environment names, contracts

Three separate but interoperable layers. Do not merge them.

## A. LiteLLM proxy layer (`litellm_config.yaml`, `xkiro_free_models.json`)

* Upstream: `https://api.xkiro.com/v1` (OpenAI-compatible, `XKIRO_API_KEY`).
* Aliases (preserved): `gemini-1.5-flash, mistral-7b, mixtral-8x7b,
  minmax-m2, deepseek-v3-flash, qwen-2.5-72b, qwen-2.5-coder-32b,
  qwen-2.5-14b, qwen-2.5-7b, qwen-plus, qwen-max`.
* AI Workspace exposes xKiro models through the `openai_compatible`
  adapter (`AI_WORKSPACE_OPENAI_BASE_URL` + `AI_WORKSPACE_OPENAI_API_KEY`)
  as a safe reference — credentials and routing are never duplicated
  into the chat registry.

## B. AI Workspace chat layer (`backend/apps/ai_workspace/`)

Registry model: `AiWorkspaceModel`. Safe frontend contract
(`ModelSerializer`, additive only): `id, provider, provider_display_name,
displayName, description, capabilities, capabilityCategories,
supported_inputs/outputs, tier, plan_access, streaming_support,
context_window, max_output_tokens, cost_policy/estimatedCredits,
execution_type (cloud|local|comfyui|mock|proxy), configured (bool),
health_status, is_development_only, sort_order`.

No secrets are serialized. `configured` is a boolean adapter probe.

### Environment names (canonical → aliases, precedence left-to-right)

| Provider | Accepted names |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google | `GOOGLE_AI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` (+ `DEEPSEEK_BASE_URL` override) |
| Meta | `META_API_KEY` (+ `AI_WORKSPACE_META_BASE_URL`, default `https://api.meta.ai/v1`) |
| Hugging Face | `HF_API_TOKEN` canonical, `HUGGINGFACE_API_KEY` alias |
| Cloudflare | `CLOUDFLARE_ACCOUNT_ID` > `CLDFLARE_ACCOUNT_ID` (legacy typo) > `CF_ACCOUNT_ID`; same for `*_API_TOKEN`. Resolver: `backend/config/settings/base.py`. |
| xKiro gateway | `AI_WORKSPACE_OPENAI_API_KEY` + `AI_WORKSPACE_OPENAI_BASE_URL` (default `https://api.xkiro.com/v1`); raw `XKIRO_API_KEY` is the LiteLLM proxy key |
| OpenRouter | `OPENROUTER_API_KEY` (+ `OPENROUTER_BASE_URL` / `AI_WORKSPACE_OPENROUTER_BASE_URL`) |
| Self-hosted | `AI_WORKSPACE_SELF_HOSTED_API_KEY` + `AI_WORKSPACE_SELF_HOSTED_BASE_URL` |
| Qwen/XAI/Mistral | `QWEN_API_KEY`, `XAI_API_KEY`, `MISTRAL_API_KEY` |

Seeding (`seed_ai_models.py`) is idempotent: new rows created verbatim;
existing rows refresh descriptive metadata only and preserve operator
customizations (`tier, cost_policy, plan_access, status, sort_order`).
Rows are never deleted or re-keyed. Unsupported models are marked
`unavailable/disabled`, not deleted.

## C. Image layer (`backend/apps/ai_tools/registry.py`)

`IMAGE_MODELS` + `OPERATION_REGISTRY` + `TASK_MODEL_ROUTES` preserved.
Backends: `huggingface, local_rmbg, local, mock, comfyui_local, cloudflare`
(+ optional `openai/stability`). Routing (`models_for_task`,
`resolve_model_for_task`, `select_model`) filters by capability, input/output
type, provider availability, feature flag, entitlement, health — a model is
never selected for a task its provider cannot execute.

## Health states

`healthy | degraded | unavailable | disabled | coming_soon`, plus
`configured` bool and Meta-style `Configured — Verification Required`
when credentials exist but the endpoint is unverified. Health probes use
short timeouts, no credit charges, no user-visible jobs, cached 60s.
