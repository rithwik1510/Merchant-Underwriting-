# GrabOn Merchant Underwriting Console

An end-to-end merchant underwriting product for the GrabOn assessment, built as a phased system rather than a one-shot demo. The project starts with merchant and benchmark truth, turns that data into deterministic credit and insurance decisions, uses a local model to narrate those decisions safely, delivers outbound WhatsApp offers, and carries the merchant all the way into a realistic mock NACH mandate flow through a frontend operator console.

The goal was not to build “an AI app that guesses loans.” The goal was to build something that feels like a real internal product a company could evolve: auditable, explainable, and operationally believable.

## Product

This project was intentionally built in layers.

It began with a simple question: if GrabOn launches merchant finance products like `GrabCredit` and `GrabInsurance`, what would a credible underwriting workflow actually look like? From there, the system was shaped around one principle:

`deterministic decisions first, AI narration second`

That led to a product journey with five clear stages:

1. merchant and benchmark data become the source of truth
2. a deterministic underwriting engine computes score, tier, and offers
3. a local model explains and formats those decisions safely
4. WhatsApp becomes the outbound delivery channel
5. the merchant can accept the offer and move through a mock NACH journey

The result is not just a backend or a dashboard. It is a complete merchant-finance workflow.

## Phase Journey

### Phase 1: Foundation and Domain Truth
The first phase established the system of record.

Implemented:
- FastAPI backend scaffold
- SQLAlchemy models and Alembic migrations
- seed data for 10 named merchants
- 6 category benchmark records
- active policy version storage
- read APIs for merchants, benchmarks, and policy

Why it mattered:
- underwriting logic is only as good as the data model beneath it
- the seeded merchants are part of the product story, not fake test data
- policy versioning had to exist before scoring logic so thresholds would not get hardcoded everywhere

### Phase 2: Deterministic Underwriting Core
This phase built the real decision engine.

Implemented:
- feature engineering from merchant history
- benchmark-aware comparisons
- hard-stop rejection rules
- manual-review rules
- weighted deterministic scorecard
- tier mapping
- post-adjustment tier synchronization for offer pricing (offers now use the final tier after review/capping logic)
- credit offer generation
- insurance offer generation
- persistent underwriting runs with stored reasons and artifacts

Why it mattered:
- the system needed to produce explainable decisions without depending on prompts
- the underwriting engine had to be reproducible, testable, and auditable
- once this phase existed, the project stopped being a data viewer and became an actual financial decision system

### Phase 3: Explanation and Communication Layer
This phase added controlled AI and outbound communications.

Implemented:
- LM Studio integration through an OpenAI-compatible API
- constrained prompt payloads built from stored underwriting artifacts only
- output validation to block unsupported claims and invented numbers
- deterministic fallback templates
- persisted explanation and WhatsApp generation records
- Twilio WhatsApp sandbox send flow
- delivery status callback handling

Why it mattered:
- the brief required explainability, not just a numeric score
- AI was used to improve readability and communication, not to decide limits or tiers
- the product began to feel like a real ops workflow once it could draft and send merchant offers

### Phase 4: Offer Acceptance and Mock NACH Flow
This phase added the post-offer journey.

Implemented:
- offer acceptance persistence
- product-type aware acceptance rules
- mock NACH mandate session
- bank selection with masked data
- OTP generation and verification
- UMRN and mandate reference generation
- state-machine validation for mandate progression

Why it mattered:
- a real embedded-finance experience does not stop at underwriting
- the project needed to show what happens after the merchant says yes
- this phase made the journey operationally complete

### Phase 5: Frontend Operator Console
The final major phase turned the backend workflow into a product experience.

Implemented:
- Next.js 14 frontend with TypeScript
- white/blue/red operator-console redesign
- dark-first theme with light toggle and persisted preference
- merchant portfolio home screen
- merchant detail view with history and benchmarks
- run ledger
- unified run workspace that keeps decision, offers, communication, acceptance, and mandate in one guided page
- communication workspace with credit / insurance / combined selection, AI summary, WhatsApp draft, and direct send action
- condensed decision-insight block with deeper breakdown hidden behind expansion
- offer summary moved behind an optional collapsible section so the main workflow stays lighter
- compact microcopy pass across shell and run flow to reduce clutter
- acceptance and mandate views

Why it mattered:
- the backend was already real, so the frontend had to surface that reality cleanly
- the UI was redesigned to reduce clutter on first glance and reveal detail progressively
- the post-underwriting flow was simplified so operators do not have to jump between multiple pages just to explain and send one merchant offer
- the project became demo-ready only once the complete flow could be driven visually

## Current Product Scope

Today, the project covers the full core journey:

- inspect merchant portfolio
- inspect merchant history and benchmark posture
- run deterministic underwriting
- inspect score, tier, reasons, and offers
- generate explanation content with LM Studio
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
- LM Studio local model provider
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
- AI only explains finalized decisions and drafts communication
- if the local model fails, deterministic templates take over

### UX Design Principle
- the UI follows progressive disclosure
- the first screen stays simple and calm
- deeper operational detail appears only when the user chooses to inspect, communicate, accept, or complete mandate steps

## How the App Works

1. Merchant history and category benchmarks are loaded as source-of-truth inputs.
2. The underwriting engine computes features from those inputs.
3. Policy rules apply hard stops and manual-review logic.
4. A weighted scorecard assigns the merchant a decision and tier.
5. Credit and insurance offers are generated from deterministic formulas.
6. The run is stored with snapshots, reasons, and offer artifacts.
7. The explanation layer uses LM Studio to narrate the stored decision safely.
8. The communication layer drafts and sends an outbound WhatsApp message.
9. The merchant can accept the offer.
10. The mandate layer simulates bank selection, OTP verification, and UMRN completion.

## Seed Merchants

The project uses 10 named merchants so the demo feels coherent and not synthetic. Examples include:

- `FreshBasket Grocers` for a strong Tier 1 path
- `QuickByte Electronics` for a refund-driven rejection
- `GlowUp Beauty` for a manual-review path
- `WanderDeals Travel` for sparse-history rejection
- `TripTrail Holidays` for reduced-confidence seasonal behavior

These merchants were designed so evaluators can inspect a profile and understand why the outcome makes sense.

## Local Setup

### Backend
From [backend](C:\Users\posan\OneDrive\Desktop\Grab%20On%20project\backend):

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The backend uses a local `.env` file. Start by copying `.env.example` to `.env` and then fill in your local values.

Required local values:

```env
DATABASE_URL=sqlite:///./grabon.db
APP_ENV=development
APP_PORT=8000

LMSTUDIO_BASE_URL=http://127.0.0.1:1234
LMSTUDIO_MODEL=qwen/qwen3-8b
LLM_PROVIDER=lmstudio

APP_BASE_URL=http://127.0.0.1:8000
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_CONTENT_SID=
TWILIO_CONTENT_VARIABLES_JSON=
```

Then seed the project:

```bash
curl -X POST http://127.0.0.1:8000/api/seed/init
```

### Frontend
From [frontend/grabOn-underwriting](C:\Users\posan\OneDrive\Desktop\Grab%20On%20project\frontend\grabOn-underwriting):

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

## Quality Gate

Run the full local verification pass from the project root:

```powershell
./scripts/quality-gate.ps1
```

This runs backend tests, frontend lint, and a frontend production build.

## WhatsApp Test Run

To test the first full message flow:

1. Start LM Studio and run the local server at `http://127.0.0.1:1234`
2. Make sure your WhatsApp number has joined the Twilio sandbox
3. Start backend and frontend
4. Open the UI and choose an approved merchant such as `FreshBasket Grocers`
5. Run underwriting
6. Open the communication page
7. Generate the AI explanation
8. Generate the WhatsApp draft
9. Enter a recipient in Twilio format:

```text
whatsapp:+91XXXXXXXXXX
```

10. Click `Send`

Expected behavior:
- the draft is generated by LM Studio when available
- if LM Studio fails, deterministic fallback still produces a message
- Twilio accepts the message and returns a queued/sent state
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
- The frontend is intentionally minimal at first glance and deeper on inspection, matching how real operator tools work.
- The mandate workflow is mocked realistically enough to demonstrate product thinking without pretending to be a live bank integration.

## With More Time

If this were extended further, the next upgrades would be:

- richer operator analytics and filters
- stronger communication controls and retry tooling
- better model-side formatting and currency normalization
- screenshot assets in this README
- Loom-ready walkthrough notes embedded into the repo
- production-style auth, roles, and audit exports

## Final Note

This project was built to demonstrate more than just implementation speed. It was built to show product judgment: what to keep deterministic, where AI belongs, how to make a demo believable, and how to shape an assessment into something that feels like an actual company tool.
