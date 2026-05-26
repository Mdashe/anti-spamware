# Email Classifier — Design Decisions

Summary of architecture and technology choices for the anti-spamware email classifier web application. Aligned with `WebApp/context/High-Level Diagram.pdf` and `WebApp/context/email_classifier_architecture.docx`.

---

## Product scope

Web application for email classification and spam detection. Users connect mail providers, view inbox, inspect emails with classifications, manage rules, and clean the mailbox. The ML classifier is **not** part of this codebase; it is consumed only via an external HTTP API.

**Classification labels (from model):** `ham`, `spam`, `suspicious`, plus a **confidence** score.

---

## Technology stack

| Layer | Choice | Notes |
|-------|--------|--------|
| Frontend | **SvelteKit** + **JavaScript** | Prefer `.js` / `.svelte` over TypeScript unless typing is needed later (e.g. JSDoc or shared OpenAPI types). |
| Backend | **Go** | REST/JSON API: auth, sessions, provider integration, rules, orchestration, model API client. |
| ML inference | **External API only** | No model training or inference in-repo. Go calls `POST /classify` and maps responses. |
| Email providers | **External APIs** | Gmail / Outlook / etc. via OAuth; normalized to internal types in Go. |
| Shared contracts | **OpenAPI or JSON Schema** | `packages/shared` — single source of truth for browser ↔ Go and internal types. |
| UI structure | **Atomic Design** | Atoms → molecules → organisms → templates → pages (see `WebApp/README.md`). |

**Principle:** Use **JavaScript wherever possible** on the client; use **Go** for everything that touches secrets, providers, or the model API. The browser **must not** call the model API directly.

---

## System boundaries

```text
SvelteKit UI  →  Go Backend API  →  Email Provider APIs (OAuth, CRUD)
                              →  Model Inference API (POST /classify)
```

The model sits **outside** the web application. Only the Go API communicates with it.

---

## Three JSON API surfaces

### 1. Browser ↔ Go (public application API)

REST/JSON for: authenticate, session, inbox list, email by id, send/delete, rules, settings, clean mailbox. Responses may include **emails + classifications** where the UI needs them.

- Auth: session cookie or JWT issued by Go after login/OAuth (choose one implementation; swimlane: Authenticate → Session).
- Example: `GET /inbox` → `{ emails: [{ id, subject, snippet, classification?: { label, confidence } }] }`.

### 2. Go ↔ Model (inference — external, not owned by this project)

```http
POST /classify
Content-Type: application/json

Request:  email content / metadata (per provider’s contract)
Response: label (ham | spam | suspicious) + confidence
```

- Go maps provider email → model request body.
- Go maps model JSON → internal `Classification` type.
- Timeouts, retries, and fallback behavior (e.g. unknown / no badge) live in Go.
- Configuration (Go only): `MODEL_API_BASE_URL`, `MODEL_API_KEY` (or equivalent).

### 3. Go ↔ Email provider

OAuth connect/refresh, list, get, send, delete. Provider-specific details stay in Go; responses are normalized to internal `Email` (and related) types before the UI or model sees them.

---

## Repository layout (target)

```text
anti-spamware/
  apps/
    web/                  # SvelteKit frontend (JavaScript)
    api/                  # Go backend API
  packages/
    shared/               # OpenAPI / JSON Schema, shared contracts
  docs/
    design-decisions.md   # this file
    architecture.md       # optional deeper architecture notes
  WebApp/
    context/              # diagrams and reference docs
    README.md             # Atomic Design reference
  infra/                  # later: docker, compose, migrations
```

`services/model-api/` from early diagrams is **external** — document URL and contract only; do not implement Python inference in this repo unless ownership changes.

---

## Responsibility split

| Concern | Go | SvelteKit |
|---------|-----|-----------|
| OAuth with mail providers | Yes | No (Connect button → redirect via Go) |
| Store refresh tokens / secrets | Yes | Never |
| Call model `POST /classify` | Yes | Never |
| Inbox, email detail, rules, settings UI | No | Yes |
| Atomic UI components | No | Yes (`lib/components/...`) |
| Session issuance / validation | Yes | Send credentials on requests to Go |

Suggested SvelteKit structure:

```text
apps/web/src/
  lib/
    api/              # fetch wrappers → Go backend only
    components/       # atoms, molecules, organisms
    stores/
    types/            # Email, User, Classification (JSDoc or generated)
  routes/
    +layout.svelte
    +page.svelte
    login/
    inbox/
    email/[id]/
    rules/
    settings/
```

---

## MVP screens and core components

**Routes (from architecture context):**

| Route | Purpose |
|-------|---------|
| `/login` | Authentication |
| `/inbox` | Email list with classifications |
| `/email/[id]` | Single email view |
| `/rules` | Rule management |
| `/settings` | Provider connect, preferences |

**Core UI components:**

- `EmailList`, `EmailPreview`, `ClassificationBadge`, `EmailToolbar`, `RuleBuilder`, `ProviderConnectButton`

**When to classify (TBD):** on list fetch (batch), on open single email, or async job — always initiated or performed by Go, not the browser.

---

## Go backend responsibilities (summary)

- REST handlers for all browser-facing endpoints.
- OAuth flows and token refresh for email providers.
- Proxy/orchestration to external model API.
- Rules engine and “clean mailbox” / run rules operations.
- Normalize provider and model payloads to shared schemas.

---

## Tooling

| Tool | Scope |
|------|--------|
| SvelteKit + Vite | Frontend (`vite.config.js`, ESLint/Prettier as needed) |
| Go modules | `apps/api` |
| OpenAPI / codegen (optional) | Keep Go structs and JS types aligned with `packages/shared` |
| Docker Compose (later) | Local `web` + `api`; model URL points to external host |

No Python in this repository’s build unless added for unrelated scripts; external model service may be Python on the vendor side.

---

## Open decisions (confirm before implementation)

1. **SvelteKit adapter:** `adapter-node` behind Go reverse proxy vs static adapter + API-only Go (affects cookies and CORS).
2. **Typing strategy:** pure JavaScript + OpenAPI docs vs JSDoc vs minimal TypeScript in `packages/shared` only.
3. **Model contract:** exact `POST /classify` request/response schema from model provider (should drive `packages/shared` first).
4. **First email provider:** Gmail vs Outlook (drives first OAuth integration in Go).
5. **Auth mechanism:** session cookie vs JWT for browser ↔ Go.

---

## Implementation discipline

When coding incrementally: change **at most one file** or **at most five lines** per step unless explicitly agreed otherwise.

---

## References

- `WebApp/context/High-Level Diagram.pdf` — swimlane: UI, Go API, provider API, model API.
- `WebApp/context/email_classifier_architecture.docx` — monorepo layout, routes, components, flow.
- `WebApp/README.md` — Atomic Design stages.
- [Atomic Design (Brad Frost)](https://atomicdesign.bradfrost.com/chapter-2/)
