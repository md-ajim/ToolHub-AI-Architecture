# QA Failures — AI Image Editor (2026-09-28 cycle)

Every failure found, its root cause, disposition, and proof. Nothing hidden.

## F1 — P0: `bg-remove` alias rejected end-to-end [FIXED + DEPLOYED]

- **Symptom:** `GET /ai/models/?tool_name=bg-remove` → empty list, `recommended: null`;
  `POST /ai/batch/` with `tool_name=bg-remove` → **HTTP 422 "Unknown operation: bg-remove"**.
- **Impact:** the DEFAULT batch operation (Background Remove) was completely unusable.
- **Root cause:** `canonical_operation()` normalized but never alias-resolved, while every
  registry dict is keyed `background-remove`. Frontend sends its own ids verbatim.
- **Fix:** `OPERATION_ALIASES` in `canonical_operation()` (single choke point;
  mirrors frontend `BACKEND_OPERATION_IDS`): bg-remove→background-remove,
  passport→passport-photo, ai-product-studio→product-photography.
- **Proof:** 4 new tests (`TestFrontendOperationAliases`) green; live re-test post-deploy:
  selector returns 3 models + recommended `local-rmbg-u2net`; batch 202s.
- **Files:** `backend/apps/ai_tools/registry.py`, `test_operation_registry.py`.

## F2 — Batch aggregate fields go stale forever [FIXED + DEPLOYED]

- **Symptom:** batch `status` stuck `processing`, `completed_count: 0` minutes after
  both items completed (verified live).
- **Impact:** API consumers see self-contradictory data. (Own frontend derives from
  the live `jobs` array, so UI was unaffected.)
- **Root cause:** counters write-once at enqueue; nothing updates them.
- **Fix:** `AIBatchJobSerializer` derives `status/completed_count/failed_count`
  live from child jobs (no migration, no write races).
- **Proof:** 4 new tests (`TestBatchAggregateHonesty`) green.

## F3 — Non-image files accepted into batch UI [FIXED + DEPLOYED]

- **Symptom:** `evil.txt` added, selected, costed (backend would 422 at Process).
- **Root cause:** `handleAddFiles` checked size/cap only, never file type.
- **Fix:** `fileValidation.ts` (mirrors backend PIL set + AVIF plugin; SVG excluded
  — backend cannot rasterize it) + honest skip toast. 4 new vitest cases green.
  Live browser re-test: toast shown, 0 thumbs added.
- **Files:** `frontend/src/components/batch/fileValidation.ts`, `BatchEditorApp.tsx`.

## F4 — Editor forces prompt text for non-prompt ops [FINDING, no change]

- **Symptom:** BG Remove Generate button disabled with "Enter a prompt to continue"
  although the backend ignores prompts for bg-remove.
- **Evidence:** `GenerationPanel.tsx:283` (`promptOk = !routing.supportsPrompt || ...`)
  vs backend `PROMPT_REQUIRED_OPERATIONS = {text-to-image, product-edit, mockup-generate}`.
- **Disposition:** UX friction, not breakage (tool works after typing). Changing it
  alters intended product behavior → **product decision required**, left untouched.

## F5 — Workspace History never populated [FIXED + DEPLOYED]

- **Symptom:** `GET /workspace/history/` returned 0 rows despite completed jobs;
  nothing in backend ever created History rows.
- **Fix:** best-effort `History` write in `_finalize_job_success` (outside the
  money transaction, fully guarded, duplicate-safe via terminal-state gate).
- **Proof:** 2 new tests green; live run produced a timestamped history row.
- **Files:** `backend/apps/ai_tools/tasks.py`, `test_batch_models.py`.

## Pre-existing suite failures (NOT caused by this cycle)

Verified identical on pristine `HEAD` worktree (`git worktree`, single-file runs):
- `billing/test_billing_safety.py::test_celery_retry_is_not_converted_into_failure_refund`
  (DID NOT RAISE Retry) — also fails pristine.
- `ecommerce_studio/test_studio.py` — 8 failures on my tree vs 9 on pristine
  (the 9th, `test_insufficient_credits_returns_402`, passes consistently on my
  tree; order-dependent flake in the file). Failing set on my tree ⊆ pristine set.
  Root causes are in studio/export paths untouched by this cycle.
- Local runs without Redis: throttle/cache-dependent tests error (environmental;
  full runs used a temporary Redis, removed afterwards).
