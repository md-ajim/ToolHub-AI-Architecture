#!/usr/bin/env python3
"""
Generate high-resolution PNG images from Mermaid diagrams in the documentation.
Uses local mermaid.js and headless Google Chrome for crisp, accurate rendering.
Reflects the latest ToolHub-AI codebase architecture (~210k LOC, Next.js 16.4, Django 6.1,
Enterprise Observability, Hybrid Classical ML scikit-learn 1.9, Admin RBAC, and 181 routes).
"""

import os
import subprocess
import time
from PIL import Image, ImageChops

OUTPUT_DIR = "/run/media/md-ajim/Linux_Data/Repo/ToolHub-AI/docs/diagrams"
TMP_HTML_DIR = "/tmp/diagrams_html"
MERMAID_JS = "/tmp/mermaid.min.js"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_HTML_DIR, exist_ok=True)

# 1. System Topology Diagram (reflecting latest codebase)
DIAGRAM_TOPOLOGY = """flowchart TD
    subgraph ClientLayer["Client & Edge Layer"]
        UserBrowser["Modern Browser (Web Speech, Canvas, EventSource, Dark/Light Mode)"]
        CFTunnel["Cloudflare Zero-Trust Tunnel (cloudflared)"]
        UserBrowser <-->|Zero Inbound Open Ports| CFTunnel
    end

    subgraph PresentationTier["Frontend Layer (Next.js 16.4 + React 19.2 + Tailwind v4)"]
        NextApp["Next.js App Router (181 Route Definitions)"]
        Shadcn["shadcn/ui + Tailwind CSS v4"]
        FabricCanvas["Fabric.js 7 Canvas + Lena.js Filters"]
        ObservabilityUI["LLM Observability Cockpit & Admin Views"]
        CFTunnel <--> NextApp
        NextApp --- Shadcn
        NextApp --- FabricCanvas
        NextApp --- ObservabilityUI
    end

    subgraph APIGatewayTier["API Gateway & Services (Django 6.1 + DRF 3.18)"]
        GunicornWSGI["Gunicorn Multi-Worker Process Model"]
        AuthModule["SimpleJWT Auth (Rotation + Blacklist) & OAuth 2.0"]
        AIGateway["Multi-Provider AI Gateway & Auto-Router"]
        LedgerService["Idempotent Credit-Safe Transaction Ledger"]
        ObsEngine["Enterprise Observability & Trace Collector"]
        AdminEngine["Admin Panel RBAC & Audit Log Engine"]
        ToolEngine["62-Tool Dispatcher & Media Engine"]
        
        NextApp <-->|REST API + SSE Streaming /api/v1/| GunicornWSGI
        GunicornWSGI --> AuthModule
        GunicornWSGI --> AIGateway
        GunicornWSGI --> LedgerService
        GunicornWSGI --> ObsEngine
        GunicornWSGI --> AdminEngine
        GunicornWSGI --> ToolEngine
    end

    subgraph AsyncWorkerTier["Async Processing & Queuing Tier"]
        CeleryWorker["Celery 5.6 Distributed Workers"]
        CeleryBeat["Celery Beat Periodic Scheduler (Sweeps & ML Retrain)"]
        RedisBroker["Redis 7/8 (Broker, Cache, Idempotency Locks)"]
        
        GunicornWSGI <-->|Task Dispatch| RedisBroker
        RedisBroker <--> CeleryWorker
        CeleryBeat --> RedisBroker
    end

    subgraph DataStorageTier["Persistence & Media Storage"]
        PostgresDB[("PostgreSQL 15 (ACID Ledger, Traces, Metadata)")]
        StorageSystem[("Media Storage (MEDIA_ROOT, Docker volume)")]
        
        GunicornWSGI <--> PostgresDB
        CeleryWorker <--> PostgresDB
        ToolEngine <--> StorageSystem
    end

    subgraph ExternalEcosystem["External Providers & Inference Services"]
        LLMProviders["15 Provider Adapters (OpenAI, Anthropic, Google, DeepSeek, Groq, etc.)"]
        ComfyUIGPU["Local GPU Worker (ComfyUI / Stable Diffusion)"]
        HybridML["Hybrid Classical ML Engine (Pure-Python + scikit-learn 1.9)"]
        PaymentGateways["Payment Gateways (Stripe, LemonSqueezy, bKash, Nagad)"]
        
        AIGateway <-->|HTTP/REST & SSE| LLMProviders
        ToolEngine <-->|Async REST job| ComfyUIGPU
        CeleryWorker <--> HybridML
        LedgerService <-->|Verified Webhooks| PaymentGateways
    end
"""

# 2. AI Streaming & Abort Reconciliation Protocol
DIAGRAM_STREAMING = """sequenceDiagram
    autonumber
    actor User as Client (Next.js 16)
    participant GW as Django AI Gateway
    participant Ledger as Credit Ledger Service
    participant Redis as Redis Cache & Locks
    participant Provider as LLM Provider Adapter (e.g. Claude 3.5 / GPT-4o)

    User->>GW: POST /api/v1/ai-workspace/conversations/{id}/messages/ (Prompt, Stream=True)
    GW->>Ledger: Calculate estimated max cost & check user balance
    alt Insufficient Credits
        Ledger-->>GW: HTTP 402 Payment Required
        GW-->>User: Show Credit Depletion Dialog
    else Balance Sufficient
        Ledger->>Redis: Set Idempotent Lock (workspace:msg_id:attempt:1)
        Ledger->>Ledger: Reserve Estimated Credits (State: RESERVED)
        GW->>Provider: Initialize Upstream Streaming Session
        Provider-->>GW: Stream chunks received
        GW-->>User: SSE Event: meta (model, provider, latency)
        
        loop Stream Token Generation
            Provider-->>GW: Token deltas
            GW-->>User: SSE Event: delta (content_chunk)
        end

        alt User clicks 'Stop' or Connection Drops (AbortController)
            User -x GW: Connection Terminated
            GW->>Provider: Abort Upstream Request
            GW->>Ledger: Calculate exact consumed tokens vs reserved
            Ledger->>Ledger: Commit consumed tokens + Refund unconsumed tokens
            Ledger->>Redis: Release Idempotency Lock
        else Generation Completes Successfully
            Provider-->>GW: End of Stream signal (usage: prompt + completion tokens)
            GW-->>User: SSE Event: done (total_tokens, final_cost)
            GW->>Ledger: Reconcile exact tokens (Commit: USED, Refund remainder)
            Ledger->>Redis: Release Idempotency Lock
        end
    end
"""

# 3. Credit-Safe Financial Ledger Architecture
DIAGRAM_LEDGER = """flowchart TD
    StartRequest["Incoming AI / Tool Request"] --> CheckEntitlements{"Server-Side Entitlement Check"}
    
    CheckEntitlements -->|Limit Exceeded| Rejection["Reject: 402 (Credits) / 403 (Tier) / 429 (Rate)"]
    CheckEntitlements -->|Authorized| GenKey["Generate Idempotency Key: workspace:{msg}:attempt:{n}"]
    
    GenKey --> AcquireLock{"Acquire Redis Lock"}
    AcquireLock -->|Key Exists / Duplicate| Discard["Reject Duplicate Request"]
    AcquireLock -->|Lock Acquired| AtomicReserve["PostgreSQL Atomic Transaction: Reserve Estimated Credits"]
    
    AtomicReserve --> ExecuteInference["Execute Inference / Processing Pipeline"]
    
    ExecuteInference --> ResultCheck{"Inference Outcome"}
    
    ResultCheck -->|Success| ExactCalc["Calculate Actual Consumed Tokens / CPU Units"]
    ExactCalc --> SettleCommit["Commit Consumed Amount + Refund Surplus Back to Wallet"]
    
    ResultCheck -->|Provider Error / Timeout| FullRefund["Automatic full refund of reservation"]
    ResultCheck -->|Client Abort / Disconnect| PartialRefund["Settle consumed tokens, refund unconsumed balance"]
    
    SettleCommit --> LogLedger["Write Immutable Audit Record to CreditTransaction Table"]
    FullRefund --> LogLedger
    PartialRefund --> LogLedger
    LogLedger --> ReleaseLock["Release Redis Lock & Finalize"]
"""

# 4. Hybrid Classical Machine Learning Pipeline (reflecting sklearn + pure-python)
DIAGRAM_ML = """flowchart LR
    subgraph DataIngestion["Feature Pipeline (Postgres ORM)"]
        DB[("User Logs & Usage")] --> Aggregator["Bulk ORM Behavioral Aggregation"]
        Aggregator --> Features["Engineered Feature Vectors:<br/>• days_active<br/>• action_volume<br/>• distinct_tools<br/>• conversations<br/>• credits_spent<br/>• account_age_days"]
    end

    subgraph CustomMLEngine["Hybrid Classical ML Engine (Pure-Python & scikit-learn 1.9)"]
        Features --> Splitter["StandardScaler & Train/Test Split"]
        Splitter --> LinReg["Ridge Linear Regression<br/>(Gaussian Elimination / OLS)"]
        Splitter --> CART["CART Decision Tree<br/>(Multiclass Gini Impurity)"]
        Splitter --> RF["Random Forest Classifier<br/>(Bootstrap Aggregation)"]
        Splitter --> KMeans["K-Means++ Clustering<br/>(Distance-Weighted Seeding)"]
        Splitter --> SVM["Linear Support Vector Classifier"]
    end

    subgraph BusinessIntelligence["Serving APIs (/api/v1/analytics/)"]
        LinReg --> Forecast["Credit-Burn Runout Forecaster"]
        CART --> Baseline["Interpretability Baseline Tree"]
        RF --> ChurnPredict["Customer Churn & Upgrade Propensity"]
        KMeans --> Segmentation["User Cohort Segmentation"]
        SVM --> Classification["High-Intent Prompt Classifier"]
    end
"""

# 5. Interview Presentation Architecture (Bengali)
DIAGRAM_BN_ARCH = """flowchart TD
    subgraph ClientLayer ["Client Layer (Frontend)"]
        Browser["Next.js 16.4 (App Router, 181 Routes) + React 19.2"]
        CanvasUI["Fabric.js 7 + Lena.js Canvas Engine"]
        EnterpriseUI["Enterprise Observability & Admin Cockpit"]
        SSEListener["SSE Stream Consumer (EventSource / Fetch)"]
    end

    subgraph GatewayRouting ["Edge & Reverse Proxy"]
        CFTunnel["Cloudflare Tunnel (Zero Open Ports)"]
        Nginx["Next.js Reverse Proxy (/api/*, /media/*)"]
    end

    subgraph BackendCore ["Core Backend (Django 6.1 + DRF 3.18 - 32 Apps)"]
        AuthMiddleware["SimpleJWT & RBAC AdminRole Guard"]
        CreditEngine["Idempotent CreditService Ledger (0005 Idempotency)"]
        AIGateway["AI Gateway Router (15 Provider Adapters)"]
        ObsService["Enterprise Observability & Trace Collector"]
        HybridML["Hybrid ML Engine (scikit-learn 1.9 + Pure-Python)"]
    end

    subgraph AsyncAndData ["Data & Task Infrastructure"]
        Postgres[(PostgreSQL 15 - ACID Ledger & Traces)]
        RedisCache[(Redis 7/8 - Distributed Locks & Buffers)]
        CeleryWorkers["Celery 5.6 Workers + Celery Beat Scheduler"]
    end

    subgraph ExternalProviders ["AI Providers & Services"]
        LLMCloud["OpenAI / Anthropic / Google Gemini / DeepSeek / Groq"]
        ComfyUI["Local ComfyUI / Stable Diffusion"]
        PaymentGateways["Stripe / LemonSqueezy / bKash / Nagad"]
    end

    Browser --> CFTunnel
    CFTunnel --> Nginx
    Nginx --> AuthMiddleware
    AuthMiddleware --> AIGateway
    AuthMiddleware --> CreditEngine
    AuthMiddleware --> ObsService

    AIGateway --> RedisCache
    AIGateway --> LLMCloud
    CreditEngine --> Postgres
    CreditEngine --> RedisCache
    ObsService --> Postgres

    CanvasUI --> CeleryWorkers
    CeleryWorkers --> ComfyUI
    CeleryWorkers --> HybridML
    PaymentGateways --> CreditEngine
"""

# 6. Next.js 16 App Router & Defensive JWT Auth Lifecycle
DIAGRAM_JWT_AUTH = """sequenceDiagram
    autonumber
    actor User as Browser / User
    participant Client as React Client (State / Fetch)
    participant MW as Next.js 16 Proxy / Middleware
    participant Server as Next.js Server (RSC)
    participant Backend as Django REST Auth Gateway
    participant Redis as Redis Cache & Blacklist

    %% 1. LOGIN
    Note over User,Redis: 1. Authentication & Cookie Issuance
    User->>Client: Submit credentials (Email / Password / OAuth)
    Client->>Backend: POST /api/v1/auth/login/
    Backend-->>Client: 200 OK + {access, refresh, user}
    Client->>Client: Set secure, HttpOnly, SameSite cookies

    %% 2. ROUTE GUARDING
    Note over User,Redis: 2. SSR Route Guarding & Middleware
    User->>MW: Request protected route (/dashboard, /ai)
    alt Missing or Expired Token
        MW-->>User: 307 Redirect to /login?next=/dashboard
    else Valid Access Token
        MW->>Server: Forward request to Server Component
    end

    %% 3. SERVER COMPONENT DATA FETCHING
    Note over User,Redis: 3. React Server Component (RSC) Fetch
    Server->>Backend: GET /api/v1/accounts/profile/ (Bearer Access Token)
    Backend-->>Server: 200 OK + User Profile & Wallet
    Server-->>User: Stream HTML & RSC Payload

    %% 4. TOKEN ROTATION
    Note over User,Redis: 4. Token Rotation & Blacklisting
    Client->>Backend: POST /api/v1/auth/token/refresh/ (Refresh Token)
    Backend->>Redis: Check Blacklist & Revoke Old Refresh Token
    Backend-->>Client: 200 OK + New Rotated Token Pair

    %% 5. LOGOUT
    Note over User,Redis: 5. Secure Logout & Blacklisting
    User->>Client: Click 'Logout'
    Client->>Backend: POST /api/v1/auth/logout/ {refresh}
    Backend->>Redis: Blacklist Refresh Token
    Client->>Client: Clear Cookies & Session State
    Client-->>User: Redirect to /login
"""

DIAGRAMS = [
    {
        "id": "01_system_topology",
        "title": "ToolHub-AI High-Level Multi-Tier System Topology",
        "code": DIAGRAM_TOPOLOGY,
        "width": 4800,
        "height": 1800,
    },
    {
        "id": "02_ai_streaming_reconciliation",
        "title": "Multi-Provider AI Streaming & Abort Reconciliation Protocol",
        "code": DIAGRAM_STREAMING,
        "width": 2800,
        "height": 2000,
    },
    {
        "id": "03_credit_safe_ledger",
        "title": "Credit-Safe Financial Ledger Architecture (Reserve -> Stream -> Commit/Refund)",
        "code": DIAGRAM_LEDGER,
        "width": 2000,
        "height": 2200,
    },
    {
        "id": "04_pure_python_ml_pipeline",
        "title": "Hybrid Classical Machine Learning Pipeline (scikit-learn 1.9 & Pure-Python)",
        "code": DIAGRAM_ML,
        "width": 2400,
        "height": 1200,
    },
    {
        "id": "05_interview_architecture_bn",
        "title": "ToolHub-AI সিস্টেম আর্কিটেকচার (আপডেটেড ইন্টারভিউ প্রেজেন্টেশন)",
        "code": DIAGRAM_BN_ARCH,
        "width": 3800,
        "height": 1600,
    },
    {
        "id": "06_nextjs16_jwt_auth_lifecycle",
        "title": "Next.js 16 App Router & JWT Authentication Lifecycle",
        "code": DIAGRAM_JWT_AUTH,
        "width": 2800,
        "height": 2200,
    },
]

def render_diagram(item):
    diag_id = item["id"]
    title = item["title"]
    code = item["code"]
    w = item["width"]
    h = item["height"]

    html_file = os.path.join(TMP_HTML_DIR, f"{diag_id}.html")
    raw_png = os.path.join(TMP_HTML_DIR, f"{diag_id}_raw.png")
    final_png = os.path.join(OUTPUT_DIR, f"{diag_id}.png")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="file://{MERMAID_JS}"></script>
  <style>
    * {{
      box-sizing: border-box;
    }}
    body {{
      background: #f8fafc;
      margin: 0;
      padding: 40px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans Bengali", sans-serif;
      display: inline-block;
      min-width: 100%;
    }}
    .container {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
      padding: 32px;
      display: inline-block;
    }}
    .header {{
      margin-bottom: 24px;
      border-bottom: 2px solid #f1f5f9;
      padding-bottom: 16px;
    }}
    .badge {{
      display: inline-block;
      background: #eff6ff;
      color: #2563eb;
      font-size: 13px;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 8px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      border: 1px solid #bfdbfe;
    }}
    .title {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      color: #0f172a;
    }}
    .mermaid {{
      display: inline-block;
    }}
    svg {{
      max-width: none !important;
      font-family: inherit !important;
    }}
    .node rect, .node circle, .node ellipse, .node polygon, .node path {{
      stroke-width: 1.5px !important;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">ToolHub-AI Architecture Specification</div>
      <h1 class="title">{title}</h1>
    </div>
    <div class="mermaid">
{code}
    </div>
  </div>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'default',
      themeVariables: {{
        primaryColor: '#e0f2fe',
        primaryTextColor: '#0f172a',
        primaryBorderColor: '#38bdf8',
        lineColor: '#64748b',
        secondaryColor: '#f1f5f9',
        tertiaryColor: '#ffffff',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, "Noto Sans Bengali", sans-serif',
        fontSize: '15px'
      }},
      flowchart: {{
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis'
      }},
      sequence: {{
        useMaxWidth: false,
        actorMargin: 50,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35
      }}
    }});
  </script>
</body>
</html>
"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[*] Rendering {diag_id}...")
    chrome_cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={w},{h}",
        "--force-device-scale-factor=2",
        "--virtual-time-budget=4000",
        f"--screenshot={raw_png}",
        html_file
    ]

    res = subprocess.run(chrome_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] Error running chrome on {diag_id}: {res.stderr}")
        return False

    if not os.path.exists(raw_png):
        print(f"[-] Raw screenshot not created for {diag_id}")
        return False

    # Auto crop using PIL
    try:
        im = Image.open(raw_png)
        bg = Image.new(im.mode, im.size, (248, 250, 252))
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()

        if bbox:
            pad = 40
            left = max(0, bbox[0] - pad)
            top = max(0, bbox[1] - pad)
            right = min(im.width, bbox[2] + pad)
            bottom = min(im.height, bbox[3] + pad)
            cropped = im.crop((left, top, right, bottom))
            cropped.save(final_png, "PNG", optimize=True)
        else:
            im.save(final_png, "PNG", optimize=True)

        size_kb = os.path.getsize(final_png) // 1024
        print(f"[+] Saved: {final_png} ({size_kb} KB)")
        return True
    except Exception as e:
        print(f"[-] Crop failed for {diag_id}: {e}")
        return False

def main():
    print("=== Generating Diagram PNG Images for ToolHub-AI ===")
    success_count = 0
    for item in DIAGRAMS:
        if render_diagram(item):
            success_count += 1
    print(f"\nFinished: {success_count}/{len(DIAGRAMS)} diagrams successfully rendered.")

if __name__ == "__main__":
    main()
