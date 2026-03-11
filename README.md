# GrabOn Merchant Underwriting Console

An end-to-end merchant underwriting product for the GrabOn assessment, built as a phased system rather than a one-shot demo. The system turns merchant and benchmark data into deterministic credit and insurance decisions, uses the active AI provider to explain those decisions safely, delivers outbound WhatsApp offers, and carries the merchant into a realistic mock NACH mandate flow through an operator console.

The goal was not to build "an AI app that guesses loans." The goal was to build something that feels like a real internal product a company could evolve: auditable, explainable, and operationally believable.

## Product

This project was built in layers around one principle:

`deterministic decisions first, AI narration second`

That led to a product journey with five stages:

1. merchant and benchmark data become the source of truth
2. a deterministic underwriting engine computes score, tier, and offers
3. a provider-based AI layer explains and formats those decisions safely
4. WhatsApp becomes the outbound delivery channel
5. the merchant can accept the offer and move through a mock NACH journey

## Phase Journey

### Phase 1: Foundation and Domain Truth
- FastAPI backend scaffold
- SQLAlchemy models and Alembic migrations
- seed data for 10 named merchants
- 6 category benchmark records
- active policy version storage
- read APIs for merchants, benchmarks, and policy

Why it mattered:
- underwriting logic is only as good as the data model beneath it
- the seeded merchants are part of the product story, not fake test data
- policy versioning prevents thresholds from being hardcoded everywhere

### Phase 2: Deterministic Underwriting Core
- feature engineering from merchant history
- benchmark-aware comparisons
- hard-stop rejection rules
- manual-review rules
- weighted deterministic scorecard
- tier mapping
- synchronized final-tier pricing for credit and insurance offers
- persistent underwriting runs with stored reasons and artifacts

Why it mattered:
- the system needed to produce explainable decisions without depending on prompts
- the underwriting engine had to be reproducible, testable, and auditable

### Phase 3: Explanation and Communication Layer
- LM Studio integration through an OpenAI-compatible API
- Claude integration through the Anthropic API
- backend-backed provider settings with runtime switching between LM Studio and Claude
- lightweight AI sanity check on underwriting runs using the active provider from Settings
- constrained prompt payloads built from stored underwriting artifacts only
- output validation to block unsupported claims and invented numbers
- deterministic fallback templates
- persisted explanation and WhatsApp generation records
- Twilio WhatsApp sandbox send flow
- delivery status callback handling

Why it mattered:
- the brief required explainability, not just a numeric score
- AI improves readability and communication, not financial truth

### Phase 4: Offer Acceptance and Mock NACH Flow
- offer acceptance persistence
- product-type aware acceptance rules
- mock NACH mandate session
- bank selection, OTP generation and verification
- UMRN and mandate reference generation
- state-machine validation for mandate progression

Why it mattered:
- the project needed to show what happens after the merchant says yes

### Phase 5: Frontend Operator Console
- Next.js 14 frontend with TypeScript
- merchant portfolio home screen
- merchant detail view with history and benchmarks
- run ledger and run workspace
- communication workspace with AI summary, WhatsApp draft, and direct send action
- acceptance and mandate views
- progressive-disclosure UI polish to reduce clutter

Why it mattered:
- the backend was already real, so the frontend had to surface that reality clearly

## Current Product Scope

Today, the project covers the full core journey:

- inspect merchant portfolio
- inspect merchant history and benchmark posture
- run deterministic underwriting
- inspect score, tier, reasons, and offers
- generate explanation content with the active provider
- run a lightweight AI sanity check against the deterministic packet
- generate and send WhatsApp drafts through Twilio sandbox
- inspect communication history
- accept an offer
- complete a realistic mock NACH mandate flow

## Architecture

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- SQLite for local development
- deterministic scorecard engine
- provider-based AI layer supporting LM Studio and Claude
- Twilio sandbox integration

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Framer Motion
- Recharts

### AI Design Principle
- underwriting decisions are deterministic
- AI never sets score, tier, limit, premium, or approval state
- the active provider can perform a lightweight sanity check on the deterministic packet
- AI explains finalized decisions and drafts communication using deterministic facts
- if the active provider fails, deterministic templates take over safely

## Local Setup

### Backend
From `backend`:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Copy `.env.example` to `.env`, then fill in local values:

```env
DATABASE_URL=sqlite:///./grabon.db
APP_ENV=development
APP_PORT=8000

LMSTUDIO_BASE_URL=http://127.0.0.1:1234
LMSTUDIO_MODEL=qwen/qwen3-8b
LLM_PROVIDER=lmstudio
CLAUDE_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-6
CLAUDE_BASE_URL=https://api.anthropic.com/v1

APP_BASE_URL=http://127.0.0.1:8000
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_CONTENT_SID=
TWILIO_CONTENT_VARIABLES_JSON=
```

Seed the project:

```bash
curl -X POST http://127.0.0.1:8000/api/seed/init
```

### Frontend
From `frontend/grabon-underwriting`:

```bash
npm install
npm run dev -- --port 3001
```

Frontend environment:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Copy `.env.local.example` to `.env.local` before starting the frontend.

Open:
- [http://localhost:3001](http://localhost:3001)
- [http://localhost:3001/settings](http://localhost:3001/settings)

If a stale dev session ever hides UI updates, restart the frontend cleanly or run the production server on a fresh port. The canonical development flow remains `3001`.

## LLM Provider Settings

Use [http://localhost:3001/settings](http://localhost:3001/settings) to:

- switch between `LM Studio` and `Claude`
- save a Claude API key into the backend environment
- update the active Claude or LM Studio model
- probe the active provider before generating explanations or WhatsApp drafts

How it works:

- the frontend settings page sends the configuration to backend LLM settings endpoints
- the backend writes the values into `backend/.env`
- runtime settings are reloaded immediately
- the next explanation or WhatsApp draft request uses the selected provider

Important design note:

- Claude is an alternative provider to LM Studio
- the API key is owned by the backend, not by the communication page
- the communication page only uses whichever provider is currently active

## Quality Gate

Run the full local verification pass from the project root:

```powershell
./scripts/quality-gate.ps1
```

This runs backend tests, frontend lint, and a frontend production build.

You can also probe provider connectivity before a demo:

```bash
curl -X POST http://127.0.0.1:8000/api/llm/probe \
  -H "Content-Type: application/json" \
  -d "{\"provider\":\"claude\"}"
```

For Claude, an `api_key_override` can be supplied in the probe request for one-off validation only; it is never persisted. A fake or expired Claude key should return `unauthorized`, not a server error.

## WhatsApp Test Run

To test the first full message flow:

1. Start LM Studio at `http://127.0.0.1:1234`, or configure Claude in Settings
2. Make sure your WhatsApp number has joined the Twilio sandbox
3. Start backend and frontend
4. Choose an approved merchant such as `FreshBasket Grocers`
5. Run underwriting
6. Generate the AI explanation
7. Generate the WhatsApp draft
8. Enter a recipient in Twilio format:

```text
whatsapp:+91XXXXXXXXXX
```

9. Click `Send`

Expected behavior:
- the explanation and draft are generated by the currently active provider
- if the active provider fails or violates the output contract, deterministic fallback still produces a safe result
- Twilio accepts the message and returns a queued or sent state
- communication history stores the outbound record

## Important API Endpoints

### Foundation
- `GET /api/health`
- `POST /api/seed/init`
- `GET /api/merchants`
- `GET /api/merchants/{merchant_id}`
- `GET /api/benchmarks`
- `GET /api/benchmarks/{category}`
- `GET /api/policies/active`

### Underwriting
- `POST /api/underwriting/run/{merchant_id}`
- `GET /api/underwriting/runs`
- `GET /api/underwriting/runs/{run_id}`

### Communication
- `GET /api/llm/settings`
- `PUT /api/llm/settings`
- `POST /api/llm/probe`
- `POST /api/underwriting/runs/{run_id}/explanation`
- `POST /api/underwriting/runs/{run_id}/whatsapp-draft`
- `POST /api/underwriting/runs/{run_id}/send-whatsapp`
- `POST /api/underwriting/webhooks/twilio/status`
- `GET /api/underwriting/runs/{run_id}/communications`

### Acceptance and Mandate
- `POST /api/offers/{run_id}/accept`
- `GET /api/offers/{run_id}/acceptance`
- `POST /api/mandates/{run_id}/start`
- `POST /api/mandates/{run_id}/select-bank`
- `POST /api/mandates/{run_id}/send-otp`
- `POST /api/mandates/{run_id}/verify-otp`
- `POST /api/mandates/{run_id}/complete`
- `GET /api/mandates/{run_id}`

## Why This Design

- The system is phased so each layer stays stable and understandable.
- The underwriting core is deterministic because financial decisions need repeatability.
- The AI layer is constrained because readability should improve trust, not replace logic.
- The seeded merchant dataset is treated as a product asset because the demo depends on narrative coherence.
- The frontend is intentionally minimal at first glance and deeper on inspection.
- The mandate workflow is mocked realistically enough to demonstrate product thinking without pretending to be a live bank integration.

## With More Time

The next improvements would be:

- richer operator analytics and filters
- stronger communication controls and retry tooling
- better model-side formatting and currency normalization
- screenshot assets in this README
- production-style auth, roles, and audit exports

## Final Note

This project was built to demonstrate more than just implementation speed. It was built to show product judgment: what to keep deterministic, where AI belongs, how to make a demo believable, and how to shape an assessment into something that feels like an actual company tool.
