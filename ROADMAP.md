# Coinsy Finance - Product Roadmap & Out-of-Scope Future Phases

Coinsy Finance is an LLM-powered personal finance tracker and companion application. This document outlines completed capabilities in Phase 1 as well as future product phases and out-of-scope architectural milestones.

---

## Phase 1: Core Engine & AI Companion (Completed)

- **Statement Parsing & Redaction**: Support for CSV and PDF bank statements across major Indian bank and UPI formats (HDFC, ICICI, SBI, PhonePe, Paytm), with automatic 10-18 digit account number and 16-digit card number redaction.
- **LLM Auto-Categorization & Few-Shot Learning**: Batched transaction processing via Anthropic Claude API into 9 default categories with user correction few-shot prompt memory.
- **Pandas Spend Analytics**: Weekly, monthly, and yearly category aggregations alongside Month-over-Month (MoM) and Week-over-Week (WoW) spend comparisons.
- **Predictive Insights & Batch Scheduler**: Next month spend forecasting using linear trend regression and daily tips pre-computed off the main thread via an asynchronous background scheduler.
- **Monthly Budget Goals & Threshold Alerts**: Real-time spending cap progress tracking evaluating 80% near-limit warning thresholds and 100% over-budget exceeded thresholds.
- **Interactive Recharts Dashboard & Heatmap**: Category donut charts, comparison bar charts, trend line charts, cash flow analytics (Income vs. Expense vs. Savings), and a 90-day daily spend intensity calendar heatmap.
- **Coinsy Mascot Widget**: Interactive bottom-right companion mascot featuring 6 mood states (idle, thinking, happy, concerned, sleepy, celebrating), cursor eye tracking, companion chat ("Ask Coinsy"), onboarding sequence, and "Reduce Coinsy" setting toggle.
- **Personality Layer & Spotify-Wrapped Recap**: Budget streak counter, financial mood engine (Thriving, Calm, Stressed), optional Roast Mode toggle, and shareable monthly money recap cards.

---

## Phase 2: Account Aggregator (AA) & Direct Bank/UPI Sync (Future Phase)

*Out of scope for initial release; planned for Phase 2.*

- **RBI Account Aggregator (AA) Integration**: Integration with licensed Account Aggregator networks (such as Setu, OneMoney, or Finvu) to allow users to securely link bank accounts via OTP consent.
- **Automated Live Statement Sync**: Periodic automated fetching of live bank account statements and UPI transactions without requiring manual CSV/PDF statement file uploads.
- **Multi-Bank Consolidated Balance**: Aggregating real-time account balances across multiple linked financial institutions.

---

## Phase 3: Investment Portfolio & Asset Allocation Engine (Future Phase)

*Out of scope for initial release; planned for Phase 3.*

- **Consolidated Account Statement (CAS) Import**: Parsing NSDL/CDSL mutual fund and stock holding statements.
- **Asset Allocation Tracking**: Monitoring net worth across equity, debt, NPS, mutual funds, real estate, and fixed deposits alongside monthly expenditure.
- **Portfolio Rebalancing Insights**: LLM-generated monthly asset allocation advice based on spending capacity and savings rate targets.

---

## Phase 4: Shared Expenses & Social Bill-Splitting (Future Phase)

*Out of scope for initial release; planned for Phase 4.*

- **Group Expenses & Splitwise Integration**: Ability to split bills with housemates or friends directly within Coinsy.
- **IOU Ledger & Settlement Tracking**: Tracking who owes what, automatically categorizing individual shares, and suggesting optimal settlement transfers.

---

## Phase 5: Native Mobile Applications (Future Phase)

*Out of scope for initial release; planned for Phase 5.*

- **React Native iOS & Android Apps**: Native mobile application experience featuring local biometrics (TouchID/FaceID).
- **Push Notification Engine**: Instant mobile push notifications for 80%/100% budget threshold alerts and mascot daily tips.
- **Home Screen Widget**: Native iOS & Android widgets for quick spend logging and Coinsy mood avatar display.
