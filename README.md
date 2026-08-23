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
│   │   ├── api/              # FastAPI endpoints (categories, transactions, statements)
│   │   ├── core/             # Configuration & environment settings
│   │   ├── db/               # SQLAlchemy models & database session engine
│   │   ├── models/           # Pydantic request & response validation schemas
│   │   ├── services/         # Business logic, CSV/PDF statement parsers, LLM categorizer
│   │   └── main.py           # FastAPI application entrypoint
│   ├── tests/                # Pytest unit & integration test suites
│   ├── requirements.txt      # Python dependencies
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/       # UI components & dashboard views
│   │   ├── App.jsx           # Main React component
│   │   └── index.css         # Tailwind base styles & theme tokens
│   ├── tailwind.config.js    # Custom Coinsy theme color configuration
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
- **User Preference Learning**: Stores explicit category corrections made by users and includes up to 5 recent corrections as few-shot prompt examples.
- **Heuristic Fallback**: Includes a rule-based categorization fallback when an API key is omitted.

---

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy 2.0, Alembic, SQLite, Pandas, pdfplumber, Anthropic Python SDK, Pytest
- **Frontend**: React 18, Vite, Tailwind CSS v3, Recharts, Framer Motion, Lucide React
- **Authentication**: JWT authentication groundwork

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

---

## License

This project is open source and available under the MIT License.
