# QA Visual Review — checkpoints (2026-09-28 cycle)

Screenshots: `docs/qa/screenshots/*.jpg`. Every claim below was seen by the
QA agent on the named file. Unviewed transitional shots are not cited.

| Shot | What was verified |
|---|---|
| `03-batch-empty.jpg` | Batch Studio renders: 7-tool sidebar, stepper, empty state, topbar identity |
| `04-editor.jpg` | Editor shell renders: header, empty canvas CTA, upload zone |
| `12-batch-done.jpg` | Batch completion UX: stepper 1✓2✓3, 100%, item "Done — 1774×887 px · click to compare", Download ZIP (1), Save, New batch |
| `20-editor-after-upload.jpg` | Upload lands on canvas; Layers panel shows BACKGROUND + Image; Inspector shows real dims/format/size; status bar Ready + file meta |
| `22-editor-bgremove-panel.jpg` | BG Remove panel: model "Local U2-Ne… free", prompt gate message, cost "1 Credit / generation" |
| `23-editor-after-run.jpg` | Post-run: "AI GENERATED / Background Remove / AI Layer" entry with thumbnail; canvas intact; undo controls active |
| `24-editor-export.jpg` | Export dialog: filename, format select, live size estimate (1448.4 KB), Download + Save-to-dashboard |
| `30-mobile390-batch.jpg` | 390px mobile: stacked layout, usable controls, no squeeze |
| `40-invalid-file.jpg` (pre-fix) | Defect evidence: `evil.txt` accepted+selected+costed |
| `41-evil-rejected.jpg` | Post-fix: toast "1 file is not a supported image and was skipped.", 0 thumbs, empty state |
| `42-after-reload.jpg` | "Resume previous session? 2 edits · timestamp" + thumbnail + Discard/Resume — draft persistence works |
| `06-dash-usage.jpg` | Real numbers: Unlimited QA, 124 processed files, ~12.4h estimated, full sidebar nav |
| `07-dash-billing.jpg` | Honest QA state: Unlimited, $0.00 lifetime, empty payment/invoice states with guidance |
| `08-ai-models.jpg` | 47 models with tier badges, costs, capabilities, rail nav, search/filters |

## Responsive (measured, not eyeballed)

`scrollWidth - clientWidth == 0` on all combos: 1440×900, 1280×800, 768×1024,
390×844 × (batch, editor, dashboard, usage, billing, ai/models).

## Visual defects noted

1. Prompt gate on non-prompt ops (see FAILURES F4) — visible in `22`.
2. Nothing else: no clipped controls, no broken images, no layout breaks
   observed on any checkpoint.
