# PRODUCTION AI EDITOR QA — FINAL GATE (2026-09-28 cycle)

Verdict legend: PASS / FAIL / NEEDS_HUMAN_REVIEW / UNVERIFIED (never guessed).

## 1. Tested tools
All 30 operations inventoried (`docs/QA_EDITOR_INVENTORY.md`). 8 model-slots
executed live with byte-verified outputs (report §Executed slots). 14 tools have
no production model — UI-state verified only (explicit unavailable, nothing
runnable offered). 8 paid slots: selector+contract verified live, execution
relies on 2026-09-26 records (no re-spend without approval).

## 2. Tested models
Executed: local-rmbg-u2net (×2 tools), local-deterministic, local-creative-compose
(×5 tools). Selector-verified live: cf-flux-klein-9b/4b, photoroom-shadow,
photoroom-ghost-mannequin, photoroom-flat-lay, hf-bria-rmbg + fal×2 + or-gemini-flash
(negative: correctly non-runnable with reasons). Never executed: mock/*,
TEST_ONLY-as-AI-proof, fal/* (403), hf-bria (402), or-gemini-flash (exhausted),
comfyui/* (server down).

## 3. Provider status
LIVE: local_rmbg, local, cloudflare (record), photoroom (record). DOWN/UNFUNDED:
fal (key rejected), huggingface (payment required), openrouter (exhausted),
comfyui_local (no server :8188). GATED: mock.

## 4. Passed tests
- New this cycle (18): 4 alias + 4 aggregate + 2 history + 4 fileValidation
  (vitest) + 4 license/error-shape... (counted in suites below).
- Backend full unit suite: 571 passed; only pre-existing failures
  (billing celery-retry + 8 ecommerce studio — verified identical-or-better
  vs pristine HEAD worktree; 1 pristine-only flake passes here).
- Frontend: tsc clean, eslint clean on touched files, vitest 112/112
  (13→14 files), `next build` exit 0 (144 pages).

## 5. Failed tests
Zero new failures. Found-and-fixed during cycle (see QA_EDITOR_FAILURES.md):
F1 bg-remove alias 422 (P0, deployed), F2 stale batch aggregates (deployed),
F3 non-image accepted (deployed), F5 empty history (deployed). F4 prompt-gate
left for product decision.

## 6. Human review items
- Subjective AI output quality (taste/aesthetics) — pixel contracts pass;
  human eye-ball of bg-remove edges, passport composition, creative outputs.
- Paid re-runs (Cloudflare/PhotoRoom) if fresh evidence wanted.
- F4 prompt requirement on non-prompt ops.
- AVIF end-to-end (decoder present server-side; no local encoder to test with).

## 7. Credit verification
Live: QA bypass 0/0 with quote recorded; scratch non-QA user 10→9 on 1 job
(reserved=1/consumed=1), cleaned up. No double charge observed. Refund/
idempotency/sweep via green unit suite (not re-proven live — would need
orchestrated failures).

## 8. Output-quality findings
Objective: all outputs valid, correct dims/modes, alpha verified for
bg-remove (54% transparent/46% opaque), resize pixel-exact 2000×2000,
creative outputs genuinely transformed (hash ≠ input). Subjective: see §6.

## 9. Responsive findings
Zero measured overflow on 9 viewport×page combos (390/768/1280/1440);
mobile batch visually usable. No clipped controls observed.

## 10. Security findings (this cycle)
- Fixed: batch alias 422 class; input validation gap (non-images reached
  enqueue path — backend rejected, now frontend too).
- Noted (pre-existing, unchanged): QA bypass by design; throttle/Redis
  dependence; review P0 items in PRODUCTION_DISCOVERY_REPORT.md before
  public launch traffic.

## 11. Regression findings
- Backend: my-tree failing set ⊆ pristine failing set (worktree-compared).
- Frontend: 112/112 incl. 4 new.
- Deploy discipline gap found: code ships only on container rebuild — backend
  AND worker containers must rebuild together (history hook runs in worker;
  verified live after rebuilding both).

## 12. Remaining provider limitations (explicit)
fal key rejected · HF unfunded (402) · OpenRouter exhausted · ComfyUI down ·
14 ops without production model · paid re-runs need approval+budget.

## 13. Exact recommended next engineering actions
1. Owner: fund/repair providers (FAL key, HF billing, OpenRouter top-up) or
   accept UNAVAILABLE states; optionally start ComfyUI for local AI paths.
2. Product decision: F4 prompt gate on non-prompt ops.
3. Rebuild + redeploy backend/celery/frontend images for all session fixes;
   re-run `python backend/scripts/qa_gen_matrix.py` after any provider change.
4. Commit this cycle's artifacts (reports, matrix, screenshots, tests).

*End of final gate. No PASS was declared without evidence; UNVERIFIED items
are listed in §§2–3, 6, 12 above.*
