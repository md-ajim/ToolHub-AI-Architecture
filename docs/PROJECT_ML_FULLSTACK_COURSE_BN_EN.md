# ToolHub-AI Project Course: Full-Stack Engineering, AI/ML Integration & Communication

**বাংলা + English | Beginner-to-intermediate | 8 weeks**

এই কোর্সটি ToolHub-AI-এর বর্তমান implementation দেখে তৈরি। এটি শুধু generic ML syllabus নয়: project-এর classical ML training, AI-provider inference, Django/Celery API, Next.js UI, evaluation এবং communication practice একসঙ্গে শেখায়।

> **সঠিক terminology:** ToolHub-AI-তে external/local generative AI model ব্যবহার করা হয়; এগুলো এই repository-তে train করা হয় না। Project-এর নিজস্ব classical ML models আলাদাভাবে train/evaluate করা হয়। Prompt intent router বর্তমানে transparent rule-based code—এটি ML model নয়।

---

## কোর্সের সংক্ষিপ্ত বিবরণ

| বিষয় | পরিকল্পনা |
|---|---|
| মেয়াদ | ৮ সপ্তাহ; সপ্তাহে ৩টি lesson |
| সময় | প্রতি lesson ১.৫–২ ঘণ্টা; প্রতি সপ্তাহে ৩–৫ ঘণ্টা project practice |
| প্রয়োজনীয় ভিত্তি | Python-এর basic syntax, JavaScript/TypeScript-এর পরিচিতি, HTTP/JSON-এর প্রাথমিক ধারণা |
| শেখার পদ্ধতি | পড়া → code trace → ছোট পরীক্ষা → project lab → লিখিত/মৌখিক ব্যাখ্যা |
| চূড়ান্ত ফল | একটি end-to-end feature design, implement-or-trace, test, evaluate, demo এবং communicate করতে পারা |

### কোর্স শেষে আপনি পারবেন

1. ToolHub-AI-এর browser-to-database architecture ব্যাখ্যা করতে।
2. Supervised learning, regression, classification, clustering এবং evaluation metric নিজের ভাষায় বোঝাতে।
3. Project-এর Linear Regression, Decision Tree, Random Forest, KNN, K-Means, Jaccard similarity ও rule-based routing-এর কাজ আলাদা করে চিনতে।
4. Data → feature → split → fit → evaluate → serialize → API inference pipeline trace করতে।
5. Next.js frontend, Django REST API, Celery worker, provider adapter, database, Redis සහ file storage-এর দায়িত্ব ব্যাখ্যা করতে।
6. Leakage, class imbalance, overfitting, cold-start, weak data এবং model limitations শনাক্ত করতে।
7. Technical update, demo, code review, incident report ও stakeholder explanation বাংলা এবং English-এ দিতে।

---

## ১. প্রজেক্টের মানচিত্র: কোন AI/ML কোথায়?

### ১.১ চারটি আলাদা বিষয় গুলিয়ে ফেলবেন না

| বিষয় | ToolHub-AI-তে উদাহরণ | কী ঘটে |
|---|---|---|
| **Generative AI inference** | AI Workspace provider adapters; ComfyUI/FAL/Cloudflare/অন্যান্য image providers | আগে থেকে তৈরি provider/local model-এ request পাঠায়; এখানে সেগুলো train করা হয় না |
| **Classical machine learning** | `backend/apps/analytics/ml/` | Behavioural বা CSV data থেকে project নিজস্ব model fit, evaluate ও serialize করে |
| **Heuristic/rule-based logic** | `backend/apps/analytics/ml/prompt_intent.py` | pattern/keyword দেখে transparent routing hint দেয়; শেখা classifier নয় |
| **Data-science processing** | `backend/apps/data_science/` | user CSV profile/clean করে, async job-এ classification/regression/segmentation চালায় |

### ১.২ Architecture-র দুটি AI processing path

```text
Interactive chat:
Next.js → Django AI Workspace API → auth/entitlement/credit reservation
→ model routing → provider adapter → response/SSE → usage settlement

Asynchronous image/creative work:
Next.js → Django API → auth/credit reservation → job record
→ Redis/Celery queue → worker/provider or ComfyUI → output storage
→ job status/result → frontend
```

এই দুই path ইচ্ছা করেই আলাদা: chat সাধারণত interactive/streaming; image generation ও ভারী processing background job। Frontend provider-specific SDK বা response shape-এর ওপর নির্ভর করে না।

### ১.৩ Classical ML data path

```text
Product events / uploaded CSV
→ validate + profile + clean
→ numeric feature matrix X and target y
→ train/test split (and CV for tuning)
→ fit model on train data
→ evaluate on held-out data
→ persist version/metrics/artifact where applicable
→ authenticated API or async job
→ UI displays prediction, metrics, explanation, or downloadable CSV
```

প্রধান source map:

| Area | কোড |
|---|---|
| Classical model implementations | `backend/apps/analytics/ml/` |
| Behavioural feature engineering | `backend/apps/analytics/ml_features.py` |
| Co-usage similarity, K-Means ও tool suggestions | `backend/apps/analytics/recommender.py` |
| Training/evaluation record | `backend/apps/analytics/models.py` (`MLModel`) |
| Training commands | `backend/apps/analytics/management/commands/` |
| Analytics endpoints | `backend/apps/analytics/views.py`, `urls.py` |
| User CSV API and ownership checks | `backend/apps/data_science/views.py` |
| Background clean/train/segment | `backend/apps/data_science/tasks.py` |
| CSV parsing/cleaning | `backend/apps/data_science/csvkit.py` |
| Frontend Data Science Studio | `frontend/src/app/tools/data-studio/` |
| AI Workspace provider orchestration | `backend/apps/ai_workspace/` |
| Image/creative AI adapters and jobs | `backend/apps/ai_tools/` |

---

## ২. আট সপ্তাহের পাঠ্যক্রম

প্রতি সপ্তাহে তিনটি lesson আছে। প্রতিটি lesson-এর জন্য: (ক) ধারণাটি শিখুন, (খ) উল্লিখিত source trace করুন, (গ) প্রশ্নের উত্তর লিখুন/মুখে বলুন, (ঘ) lab-এ ফল যাচাই করুন।

### Week 1 — Product, Full-Stack Map ও Developer Workflow

**Lesson 1: ToolHub-AI product tour**
- AI Workspace, Image Editor, utility tools, Dashboard ও Data Science Studio-এর ব্যবহারকারী-সমস্যা চিহ্নিত করুন।
- `README.md` ও `docs/03-system-architecture.md` থেকে Next.js, Django REST Framework, PostgreSQL, Redis, Celery এবং model/provider integration-এর ভূমিকা আঁকুন।
- অনুশীলন: একটি feature বেছে user action → API → backend → data/model → UI response-এর sequence diagram লিখুন।

**Lesson 2: Repository orientation**
- `frontend/src/app/`, `frontend/src/services/`, `backend/apps/`, `backend/config/`-এর দায়িত্ব।
- Route, page/component, service, serializer, view, model, task, provider adapter—এই স্তরগুলোর পার্থক্য।
- অনুশীলন: Data Studio upload এবং job-status flow-এ প্রতিটি স্তরের একটি করে file খুঁজে flow-টি trace করুন।

**Lesson 3: Local development ও safe changes**
- Environment variables, API base URL, migrations, frontend/backend process এবং Git diff পড়া।
- ব্যবহারকারীর data বা secret log/commit না করা; ছোট, পরীক্ষাযোগ্য পরিবর্তন করা।
- অনুশীলন: পরিবর্তন না করে README অনুযায়ী app চালানোর prerequisite লিখুন এবং একটি endpoint-এর request/response contract নোট করুন।

**সপ্তাহের deliverable:** architecture sketch + 2-minute বাংলা/English project introduction।

### Week 2 — ML Foundations, Data Types ও Problem Framing

**Lesson 4: Feature, label, sample ও prediction**
- `X` = feature matrix; `y` = target/label; row = sample।
- Classification label বনাম regression numeric target; unsupervised clustering-এ target label থাকে না।
- Project examples: user churn (`0/1`), credit-spend forecast (numeric), customer/tool segments (cluster ID)।

**Lesson 5: Supervised, unsupervised ও similarity**
- Classification: ভবিষ্যৎ class; regression: continuous value; clustering: similarity-ভিত্তিক group।
- Jaccard similarity: `|A ∩ B| / |A ∪ B|`—একই tool ব্যবহার করা user-set কতটা overlap করে।
- K-Means: centroid-ভিত্তিক group; cluster ID নিজে থেকে “ভালো/খারাপ customer” বোঝায় না।

**Lesson 6: Problem framing ও data labels**
- Churn label code-এ observation window-এ সক্রিয় কিন্তু সাম্প্রতিক gap-এ নীরব user-কে churn হিসেবে চিহ্নিত করে।
- Upgrade label-এর অর্থ paid plan-এ থাকা; correlation কোনো কারণ প্রমাণ করে না।
- অনুশীলন: churn prediction-এর জন্য সময়ের ক্রম, label window, সম্ভাব্য leakage ও ভুল label কী হতে পারে লিখুন।

**সপ্তাহের deliverable:** তিনটি ML problem card—business question, sample, features, target, action, risk।

### Week 3 — Data Engineering, Cleaning ও Feature Engineering

**Lesson 7: CSV ingest, validation ও profiling**
- Data Studio flow: authenticated upload → CSV/size/row validation → preview/profile।
- Project limits: CSV সর্বোচ্চ 2 MB; configured row limit 5,000। বর্তমান upload code `len(rows) >= MAX_ROWS` হলে reject করে, তাই boundary test-এ 4,999 বনাম 5,000 nonblank data row যাচাই করুন (বর্তমানে 4,999 পর্যন্ত গ্রহণযোগ্য)।
- `backend/apps/data_science/views.py` ও `csvkit.py` পড়ুন।
- অনুশীলন: missing, type, unique value ও invalid-row রিপোর্টের acceptance criteria লিখুন।

**Lesson 8: Cleaning ও encoding**
- Missing value strategy: mean/median/zero/mode/empty; scaling; one-hot/label encoding।
- Transformation training-serving parity-তে গুরুত্বপূর্ণ: training-এ যে transformation, inference-এ একই fitted transformation ব্যবহার করতে হয়।
- অনুশীলন: categorical values-সহ ছোট CSV বানিয়ে expected cleaned output হাতে হিসাব করুন।

**Lesson 9: Product-event feature engineering**
- Behavioural feature set: `days_active`, `actions`, `distinct_tools`, `conversations`, `credits_spent`, `account_age_days`।
- ORM aggregation কেন per-user loop/N+1 query-এর চেয়ে কার্যকর; churn label এবং observation window কীভাবে তৈরি হয়।
- `backend/apps/analytics/ml_features.py` trace করুন।
- অনুশীলন: একটি user row feature vector-এ রূপান্তর করে প্রতিটি feature-এর unit এবং source table লিখুন।

**সপ্তাহের deliverable:** data dictionary + data-quality checklist + একটি cleaned sample CSV।

### Week 4 — Classical ML Algorithms in This Repository

**Lesson 10: Linear Regression**
- ধারণা: `y = intercept + Σ(coefᵢ × xᵢ)`; least squares residual কমায়।
- Project use: daily credit-burn forecast, prompt cost estimate, Data Studio regression।
- Metrics: MAE এবং R²; negative R² হলে model held-out data-তে mean baseline-এর চেয়েও খারাপ।
- Source: `backend/apps/analytics/ml/linear.py`।

**Lesson 11: Decision Tree ও Random Forest**
- Decision Tree feature threshold দিয়ে ভাগ করে; CART/Gini impurity-র মাধ্যমে split বেছে।
- Random Forest bootstrap sample-এ অনেক tree fit করে, split-এ feature subset ব্যবহার করে, তারপর vote নেয়।
- Project use: churn classifier; upgrade classifier training; Data Studio classification comparison।
- Source: `tree.py`, `forest.py`; model package-এর সব path `backend/apps/analytics/ml/`-এর অধীনে।

**Lesson 12: KNN, K-Means ও Jaccard**
- KNN: nearest `k` points-এর label vote; distance-sensitive বলে feature scaling জরুরি।
- K-Means: unlabeled numeric rows-কে `k` cluster-এ ভাগ করে।
- Tool recommendation: user-set-এর Jaccard co-usage affinity, তারপর tool-affinity rows-এ K-Means clustering।
- KNN training rows ধরে রাখে—তাই Data Studio artifact-এ 2,000-row cap আছে।
- Source: `knn.py`, `recommender.py`।

**সপ্তাহের deliverable:** একই ছোট dataset-এ কোন problem-এ কোন algorithm নেবেন—কারণসহ তুলনামূলক নোট।

### Week 5 — Training Pipeline, Evaluation ও Model Reliability

**Lesson 13: Train/test split, stratification ও scaling**
- Test data model selection বা fit-এর সময় দেখা যাবে না; নইলে performance অতিরঞ্জিত হয়।
- Classification-এ stratified split class ratio বজায় রাখে; regression-এর জন্য সাধারণ shuffled split।
- Scaler শুধু train data-তে fit হবে; train এবং test-এ একই mean/scale প্রয়োগ হবে।
- Source: `preprocessing.py`, churn training command।

**Lesson 14: Metrics নির্বাচন**
- Confusion matrix: actual বনাম predicted; `TP`, `FP`, `FN`, `TN`।
- Precision = `TP/(TP+FP)`; Recall = `TP/(TP+FN)`; F1 = precision/recall-এর harmonic mean।
- Accuracy class imbalance-এ বিভ্রান্ত করতে পারে; multiclass-এ macro scores ও per-class breakdown দেখুন।
- Regression: MAE, R² এবং mean-baseline MAE একসঙ্গে পড়ুন।

**Lesson 15: Tuning, explainability ও serialization**
- Grid search + stratified k-fold CV: training split-এর ভিতরে parameter তুলনা; final held-out test-এ একবার evaluate।
- Permutation importance: একটি feature shuffle করলে score কত কমে; এটি causal effect নয়।
- Artifact + scaler + feature order/version একসঙ্গে রাখতে হবে; `to_dict/from_dict` round-trip পরীক্ষা করুন।
- Source: `tuning.py`, `evaluate.py`, `models.py`।

**সপ্তাহের deliverable:** একটি model card—intended use, data period, features, test metrics, failure cases, version।

### Week 6 — Project ML Features: From Product Event to API

**Lesson 16: Churn/upgrade training**
- Churn pipeline: feature rows → labelled target → stratified 80/20 split → train-only scaling → CV grid search → forest/tree/KNN comparison on test → permutation importance → versioned artifact.
- Training command: `python manage.py train_churn_model`; upgrade training command is `python manage.py train_upgrade_model`.
- Insufficient labels/data থাকলে command model না লিখে old model অক্ষত রাখে; cold-start-এ prediction না-ও থাকতে পারে।
- Source: `backend/apps/analytics/management/commands/`।

**Lesson 17: Segmentation, forecast ও tool affinity**
- Segmentation: behaviour features scale → K-Means → cluster size/activity rank; segment label descriptive, judgement নয়।
- Credit forecast: historical daily spend থেকে burn estimate; যথেষ্ট history না থাকলে `insufficient_data`/not available—বিশ্বাসযোগ্যতা জোর করে দেখাবেন না।
- Tool affinity: `Usage` এবং complete হওয়া AI/studio events থেকে recommendation; co-usage হলো association, causal recommendation নয়।
- Source: analytics training commands, `recommender.py`, analytics views।

**Lesson 18: Prompt routing ও external AI model routing**
- `prompt-route/` prompt-কে code/math/creative/research/chat category-তে keyword/pattern দিয়ে classify করে; confidence/reasons/capability hints advisory মাত্র।
- এটি intent ML classifier নয় এবং নিজে provider/model বেছে নেওয়া বা user choice override করা উচিত নয়।
- AI Workspace model routing/provider adapters generative inference orchestration করে; prompt intent heuristic এবং LLM provider router-কে আলাদা করে ব্যাখ্যা করুন।
- Source: `prompt_intent.py`; `backend/apps/ai_workspace/routing.py`, `gateway.py`, `provider_registry.py`, `providers/`।

**সপ্তাহের deliverable:** churn অথবা recommendation flow-এর sequence diagram + API contract।

### Week 7 — Full-Stack Integration, Async Jobs ও Security

**Lesson 19: Django API contract**
- URL → permission/auth → input validation/serializer → view/service → response envelope।
- Analytics endpoints: `recommendations/`, `credit-forecast/`, `churn/`, `segments/`, `model-metrics/`, `prompt-route/`, `prompt-cost-estimate/` under `/api/v1/analytics/`।
- Data Studio endpoints-এ authenticated owner check; নিজের dataset/job-ই status/download করতে পারবে।
- অনুশীলন: endpoint-এর success, validation error, no-model/insufficient-data, unauthorized response লিখুন।

**Lesson 20: Celery job lifecycle**
- Request দ্রুত job তৈরি/enqueue করে; Redis broker; worker queued → processing → completed/failed status রাখে।
- UI status poll করে; file processing এবং downloadable output worker-এ হয়।
- Job failure user/admin-এর কাছে স্পষ্ট status/error হিসেবে পৌঁছাতে হবে; silent success-shaped fallback নয়।
- Source: `backend/apps/data_science/views.py`, `tasks.py`।

**Lesson 21: Next.js integration ও UX**
- UI service API call encapsulate করে; loading, empty, error, stale/cancelled request এবং download state দেখায়।
- Data Studio route `/tools/data-studio`; upload/profile → clean → train → segment workflow।
- ML output-কে prediction, confidence/metric, data limitation ও next step-সহ দেখান; opaque “AI says” label নয়।
- অনুশীলন: result panel-এর states আঁকুন এবং keyboard/screen-reader-এ ব্যবহারযোগ্যতার checklist দিন।

**সপ্তাহের deliverable:** user-uploaded CSV classification feature-এর UI→API→Celery→result flow diagram ও test plan।

### Week 8 — Production Thinking, Testing, Communication & Capstone

**Lesson 22: Testing ও reproducibility**
- Pure ML math tests, API permission/ownership tests, Celery/job state tests, frontend service/component tests আলাদা করুন।
- Seed, model version, feature order, training rows, test metrics, dataset period record করুন।
- Existing suite: `backend/tests/unit/apps/analytics/test_ml_suite.py`—বর্তমান report-এ 48টি test passing উল্লেখ আছে; নিজের checkout-এ পুনরায় চালিয়ে নিশ্চিত করুন।

**Lesson 23: Privacy, fairness, drift ও responsible release**
- Personal/product data minimization, authorization, upload limits, secret handling, retention policy।
- Bias/imbalance, subgroup metrics, temporal drift, calibration ও threshold review—যে কোনো model release-এর আগে বিবেচনা।
- Churn-risk factor correlation; ব্যবহারকারীকে শাস্তি/অস্বীকৃতি দেওয়ার একমাত্র ভিত্তি নয়।
- Model/API outage, provider timeout, queue backlog ও stale model-এর fallback behavior document করুন।

**Lesson 24: Demo, handoff ও capstone**
- 5-minute demo: user problem → data → pipeline → architecture → metric → limitation → next step।
- Code review handoff: changed files, behavior, tests, known risks, rollback/monitoring।
- Capstone rubric ও communication templates নিচে।

**সপ্তাহের deliverable:** bilingual capstone demo + one-page model/feature handoff।

---

## ৩. Capstone: “Explainable Customer/Tool Insights”

### প্রস্তাবিত capstone

Data Science Studio-তে একটি CSV upload করে:
1. dataset profile এবং missing-value report দেখান;
2. cleaning/encoding-এর সিদ্ধান্ত লিখুন;
3. একটি target বেছে classification অথবা regression চালান;
4. train/test split এবং প্রাসঙ্গিক metrics report করুন;
5. confusion matrix বা regression-vs-baseline ফল ব্যাখ্যা করুন;
6. feature importance-কে correlation/association হিসাবে সতর্ক ভাষায় উপস্থাপন করুন;
7. job status, error, ownership, download এবং UI states যাচাই করুন;
8. 5 মিনিটে বাংলা ও English-এ ফল demo করুন।

**সীমা:** Studio-র CSV upload সর্বোচ্চ 2 MB; row parser-এর configured limit 5,000, তবে upload validation `len(rows) >= MAX_ROWS` reject করে—তাই বর্তমান আচরণে 4,999 পর্যন্ত nonblank data rows গ্রহণযোগ্য। Classification-এ ন্যূনতম 20 rows, অন্তত 2 class, সর্বোচ্চ 30 class; segmentation-এ কমপক্ষে 4 rows। Evaluation ছোট dataset-এ indicative মাত্র।

### Capstone মূল্যায়ন (100 points)

| অংশ | পয়েন্ট |
|---|---:|
| Business problem, target ও data dictionary | 15 |
| Data validation/cleaning ও leakage awareness | 15 |
| সঠিক algorithm/task framing | 15 |
| Held-out evaluation ও metric interpretation | 20 |
| API/job/UI error states এবং authorization | 15 |
| Reproducibility, tests ও model limitations | 10 |
| পরিষ্কার bilingual demo ও প্রশ্নের উত্তর | 10 |

---

## ৪. Communication Skills: বাংলা + English অনুশীলন

প্রতি সপ্তাহে একটি 60-second stand-up, একটি 3-minute technical explanation এবং একটি written update দিন। English বলার সময় ছোট বাক্য, নির্দিষ্ট evidence এবং পরিষ্কার limitation ব্যবহার করুন।

### A. Stand-up template

**বাংলা**
> গতকাল আমি [কাজ] করেছি। আজ [পরবর্তী কাজ] করব। [বাধা/ঝুঁকি] আছে, কারণ [কারণ]। এগোতে আমার [নির্দিষ্ট সাহায্য] দরকার।

**English**
> Yesterday, I worked on [task]. Today, I will [next step]. I am blocked by [blocker] because [reason]. I need [specific help] to proceed.

### B. ML ফলাফল ব্যাখ্যা

**বাংলা**
> মডেলটি [target] অনুমান করে [data window]-এর [feature]-গুলো ব্যবহার করে। Holdout test-এ [metric] ছিল [value]। এটি [ব্যবহারের সীমা]; ফলাফল [limitation]-এর কারণে চূড়ান্ত সিদ্ধান্ত নয়।

**English**
> The model predicts [target] from [features] over [data window]. On the held-out test set, [metric] was [value]. This is intended for [use], and it is not a final decision because of [limitation].

### C. Code review comment

**বাংলা**
> এই পরিবর্তনটি [আচরণ] উন্নত করছে। আমি [নির্দিষ্ট case] নিয়ে উদ্বিগ্ন, কারণ [প্রমাণ/কারণ]। আমরা কি [পরীক্ষাযোগ্য প্রস্তাব] যোগ করতে পারি?

**English**
> This change improves [behavior]. I am concerned about [specific case] because [evidence/reason]. Could we add [testable suggestion]?

### D. Demo structure

**বাংলা**
1. সমস্যাটি: ব্যবহারকারী কী করতে চান?
2. প্রবাহটি: UI থেকে API/worker/model কীভাবে কাজ করে?
3. প্রমাণ: কোন test বা metric ফল সমর্থন করে?
4. সীমাবদ্ধতা: কোথায় ভুল হতে পারে?
5. পরের ধাপ: কী উন্নতি বা monitoring প্রয়োজন?

**English**
1. Problem: What is the user trying to do?
2. Flow: How does the UI/API/worker/model work together?
3. Evidence: Which test or metric supports the result?
4. Limitation: Where can it fail?
5. Next step: What improvement or monitoring is needed?

### E. 10-minute daily speaking drill

1. 2 মিনিটে একটি concept বাংলায় ব্যাখ্যা করুন।
2. একই ব্যাখ্যা 2 মিনিটে English-এ বলুন; বাক্য ছোট রাখুন।
3. “What evidence supports this?” প্রশ্নের উত্তর দিন।
4. একটি সীমাবদ্ধতা এবং একটি follow-up action বলুন।
5. নিজের recording শুনে filler words, unclear terms এবং unsupported claims লিখে সংশোধন করুন।

---

## ৫. শেখার জন্য প্রস্তাবিত কাজ ও যাচাই

### প্রতি lesson-এর workflow

1. প্রথমে feature-এর user story ও acceptance criteria লিখুন।
2. source trace করে request/data flow আঁকুন।
3. হাতে ছোট example হিসাব করুন; বিশেষ করে metric ও split।
4. test বা synthetic sample দিয়ে behavior যাচাই করুন।
5. ফলাফলের সীমা লিখুন—শুধু “works” বলবেন না।
6. 60-second spoken summary বাংলায় এবং English-এ রেকর্ড করুন।

### Self-check প্রশ্ন

- এই feature কি generative inference, trained ML, clustering নাকি heuristic?
- `X` এবং `y` কী? কোন তথ্য prediction-এর সময় সত্যিই পাওয়া যাবে?
- Scaler/encoder কোথায় fit হয়েছে? Test data কি training/tuning-এ ঢুকেছে?
- Dataset ছোট, imbalanced, stale বা biased হলে কী বদলাবে?
- কোন metric business risk-এর সঙ্গে মেলে?
- API failure, queue failure, no-model ও unauthorized user-এ UI কী দেখায়?
- Feature importance-কে causal explanation হিসেবে বলা হচ্ছে কি?
- User বা reviewer-কে এই ফলাফল 30 সেকেন্ডে কীভাবে বোঝাব?

### কী দিয়ে শুরু করবেন (পড়ার ক্রম)

1. Repository `README.md`
2. `docs/03-system-architecture.md`
3. `docs/12-ai-processing-architecture-v2.0.md`
4. `docs/32-ai-multi-model-workspace-architecture-v2.0.md`
5. `ML_IMPLEMENTATION_REPORT.md`—বিশেষ করে algorithm, lifecycle, সীমাবদ্ধতা ও test অংশ
6. `backend/apps/analytics/ml/` এবং `backend/apps/data_science/`
7. `backend/tests/unit/apps/analytics/test_ml_suite.py`
8. `frontend/src/app/tools/data-studio/` ও সংশ্লিষ্ট API service

---

## ৬. Known Limitations: যা course project-এ সৎভাবে বলতে হবে

- Churn/upgrade supervised model-এর জন্য যথেষ্ট বাস্তব labelled row ও উভয় class দরকার; cold-start-এ model অনুপস্থিত হতে পারে। কৃত্রিম label বানানো সমাধান নয়।
- Prompt intent router এখন keyword/pattern-based heuristic; embedding classifier হিসেবে বর্ণনা করা ভুল।
- Provider/ComfyUI model repository-তে ব্যবহৃত inference dependency; classical ML pipeline-এর অংশ নয়।
- K-Means cluster number/scale/initialization-এ সংবেদনশীল; cluster ID ক্রম/ব্যবসায়িক মূল্য বোঝায় না।
- Data Studio task detection heuristic; numeric target-কে সবসময় regression ধরা যাবে না।
- Small test set-এর score অনিশ্চিত; production release-এ আরও real-world validation প্রয়োজন।
- Report-এ anomaly detection বিবেচিত হয়েছে, কিন্তু বাস্তব implementation নেই।
- Model metric ভালো হলেই causal insight, fairness, calibration, drift resistance বা business value প্রমাণ হয় না।

---

# English Version — ToolHub-AI Project Course

## Course overview

An eight-week, project-based course for learning **Full-Stack Engineering, AI/ML Integrations, and technical communication** through the actual ToolHub-AI repository. It covers how the product uses external generative models, where project-trained classical ML exists, how data moves through Django/Celery and Next.js, and how to evaluate and explain the result.

**Important distinction:** The repository consumes external/local generative models; it does not train those foundation models. The repository separately implements and trains classical ML models. The prompt-intent router is currently transparent, rule-based logic—not a learned ML classifier.

### Format and outcomes

- **Duration:** 8 weeks; 3 lessons per week.
- **Effort:** 1.5–2 hours per lesson plus 3–5 hours of weekly project practice.
- **Prerequisites:** Basic Python, familiarity with JavaScript/TypeScript, and introductory HTTP/JSON.
- **By the end:** You can explain the full-stack architecture; distinguish inference, trained ML, clustering, and heuristics; trace data through feature engineering, training, evaluation, serialization, APIs, and UI; identify leakage/overfitting/data limitations; and present a technical feature in both Bengali and English.

## 1. Project map: what AI/ML is used where?

| Area | ToolHub-AI example | What it does |
|---|---|---|
| **Generative AI inference** | AI Workspace provider adapters; ComfyUI/FAL/Cloudflare/other image providers | Sends requests to existing provider/local models; these models are not trained in this repository |
| **Classical machine learning** | `backend/apps/analytics/ml/` | Fits, evaluates, and serializes project models from behavioral or uploaded CSV data |
| **Heuristic/rule-based logic** | `backend/apps/analytics/ml/prompt_intent.py` | Uses transparent patterns/keywords to provide routing hints; it is not a learned classifier |
| **Data-science processing** | `backend/apps/data_science/` | Profiles/cleans user CSVs and runs classification, regression, or segmentation as async jobs |

### Two AI-processing paths

```text
Interactive chat:
Next.js → Django AI Workspace API → auth/entitlement/credit reservation
→ model routing → provider adapter → response/SSE → usage settlement

Asynchronous image/creative work:
Next.js → Django API → auth/credit reservation → job record
→ Redis/Celery queue → worker/provider or ComfyUI → output storage
→ job status/result → frontend
```

They are separate by design: chat is interactive/streaming, while image generation and heavy processing run as background jobs. The frontend does not depend on provider-specific SDKs or response formats.

### Classical ML lifecycle

```text
Product events / uploaded CSV
→ validate + profile + clean
→ numeric feature matrix X and target y
→ train/test split (and CV for tuning)
→ fit on training data
→ evaluate on held-out data
→ persist version/metrics/artifact where applicable
→ authenticated API or async job
→ UI displays prediction, metrics, explanation, or downloadable CSV
```

Key source locations:

| Area | Code |
|---|---|
| Classical ML implementations | `backend/apps/analytics/ml/` |
| Behavioral feature engineering | `backend/apps/analytics/ml_features.py` |
| Co-usage similarity, K-Means, and tool suggestions | `backend/apps/analytics/recommender.py` |
| Training/evaluation record | `backend/apps/analytics/models.py` (`MLModel`) |
| Training commands | `backend/apps/analytics/management/commands/` |
| Analytics endpoints | `backend/apps/analytics/views.py`, `urls.py` |
| User CSV API and ownership checks | `backend/apps/data_science/views.py` |
| Background cleaning/training/segmentation | `backend/apps/data_science/tasks.py` |
| CSV parsing/cleaning | `backend/apps/data_science/csvkit.py` |
| Frontend Data Science Studio | `frontend/src/app/tools/data-studio/` |
| AI Workspace provider orchestration | `backend/apps/ai_workspace/` |
| Image/creative AI adapters and jobs | `backend/apps/ai_tools/` |

## 2. Eight-week curriculum

Each week has three lessons. For every lesson: learn the concept, trace the listed source, answer the questions in writing or aloud, then verify the behavior in the lab.

### Week 1 — Product, full-stack map, and developer workflow

**Lesson 1: Tour the product**
- Identify user problems addressed by the AI Workspace, Image Editor, utility tools, Dashboard, and Data Science Studio.
- Use `README.md` and `docs/03-system-architecture.md` to map Next.js, Django REST Framework, PostgreSQL, Redis, Celery, and model/provider integrations.
- Lab: draw a sequence diagram for user action → API → backend → data/model → UI response.

**Lesson 2: Repository orientation**
- Understand the responsibilities of `frontend/src/app/`, `frontend/src/services/`, `backend/apps/`, and `backend/config/`.
- Distinguish routes/pages/components, services, serializers, views, models, tasks, and provider adapters.
- Lab: find one file per layer in the Data Studio upload/status flow and trace the request.

**Lesson 3: Local development and safe changes**
- Environment variables, API base URL, migrations, frontend/backend processes, and reading a Git diff.
- Never log or commit user data/secrets; prefer small, testable changes.
- Lab: document the prerequisites to run the app and one endpoint's request/response contract.

**Deliverable:** architecture sketch and a two-minute project introduction in Bengali and English.

### Week 2 — ML foundations, data types, and problem framing

**Lesson 4: Features, labels, samples, and predictions**
- `X` is the feature matrix; `y` is the target/label; each row is a sample.
- Classification predicts a class; regression predicts a numeric value; clustering has no target label.
- Project examples: user churn (`0/1`), credit-spend forecast (numeric), customer/tool segments (cluster ID).

**Lesson 5: Supervised learning, unsupervised learning, and similarity**
- Classification: a future class; regression: a continuous value; clustering: groups by similarity.
- Jaccard similarity: `|A ∩ B| / |A ∪ B|` measures overlap between user sets for two tools.
- K-Means assigns centroid-based groups; a cluster ID does not inherently mean a “good” or “bad” customer.

**Lesson 6: Problem framing and labels**
- The churn-label code identifies users active in an observation window but silent in the recent gap.
- The upgrade label means a user has a paid plan; correlation does not establish causation.
- Lab: document the time ordering, label window, potential leakage, and label errors for churn prediction.

**Deliverable:** three ML problem cards covering business question, sample, features, target, action, and risk.

### Week 3 — Data engineering, cleaning, and feature engineering

**Lesson 7: CSV ingestion, validation, and profiling**
- Data Studio flow: authenticated upload → CSV/size/row validation → preview/profile.
- The project limit is 2 MB and the parser's configured row limit is 5,000. Upload validation currently rejects `len(rows) >= MAX_ROWS`, so test the boundary at 4,999 vs 5,000 nonblank data rows (currently up to 4,999 are accepted).
- Read `backend/apps/data_science/views.py` and `csvkit.py`.
- Lab: define acceptance criteria for missing values, types, unique values, and invalid rows.

**Lesson 8: Cleaning and encoding**
- Missing-value strategies: mean/median/zero/mode/empty; scaling; one-hot/label encoding.
- Transformation parity matters: inference must use the same fitted transformation as training.
- Lab: create a small CSV with categorical values and calculate the expected cleaned output.

**Lesson 9: Product-event feature engineering**
- Behavioral feature set: `days_active`, `actions`, `distinct_tools`, `conversations`, `credits_spent`, `account_age_days`.
- Learn why ORM aggregation avoids per-user loops/N+1 queries, and how the churn observation window/label are built.
- Trace `backend/apps/analytics/ml_features.py`.
- Lab: build one user feature vector and document each feature's unit and source table.

**Deliverable:** data dictionary, data-quality checklist, and one cleaned sample CSV.

### Week 4 — Classical ML algorithms in this repository

**Lesson 10: Linear Regression**
- Concept: `y = intercept + Σ(coefᵢ × xᵢ)`; least squares minimizes residuals.
- Project uses: daily credit-burn forecast, prompt-cost estimate, and Data Studio regression.
- Metrics: MAE and R²; a negative R² means the model is worse than the mean baseline on held-out data.
- Source: `backend/apps/analytics/ml/linear.py`.

**Lesson 11: Decision Tree and Random Forest**
- A Decision Tree splits using feature thresholds and CART/Gini impurity.
- A Random Forest fits many trees on bootstrap samples, subsamples features at splits, then votes.
- Project uses: churn classification; upgrade-model training; Data Studio classification comparison.
- Sources: `tree.py`, `forest.py` under `backend/apps/analytics/ml/`.

**Lesson 12: KNN, K-Means, and Jaccard**
- KNN votes among the nearest `k` points; it is distance-sensitive, so feature scaling matters.
- K-Means assigns unlabeled numeric rows to `k` clusters.
- Tool recommendations use Jaccard co-usage affinity between user sets, then cluster tool-affinity rows using K-Means.
- KNN retains training rows, so Data Studio caps its artifact at 2,000 rows.
- Sources: `knn.py`, `recommender.py`.

**Deliverable:** compare algorithms for a small dataset and justify the choice for each task.

### Week 5 — Training pipeline, evaluation, and reliability

**Lesson 13: Train/test split, stratification, and scaling**
- Test data must not be seen during model fitting or selection; otherwise performance is overstated.
- Stratified splits preserve class ratios; regression uses a regular shuffled split.
- Fit the scaler on training data only, then apply the same mean/scale to train and test.
- Sources: `preprocessing.py` and the churn training command.

**Lesson 14: Choosing metrics**
- A confusion matrix compares actual vs predicted: `TP`, `FP`, `FN`, and `TN`.
- Precision = `TP/(TP+FP)`; Recall = `TP/(TP+FN)`; F1 is their harmonic mean.
- Accuracy can mislead with class imbalance; inspect macro scores and per-class breakdowns for multiclass tasks.
- For regression, read MAE, R², and mean-baseline MAE together.

**Lesson 15: Tuning, explainability, and serialization**
- Grid search + stratified k-fold CV compares parameters within training data; evaluate the final model once on the held-out test set.
- Permutation importance measures score change after shuffling a feature; it is not a causal effect.
- Persist the artifact, scaler, feature order, and version together; test `to_dict/from_dict` round trips.
- Sources: `tuning.py`, `evaluate.py`, and `models.py`.

**Deliverable:** a model card documenting intended use, data period, features, test metrics, failure cases, and version.

### Week 6 — Project ML features: product events to APIs

**Lesson 16: Churn/upgrade training**
- Churn pipeline: feature rows → labelled target → stratified 80/20 split → train-only scaling → CV grid search → forest/tree/KNN comparison on test → permutation importance → versioned artifact.
- Commands: `python manage.py train_churn_model` and `python manage.py train_upgrade_model`.
- If there is insufficient labelled data, training does not replace the existing model; cold-start instances may have no prediction.
- Sources: `backend/apps/analytics/management/commands/`.

**Lesson 17: Segmentation, forecasts, and tool affinity**
- Segmentation: scale behavior features → K-Means → cluster size/activity ranking; a segment name is descriptive, not a judgement.
- Credit forecast estimates burn from daily spend history; with insufficient history, return `insufficient_data`/unavailable rather than overstating certainty.
- Tool affinity uses `Usage` and completed AI/Studio events; co-usage is association, not causal recommendation.
- Sources: analytics training commands, `recommender.py`, and analytics views.

**Lesson 18: Prompt intent and external AI model routing**
- `prompt-route/` classifies prompts into code/math/creative/research/chat using keywords/patterns; confidence/reasons/capability hints are advisory.
- It is not an intent ML classifier and should not independently select a provider/model or override user choice.
- AI Workspace routing/adapters orchestrate generative inference; explain the heuristic prompt intent router separately from the LLM provider router.
- Sources: `prompt_intent.py`; `backend/apps/ai_workspace/routing.py`, `gateway.py`, `provider_registry.py`, and `providers/`.

**Deliverable:** sequence diagram and API contract for a churn or recommendation flow.

### Week 7 — Full-stack integration, async jobs, and security

**Lesson 19: Django API contract**
- URL → permission/authentication → input validation/serializer → view/service → response envelope.
- Analytics endpoints under `/api/v1/analytics/`: `recommendations/`, `credit-forecast/`, `churn/`, `segments/`, `model-metrics/`, `prompt-route/`, and `prompt-cost-estimate/`.
- Data Studio endpoints require authentication and owner checks; users can only access their own datasets/jobs.
- Lab: specify success, validation error, no-model/insufficient-data, and unauthorized responses.

**Lesson 20: Celery job lifecycle**
- A request creates/enqueues a job; Redis acts as broker; a worker records queued → processing → completed/failed.
- The UI polls job status; file processing and downloadable outputs happen in the worker.
- Failures must appear as an explicit status/error, not a silent success-shaped fallback.
- Sources: `backend/apps/data_science/views.py` and `tasks.py`.

**Lesson 21: Next.js integration and UX**
- UI services encapsulate API calls and expose loading, empty, error, stale/cancelled request, and download states.
- Data Studio lives at `/tools/data-studio`: upload/profile → clean → train → segment.
- Present predictions with metrics, limitations, and next steps—not as an opaque “AI says” result.
- Lab: draw result-panel states and check keyboard/screen-reader usability.

**Deliverable:** UI-to-API-to-Celery-to-result flow and test plan for CSV classification.

### Week 8 — Production thinking, testing, communication, and capstone

**Lesson 22: Testing and reproducibility**
- Separate pure ML math tests, API permission/ownership tests, Celery/job-state tests, and frontend service/component tests.
- Record seed, model version, feature order, training rows, test metrics, and data period.
- Existing suite: `backend/tests/unit/apps/analytics/test_ml_suite.py`; the implementation report mentions 48 passing tests—rerun on your checkout.

**Lesson 23: Privacy, fairness, drift, and responsible release**
- Consider personal/product data minimization, authorization, upload limits, secret handling, and retention.
- Review bias/imbalance, subgroup metrics, temporal drift, calibration, and decision thresholds before release.
- Churn-risk factors are correlations, not causal explanations or sole grounds for penalizing/denying users.
- Document provider timeouts, queue backlogs, model outages, and stale-model fallback behavior.

**Lesson 24: Demo, handoff, and capstone**
- Five-minute demo: user problem → data → pipeline → architecture → metric → limitation → next step.
- Code-review handoff: changed files, behavior, tests, known risks, rollback/monitoring.
- Use the capstone rubric and communication templates below.

**Deliverable:** bilingual capstone demo and one-page feature/model handoff.

## 3. Capstone: “Explainable Customer/Tool Insights”

Upload a CSV to Data Science Studio and:
1. Show the dataset profile and missing-value report.
2. Document cleaning/encoding decisions.
3. Select a target and run classification or regression.
4. Report the train/test split and relevant metrics.
5. Explain the confusion matrix or regression-vs-baseline result.
6. Present feature importance as association, not causation.
7. Verify job status, errors, ownership, downloads, and UI states.
8. Demo the result in Bengali and English in five minutes.

**Constraints:** CSV upload up to 2 MB; the parser is configured for 5,000 rows, but upload validation rejects `len(rows) >= MAX_ROWS`, so currently up to 4,999 nonblank data rows are accepted. Classification requires at least 20 rows, at least 2 classes, and no more than 30 classes; segmentation requires at least 4 rows. Metrics on small datasets are indicative only.

| Assessment area | Points |
|---|---:|
| Business problem, target, and data dictionary | 15 |
| Data validation/cleaning and leakage awareness | 15 |
| Correct algorithm/task framing | 15 |
| Held-out evaluation and metric interpretation | 20 |
| API/job/UI error states and authorization | 15 |
| Reproducibility, tests, and model limitations | 10 |
| Clear bilingual demo and Q&A | 10 |

## 4. Communication skills: bilingual practice

Each week, deliver a 60-second stand-up, a three-minute technical explanation, and a written update. In English, use short sentences, specific evidence, and clear limitations.

### A. Stand-up

**বাংলা**
> গতকাল আমি [কাজ] করেছি। আজ [পরবর্তী কাজ] করব। [বাধা/ঝুঁকি] আছে, কারণ [কারণ]। এগোতে আমার [নির্দিষ্ট সাহায্য] দরকার।

**English**
> Yesterday, I worked on [task]. Today, I will [next step]. I am blocked by [blocker] because [reason]. I need [specific help] to proceed.

### B. Explain an ML result

**বাংলা**
> মডেলটি [target] অনুমান করে [data window]-এর [feature]-গুলো ব্যবহার করে। Holdout test-এ [metric] ছিল [value]। এটি [ব্যবহারের সীমা]; ফলাফল [limitation]-এর কারণে চূড়ান্ত সিদ্ধান্ত নয়।

**English**
> The model predicts [target] from [features] over [data window]. On the held-out test set, [metric] was [value]. This is intended for [use], and it is not a final decision because of [limitation].

### C. Code review comment

**বাংলা**
> এই পরিবর্তনটি [আচরণ] উন্নত করছে। আমি [নির্দিষ্ট case] নিয়ে উদ্বিগ্ন, কারণ [প্রমাণ/কারণ]। আমরা কি [পরীক্ষাযোগ্য প্রস্তাব] যোগ করতে পারি?

**English**
> This change improves [behavior]. I am concerned about [specific case] because [evidence/reason]. Could we add [testable suggestion]?

### D. Demo structure

1. **Problem:** What is the user trying to do?
2. **Flow:** How do the UI, API, worker, and model work together?
3. **Evidence:** Which test or metric supports the result?
4. **Limitation:** Where can it fail?
5. **Next step:** What improvement or monitoring is needed?

### E. Ten-minute daily speaking drill

1. Explain one concept in Bengali for two minutes.
2. Explain it again in English for two minutes, using short sentences.
3. Answer: “What evidence supports this?”
4. State one limitation and one follow-up action.
5. Review a recording; note filler words, unclear terms, and unsupported claims, then revise.

## 5. Study workflow and self-check

For each lesson:
1. Write the user story and acceptance criteria.
2. Trace the source and draw the request/data flow.
3. Work through a small example by hand, especially the metric and split.
4. Verify behavior with a test or synthetic sample.
5. Document limitations; do not stop at “it works.”
6. Record a 60-second summary in Bengali and English.

Ask yourself:
- Is this generative inference, trained ML, clustering, or a heuristic?
- What are `X` and `y`? Will the features actually exist at prediction time?
- Where was the scaler/encoder fit? Did test data enter training/tuning?
- What changes if the dataset is small, imbalanced, stale, or biased?
- Which metric matches the business risk?
- What does the UI show on API failure, queue failure, no model, or unauthorized access?
- Is feature importance being described as causal?
- How can I explain the result to a user or reviewer in 30 seconds?

### Suggested reading order

1. Repository `README.md`
2. `docs/03-system-architecture.md`
3. `docs/12-ai-processing-architecture-v2.0.md`
4. `docs/32-ai-multi-model-workspace-architecture-v2.0.md`
5. `ML_IMPLEMENTATION_REPORT.md`—algorithms, lifecycle, limitations, and tests
6. `backend/apps/analytics/ml/` and `backend/apps/data_science/`
7. `backend/tests/unit/apps/analytics/test_ml_suite.py`
8. `frontend/src/app/tools/data-studio/` and the related API service

## 6. Known limitations to state honestly

- Churn/upgrade supervised models need enough real labelled rows and both classes; a cold-start instance may have no model. Inventing labels is not a solution.
- Prompt intent routing is currently keyword/pattern-based; calling it an embedding classifier is incorrect.
- Provider/ComfyUI models are inference dependencies, not part of the repository's classical ML training pipeline.
- K-Means is sensitive to cluster count, scaling, and initialization; cluster IDs do not encode order or business value.
- Data Studio task detection is heuristic; a numeric target is not always a regression task.
- Small test-set scores are uncertain; production release needs more real-world validation.
- Anomaly detection was considered in the report but is not implemented.
- Good model metrics alone do not prove causality, fairness, calibration, drift resistance, or business value.
