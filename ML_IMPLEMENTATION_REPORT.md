# ML Implementation Report — Classical ML in ToolHub-AI

> Session report: 2026-10-03. Classical ML অ্যালগরিদম (Linear Regression,
> Decision Tree, Random Forest + tuning, KNN, KMeans, Feature Engineering,
> Feature Importances, Confusion Matrix) প্রজেক্টে কোথায়, কীভাবে বসানো
> হয়েছে — তার সম্পূর্ণ বিবরণ। সব দাবি কোড-যাচাইকৃত।

---

## 1. সারসংক্ষেপ

| Phase | বিষয় | অবস্থা |
|---|---|---|
| Phase 1 | Tool co-usage clustering → শেখা recommendation | ✅ সম্পূর্ণ |
| Phase 1.1 | AI-job + studio-step signal যোগ (slug mapping সহ) | ✅ সম্পূর্ণ |
| Phase 2 | Full ML suite: churn RF, segmentation, credit forecast, metrics API, billing widget | ✅ সম্পূর্ণ |
| Phase 3 | বাদপড়া অংশ (additive): upgrade model, cost model, prompt router, Data Science Studio | ✅ সম্পূর্ণ |

**নীতি:** sklearn/pandas ছাড়াই pure-Python implementation (Docker image হালকা থাকে);
training Celery/management-command-এ, serving API-তে; ডেটা কম থাকলে graceful
fallback — UI কখনো ভাঙে না। আগের কোনো config/আচরণ মোছা বা বদলানো হয়নি।

---

## 2. Phase 1 — Learned Tool Recommendations (Clustering)

**ধারণা:** `SmartToolRecommendations.tsx`-এর hardcoded টেবিলের বদলে ব্যবহার-ডেটা
থেকে শেখা suggestion।

| ফাইল | কাজ |
|---|---|
| `backend/apps/analytics/recommender.py` | Jaccard co-usage matrix + dependency-free KMeans (k-means++, deterministic seed) — pure function, Django ছাড়াই টেস্টযোগ্য |
| `backend/apps/analytics/models.py` → `ToolAffinity` | শেখা pair-এর cache টেবিল (source, recommended, score, cluster_id) + migration `0002` |
| `.../management/commands/train_tool_affinity.py` | `Usage(user, tool, date)` পড়ে → affinity → KMeans → টেবিল full-refresh (transaction) |
| `backend/apps/analytics/views.py` → `ToolRecommendationView` | `GET /api/v1/analytics/recommendations/?tool=X` (AllowAny — শুধু aggregate পরিসংখ্যান) |
| `backend/apps/analytics/urls.py` + `config/urls.py` | `api/v1/analytics/` mount |
| `frontend/src/services/image.service.ts` → `fetchToolRecommendations()` | ব্যর্থ হলে `[]` — caller fallback দেখায় |
| `frontend/.../SmartToolRecommendations.tsx` | শেখা suggestion + **"learned" badge**; untrained/error/loading-এ curated তালিকা; tool-keyed + cancelled guard (stale paint অসম্ভব) |

**যাচাই:** synthetic ডেটায় photo/doc cluster সঠিক আলাদা; empty/single/determinism edge case পাস।

### Phase 1.1 — AI signal যোগ

Training source এখন ৩টা: `Usage` + `AIProcessingJob` (completed only) +
`StudioSessionStep` (completed only)। Backend slug → frontend `ToolType` mapping
(`OPERATION_ALIASES` reverse + identity-wins + backend-only op drop) — 18 কেস
টেস্ট পাস। Summary-তে per-source count। `UsageService.record()` ইচ্ছা করে AI
path-এ বসানো হয়নি (daily quota double-count হতো)।

---

## 3. Phase 2 — Full ML Suite

### 3.1 ML লাইব্রেরি (`backend/apps/analytics/ml/`)

| মডিউল | অ্যালগরিদম | ব্যবহার |
|---|---|---|
| `linear.py` | OLS Linear Regression (ridge-stabilised, Gaussian elimination) | credit-burn forecast, reply cost model, AutoML regression |
| `tree.py` | CART Decision Tree (multiclass Gini, JSON-serialisable) | interpretable baseline, binary + multiclass |
| `forest.py` | Random Forest (bootstrap + √feature subsample, majority vote) | churn / upgrade classifier, binary + multiclass |
| `knn.py` | KNN classifier (majority vote) | honest baseline — ভালো হলে মেট্রিক্সে ধরা পড়ে; binary + multiclass |
| `evaluate.py` | N-class confusion matrix, accuracy/macro precision/recall/F1, unclamped R²/MAE, permutation importance, model compare | সব training run-এর মূল্যায়ন |
| `tuning.py` | Grid search + stratified k-fold CV (F1) | hyperparameter tuning |
| `preprocessing.py` | StandardScaler (serialisable), stratified split/k-fold, plain train/test split | feature scaling, honest split |

**যাচাই:** synthetic churn ডেটায় forest F1 0.96; importance ranking সঠিক
(`days_active` > `total_actions` > `night_ratio≈0`); tuning সেরা config বাছে;
serialization round-trip পাস।

### 3.2 Feature Engineering (`ml_features.py`)

`Usage` + `CreditTransaction` + `AiConversation` + account age থেকে bulk ORM
aggregate-এ (N+1 query নয়) ৬ ফিচার: `days_active, actions, distinct_tools,
conversations, credits_spent, account_age_days`। Label mode: `churn` (gap-এ
নীরব) / `upgrade` (কখনো paid plan)।

### 3.3 Model Store + Training Command

- `MLModel(kind, version, params, metrics, artifact, feature_names, training_rows, trained_at)` + migration `0003`/`0004`; serving view সবসময় latest row ব্যবহার করে।
- `train_churn_model` — tuned RF + tree/KNN তুলনা + confusion matrix + importances।
- `train_upgrade_model` — একই machinery, paid-plan label।
- `train_segmentation` — KMeans (activity-ranked নাম: Power/Regular/Casual/Dormant) + inertia।
- `train_cost_model` — prompt→reply pair-এ (binary-search pairing) দুটো OLS regression (tokens, latency) + R²।
- `train_tool_affinity_task` সহ Celery `shared_task` wrapper (`tasks.py`) — nightly retrain প্রস্তুত।

### 3.4 API endpoint (`/api/v1/analytics/`)

| Endpoint | Auth | কাজ |
|---|---|---|
| `recommendations/?tool=X` | open | শেখা next-tool |
| `credit-forecast/` | login | daily burn, days_remaining, depletion_date, r² (ডেটা কম হলে `insufficient_data`) |
| `churn/` | login | probability + label + top risk factors + model version |
| `segments/` | login | segment_id + name + size |
| `model-metrics/` | admin | confusion matrix, tuning table, importances (artefact বাদে) |
| `prompt-route/` (POST) | login | intent category + confidence + কারণ + reasoning/long-context hint (advisory only) |
| `prompt-cost-estimate/` (POST) | login | est tokens/latency + R²; untrained হলে লেবেলসহ heuristic |

### 3.5 Frontend

- Billing পেজে **CreditForecastCard** — pace, depletion date, <7 দিনে top-up CTA; backendUnreachable/ডেটা না থাকলে নিজে লুকিয়ে যায়।
- `fetchCreditForecast()` — throw করে না (`null` ফেরত)।

---

## 4. Phase 3 — User-Facing Data Science Studio (additive app)

নতুন Django app `data_science/` (INSTALLED_APPS + `api/v1/data/` mount — ২ লাইনই
একমাত্র বিদ্যমান-ফাইল স্পর্শ):

| ফাইল | কাজ |
|---|---|
| `models.py` | `Dataset` (CSV ≤2MB/5000 row) + `DSJob` (clean/train/segment, queued→processing→completed/failed) + migration `0001` |
| `csvkit.py` | stdlib CSV parse/profile/clean: missing-fill (mean/median/zero/mode), standardisation, one-hot/label encoding, target exclusion |
| `tasks.py` | Celery `run_ds_job` — clean→CSV download; train→auto task-detect (numeric target = linear regression + R²/MAE, নইলে RF-vs-tree-vs-KNN + confusion + importances); segment→KMeans + labeled-CSV download |
| `views.py` | upload/profile/clean/train/segment enqueue + owner-checked status/download (7 endpoint) |

Frontend (`/tools/data-studio`, registry-তে ১ entry append):
- ৪ tab: Upload & Profile (dtype/missing টেবিল) → Clean (৪ option) → AutoML (target select, comparison table, **confusion heatmap**, **importance bar** — CSS/SVG, dep নেই) → Segment (k select, cluster bar, download)।
- 2s polling, owner-safe download (`downloadUrl` auth contract), `ToolLayout` + breadcrumb।

---

## 5. প্রস্তাব-বনাম-বাস্তব (চূড়ান্ত অডিট)

| প্রস্তাবের পয়েন্ট | অবস্থা |
|---|---|
| Prompt clustering + smart router | ✅ intent router + routing hint API |
| Token/latency prediction (Linear Regression) | ✅ cost model + estimate API |
| Churn + upgrade prediction (RF/DT) | ✅ দুটো আলাদা tuned মডেল |
| Feature Engineering/Transformation | ✅ internal features + user-facing cleaner |
| Feature Importances | ✅ permutation importance (API + UI) |
| Confusion Matrix + P/R | ✅ metrics API + heatmap UI |
| Dataset Cleaner | ✅ Studio tab 2 |
| No-Code AutoML (Linear/Tree/RF/KNN) | ✅ Studio tab 3 |
| Evaluation & Explainability UI | ✅ heatmap + importance bar |
| Customer Segmentation tool | ✅ Studio tab 4 |

---

## 6. চালানো

```bash
docker compose exec backend python manage.py migrate analytics data_science
docker compose exec backend python manage.py train_tool_affinity
docker compose exec backend python manage.py train_churn_model
docker compose exec backend python manage.py train_upgrade_model
docker compose exec backend python manage.py train_segmentation
docker compose exec backend python manage.py train_cost_model
# nightly (beat schedule-এ এক লাইন): apps.analytics.tasks.train_tool_affinity_task
```

তারপর: `/tools/data-studio`-তে CSV আপলোড; billing-এ forecast card; editor-এ "learned" badge।

## 7. যাচাই ফলাফল

- Python `py_compile`: সব নতুন/ছোঁয়া ফাইল OK
- Math checks: KMeans co-usage, full ML lib (F1/importance/tuning/round-trip), intent 6 কেস, slug mapping 18 কেস, csvkit end-to-end — সব পাস
- `tsc --noEmit` + সংশ্লিষ্ট `eslint`: ক্লিন (billing পেজের ১ lint error pre-existing — HEAD-এও আছে, ছোঁয়া হয়নি)

## 8. প্রতিটা ফিচার কী কাজ করে (ব্যবহার-ভিত্তিক নির্দেশিকা)

### 8.1 Image Editor — "Continue with" (শেখা suggestion)
- **কোথায়:** Image Editor-এ যেকোনো টুল চালু করলে নিচে "Continue with" strip।
- **কী করে:** backend-এর `ToolAffinity` টেবিল থেকে ওই টুলের শেখা next-tool আনে
  (যেমন `bg-remove` → Enhance, Upscale)। শেখা থাকলে ছোট **"learned" badge** দেখায়।
- **কখন কী দেখায়:** training হয়নি / backend বন্ধ / loading — আগের curated তালিকা;
  কোনো অবস্থাতেই খালি হয় না। Chip-এ ক্লিক = টুল বদলে যায়।

### 8.2 Billing — Credit Forecast Card
- **কোথায়:** Dashboard → Billing, Credit overview-এর নিচে।
- **কী করে:** গত ৩০ দিনের খরচে regression চালিয়ে বলে — "প্রতিদিন ~X credit হারে
  ব্যালেন্স ~N দিন চলবে (তারিখ)"। pace শূন্য হলে "top-up দরকার নেই"। ৭ দিনের কম
  থাকলে pricing-লিংকসহ সতর্কবার্তা।
- **কখন লুকায়:** খরচের ইতিহাস <5 দিন হলে বা backend না পেলে — card নিজে অদৃশ্য হয়,
  billing পেজ ভাঙে না।

### 8.3 Churn / Upgrade / Segment API (কে ব্যবহার করে)
- **`churn/`** — login ইউজারের ঝরে-যাওয়ার সম্ভাবনা (0–1) + healthy/at_risk লেবেল +
  top risk factor (যেমন `days_active`)। Retention ইমেইল/promo trigger-এর input।
- **`upgrade/` (train_upgrade_model)** — একই API পরিবার; free→paid সম্ভাবনা —
  sales/priority-support তালিকায় লাগে। *(endpoint `churn/`-এর মতো করে `upgrade/`
  যোগ করা এক লাইনের কাজ — মডেল kind প্রস্তুত।)*
- **`segments/`** — ইউজারের segment (Power users / Regulars / Casual users /
  Dormant) + segment size। Dashboard-এ personalized টিপস বা admin রিপোর্টে লাগে।
- **`model-metrics/`** (admin) — প্রতিটা মডেলের confusion matrix, precision/recall/F1,
  tuning table, feature importance — QA/audit-এর প্রমাণ।

### 8.4 Prompt Route + Cost Estimate (composer-এর সহকারী)
- **`prompt-route/`** — prompt পাঠালে category (code/math/creative/research/chat) +
  confidence + কারণের তালিকা + hint (`use_reasoning`, `needs_long_context`,
  `suggested_capability`)। শুধু পরামর্শ — ইউজারের মডেল-পছন্দ কখনো override করে না।
- **`prompt-cost-estimate/`** — prompt + tier দিলে আনুমানিক reply length (token) ও
  latency (ms) + R²। মডেল না থাকলে "heuristic" লেবেলসহ মোটামুটি হিসাব — নীরবে
  বানানো সংখ্যা নয়।

### 8.5 Data Science Studio (`/tools/data-studio`) — ৪ tab-এর কাজ
1. **Upload & Profile** — CSV (≤2MB/5000 row) আপলোড → preview + প্রতি কলামের
   profile: numeric/categorical, missing %, unique সংখ্যা, mean/min-max বা top value।
2. **Clean & Transform** — ৪ option (numeric fill: mean/median/zero; categorical:
   mode/empty; scaling; one-hot/label/none) → Celery job → **ML-ready CSV download**
   + কী কী transform হলো তার রিপোর্ট।
3. **AutoML Train** — target কলাম বাছুন → job → ফলাফল: task auto-detect
   (classification: RF-vs-tree-vs-KNN তুলনা টেবিল; regression: R²/MAE বনাম baseline),
   **confusion-matrix heatmap**, **importance bar chart**। 2s polling-এ লাইভ আপডেট।
4. **Segment** — k (2–8) বাছুন → KMeans → cluster-size bar + **cluster কলামসহ CSV
   download** (ই-কমার্স কাস্টমার ভাগ)।

### 8.6 Training command — কোনটা চালালে কী হয়
| Command | Input | Output |
|---|---|---|
| `train_tool_affinity` | Usage + completed AI job + studio step (90 দিন) | `ToolAffinity` refresh → এডিটর suggestion বদলায় |
| `train_churn_model` | 30 দিন behavior + 14 দিন gap | `MLModel(churn)` v+1 → `churn/` স্কোর বদলায় |
| `train_upgrade_model` | behavior + paid-plan ইতিহাস | `MLModel(upgrade)` v+1 |
| `train_segmentation` | গত 30 দিন active user | centroids v+1 → `segments/` বদলায় |
| `train_cost_model` | prompt→reply pair (token/latency) | ২ regression v+1 → estimate API বদলায় |

ডেটা অপ্রতুল হলে প্রতিটা command **warning দিয়ে থামে** — পুরনো মডেল অক্ষত থাকে,
কখনো খালি/ভুল মডেল লেখে না।

## 9. সীমা ও পরবর্তী ধাপ

- Django এই মেশিনে নেই → `migrate` + command run Docker-এ।
- CSV cap 2MB/5000 row; KNN artefact ≤2000 row; DS job-এ credit charge নেই (নীতি-সিদ্ধান্ত বাকি)।
- পরবর্তী: embedding-centroid intent (embedding infra এলে), upgrade/churn retention hook (email/promo trigger), DS Studio-তে grid-search toggle।

---

## 10. Session 2026-10-05 — correctness, multiclass & evaluation fixes

Priorities were correctness, reliability and real product value. No new
algorithms were added (no Logistic Regression / Naive Bayes / SVM / neural
nets — none is required by a ToolHub-AI product need today).

### 10.1 AI inference vs Machine Learning (terminology contract)

- **AI inference** = external/local generative models used for chat, vision,
  research, image generation/editing (LiteLLM / provider gateways, ComfyUI,
  Cloudflare workers). These models are *consumed*, never trained here.
- **Machine learning** = project-trained classical models listed below, used
  for recommendations, prediction, segmentation, forecasting and data
  analysis. All live under `backend/apps/analytics/ml/` (+ `recommender.py`,
  `ml_features.py`) and `backend/apps/data_science/`, trained via management
  commands / Celery, served via `/api/v1/analytics/` and `/api/v1/data/`.

### 10.2 Algorithms actually implemented (verified in code + tests)

| Algorithm | Module | Where used | Binary | Multiclass |
|---|---|---|---|---|
| Linear Regression (OLS, ridge-stabilised) | `ml/linear.py` | credit-burn forecast, prompt cost model, Studio regression | n/a (regression) | n/a |
| Decision Tree (CART, Gini) | `ml/tree.py` | churn/upgrade comparison baseline, Studio AutoML | ✅ | ✅ (fixed this session) |
| Random Forest (bagged trees, √features) | `ml/forest.py` | churn model, upgrade model, Studio AutoML | ✅ | ✅ (fixed this session) |
| KNN (majority vote, k=5 default) | `ml/knn.py` | comparison baseline, Studio AutoML | ✅ | ✅ (fixed this session) |
| K-Means (k-means++, deterministic seed) | `recommender.py` | tool-affinity clustering, user segmentation, Studio segment tab | n/a (clustering) | n/a |
| Rule-based prompt intent router | `ml/prompt_intent.py` | `prompt-route/` API (NOT ML — transparent rules, advisory only) | — | — |

Grid search + stratified k-fold CV (`ml/tuning.py`), StandardScaler +
stratified / plain train-test splits (`ml/preprocessing.py`), and
permutation importance (`ml/evaluate.py`) support the above.

### 10.3 Problems found → fixed

1. **Binary-only classifiers vs multiclass Studio.** `tree.py`/`forest.py`
   summed 0/1 labels for Gini and thresholded at 0.5; `knn.py` averaged
   labels; `evaluate.py` only emitted `{tn,fp,fn,tp}`. Any target with >2
   classes silently collapsed. → All three models now use multiclass Gini /
   majority vote, store `classes_`, expose `predict_dist()`; `predict()`
   returns true class labels. Binary API (`predict_proba` → P(class=1),
   legacy `{tn,fp,fn,tp}` matrix) is preserved, including loading
   pre-multiclass artefacts. `classification_scores` returns macro-averaged
   precision/recall/F1 + per-class breakdown + N-class matrix for >2
   classes. Studio `_run_train` label-encodes targets, rejects single-class
   and >30-class targets with clear errors, and returns `labels`,
   `num_classes`, `class_distribution`, train/test row counts. Frontend
   confusion matrix renders an N-class heatmap; the comparison-table reader
   was fixed (it read `result.comparison`, backend nests under
   `result.metrics` — top-level aliases added for old builds).
2. **Regression scored on training data.** Studio trained OLS on all rows
   and reported training R²/MAE as performance; `r_squared()` clamped
   negatives to 0.0, hiding bad fits; `train_cost_model` and
   `CreditForecastView` had the same train-as-test flaw. → Studio now uses
   an 80/20 `train_test_split` (train-only fit, test-only R²/MAE/baseline,
   plus train-R² for overfit inspection and a small-test-set warning);
   `r_squared()` no longer clamps (negative = worse than mean, reported
   honestly); cost model trains on 80% / reports test R²+MAE; forecast view
   holds out the most recent 20% (time-ordered, R²=None with an explicit
   note when <10 active days).
3. **Weak recommendations unfiltered.** `recommend()` surfaced any
   positive Jaccard pair. → New `min_score` threshold (training default
   0.05 via `--min-score`, API `?min_score=` override, legacy default 0.0
   preserved), new `?exclude=` param so callers can hide already-used
   tools, and a `reason` string + `fallback` notice per response.
4. **Churn explainability thin.** Response carried only a global importance
   list. → Now returns `risk_score` (+ legacy `churn_probability`), `label`,
   `model_version`/`model_kind`/`trained_at`/`training_rows`,
   `user_features`, per-factor `{feature, importance, user_value, note}`
   with correlation-not-cause wording, an `explanation` sentence, impurity
   importances fallback, and NaN/inf vector validation. Training persists
   `evaluation`, `train_rows`/`test_rows`, `class_distribution` for audit.
5. **No ML tests.** → `backend/tests/unit/apps/analytics/test_ml_suite.py`:
   48 tests, all passing (see §10.5).

### 10.4 Training / inference / evaluation per model

- **Churn / upgrade (RF):** features from `ml_features.py` (6 behavioural
  aggregates, bulk ORM); `train_churn_model` / `train_upgrade_model` do
  stratified 80/20 split → scaler fit on train → grid-search CV on train →
  RF/tree/KNN comparison on test → permutation importances → versioned
  `MLModel(kind, artifact={forest,scaler}, metrics={comparison,
  feature_importances, tuning_table, evaluation, train/test rows,
  class_distribution})`. Inference: `ChurnScoreView` rebuilds the caller
  vector, scales, returns P(churn). Metrics: accuracy, precision, recall,
  F1, binary confusion matrix.
- **Segmentation (KMeans):** `train_segmentation` standardises recent
  behaviour → k-means → activity-ranked names → centroids persisted;
  `SegmentView` assigns nearest centroid. Metric: inertia + cluster sizes.
- **Cost (2× OLS):** `train_cost_model` pairs prompts→replies → 80/20 split
  → test R²/MAE per head. `prompt-cost-estimate/` serves or labels the
  heuristic fallback.
- **Credit forecast (OLS):** per-request fit over daily spend; burn from
  full fit, R² from recent-20% holdout (or None + note).
- **Tool affinity (Jaccard + KMeans):** `train_tool_affinity` (Usage +
  completed AI jobs + studio steps, `--min-users`, `--min-score`) refreshes
  `ToolAffinity`; `recommendations/` serves with reason/exclude support.
- **Studio AutoML:** classification → stratified split + RF-vs-tree-vs-KNN
  + macro scores + N-class matrix + importances; regression → 80/20 split +
  test R²/MAE vs mean baseline. Min 20 rows, ≥2 classes, ≤30 classes.

### 10.5 Tests

`backend/tests/unit/apps/analytics/test_ml_suite.py` — **48 passed**.
Linear fit/R² (incl. negative-R² honesty)/MAE/serialisation; tree/forest/KNN
binary + 3-class predictions, distribution normalisation, importances,
serialisation round-trips, legacy-artefact load, empty/single-class
rejection, constant-feature safety; binary legacy + N-class confusion
matrices, macro scores, model comparison, permutation-importance ranking;
scaler (incl. constant column), stratified + plain splits + rejections;
Jaccard/affinity/KMeans behaviour, determinism, min-score filtering,
reason text; csvkit missing-value profiling/cleaning to ML-ready floats.

### 10.6 Anomaly detection — considered, NOT implemented

`analytics.Event`/`PageView` give raw activity streams but there are no
per-user baselines, no labelled incidents, no alerting consumer and no
evaluation protocol — any detector shipped now would be an untestable
false-positive generator. Decision: no implementation. Prerequisites if
revisited: per-user daily-count baselines, a notification/audit consumer,
and backtested precision/recall on labelled windows.

### 10.7 Remaining limitations / next steps

- Studio task detection is heuristic (float target with >10 uniques ⇒
  regression); integer-coded multiclass targets with many levels hit the
  30-class guard by design.
- Churn/upgrade need ≥20 labelled rows with both classes or training is
  skipped (old model kept) — correct, but means cold-start instances have
  `untrained` APIs until real behaviour accrues. No synthetic labels are
  ever invented.
- No model calibration / drift monitoring / retention hooks yet; DS Studio
  has no grid-search toggle; intent router stays rule-based until an
  embedding service lands.
- Verify in Docker: `migrate analytics data_science`, the five training
  commands, and the Studio upload→train→segment flow (this box has no
  Django runtime; pure-ML tests + `py_compile` pass here).
