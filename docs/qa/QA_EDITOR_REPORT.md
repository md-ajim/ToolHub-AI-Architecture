# QA Editor Report — per-tool results (2026-09-28 cycle)

Principal: qa-test@toolhub.local (QA bypass; provider spend still real — $0
paths only for execution). Fixture: `backend/ai-inputs/3.png` (1774×887 product shot).
Matrix input: `docs/QA_EDITOR_MATRIX.json` (generated, not hand-written).

Result vocabulary: PASS (verified) / FAIL (broken) / NEEDS_HUMAN_REVIEW (judgment
needed) / NO_RUN (not executed — reason stated) / RELY_ON_RECORD (paid provider,
2026-09-26 live record stands; selector+contract verified live).

## Executed slots (8/8 PASS, byte-verified outputs)

| Tool | Operation | Model / Provider | Fixture → Output | ms | Credits (res/con/quote) | Output proof | Result |
|---|---|---|---|---|---|---|---|
| Background Remove | background-remove | local-rmbg-u2net / local_rmbg | 1774×887 PNG → RGBA 1774×887, 1.09 MB | ~5050–66000 | 0/0/1 (QA bypass) | alpha 0–255, 54% transparent, 46% opaque (subject kept) | PASS |
| Passport Photo | passport-photo | local-rmbg-u2net / local_rmbg | → 600×600 RGB composed | 5056 | 0/0/1 | valid, dims match doc-photo contract | PASS |
| Marketplace Resize | marketplace-resize | local-deterministic / local | → **2000×2000** RGBA | 5057 | 0/0/1 | pixel-exact amazon-main preset | PASS |
| Infographic | infographic | local-creative-compose / local | → 1774×1307 RGBA, hash ≠ input | 5059 | 0/0/1 | transformed, valid | PASS |
| Size Chart | size-chart | local-creative-compose / local | → 1000×760 RGBA, hash ≠ input | 5048 | 0/0/1 | transformed, valid | PASS |
| Carousel | carousel | local-creative-compose / local | → 3000×600 RGBA, hash ≠ input | 5055 | 0/0/1 | transformed, valid | PASS |
| Social Creative | social-creative | local-creative-compose / local | → 1080×1080 RGBA, hash ≠ input | 5045 | 0/0/1 | transformed, valid | PASS |
| Ad Creative | ad-creative | local-creative-compose / local | → 1200×628 RGBA, hash ≠ input | 5049 | 0/0/1 | transformed, valid | PASS |

Deterministic-path note: the six non-AI slots assert pixel-exact/validity contracts
only — no AI-quality claim is made (see inventory §5).

## Selector + contract per tool (all 30, live API)

- READY tools (16): selector returns compatible models with honest flags;
  `local-rmbg-u2net` runnable for bg-remove/passport; `photoroom-shadow` runnable;
  cf-flux pair runnable; failed models (fal×2, hf-bria, or-gemini-flash) listed
  non-runnable with reasons; recommended pointers correct.
- UNAVAILABLE tools (14): `recommended_model: null`; upscale lists failed models
  with reasons; nothing runnable offered anywhere. UI must show the explicit
  unavailable state (browser check on batch rail: pending badges shown).
- Alias resolution live: `tool_name=bg-remove` → `operation: background-remove`,
  models listed, batch 202s (was 422 before F1 fix).

## Layer / History / Export (browser-verified, bg-remove run)

- Layer: result arrives as "AI GENERATED / Background Remove / AI Layer" with
  thumbnail; original layer preserved (non-destructive) — screenshot 23.
- History: snapshot undo works (clicked, verified); reload offers draft resume
  with edit count + timestamp — screenshots 41/42.
- Export: dialog with filename/format/live size estimate; Download + Save to
  dashboard offered — screenshot 24. File download verified end-to-end via
  batch ZIP (1,088,536 bytes, nonzero).

## Credits (live)

- QA runs: reserved=0/consumed=0, quoted=1 (bypass, no charge) — recorded per job.
- Real-money path: scratch non-QA user, 10→9 balance on 1 bg-remove
  (reserved=1/consumed=1), user+jobs cleaned afterwards. No double charge
  (single ledger movement observed).
- Refund/idempotency/stale-sweep: covered by backend suite (green), not
  re-proven live (would require orchestrated failures).

## Error battery (live, all honest)

`bad tool→422`, `bad model→422`, `no auth→401`, `text-as-image→422`,
`t2i-without-prompt→422` (prompt enforcement works), `unknown job→404`,
`unknown tool selector→200 empty+null` (no crash). UI: non-image rejected
pre-queue with toast (F3 fix verified live).

## Batch (live, browser + API)

- 2-image bg-remove: 202, auto-selected local-rmbg-u2net, both items completed
  with outputs; progress 100%; per-item Done/Save; ZIP download verified by bytes.
- Aggregate staleness found → fixed via live-derived serializer (F2), unit-tested.

## Responsive (measured zero-overflow + visual)

1440×900, 1280×800, 768×1024, 390×844 × batch/editor/dashboard/usage/billing/models.
Mobile batch usable (screenshot 30). Dashboard sidebar/nav complete incl. Affiliate.

## Dashboard (browser + API)

- Usage: real numbers (Unlimited QA, 124 processed, ~12.4h estimated).
- Billing: honest QA state ($0.00, empty histories with guidance).
- History: was permanently empty (nothing ever wrote it) → fixed (F5);
  live run produced a timestamped row.
- Favorites/projects/files/settings: covered by unit suites + smoke loads
  (favorites/settings wired in prior session; files/history/settings pages
  render without errors).

## What was NOT executed (explicitly UNVERIFIED, never faked)

- Paid providers (cloudflare/photoroom): RELY_ON_RECORD + live selector/contract
  checks only. Re-running spends owner funds — needs approval + budget.
- ComfyUI-dependent paths: server down (:8188).
- Failed-provider models (fal 403, HF 402, OpenRouter exhausted): negative
  checks only (excluded from compatible, visible with reasons).
- Subjective visual quality of AI outputs: NEEDS_HUMAN_REVIEW by design —
  pixel/contract assertions are objective; taste is not claimed.
