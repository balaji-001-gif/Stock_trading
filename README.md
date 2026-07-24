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

---

## 🔌 **External API Integration Connectors — 20 APIs**

All 20 external integrations are built in **stub-to-live** mode — fully functional in simulation without credentials. Live mode activates automatically when API keys are configured via the Integration Settings DocType. No code changes required to switch between modes.

### Architecture

Each connector:
1. Inherits from `BaseConnector` (in `integrations/base_connector.py`)
2. Has `stub_*()` methods — simulated responses with realistic test data
3. Has `live_*()` methods — `NotImplementedError` until production credentials are configured
4. Logs all requests to `Integration Request Log` for audit trail
5. Is configured via `Integration Settings` DocType (`connector_name`, `api_key`, `api_secret`, `endpoint_url`)

### Centralized API Endpoints

All 20 connectors expose their functions through a single API file:
**`bizaxl/api/integration_connectors.py`** — Sections 1–22

```python
# Example: Calling a connector from Python
from bizaxl.bizaxl.integrations.uidai_ekyc import UIDAIConnector
connector = UIDAIConnector()
result = connector.send_otp("123456789012")
print(result["mode"])  # "stub" until API credentials are configured
```

```javascript
// Example: Calling from Frappe Desk
frappe.call({
    method: "bizaxl.api.integration_connectors.send_ekyc_otp",
    args: { investor: "INV-001", aadhaar_number: "123456789012" },
    callback: function(r) { console.log(r.message); }
});
```

---

### 📋 **Connector Reference (All 20 APIs)**

#### 1️⃣ UIDAI Aadhaar eKYC
**File:** `integrations/uidai_ekyc.py` | **Class:** `UIDAIConnector` | **Connector Name:** `uidai_ekyc`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `send_otp(aadhaar, consent)` | Send OTP to Aadhaar-linked mobile | eKYC Request |
| `verify_otp(txn_id, otp)` | Verify OTP & retrieve KYC data | eKYC Request |
| `verify_offline_xml(xml, share_code)` | Decrypt & verify Aadhaar Offline XML | eKYC Request |
| `get_ekyc_status(txn_id)` | Check eKYC transaction status | — |
| `get_investor_details(aadhaar)` | Get masked investor details | — |

**Stub:** OTP `123456`/`000000` always works. Returns simulated KYC data (Aarav Sharma, Priya Patel).
**Live:** Requires AUA/KUA credentials from UIDAI. Endpoint: `https://ekyc.uidai.gov.in`
**API Endpoints:** `send_ekyc_otp()`, `verify_ekyc_otp()`, `verify_offline_xml()`, `get_ekyc_request()`, `list_ekyc_requests()`

---

#### 2️⃣ NSDL/CDSL Demat
**File:** `integrations/nsdl_cdsl_demat.py` | **Class:** `DematConnector` | **Connector Name:** `nsdl_cdsl_demat`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `verify_bo_id(bo_id, dp)` | Verify BO ID format & validity | Demat Holdings Fetch |
| `fetch_holdings(bo_id, dp, as_of)` | Fetch current demat portfolio | Demat Holdings Fetch |
| `fetch_corporate_actions(bo_id, from, to)` | Get corporate action events | Corporate Actions |
| `fetch_transactions(bo_id, from, to)` | Get demat transaction history | — |

**Stub:** 12 Indian stocks with realistic ISINs and prices. NSDL (10-digit) and CDSL (16-digit) BO ID validation.
**Live:** Requires NSDL/CDSL STS API credentials (DP ID + Secret).
**API Endpoints:** `verify_demat_account()`, `fetch_demat_holdings()`, `get_demat_corporate_actions()`, `get_demat_transactions()`, `link_demat_holdings_to_portfolio()`, `list_demat_fetches()`

---

#### 3️⃣ CKYC Registry (CERSAI)
**File:** `integrations/ckyc_registry.py` | **Class:** `CKYCConnector` | **Connector Name:** `ckyc_registry`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `fetch_ckyc(pan)` | Lookup CKYC record by PAN | CKYC Record |
| `upload_ckyc(kyc_data)` | Upload KYC to central registry | CKYC Record |
| `verify_ckyc(pan)` | Check CKYC registration status | CKYC Record |
| `update_ckyc(pan, data)` | Update existing CKYC record | CKYC Record |

**Stub:** 4 pre-built CKYC records (Priya Patel/ABCDE1234F, Vikram Singh/PQRSW5678W, etc.) with full KYC details.
**Live:** Requires CKYC Registry API credentials (CERSAI registration).
**API Endpoints:** `fetch_ckyc_record()`, `upload_kyc_to_ckyc()`, `verify_ckyc_status()`, `list_ckyc_records()`

---

#### 4️⃣ CAMS / Karvy KRA
**File:** `integrations/cams_karvy_kra.py` | **Class:** `KRAConnector` | **Connector Name:** `cams_karvy_kra`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `kra_kyc_check(pan, kra)` | Verify KYC across KRA | CAS Import |
| `fetch_cas(pan, from, to)` | Get Consolidated Account Statement | CAS Import |
| `fetch_mf_transactions(pan, from, to)` | Get MF transaction history | — |
| `fetch_scheme_master(amc, cat)` | Get MF scheme master data | — |

**Stub:** 10 AMCs (SBI, HDFC, ICICI, AXIS, KOTAK, UTI, NIPPON, ADITYA, FRANKLIN, MIRAE), 15 schemes with realistic NAVs, CAS with random folio generation, 9 transaction types.
**Live:** Requires CAMS/Karvy KRA API credentials.
**API Endpoints:** `kra_kyc_check()`, `import_cas()`, `list_cas_imports()`, `fetch_mf_transactions()`, `fetch_scheme_master()`

---

#### 5️⃣ NSE / BSE Market Data
**File:** `integrations/nse_bse_market.py` | **Class:** `MarketDataConnector` | **Connector Name:** `nse_bse_market`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `get_equity_quote(symbol)` | Get real-time equity quote | Market Data Feed |
| `get_bulk_quotes(symbols)` | Get quotes for multiple symbols | Market Data Feed |
| `get_eod_data(symbol)` | Get end-of-day OHLCV data | Market Data Feed |
| `get_fo_chain(symbol)` | Get F&O options chain | — |
| `get_index_values(indices)` | Get live index values | — |
| `get_live_ticker(symbols)` | Simulated real-time ticker feed | — |

**Stub:** 20 NSE equities (RELIANCE ₹2,950, TCS ₹3,890, HDFC ₹1,680, INFY ₹1,520, etc.) with realistic prices, 6 indices with advance/decline, options chain with 11 strikes around ATM.
**Live:** Requires NSE/BSE market data feed subscription.
**API Endpoints:** `get_equity_quote()`, `get_bulk_quotes()`, `get_index_values()`, `get_fo_chain()`, `get_live_ticker()`

---

#### 6️⃣ AMFI NAV & MF Data
**File:** `integrations/amfi_nav.py` | **Class:** `NAVConnector` | **Connector Name:** `amfi_nav`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `get_daily_nav(scheme)` | Get latest NAV for scheme(s) | NAV History |
| `get_scheme_master(amc, cat)` | Search scheme master data | — |
| `get_nav_history(scheme, from, to)` | Get historical NAV data | — |
| `file_nav_to_amfi(nav_data)` | File NAV to AMFI portal | — |

**Stub:** 22 schemes across 9 AMCs with real scheme codes (119121=SBI Bluechip, 120577=HDFC Balanced, 116065=ICICI Pru Value, etc.), 365-day NAV history simulation.
**Live:** Requires AMFI data feed or direct AMC API access.
**API Endpoints:** `get_daily_nav()`, `get_nav_history()`, `get_scheme_master()`

---

#### 7️⃣ BSE StarMF / NSE NMF II
**File:** `integrations/bse_starmf_nmf.py` | **Class:** `MFPlatformConnector` | **Connector Name:** `bse_starmf_nmf`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `place_purchase(scheme, amount, type)` | Place lumpsum/SIP purchase order | MF Transaction Order |
| `place_redemption(scheme, units)` | Place redemption order | MF Transaction Order |
| `place_switch(from, to, units)` | Place switch between schemes | MF Transaction Order |
| `get_order_status(order_ref)` | Track order status | — |
| `register_sip_mandate(pan, bank, amount)` | Register SIP auto-debit mandate | — |

**Stub:** Settlement T+2 for purchase, T+3 for redemption. NACH mandate registration with UMRN.
**Live:** Requires BSE/NSE MF platform API credentials (member ID, password).
**API Endpoints:** `place_mf_purchase()`, `place_mf_redemption()`, `place_mf_switch()`, `get_mf_order_status()`, `register_sip_mandate()`, `list_mf_orders()`

---

#### 8️⃣ NSDL CRA (NPS)
**File:** `integrations/nsdl_cra_nps.py` | **Class:** `NPSCRAConnector` | **Connector Name:** `nsdl_cra_nps`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `register_pran(subscriber)` | Generate PRAN with Tier I/II | NPS CRA Request |
| `upload_contribution(sub, amount)` | Upload contribution to CRA | NPS Contribution |
| `fetch_pfm_nav(pfm)` | Get PFM scheme NAVs | Pension Fund Manager |
| `allocate_units(sub, contribution)` | Allocate units at PFM NAVs | NPS Contribution |
| `process_withdrawal(annuity)` | Process exit/annuity withdrawal | NPS Annuity Request |

**Stub:** PRAN generation (PRAN+random), 5 PFMs with realistic NAVs (SBI E=85.40, LIC E=78.60, UTI E=82.10), E/C/G/A allocation.
**Live:** Requires NSDL CRA API credentials for NPS operations.
**API Endpoints:** `register_nps_pran()`, `upload_nps_contribution()`, `fetch_pfm_nav()`, `process_nps_withdrawal()`, `list_nps_cra_requests()`

---

#### 9️⃣ NACH / UPI AutoPay
**File:** `integrations/nach_upi_autopay.py` | **Class:** `AutoPayConnector` | **Connector Name:** `nach_upi_autopay`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `register_nach_mandate(data)` | Register eNACH mandate (UMRN) | — |
| `revoke_nach_mandate(mandate_ref)` | Revoke existing mandate | — |
| `register_upi_autopay(vpa, amount)` | Register UPI AutoPay mandate | — |
| `get_mandate_status(mandate_ref)` | Check mandate status | — |
| `process_debit(mandate_ref, amount)` | Process automated debit | — |
| `get_bounce_report(from, to)` | Get bounced debit report | — |

**Stub:** eNACH generates UMRN, UPI AutoPay generates mandate_ref. Debit has 90% success rate; failed returns a bounce reason.
**Live:** Requires NPCI/NACH API credentials or bank sponsorship.
**API Endpoints:** `register_nach_mandate()`, `register_upi_autopay()`, `get_mandate_status()`, `process_auto_debit()`, `get_bounce_report()`

---

#### 1️⃣0️⃣ SMS / WhatsApp / Email Notifications
**File:** `integrations/notification_service.py` | **Class:** `NotificationConnector` | **Connector Name:** `notification_service`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `send_sms(mobile, message, template)` | Send SMS alert | Notification Log |
| `send_whatsapp(mobile, message, media)` | Send WhatsApp message | Notification Log |
| `send_email(to, subject, html)` | Send HTML email | Notification Log |
| `send_bulk(channel, recipients, template)` | Send bulk notifications | Notification Log |

**Stub:** 6 HTML email templates (OTP, Drawdown Notice, Redemption Confirmation, NAV Alert, Dividend Notice, Statement Available). Multi-channel with delivery tracking. SMS returns carrier info, WhatsApp returns read receipt.
**Live:** Requires SMS gateway, WhatsApp Business API, and SMTP/email service credentials.
**API Endpoints:** `send_notification()`, `send_bulk_notification()`, `get_notification_logs()`

---

#### 1️⃣1️⃣ AML / Sanctions Screening
**File:** `integrations/aml_screening.py` | **Class:** `AMLScreeningConnector` | **Connector Name:** `aml_screening`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `screen_pep(name, country)` | Check against PEP database | AML Screening Request |
| `screen_sanctions(name)` | Check OFAC/UN/EU sanctions | AML Screening Request |
| `full_screen(name, pan)` | Run all checks + risk score | AML Screening |
| `screen_adverse_media(name)` | Check negative news coverage | — |

**Stub:** 4 PEP records (Narendra Modi, Droupadi Murmu, Nirmala Sitharaman, Shaktikanta Das). 3 sanctions records (Dawood Ibrahim/OFAC SDN, Hafiz Saeed/UN 1267, Masood Azhar/UN 1267). Risk scoring: <25 Low, <50 Medium, <75 High, 75+ Critical. Auto-creates AML Screening + AML Compliance Register records on full screen.
**Live:** Requires World-Check, LexisNexis, or similar AML API subscription.
**API Endpoints:** `run_full_aml_screening()`, `screen_pep_only()`, `list_aml_requests()`

---

#### 1️⃣2️⃣ e-Sign / DigiLocker
**File:** `integrations/esign_digilocker.py` | **Class:** `ESignConnector` | **Connector Name:** `esign_digilocker`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `request_esign(name, aadhaar, hash, purpose)` | Request Aadhaar e-Sign | e-Sign Request |
| `verify_esign(ref, signed_hash)` | Verify signed doc authenticity | — |
| `fetch_digilocker_document(aadhaar, type)` | Fetch verified document | KYC Document |
| `get_digilocker_issued_docs(aadhaar)` | List all available documents | — |

**Stub:** 4 e-Sign providers (CDAC, NSDL e-Sign, eMudhra, CAMS). 6 DigiLocker document types (Aadhaar, PAN, DL, Voter ID, Marksheet, Vehicle Registration) with issuer info and URIs.
**Live:** Requires CDAC/NSDL e-Sign ASA/ASP registration + DigiLocker API credentials.
**API Endpoints:** `request_esign()`, `fetch_digilocker_document()`, `get_digilocker_issued_docs()`

---

#### 1️⃣3️⃣ GSTN / TAN / TDS Portal
**File:** `integrations/gstn_tds_portal.py` | **Class:** `TDSPortalConnector` | **Connector Name:** `gstn_tds_portal`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `compute_tds(amount, rate, pan, section)` | Compute TDS with surcharge+cess | TDS Filing Record |
| `file_tds_return(tan, type, fy, quarter)` | File TDS return (24Q/26Q) | TDS Filing Record |
| `generate_form_16a(tan, pan, fy, quarter)` | Issue Form 16A certificate | — |
| `verify_gstin(gstin)` | Verify GSTIN validity | — |
| `verify_tan(tan)` | Verify TAN status | — |

**Stub:** TDS calculation with surcharge (10% for >₹50L, 15% for >₹1Cr) + 4% education cess. GSTIN format validation (15 chars: XXAAAAX0000X000). TAN format validation (10 chars: AAAA00000A).
**Live:** Requires GSTN API and TRACES/TIN-NSDL credentials.
**API Endpoints:** `compute_tds()`, `file_tds_return()`, `generate_form_16a()`, `verify_gstin()`, `verify_tan()`, `list_tds_filings()`

---

#### 1️⃣4️⃣ SEBI Reporting Portal
**File:** `integrations/sebi_portal.py` | **Class:** `SEBIConnector` | **Connector Name:** `sebi_portal`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `generate_report(type, fund)` | Generate SEBI compliance report | SEBI Report |
| `submit_report(doc)` | Submit to SEBI portal | SEBI Report |
| `get_compliance_calendar(category)` | Get filing deadlines | Compliance Calendar |
| `get_annex_vi(report)` | Extract AIF Annex VI data | — |

**Stub:** 5 report types (AIF Annex VI, PMS Quarterly, REIT Periodic, MF Portfolio, IA Compliance) with realistic Indian compliance data. Each has different field structures. Compliance deadlines by regulatory category.
**Live:** Requires SEBI portal API credentials (registered intermediary login).
**API Endpoints:** `generate_sebi_report()`, `submit_sebi_report()`, `get_sebi_compliance_calendar()`, `get_sebi_annex_vi()`, `list_sebi_reports()`

---

#### 1️⃣5️⃣ Bloomberg / Refinitiv / ICRA Bond Pricing
**File:** `integrations/bloomberg_refinitiv.py` | **Class:** `BondPricingConnector` | **Connector Name:** `bloomberg_refinitiv`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `get_bond_price(isin)` | Get latest price, yield, spread | Bond Pricing Feed |
| `get_bulk_prices(isins)` | Get prices for multiple bonds | Bond Pricing Feed |
| `get_credit_rating(isin)` | Fetch credit rating & outlook | Bond Pricing Feed |
| `calculate_fi_analytics(isin, price)` | Compute YTM, duration, convexity | — |
| `search_bond_master(query)` | Search bond master database | — |

**Stub:** 10 pre-built bonds (Govt, Corporate, NCD, PSU, SDL) with realistic ISINs and AAA-to-AA+ ratings. Bloomberg source returns BGN/BVAL composite. ICRA source uses rating-based matrix pricing. Analytics include Macaulay duration, modified duration, convexity, DV01.
**Live:** Requires Bloomberg Terminal API, Refinitiv Eikon, or ICRA data feed subscription.
**API Endpoints:** `get_bond_price()`, `get_bond_analytics()`, `get_credit_rating_history()`, `fetch_bond_pricing_from_source()`, `list_bond_pricing()`

---

#### 1️⃣6️⃣ FATCA / CRS Filing
**File:** `integrations/fatca_crs_filing.py` | **Class:** `FATCAConnector` | **Connector Name:** `fatca_crs_filing`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `generate_report(type, year)` | Generate FATCA/CRS report | FATCA Filing Record |
| `generate_xml(type, year)` | Generate US FATCA XML | — |
| `submit_filing(doc)` | Submit filing to IT Department | FATCA Filing Record |

**Stub:** 3 filing types (FATCA: US accounts >$50k, CRS: foreign accounts, Form 61B: combined). Generates account pools with balance ranges. XML with schema header and reporting FI details. Returns filing token + acknowledgment reference.
**Live:** Requires Income Tax Department filing portal credentials + XML schema compliance.
**API Endpoints:** `submit_fatca_filing()`, `generate_fatca_report()`, `submit_fatca_to_income_tax()`, `generate_fatca_xml()`, `get_filing_status()`, `list_fatca_filings()`

---

#### 1️⃣7️⃣ Video KYC
**File:** `integrations/video_kyc.py` | **Class:** `VideoKYCConnector` | **Connector Name:** `video_kyc`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `get_agent_queue(status)` | Get available KYC agents | — |
| `assign_agent(name, language)` | Assign agent for video call | Video KYC Session |
| `start_session(name, pan, type)` | Start video KYC session | Video KYC Session |
| `complete_session(session_id)` | End session with verification | Video KYC Session |
| `get_session_status(session_id)` | Check session progress | — |
| `capture_frame(session_id)` | Capture live video frame | — |
| `check_liveness(frame)` | Run liveness detection | — |
| `verify_document(image, type)` | OCR and verify identity doc | — |

**Stub:** 5-agent pool (Rahul Verma, Priya Singh, Amit Kumar, etc.) with language skills (Hindi, English, Tamil, Telugu, Kannada, Marathi, Gujarati, Punjabi). 85% verification success rate. Liveness detection with depth analysis, blink detection, movement detection. Document OCR for PAN/Aadhaar/Voter ID/Driving License. Auto-updates Investor Profile KYC status on verification.
**Live:** Requires SignDesk, Jocata, or similar video KYC platform integration.
**API Endpoints:** `start_video_kyc()`, `complete_video_kyc()`, `get_agent_queue()`, `list_vkyc_sessions()`

---

#### 1️⃣8️⃣ AI / ML Analytics Engine
**File:** `integrations/ai_ml_analytics.py` | **Class:** `MLAnalyticsConnector` | **Connector Name:** `ai_ml_analytics`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `calculate_risk_metrics(port, bench, rfr)` | Sharpe, Sortino, Alpha, Beta, VaR | AI Analytics Result |
| `run_stress_test(holdings, scenarios)` | Test vs 2008, COVID, Rate Hike | AI Analytics Result |
| `find_tax_harvest_opps(holdings, value)` | Identify loss harvesting opps | AI Analytics Result |
| `recommend_rebalance(current, target)` | Detects drift > threshold | AI Analytics Result |
| `calculate_attribution(port, bench, sectors)` | Brinson-style attribution | AI Analytics Result |
| `detect_market_regime(index, days)` | Bull/bear/sideways detection | AI Analytics Result |
| `analyze_sentiment(texts, entities)` | NLP sentiment for holdings | AI Analytics Result |

**Stub:** Algorithmic calculations with realistic data. Risk metrics include up/down capture ratio, Calmar ratio. 6 stress test scenarios. 25% random tax-loss opportunity detection. Rebalancing drift threshold configuration. Market regime with golden cross/death cross signals. Creates AI Insight records automatically from analysis results.
**Live:** Requires TensorFlow/PyTorch model deployment or cloud ML service.
**API Endpoints:** `run_risk_analysis()`, `run_tax_harvest_analysis()`, `run_rebalancing_analysis()`, `run_performance_attribution()`, `run_market_regime_analysis()`, `list_ai_analyses()`

---

#### 1️⃣9️⃣ MCA21 / RoC
**File:** `integrations/mca21_roc.py` | **Class:** `MCA21Connector` | **Connector Name:** `mca21_roc`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `search_company(cin, pan, name)` | Search MCA21 company registry | — |
| `verify_director(din, pan)` | Verify DIN status & KYC | — |
| `file_mca_form(type, cin, data)` | File SH-7/PAS-3/MGT-14/CHG-1 | — |
| `get_filing_status(srn)` | Check filing by Service Request # | — |
| `get_compliance_status(cin)` | RoC compliance health check | — |
| `get_company_master_data(cin)` | Full company master data | — |
| `register_charge(cin, details)` | Register charge (CHG-1) | — |
| `get_shareholding_pattern(cin)` | Shareholding pattern from MCA | — |

**Stub:** 6 companies with realistic CINs (L67120MH1995PLC091310=Reliance, L65110MH1994PLC080123=HDFC Bank, etc.). 5 directors with DINs. 8 form types supported. SRN generation with fee calculation. RoC compliance status (annual filings, board meetings, director KYC). Shareholding pattern by category (Promoter 52%, FII 18%, DII 12%, Retail 10%, Others 8%).
**Live:** Requires MCA21 V3 API with registered DSC (Digital Signature Certificate).
**API Endpoints:** `search_mca_company()`, `verify_din()`, `file_mca_form()`, `get_mca_filing_status()`, `get_mca_company_master()`, `get_shareholding_pattern()`

---

#### 2️⃣0️⃣ SWIFT / SFTP Custodian
**File:** `integrations/swift_sftp_custodian.py` | **Class:** `CustodianConnector` | **Connector Name:** `swift_sftp_custodian`

| Method | Description | DocTypes |
|--------|-------------|----------|
| `fetch_positions(portfolio, as_of)` | MT950 position statement | Custodian Statement |
| `fetch_transactions(port, from, to)` | MT940 cash transactions | Custodian Statement |
| `fetch_cash_balance(portfolio)` | Custodian cash balance | Custodian Statement |
| `reconcile_positions(port, internal)` | Match custodian vs internal holdings | Custodian Statement |
| `reconcile_cash(port, internal_bal)` | Cash reconciliation | Custodian Statement |
| `fetch_sftp_files(path, pattern)` | List/download SFTP files | — |
| `process_mt940_message(text)` | Parse SWIFT MT940 message | — |

**Stub:** 10 security holdings (RELIANCE, HDFC Bank, Infosys, ICICI Bank, LTIMindtree, 2 govt bonds, NCD, 2 MFs) with realistic ISINs. MT940: 5-15 transactions per fetch (dividend, purchase, redemption, fee). Reconciliation with match/break detection and difference value. SFTP file listing with file types (STMT=MT940, POS=MT950, CA=Corporate Action, TC=Trade Confirm).
**Live:** Requires custodian SFTP credentials (SSH key) and SWIFT message validation setup.
**API Endpoints:** `fetch_custodian_positions()`, `fetch_custodian_transactions()`, `reconcile_custodian_positions()`, `fetch_custodian_cash()`, `list_custodian_statements()`

---

### ⚙️ **Configuration Guide**

#### Enabling a Connector

All connectors use the same configuration mechanism via the `Integration Settings` DocType:

1. **Navigate** to BIZAXL Workspace → Integration Settings
2. **Select** the connector from the list (e.g., `uidai_ekyc`)
3. **Configure** the required credentials:
   - `API Key` — Your provider-specific API key/ID
   - `API Secret` — Your provider-specific secret/token
   - `Endpoint URL` — (Optional) Override default API endpoint
   - `Environment` — Production or Staging/Test
4. **Save** — The connector automatically switches from `stub` to `live` mode

#### Checking Connector Status

```bash
# Frappe Console
bench --site bizaxl.site console
```
```python
import frappe
from bizaxl.api.integration_connectors import get_integration_dashboard
dashboard = get_integration_dashboard()
for c in dashboard["connectors"]:
    print(f"{c['connector_name']}: {c['active_mode']} ({c['connector_status']})")
```

#### Viewing Request Logs

All connector activity is logged to `Integration Request Log`:
- Method name, request/response data, timestamp
- Mode indicator (stub vs live)
- Success/failure status with error messages
- Accessible via API or workspace dashboard

---

### 🧪 **Testing Connectors in Stub Mode**

No credentials needed. Each connector produces realistic test data out of the box.

```python
# Example: Test AML screening
frappe.call({
    "method": "bizaxl.api.integration_connectors.run_full_aml_screening",
    "args": {"investor": "INV-001"},
})
# Returns: { "overall_status": "Cleared", "risk_score": 15, "risk_level": "Low", ... }
```

Key test values per connector:

| Connector | Stub Test Values |
|-----------|------------------|
| UIDAI eKYC | Valid OTP: `123456` or `000000`. Offline XML share code: `1234` |
| NSDL/CDSL | Any valid-format BO ID works (10-digit for NSDL, 16-digit for CDSL) |
| CKYC | PANs: `ABCDE1234F` (Priya Patel), `PQRSW5678W` (Vikram Singh) |
| Market Data | Symbols: `RELIANCE`, `TCS`, `HDFC`, `INFY`, `ICICIBANK`, `SBIN` |
| AMFI NAV | Scheme: `119121` (SBI Bluechip), `120577` (HDFC Balanced), `116065` (ICICI Value) |
| AML | PEP names match: `Narendra`, `Droupadi`, `Nirmala`, `Shaktikanta` |
| MCA21 | CINs: `L67120MH1995PLC091310` (Reliance), `L65110MH1994PLC080123` (HDFC Bank) |
| NACH | eNACH UMRN auto-generated, UPI AutoPay mandate_ref auto-generated |
| Video KYC | Languages: `English`, `Hindi`, `Tamil`, `Telugu` — agents auto-assigned |
| Custodian | Portfolios: any string works (e.g., `PORT-001`, `FUND-A`) |

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
- [x] All 20 external API connectors built (stub-to-live mode)
- [x] Integration Settings management and request logging
- [x] 18 supporting DocTypes for tracking integration requests
- [ ] Mobile app for investors/advisors
- [ ] Real-time market data feeds (NSE/BSE WebSocket) — live mode
- [ ] Production API credentials for all 20 connectors
- [ ] End-to-end integration testing suite

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
