# 🏦 **BIZAXL** — Investment & Wealth Platform

### *Accelerate Your Growth*

**Version 1.0 — Built on Frappe Framework**

BIZAXL is a complete, production-ready investment and wealth management platform covering all **12 investment verticals** active in the Indian capital markets. Built on Frappe/ERPNext, it embeds SEBI, RBI, IRDAI, and PFRDA compliance, automated fund accounting, NAV calculation, and wealth management workflows into a modern SaaS platform.

---

## 📋 **Platform Overview**

| 12 Verticals | 74+ DocTypes | 13 API Modules | 10 User Roles |
|:---:|:---:|:---:|:---:|
| All investment types | Fully modeled | Endpoints ready | Granular access |

**59 workspace cards** on the BIZAXL dashboard (6+4+8+5+4+4+4+4+4+4+4+4+4 across 13 modules)

### The 12 Investment Verticals

| # | Vertical | Core Modules Used | Key DocTypes |
|---|----------|-------------------|--------------|
| 1 | 🏦 **Mutual Funds / CIS** | 1→2→3→4→7 | Fund Master, NAV History, Subscription, SIP |
| 2 | 📊 **PMS** | 1→3→5→6→13 | Fee Structure, Holdings, Advisor Portal |
| 3 | 🏗️ **AIF (Cat I/II/III)** | 1→3→5→7 | Capital Call, Carried Interest Waterfall, SEBI Report |
| 4 | 📈 **Hedge Funds** | 3→4→5→9 | NAV History, Performance Fee, Risk Analytics |
| 5 | 💼 **Private Equity** | 1→10 | Family Office, Consolidated Portfolio, Succession Plan |
| 6 | 🚀 **Venture Capital** | 1→10 | Deal pipeline via Consolidated Portfolio |
| 7 | 📋 **Bonds / NCDs / FD** | 1→6 | Holdings Register, TDS Computation |
| 8 | 🏠 **Real Estate / REITs** | 6→10 | Consolidated Portfolio, Holdings Register |
| 9 | 📉 **Stock Broking** | **Module 12** | Trading Account, Trade Order, Contract Note, Margin |
| 10 | 👨‍👩‍👧‍👧 **Family Office** | **Module 10** | Family Office Master, Tax Optimization, Succession Plan |
| 11 | 🏦 **Pension Funds / NPS** | **Module 11** | NPS Subscriber, NPS Contribution, Annuity Request |
| 12 | 🧑‍💼 **Advisor Portal** | **Module 13** | Advisor Profile, Client Plan, Commission, Compliance |

---

## 🗺️ **End-to-End Workflows (SOP Guide)**

### 🔷 **Workflow 1: Mutual Fund Setup → Investment → NAV → Reporting**
*The complete lifecycle for a Mutual Fund / AIF / PMS structure*

```
Step 1: FUND CONFIGURATION
┌─────────────────────────────────────────────────────┐
│ Create Fund Master → Add Share Classes →            │
│ Configure Fee Structure → Set Regulatory Category   │
│ → Create Fund Configuration (links it all together) │
└─────────────────────────────────────────────────────┘
                          ↓
Step 2: INVESTOR ONBOARDING
┌─────────────────────────────────────────────────────┐
│ Create Investor Profile → Upload KYC Documents →    │
│ Run AML Screening → Complete Risk Profile           │
│ → Verify KYC (status: Verified → investor active)   │
└─────────────────────────────────────────────────────┘
                          ↓
Step 3: SUBSCRIPTION & ALLOTMENT
┌─────────────────────────────────────────────────────┐
│ Create Commitment (LP/investor capital promise) →   │
│ Issue Capital Call (drawdown %) →                   │
│ Receive Subscription Request →                      │
│ Process Allotment at applicable NAV →               │
│ Or set up SIP/SWP/STP systematic plans              │
└─────────────────────────────────────────────────────┘
                          ↓
Step 4: NAV CALCULATION (Daily/Periodic)
┌─────────────────────────────────────────────────────┐
│ Run MTM Valuation (mark holdings to market) →       │
│ Apply Dynamic Ratios (expense, accrual) →           │
│ Create NAV History entry for each share class →     │
│ System auto-creates NAV Audit Trail entry           │
│ → NAV published, Share Class updated                │
└─────────────────────────────────────────────────────┘
                          ↓
Step 5: FEE COMPUTATION
┌─────────────────────────────────────────────────────┐
│ Calculate Fee Accrual (management fee at AUM-based  │
│ rate, prorated for days) →                          │
│ Or run Performance Fee Engine (high watermark,      │
│ hurdle rate check) →                                │
│ Or run Carried Interest Waterfall (4-tier:          │
│ return capital → preferred return → GP catch-up     │
│ → LP/GP 80/20 split) →                              │
│ Compute TDS on distributions                        │
└─────────────────────────────────────────────────────┘
                          ↓
Step 6: PORTFOLIO MANAGEMENT
┌─────────────────────────────────────────────────────┐
│ Holdings Register tracks all positions (equity,     │
│ debt, gold, RE, unlisted) with lot-wise cost basis │
│ → Process Corporate Actions (bonus, split,         │
│ dividend, merger) → Sell from lots using FIFO/LIFO │
│ → P&L Attribution records realized/unrealized P&L  │
└─────────────────────────────────────────────────────┘
                          ↓
Step 7: COMPLIANCE & REPORTING
┌─────────────────────────────────────────────────────┐
│ Generate SEBI Reports (MF/AIF/PMS quarterly) →      │
│ File FATCA/CRS for foreign investors →              │
│ Track AML cases → Create Board Packs with agenda    │
│ → Monitor Compliance Calendar for deadlines         │
└─────────────────────────────────────────────────────┘
                          ↓
Step 8: INVESTOR COMMUNICATION
┌─────────────────────────────────────────────────────┐
│ Generate Capital Account Statements →               │
│ Generate SOA/CAS for consolidated view →            │
│ Dispatch Auto Correspondence (welcome letters,      │
│ NAV alerts, distribution notices via Email/SMS/WApp)│
│ → Process e-Sign Requests (agreements, KYC docs)    │
└─────────────────────────────────────────────────────┘
                          ↓
Step 9: ANALYTICS & INSIGHTS
┌─────────────────────────────────────────────────────┐
│ Run Performance Attribution (TWRR/MWRR, benchmark) →│
│ Compute Risk Analytics (Sharpe, Alpha, Beta, VaR) → │
│ Generate MIS Reports (scheduled/on-demand) →        │
│ AI Insights auto-detect concentration risk,         │
│ performance decline, tax-harvest opportunities      │
└─────────────────────────────────────────────────────┘
```

---

### 🔷 **Workflow 2: Stock Broking Operations**
*Complete trading lifecycle*

```
Create Trading Account (link to Investor Profile)
       → Activate segments (Equity, F&O, Currency, Commodity)
       → Complete KYC, IPV, RDD sign, DDPI/POA execution
       → Set exposure limits
                          ↓
Place Trade Order (Market/Limit/SL/SL-M/AMO/GTT)
       → Buy or Sell, symbol, quantity, exchange
       → Order validated, submitted, status tracking
                          ↓
Monitor Margin Account (SPAN margin, exposure margin)
       → Track MTF usage, pledged securities
       → Auto-alert if shortfall >25%, square-off >50%
                          ↓
Generate Contract Note (SEBI-compliant format)
       → Calculate: Brokerage + STT + GST(18%) + SEBI fees
         + Stamp duty → Net Payable/Receivable
       → Settlement: T+1 equity, T+2, T+7 F&O expiry
                          ↓
SEBI Compliance: Turnover reports, audit trail
```

---

### 🔷 **Workflow 3: Family Office & Wealth Management**
*Multi-generational wealth consolidation*

```
Create Family Office Master → Add Family Members
       (Individual, HUF, Trust, Company with generation tracking)
                          ↓
Add Assets to Consolidated Portfolio
       (15+ asset classes: equity, PE, MF, bonds, RE, gold,
        art, insurance, NPS, EPF — with valuation method)
                          ↓
Create Tax Optimization Plan
       (STCG/LTCG tracking, tax-loss harvesting,
        grandfathering as of Jan 31, 2018)
                          ↓
Create Succession Plan
       (Will, Trust Deed, Estate Plan with trustees,
        beneficiaries, executor, estate valuation)
                          ↓
Dashboard: Total wealth, asset allocation, generation report
```

---

### 🔷 **Workflow 4: NPS / Pension Operations**

```
Register NPS Subscriber (PRAN, Tier I/II, scheme choice)
       → Set Active/Auto lifecycle, select PFMs (E/C/G/A)
                          ↓
Record NPS Contributions (employee + employer split)
       → Allocate to schemes at per-scheme NAVs
       → Update subscriber corpus (contributions + returns)
                          ↓
Process Exit/Annuity (Partial 25%, Exit at 60, Premature, Death)
       → 60% lump sum (tax-free)/40% annuity at 60
       → 80% annuity for premature exit
       → Annuity type, ASP selection, settlement
```

---

### 🔷 **Workflow 5: Advisor Portal (RIA/MFD) Operations**

```
Register Advisor (SEBI IA/AMFI registration)
       → ARN, EUIN, NISM certification, CPE tracking
       → BSE StarMF / NSE NMF II platform codes
                          ↓
Create Client Plans (goal-based financial planning)
       → 10+ goal types (Retirement, Education, Marriage, etc.)
       → Risk profile mapping (Conservative→Aggressive)
       → Compound growth projection (6-14% return)
       → Model portfolios, SIP calculator
                          ↓
Track Advisor Commissions (Upfront, Trail, NFO, Advisory)
       → TDS deduction, net commission calculation
       → Monthly revenue breakdown dashboard
                          ↓
Advisor Compliance Calendar
       → SEBI half-yearly cert, ARN renewal, NISM renewal
       → Client suitability assessment, AML/KYC review
       → Auto-overdue detection
```

---

## 🏗️ **Architecture: 9 Core Modules + 13 API Files**

| Module | API Endpoint | Key DocTypes | API Endpoints |
|--------|-------------|--------------|---------------|
| 1. Fund Configuration | `fund_configuration.py` | Fund Master, Share Class, Fund Series, Fee Structure, Regulatory Category, Fund Configuration | `create_fund()`, `get_fund_overview()`, `list_all_funds()`, `calculate_management_fee()`, `get_fund_dashboard_data()` |
| 2. Investor Onboarding | `investor_onboarding.py` | Investor Profile, KYC Document, AML Screening, Risk Profile | `onboard_investor()`, `get_onboarding_status()`, `upload_kyc_document()`, `get_fatca_declaration()`, `get_dashboard_stats()` |
| 3. Subscription & Redemption | `subscription_redemption.py` | Subscription Request, Commitment, Capital Call, Allotment Detail, Redemption Request, SIP/SWP/STP Plan | `process_subscription_and_allot()`, `get_holdings_summary()`, `get_drawdown_status()`, `get_investor_plans()`, `get_subscription_dashboard()` |
| 4. NAV Calculation Engine | `nav_engine.py` | NAV History, MTM Valuation, Dynamic Ratios, NAV Period, NAV Audit Trail | `compute_and_record_nav()`, `get_nav_timeline()`, `run_daily_valuation()`, `get_nav_audit_log()`, `get_nav_dashboard()` |
| 5. Fee & Income Engine | `fee_engine.py` | Fee Accrual, Carried Interest Waterfall, Performance Fee Engine, TDS Computation | `accrue_monthly_fee()`, `run_waterfall()`, `crystallize_performance()`, `compute_tds_deduction()`, `get_income_dashboard()` |
| 6. Portfolio & Holdings | `portfolio_engine.py` | Holdings Register, Lot Tracking, Corporate Actions, P&L Attribution | `get_portfolio()`, `add_holding()`, `sell_from_portfolio()`, `process_corporate_action()`, `get_pnl_report()`, `get_portfolio_dashboard()` |
| 7. Compliance & Regulatory | `compliance_engine.py` | SEBI Report, FATCA/CRS Filing, AML Compliance Register, Board Pack | `get_pending_regulatory_filings()`, `get_regulatory_calendar()`, `get_aml_dashboard()`, `get_board_schedule()`, `get_compliance_dashboard()` |
| 8. Investor Portal | `investor_portal.py` | Capital Account Statement, SOA/CAS, Auto Correspondence, e-Sign Request | `get_investor_capital_statements()`, `generate_soa()`, `dispatch_notification()`, `request_esign()`, `get_investor_dashboard()` |
| 9. MIS, Analytics & Mobile | `analytics_engine.py` | MIS Report, Performance Attribution, Risk Analytics, AI Insight | `run_report()`, `run_attribution()`, `compute_risk()`, `generate_insights()`, `get_analytics_dashboard()` |
| 10. Family Office | `family_office_engine.py` | Family Office Master, Family Member (CT), Consolidated Portfolio, Tax Optimization Plan, Succession Plan | `create_family_office()`, `get_wealth_summary()`, `create_tax_plan()`, `get_succession_overview()`, `get_family_wealth_dashboard()` |
| 11. Pension Funds & NPS | `pension_engine.py` | NPS Subscriber, NPS Contribution, NPS Annuity Request, Pension Fund Manager | `register_nps_subscriber()`, `record_nps_contribution()`, `process_nps_exit()`, `list_pension_fund_managers()`, `get_nps_full_dashboard()` |
| 12. Stock Broking & Trading | `trading_engine.py` | Trading Account, Trade Order, Contract Note, Margin Account | `open_account()`, `place_trade_order()`, `generate_contract_note()`, `get_margin_overview()`, `get_trading_dashboard()` |
| 13. Advisor Portal (RIA/MFD) | `advisor_portal_engine.py` | Advisor Profile, Client Plan, Advisor Commission, Advisor Compliance | `register_new_advisor()`, `create_client_financial_plan()`, `get_commission_report()`, `get_advisor_compliance()`, `get_advisor_full_dashboard()` |

---

## 🧑‍💼 **User Roles & Access Control**

| Role | Key Access | Desk Access |
|------|-----------|:-----------:|
| **System Manager** | Full access — all modules, roles, system settings | ✅ |
| **Fund Manager** | Portfolio strategy, trade orders, model portfolios, valuation | ✅ |
| **Fund Accountant** | NAV calculation, fee computation, TDS, reconciliation | ✅ |
| **Compliance Officer** | SEBI filing, KYC/AML review, regulatory reports, audit trail | ✅ |
| **Investor Relations** | Investor onboarding, subscription/redemption, statements | ✅ |
| **Advisor (RIA/MFD)** | Own client portfolios, goal planning, proposals, commission | ✅ |
| **Dealer / Trader** | Order placement, trade confirmation, margin status | ✅ |
| **Risk Officer** | Risk metrics, VaR reports, concentration risk (read-only risk) | ✅ |
| **Auditor** | Read-only across all modules, full export capability | ✅ |
| **Investor (Self-Service)** | Own portfolio view, statements, tax reports (portal only) | ❌ |

---

## 🚀 **Installation**

### Prerequisites
- Frappe Framework v15+
- ERPNext v15+ (optional, for accounting integration)
- Python 3.10+
- Node.js 18+
- Redis, MariaDB/PostgreSQL

### Setup

```bash
# 1. Create a Frappe bench
bench init frappe-bench
cd frappe-bench

# 2. Get the BIZAXL app
bench get-app https://github.com/balaji-001-gif/Stock_trading.git
# Or if you renamed the repo:
bench get-app https://github.com/your-org/bizaxl

# 3. Create a new site
bench new-site bizaxl.site --db-root-password your-password

# 4. Install the app on your site
bench --site bizaxl.site install-app bizaxl

# 5. Build frontend assets
bench build --app bizaxl

# 6. Apply all doctypes and configurations
bench --site bizaxl.site migrate

# 7. Start the development server
bench start
```

### Post-Installation

After installation, the following is automatically set up by `setup.py`:
- **9 custom roles** created with proper permissions
- **56 workspace cards** on the BIZAXL dashboard
- All 74 DocTypes ready with their fields and validations

---

## 🧪 **Quick Start Guide (First Run)**

### 1. Set up a Fund
```
→ Open the BIZAXL workspace
→ Click "Fund Master" → Create a new fund
→ Add Share Classes (Growth/Dividend/Regular)
→ Configure Fee Structure (management fee rate)
→ Set Regulatory Category (MF/AIF/PMS)
→ Create Fund Configuration linking everything
```

### 2. Onboard an Investor
```
→ Click "Investor Profile" → Create with PAN, Aadhaar, email
→ Upload KYC Documents (PAN card, Aadhaar, etc.)
→ Run AML Screening
→ Complete Risk Profile questionnaire
→ Verify KYC → Investor is Active
```

### 3. Process a Subscription
```
→ Create a Commitment (investor's capital promise)
→ Issue a Capital Call (specify % of commitment)
→ Process Subscription Request → Allot units at NAV
→ System updates Holdings Register automatically
```

### 4. Calculate NAV
```
→ Run MTM Valuation for all holdings
→ Apply Dynamic Ratios
→ Create NAV History entry
→ System creates NAV Audit Trail automatically
```

### 5. Run Reports & Analytics
```
→ Generate Performance Attribution (TWRR/MWRR)
→ Compute Risk Analytics (Sharpe, Alpha, Beta, VaR)
→ Generate MIS Reports
→ View AI Insights for portfolio recommendations
```

---

## 📚 **API Usage Examples**

The platform provides 13 centralized API files under `bizaxl/api/`. All methods are `@frappe.whitelist()` and can be called via HTTP or from within Frappe.

### From JavaScript (Frappe Desk)
```javascript
frappe.call({
    method: "bizaxl.api.fund_configuration.create_fund",
    args: {
        fund_name: "Growth Equity Fund",
        fund_code: "GEF-001",
        fund_type: "Open-Ended",
        fund_category: "Equity"
    },
    callback: function(r) {
        console.log("Fund created:", r.message);
    }
});
```

### From Python
```python
import frappe
from bizaxl.api.nav_engine import compute_and_record_nav

nav = compute_and_record_nav(
    fund_master="GEF-001",
    share_class="Growth",
    nav_value=105.42,
    nav_date="2026-01-15"
)
```

### From REST API
```bash
curl -X POST https://bizaxl.site/api/method/bizaxl.api.investor_onboarding.onboard_investor \
  -H "Authorization: token YOUR_API_KEY:YOUR_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Rajesh",
    "pan_number": "ABCDE1234F",
    "email": "rajesh@example.com",
    "mobile_number": "9876543210",
    "investor_category": "Retail Individual"
  }'
```

---

## 🗺️ **Roadmap**

- [x] Core framework — All 13 modules with 74+ DocTypes
- [x] 13 centralized API endpoint files
- [x] 9 custom roles + workspace configuration
- [x] All 12 SEBI/PFRDA investment verticals modeled
- [x] All 20 external API integration placeholders (data models)
- [ ] Actual API connectors for the 20 external integrations
- [ ] Mobile app for investors/advisors
- [ ] Real-time market data feeds (NSE/BSE WebSocket)
- [ ] Automated NACH/UPI mandate processing
- [ ] Video KYC integration
- [ ] AI/ML structured analytics engine

---

## 📄 **License**

GNU General Public License v3

---

## 👥 **About**

Built by **bizaxl Optimisations LLP**  
*Investment Platform v1.0 · Internal Specification*

For inquiries, contributions, or support, please reach out to the bizaxl team.

---

*"Same platform handles a 10-investor seed fund and a ₹5,000Cr AUM mutual fund house — no configuration changes needed."*
