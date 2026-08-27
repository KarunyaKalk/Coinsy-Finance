# Coinsy Finance

Coinsy Finance is an LLM-powered personal finance tracking application that auto-categorizes bank and UPI statements, tracks spending trends, provides predictive insights, and offers a personalized companion experience guided by Coinsy, an interactive financial mascot.

---

## Technical Architecture

The project is structured as a monorepo with distinct backend and frontend services:

```
Coinsy Finance/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers (auth, analytics, budgets, categories, insights, personality, statements, transactions)
│   │   ├── core/             # Configuration, security, rate limiting, JWT auth, and background scheduler
│   │   ├── db/               # SQLAlchemy models & database session engine
│   │   ├── models/           # Pydantic request & response validation schemas
│   │   ├── services/         # Business logic, CSV/PDF parsers, LLM categorizer, analytics, insights, and mascot companion service
│   │   └── main.py           # FastAPI entrypoint with lifespan background job scheduler and health check
│   ├── tests/                # Pytest unit, integration & end-to-end user flow test suites
│   ├── Dockerfile            # Production multi-stage Docker container build
│   ├── render.yaml           # Infrastructure-as-code blueprint for Docker + Managed PostgreSQL
│   └── requirements.txt      # Python dependencies (FastAPI, SQLAlchemy, psycopg2-binary, Pandas, Anthropic)
├── frontend/
│   ├── src/
│   │   ├── api/              # Centralized Axios API client layer with Bearer token interceptors
│   │   ├── components/       # UI components, layout, guarded routes, Recharts charts, heatmap, and Coinsy widget
│   │   ├── context/          # React AuthContext for JWT state management
│   │   ├── pages/            # Application views (LoginPage, SignupPage, DashboardPage, BudgetsPage, ImportPage, SettingsPage)
│   │   ├── App.jsx           # Main React App with React Router routing
│   │   └── index.css         # Tailwind base styles and directives
│   ├── vercel.json           # Vercel SPA routing rewrite rules
│   ├── netlify.toml          # Netlify build and redirect configuration
│   ├── package.json
│   └── vite.config.js
├── .env.example              # Environment variables template
├── DEPLOYMENT.md             # Production deployment and infrastructure guide
├── ROADMAP.md                # System completion status and future phase roadmap
└── README.md
```

---

## Core Capabilities

### 1. Multi-Format Statement Import & Account Masking
- **CSV & PDF Import**: Parses statement formats across major Indian bank and UPI formats (HDFC, ICICI, SBI, PhonePe, Paytm) with table extraction via `pdfplumber`.
- **Password Protection**: Supports password-encrypted PDFs with interactive password prompt handling.
- **Account Number Redaction**: Automatically masks 10-18 digit account numbers and 16-digit card numbers prior to storage and prior to sending text to LLM prompts.
- **Data Privacy Consent**: Includes a first-import consent screen detailing statement processing policies, local parsing, and account redaction.

### 2. LLM Auto-Categorization & Few-Shot Learning
- **Batched Processing**: Groups transactions into batched prompts for the Anthropic Claude API to minimize token usage and latency.
- **Fixed Category Taxonomy**: Categorizes transactions into 9 default categories: Food, Transport, Rent, Utilities, Shopping, Entertainment, Subscriptions, Investments, and Other.
- **User Preference Learning**: Remembers explicit category corrections made by users and includes recent corrections as few-shot prompt examples.
- **Heuristic Fallback**: Includes a rule-based categorization fallback when an API key is omitted or an external API call fails.

### 3. Pandas Spend Analytics & Period Comparisons
- **Timeframe Aggregations**: Grouping and resample calculations for weekly (ISO week format), monthly, and yearly spend by category using Pandas.
- **Month-over-Month & Week-over-Week Comparisons**: Category-level and total spend comparison metrics, computing change amounts, percentage changes, and trend directions.
- **Natural Language Period Summaries**: LLM-generated executive summaries of notable spend shifts across periods.

### 4. Trend Predictions & Asynchronous Scheduler
- **Spend Forecasting**: Linear trend regression models fitted over 3 to 6 months of historical spend to forecast next month's spend per category.
- **One-Line LLM Explanation**: Concise natural language driver explanations accompanying predictions.
- **Background Job Scheduler**: Asynchronous background thread scheduler that pre-computes predictions and tips off the main HTTP thread and persists insights for instant response delivery.

### 5. Monthly Budget Goals & Threshold Alerts
- **Category Caps**: User-defined monthly spending limits per category.
- **Real-Time Threshold Evaluation**: Progress tracking evaluating 80% near-limit warning thresholds and 100% over-budget exceeded thresholds.
- **Stored Notification Triggers**: Automatic generation of stored notification records (`CoinsyMessage`) with mascot mood reactions (`concerned`, `happy`, `celebrating`).

### 6. Interactive Visualizations & Heatmaps
- **Recharts Components**: Donut charts for category distribution, grouped bar charts for period comparisons, and line charts for historical spend trends.
- **Daily Spend Intensity Heatmap**: 90-day calendar intensity grid displaying daily spend levels from 0 to 4 with interactive tooltips.
- **Cash Flow Analytics**: Multi-period Income vs. Expense vs. Net Savings charts and average savings rate calculation.

### 7. Interactive Coinsy Mascot Companion Widget
- **Six Mascot Mood States**: Animated SVG expressions for `idle`, `thinking`, `happy`, `concerned`, `sleepy`, and `celebrating`.
- **Interactive Animations**: Idle breathing, periodic blinking, mouse-tracking pupil movement, click-to-wiggle interaction, and welcome-back entry bounce animation.
- **Ask Coinsy Companion Chat**: Interactive chat panel wired to LLM companion endpoint (`POST /api/v1/insights/ask`) responding with financial advice and mascot mood reactions.
- **Onboarding Walkthrough**: Step-by-step introduction sequence guiding users through statement import and budget setup.
- **Reduce Coinsy Setting**: Toggle switch in settings to disable proactive speech bubble popups while keeping click-to-ask companion chat active.

### 8. Personality Layer & Spotify-Wrapped Style Recap
- **Budget Streak Counter**: Tracks consecutive days spent within daily budget allowances.
- **Money Mood Engine**: Calculates financial mood (Thriving, Calm, or Stressed) derived from budget status and savings rate.
- **Roast Mode Toggle**: User setting that transforms LLM tip generation into witty, lighthearted financial roasts based on actual spending habits.
- **Shareable Monthly Money Recap**: Month-end Spotify-Wrapped style recap card featuring spending personas (such as The Foodie Adventurer, The Trendsetter, or The Wealth Architect), top merchant metrics, biggest single purchase, and financial recap stories.

### 9. Production Readiness & Security
- **LLM Endpoint Rate Limiting**: In-memory rate limiter protecting LLM-calling endpoints against API quota drain (maximum 30 requests per minute).
- **Health & Monitoring**: Enhanced `GET /api/v1/health` endpoint monitoring database connectivity and background scheduler execution state.
- **Containerized Deployment**: Docker containerization with PostgreSQL database support, CORS whitelist configuration, and SPA routing manifests (`vercel.json`, `netlify.toml`, `render.yaml`).

---

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL / SQLite, Pandas, PyJWT, bcrypt, pdfplumber, Anthropic Python SDK, Pytest, Docker
- **Frontend**: React 18, Vite, Tailwind CSS v4, Recharts, Axios, React Router v6, Lucide React
- **Authentication**: JWT Bearer Token Authentication
- **Deployment**: Railway / Render (Backend + PostgreSQL), Vercel / Netlify (Frontend)

---

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

### Running Backend Tests

Run the Pytest suite from the `backend` directory:
```bash
PYTHONPATH=. pytest
```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend application will be available at `http://localhost:5173`.

4. Build for production:
   ```bash
   npm run build
   ```

---

## Deployment & Future Roadmap

- Refer to [`DEPLOYMENT.md`](file:///Users/karunya/Coinsy%20Finance/DEPLOYMENT.md) for production hosting guides on Railway, Render, Vercel, and Netlify.
- Refer to [`ROADMAP.md`](file:///Users/karunya/Coinsy%20Finance/ROADMAP.md) for out-of-scope future product phases (Account Aggregator live sync, investment portfolio tracking, social bill-splitting, native mobile app).

---

## License

This project is open source and available under the MIT License.
