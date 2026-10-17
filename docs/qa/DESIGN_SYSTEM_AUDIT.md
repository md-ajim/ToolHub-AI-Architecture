# ToolHub-AI — Design System Audit

Date: 2026-09-30. Static inspection only.

## Canonical primitives (reuse these)

Buttons `ui/button.tsx` (default/outline/secondary/ghost/destructive/link; xs/sm/default/lg/icon*) · Inputs (`input`, `password-input`, `input-group`, `textarea`, `label`) · `badge.tsx` (tier/status) · `card.tsx` · `table.tsx` · `tabs.tsx` · `accordion.tsx` · `slider.tsx` · `switch.tsx` · `progress.tsx` · `skeleton.tsx` · `tooltip.tsx` · `sonner.tsx` (Toaster) · `command.tsx` · `dropdown-menu.tsx` · `select.tsx` · `dialog.tsx` · `alert-dialog.tsx` · `sheet.tsx` · `scroll-area.tsx` · `toggle-group.tsx` · `navigation-menu.tsx`.
Tokens: `lib/design/tokens.ts` (primary orange 500 #f97316 scale, accent green, surface slate, radii 0–full, spacing xs–3xl, Inter/Space Grotesk + canvas fonts incl. Bengali coverage).
Editor inspector: `InspectorPrimitives.tsx` + `inspector/th-ui.tsx` (`ThInput/ThSelect/ThOption`); ToolHub kit: `toolhub/*` (Panel/PanelSection/ModelSelector/ModelBadge/Spinner/EmptyState).

## Findings

1. Toast duality (P3): `sonner` is primary (39 files, Toaster mounted in root layout) but legacy Radix `ui/toast.tsx` + `useToastManager` still ships. No user-facing break; recommend deprecating the Radix path, not deleting yet (rule 14 — trace runtime refs first).
2. Select duality (P3, intentional): Radix `select.tsx` for app UI + `ThSelect` for editor inspector density. Acceptable — different density contexts; both route through shared tokens.
3. Button access: canonical `Button` used in 90 files; `focus-visible` ring + `disabled:opacity-50` + `pointer-events-none` baked into the variant — consistent focus/disabled language. Icon size normalized (`size-4` default, `size-3/3.5` for xs/sm).
4. Modal sizes: `dialog` / `alert-dialog` / `sheet` each own their sizing (sheets `w-[300px] sm:w-[400px]` for mobile nav); no page-specific modal hacks found in sample.
5. Loading indicators: `Skeleton` (11 files) + `ToolHubSpinner(size)` + `Loader2` spinners for short actions + `Progress` for measurable work + AI job status overlay — matches the loading standard (skeleton=content, spinner=short action, status=long AI job). No giant center-spinner-everywhere pattern found.
6. Typography: Inter body + Space Grotesk display + canvas catalog (Poppins/Montserrat/Playfair/Roboto/Noto Bengali/Hind Siliguri) loaded once in root layout — coherent identity, international coverage.
7. Colors: single orange-primary/green-accent system; no competing design systems found across marketing/dashboard/editor/billing samples.
8. `prefers-reduced-motion`: respected in `app/globals.css` (×2) + `lib/design/theme.css`. PASS (static).
9. Icons: `lucide-react` (optimized via `optimizePackageImports`) + `ProviderIcons` brand SVGs with `mock` fallback case. Consistent sizing via button normalization.

## Verdict

No P0/P1 design-system break. Two P3 deprecation notes (legacy toast, dual select — both intentional today). Fix policy: new UI must reuse the primitives above; no page-specific button/modal/dropdown forks.
