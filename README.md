# Coinsy Finance

Coinsy Finance is an LLM-powered personal finance tracking application that auto-categorizes bank and UPI statements, tracks spending trends, provides predictive insights, and offers a personalized companion experience guided by Coinsy, an interactive financial mascot.

---

## Technical Architecture

The project is structured as a monorepo with distinct backend and frontend services:

```
Coinsy Finance/
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── api/              # FastAPI routers (auth, analytics, audit, budgets, categories, insights, interview_prep, jobs, personality, settings, statements, transactions)
│   │   ├── core/             # Application configuration, security, JWT auth, and background scheduler
│   │   ├── db/               # SQLAlchemy models & database session engine
│   │   ├── models/           # Pydantic request & response validation schemas
│   │   ├── services/         # Business logic, CSV/PDF parsers, LLM categorizer, analytics, insights, interview prep, settings, and audit service
│   │   └── main.py           # FastAPI application entrypoint with lifespan background job scheduler
│   ├── tests/                # Pytest unit & integration test suites
│   ├── requirements.txt      # Python dependencies
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios API client layer with Bearer token interceptors
│   │   ├── components/       # UI components, layout, guarded routes, Recharts charts, heatmap, AuditFeed, PrepPackChecklist, and Coinsy widget
│   │   ├── context/          # React AuthContext for JWT state management
│   │   ├── pages/            # Application views (LoginPage, SignupPage, DashboardPage, BudgetsPage, JobTrackerPage, ImportPage, SettingsPage)
│   │   ├── App.jsx           # Main React App with React Router routing
│   │   └── index.css         # Tailwind base styles and directives
│   ├── tailwind.config.js
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Core Capabilities

### 1. Multi-Format Statement Import
- **CSV Import**: Parses statement formats with flexible header mappings across major Indian bank and UPI formats (HDFC, ICICI, SBI, PhonePe, Paytm).
- **PDF Import**: Table extraction via `pdfplumber` with fallback to LLM-assisted raw text extraction when table grids are unformatted.
- **Password-Protected PDFs**: Detects encrypted PDFs and supports password decryption during upload.
- **Account Masking**: Redacts 10-18 digit account numbers and 16-digit card numbers prior to storage.
- **Smart Deduplication**: Prevents duplicate transaction records within matching date ranges.

### 2. LLM Auto-Categorization & Few-Shot Learning
- **Batched Processing**: Groups transactions into batched prompts for the Anthropic Claude API to minimize token usage and latency.
- **Fixed Category Taxonomy**: Categorizes transactions into 9 default categories: Food, Transport, Rent, Utilities, Shopping, Entertainment, Subscriptions, Investments, and Other.
- **User Preference Learning**: Stores explicit category corrections made by users and includes recent corrections as few-shot prompt examples.
- **Heuristic Fallback**: Includes a rule-based categorization fallback when an API key is omitted or an external API call fails.

### 3. Pandas Spend Analytics & Period Comparisons
- **Timeframe Aggregations**: Grouping and resample calculations for weekly (ISO week format), monthly, and yearly spend by category using Pandas.
- **Month-over-Month & Week-over-Week Comparisons**: Category-level and total spend comparison metrics, computing change amounts, percentage changes, and trend directions (increased, decreased, unchanged, new).
- **Natural Language Period Summaries**: LLM-generated executive summaries of notable spend shifts across periods, with rule-based fallback generation.

### 4. Trend Predictions & Background Batch Scheduler
- **Spend Forecasting**: Linear trend regression models fitted over 3 to 6 months of historical spend to forecast next month's spend per category.
- **One-Line LLM Explanation**: Concise natural language driver explanations accompanying predictions.
- **Asynchronous Scheduler**: Asynchronous background thread scheduler that pre-computes predictions and tips off the main HTTP request loop and persists insights to the database for instant response delivery.

### 5. Monthly Budget Goals & Threshold Alerts
- **Category Caps**: User-defined monthly spending limits per category.
- **Threshold Evaluation**: Real-time progress tracking evaluating 80% near-limit warning thresholds and 100% over-budget exceeded thresholds.
- **Stored Notification Triggers**: Automatic generation of stored notification records (`CoinsyMessage`) with mascot mood reactions (`concerned`, `happy`, `celebrating`).

### 6. Interactive Visualizations & Analytics
- **Recharts Components**: Donut charts for category distribution, grouped bar charts for period comparisons, and line charts for historical spend trends.
- **Timeframe View Toggles**: Header control switching queries dynamically between Weekly, Monthly, and Yearly aggregation views.
- **Daily Spend Intensity Heatmap**: 90-day calendar intensity grid displaying daily spend levels from 0 to 4 with interactive tooltips.
- **Cash Flow Analytics**: Multi-period Income vs. Expense vs. Net Savings charts and average savings rate calculation.

### 7. Personality Layer & Spotify-Wrapped Style Recap
- **Budget Streak Counter**: Tracks consecutive days spent within daily budget allowances.
- **Money Mood Engine**: Calculates financial mood (Thriving, Calm, or Stressed) derived from budget status and savings rate.
- **Roast Mode Toggle**: User setting that transforms LLM tip generation into witty, lighthearted financial roasts based on actual spending habits.
- **Shareable Monthly Money Recap**: Month-end Spotify-Wrapped style recap card featuring spending personas (such as The Foodie Adventurer, The Trendsetter, or The Wealth Architect), top merchant metrics, biggest single purchase, and financial recap stories.

### 8. Interview Prep Pack Generator & Job Application Tracker
- **Job Tracker**: Track job applications with statuses (Applied, Interview, Offered, Rejected).
- **Automated Prep Pack Action**: Action trigger enabled on any job marked with Interview status.
- **Claude AI Prep Pack Generation**: Generates technical and behavioral questions based on Job Description (JD) and candidate resume overlap and gaps, company background context, and STAR-format draft answers mapped to actual resume bullets.
- **Checkable Prep Pack UI**: Interactive prep checklist with category filters (Technical, Behavioral, STAR Answers, Company Notes), progress bars, and editable custom notes fields per item.

### 9. Central Settings, Audit Log & Graceful Failure Handling
- **Central Settings UI**: Configuration controls for scan frequency (1 hour to 24 hours), ATS score match threshold slider, daily application cap, and daily cold-email cap.
- **Platform Management**: Active and inactive toggles with credentials management for platforms (LinkedIn, Indeed, Glassdoor, Wellfound, ZipRecruiter).
- **Notification Webhooks**: Configurable Telegram bot webhook URL and alert email notification address.
- **Filterable Audit Log Activity Feed**: Transparent activity trail logging all scrape runs, resume generations, ATS score evaluations, application submissions, cold emails, and block events.
- **Graceful CAPTCHA and Block Failure Handling**: Automatic halting of automation upon hitting CAPTCHAs or platform blocks without aggressive retries, generating in-app mascot notifications and webhook alert dispatches.

### 10. App-Wide UI Polish Pass
- **Consistent Visual Hierarchy**: Refined loading states, empty state placeholders with icons, responsive grid layouts, card hover micro-animations, and status badges across all pages (Dashboard, Budgets, Job Tracker, Import, and Settings).

---

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy 2.0, Alembic, SQLite, Pandas, PyJWT, bcrypt, pdfplumber, Anthropic Python SDK, Pytest
- **Frontend**: React 18, Vite, Tailwind CSS v4, Recharts, Axios, React Router v6, Lucide React
- **Authentication**: JWT Bearer Token Authentication

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
PYTHONPATH=. pytest tests
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

## License

This project is open source and available under the MIT License.
