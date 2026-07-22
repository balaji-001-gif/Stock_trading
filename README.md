# BIZAXL — Investment & Wealth Platform

**Accelerate Your Growth**

BIZAXL is a comprehensive Frappe-based investment and wealth management platform covering 12 investment verticals:

| # | Vertical | Status |
|---|----------|--------|
| 1 | Mutual Funds / CIS | 🟡 In Progress |
| 2 | Portfolio Management Services (PMS) | ⬜ Planned |
| 3 | Alternative Investment Funds (AIF) | ⬜ Planned |
| 4 | Hedge Funds | ⬜ Planned |
| 5 | Private Equity | ⬜ Planned |
| 6 | Venture Capital | ⬜ Planned |
| 7 | Bonds / NCDs / Fixed Deposits | ⬜ Planned |
| 8 | Real Estate Funds / REITs / InvITs | ⬜ Planned |
| 9 | Stock Broking & Trading | ⬜ Planned |
| 10 | Family Office & Wealth Management | ⬜ Planned |
| 11 | Pension Funds / NPS | ⬜ Planned |
| 12 | Advisor Portal (RIA / MFD) | ⬜ Planned |

## Architecture

9 Core Modules across all verticals:

1. 🏛️ **Fund Configuration & Master Setup** — Fund master, share classes, series, fee config
2. 👤 **Investor Onboarding & KYC** — Digital onboarding, eKYC, risk profiling
3. 📝 **Subscription & Redemption** — Capital calls, allotment, SIP/SWP
4. 📊 **NAV Calculation Engine** — MTM valuation, dynamic ratios, accrual
5. 💰 **Fee & Income Engine** — Management fee, carry/waterfall, TDS
6. 💼 **Portfolio & Holdings Management** — Multi-asset holdings, corporate actions
7. 🛡️ **Compliance & Regulatory Reporting** — SEBI, RBI, FATCA/CRS, AML
8. 📈 **Investor Portal & Communications** — Capital accounts, SOA, e-Sign
9. 📱 **MIS, Analytics & Mobile** — Performance attribution, risk analytics, AI

## Installation

```bash
# Get the app
bench get-app https://github.com/your-org/bizaxl

# Install on your site
bench --site your-site install-app bizaxl

# Build frontend assets
bench build --app bizaxl
```

## Modules

### Investment Core
Foundation module containing master data: Fund Master, Share Class, Series Setup, Fee Structures, Regulatory Categories, Currency Settings.

### License
GNU General Public License v3
