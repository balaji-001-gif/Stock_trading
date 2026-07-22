# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""BIZAXL setup module — creates roles, permissions, and initial data."""

import frappe
from frappe.permissions import add_permission


BIZAXL_ROLES = [
    {
        "role_name": "Fund Manager",
        "role_type": "System",
        "desk_access": 1,
        "description": "Manages fund strategy, portfolio decisions, and model portfolios",
    },
    {
        "role_name": "Fund Accountant",
        "role_type": "System",
        "desk_access": 1,
        "description": "Handles NAV calculation, fee computation, reconciliation",
    },
    {
        "role_name": "Compliance Officer",
        "role_type": "System",
        "desk_access": 1,
        "description": "SEBI/RBI filing, KYC verification, AML review, audit trail",
    },
    {
        "role_name": "Investor Relations",
        "role_type": "System",
        "desk_access": 1,
        "description": "Investor onboarding, subscription/redemption, statements",
    },
    {
        "role_name": "Advisor (RIA/MFD)",
        "role_type": "System",
        "desk_access": 1,
        "description": "Client onboarding, goal planning, proposal generation, AUM view",
    },
    {
        "role_name": "Dealer / Trader",
        "role_type": "System",
        "desk_access": 1,
        "description": "Order placement, margin status, trade execution",
    },
    {
        "role_name": "Risk Officer",
        "role_type": "System",
        "desk_access": 1,
        "description": "Risk metrics, VaR reports, concentration risk, limit monitoring",
    },
    {
        "role_name": "Auditor",
        "role_type": "System",
        "desk_access": 1,
        "description": "Read-only access to all transactions, NAV history, fee calculations",
    },
    {
        "role_name": "Investor (Self-Service)",
        "role_type": "System",
        "desk_access": 0,
        "description": "Portal access to own portfolio, statements, tax reports",
    },
]


def after_install():
    """Hook called after app installation."""
    create_roles()
    create_custom_fields()
    create_workspaces()


def before_install():
    """Hook called before app installation."""
    pass


def create_roles():
    """Create BIZAXL-specific roles if they don't exist."""
    for role_data in BIZAXL_ROLES:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc({
                "doctype": "Role",
                **role_data,
            })
            role.insert()
            frappe.log_error(f"Role '{role_data['role_name']}' created.", "BIZAXL Setup")


def create_custom_fields():
    """Create any custom fields needed by BIZAXL."""
    # Custom fields will be added as needed by specific modules
    pass


def create_workspaces():
    """Create BIZAXL workspace pages."""
    workspaces = [
        {
            "title": "BIZAXL",
            "icon": "graph",
            "module": "Investment Core",
            "content": '<div class="workspace-bizaxl"><h3>Investment & Wealth Platform</h3></div>',
            "cards": get_workspace_cards(),
        }
    ]
    # Workspace creation happens through standard Frappe workspace DocTypes
    pass


def get_workspace_cards():
    """Return workspace cards for the BIZAXL dashboard."""
    return [
        # Module 1: Fund Configuration
        {"label": "Fund Master", "type": "Link", "link_to": "Fund Master", "doc_type": "Fund Master"},
        {"label": "Share Class", "type": "Link", "link_to": "Share Class", "doc_type": "Share Class"},
        {"label": "Fund Series", "type": "Link", "link_to": "Fund Series", "doc_type": "Fund Series"},
        {"label": "Fee Structure", "type": "Link", "link_to": "Fee Structure", "doc_type": "Fee Structure"},
        {"label": "Regulatory Category", "type": "Link", "link_to": "Regulatory Category", "doc_type": "Regulatory Category"},
        {"label": "Fund Configuration", "type": "Link", "link_to": "Fund Configuration", "doc_type": "Fund Configuration"},
        # Module 2: Investor Onboarding & KYC
        {"label": "Investor Profile", "type": "Link", "link_to": "Investor Profile", "doc_type": "Investor Profile"},
        {"label": "KYC Document", "type": "Link", "link_to": "KYC Document", "doc_type": "KYC Document"},
        {"label": "AML Screening", "type": "Link", "link_to": "AML Screening", "doc_type": "AML Screening"},
        {"label": "Risk Profile", "type": "Link", "link_to": "Risk Profile", "doc_type": "Risk Profile"},
        # Module 3: Subscription & Redemption
        {"label": "Commitment", "type": "Link", "link_to": "Commitment", "doc_type": "Commitment"},
        {"label": "Capital Call", "type": "Link", "link_to": "Capital Call", "doc_type": "Capital Call"},
        {"label": "Subscription Request", "type": "Link", "link_to": "Subscription Request", "doc_type": "Subscription Request"},
        {"label": "Allotment Detail", "type": "Link", "link_to": "Allotment Detail", "doc_type": "Allotment Detail"},
        {"label": "Redemption Request", "type": "Link", "link_to": "Redemption Request", "doc_type": "Redemption Request"},
        {"label": "SIP Plan", "type": "Link", "link_to": "SIP Plan", "doc_type": "SIP Plan"},
        {"label": "SWP Plan", "type": "Link", "link_to": "SWP Plan", "doc_type": "SWP Plan"},
        {"label": "STP Plan", "type": "Link", "link_to": "STP Plan", "doc_type": "STP Plan"},
        # Module 4: NAV Calculation Engine
        {"label": "NAV History", "type": "Link", "link_to": "NAV History", "doc_type": "NAV History"},
        {"label": "MTM Valuation", "type": "Link", "link_to": "MTM Valuation", "doc_type": "MTM Valuation"},
        {"label": "Dynamic Ratios", "type": "Link", "link_to": "Dynamic Ratios", "doc_type": "Dynamic Ratios"},
        {"label": "NAV Period", "type": "Link", "link_to": "NAV Period", "doc_type": "NAV Period"},
        {"label": "NAV Audit Trail", "type": "Link", "link_to": "NAV Audit Trail", "doc_type": "NAV Audit Trail"},
        # Module 5: Fee & Income Engine
        {"label": "Fee Accrual", "type": "Link", "link_to": "Fee Accrual", "doc_type": "Fee Accrual"},
        {"label": "Performance Fee Engine", "type": "Link", "link_to": "Performance Fee Engine", "doc_type": "Performance Fee Engine"},
        {"label": "Carried Interest Waterfall", "type": "Link", "link_to": "Carried Interest Waterfall", "doc_type": "Carried Interest Waterfall"},
        {"label": "TDS Computation", "type": "Link", "link_to": "TDS Computation", "doc_type": "TDS Computation"},
        # Module 6: Portfolio & Holdings Management
        {"label": "Holdings Register", "type": "Link", "link_to": "Holdings Register", "doc_type": "Holdings Register"},
        {"label": "Lot Tracking", "type": "Link", "link_to": "Lot Tracking", "doc_type": "Lot Tracking"},
        {"label": "Corporate Actions", "type": "Link", "link_to": "Corporate Actions", "doc_type": "Corporate Actions"},
        {"label": "P&L Attribution", "type": "Link", "link_to": "P&L Attribution", "doc_type": "P&L Attribution"},
        # Module 7: Compliance & Regulatory Reporting
        {"label": "SEBI Report", "type": "Link", "link_to": "SEBI Report", "doc_type": "SEBI Report"},
        {"label": "FATCA/CRS Filing", "type": "Link", "link_to": "FATCA/CRS Filing", "doc_type": "FATCA/CRS Filing"},
        {"label": "AML Compliance Register", "type": "Link", "link_to": "AML Compliance Register", "doc_type": "AML Compliance Register"},
        {"label": "Board Pack", "type": "Link", "link_to": "Board Pack", "doc_type": "Board Pack"},
        # Module 8: Investor Portal & Communications
        {"label": "Capital Account Statement", "type": "Link", "link_to": "Capital Account Statement", "doc_type": "Capital Account Statement"},
        {"label": "SOA/CAS", "type": "Link", "link_to": "SOA/CAS", "doc_type": "SOA/CAS"},
        {"label": "Auto Correspondence", "type": "Link", "link_to": "Auto Correspondence", "doc_type": "Auto Correspondence"},
        {"label": "e-Sign Request", "type": "Link", "link_to": "e-Sign Request", "doc_type": "e-Sign Request"},
        # Module 9: MIS, Analytics & Mobile
        {"label": "MIS Report", "type": "Link", "link_to": "MIS Report", "doc_type": "MIS Report"},
        {"label": "Performance Attribution", "type": "Link", "link_to": "Performance Attribution", "doc_type": "Performance Attribution"},
        {"label": "Risk Analytics", "type": "Link", "link_to": "Risk Analytics", "doc_type": "Risk Analytics"},
        {"label": "AI Insight", "type": "Link", "link_to": "AI Insight", "doc_type": "AI Insight"},
        # Module 10: Family Office & Wealth Management
        {"label": "Family Office Master", "type": "Link", "link_to": "Family Office Master", "doc_type": "Family Office Master"},
        {"label": "Consolidated Portfolio", "type": "Link", "link_to": "Consolidated Portfolio", "doc_type": "Consolidated Portfolio"},
        {"label": "Tax Optimization Plan", "type": "Link", "link_to": "Tax Optimization Plan", "doc_type": "Tax Optimization Plan"},
        {"label": "Succession Plan", "type": "Link", "link_to": "Succession Plan", "doc_type": "Succession Plan"},
        # Module 11: Pension Funds & NPS
        {"label": "NPS Subscriber", "type": "Link", "link_to": "NPS Subscriber", "doc_type": "NPS Subscriber"},
        {"label": "NPS Contribution", "type": "Link", "link_to": "NPS Contribution", "doc_type": "NPS Contribution"},
        {"label": "NPS Annuity Request", "type": "Link", "link_to": "NPS Annuity Request", "doc_type": "NPS Annuity Request"},
        {"label": "Pension Fund Manager", "type": "Link", "link_to": "Pension Fund Manager", "doc_type": "Pension Fund Manager"},
        # Module 12: Stock Broking & Trading
        {"label": "Trading Account", "type": "Link", "link_to": "Trading Account", "doc_type": "Trading Account"},
        {"label": "Trade Order", "type": "Link", "link_to": "Trade Order", "doc_type": "Trade Order"},
        {"label": "Contract Note", "type": "Link", "link_to": "Contract Note", "doc_type": "Contract Note"},
        {"label": "Margin Account", "type": "Link", "link_to": "Margin Account", "doc_type": "Margin Account"},
        # Module 13: Advisor Portal (RIA/MFD)
        {"label": "Advisor Profile", "type": "Link", "link_to": "Advisor Profile", "doc_type": "Advisor Profile"},
        {"label": "Client Plan", "type": "Link", "link_to": "Client Plan", "doc_type": "Client Plan"},
        {"label": "Advisor Commission", "type": "Link", "link_to": "Advisor Commission", "doc_type": "Advisor Commission"},
        {"label": "Advisor Compliance", "type": "Link", "link_to": "Advisor Compliance", "doc_type": "Advisor Compliance"},
        # Module 14: Integration Connectors (20 External APIs)
        {"label": "Integration Settings", "type": "Link", "link_to": "Integration Settings", "doc_type": "Integration Settings"},
        {"label": "eKYC Request", "type": "Link", "link_to": "eKYC Request", "doc_type": "eKYC Request"},
        {"label": "Demat Holdings Fetch", "type": "Link", "link_to": "Demat Holdings Fetch", "doc_type": "Demat Holdings Fetch"},
        {"label": "CKYC Record", "type": "Link", "link_to": "CKYC Record", "doc_type": "CKYC Record"},
        {"label": "CAS Import", "type": "Link", "link_to": "CAS Import", "doc_type": "CAS Import"},
        {"label": "Market Data Feed", "type": "Link", "link_to": "Market Data Feed", "doc_type": "Market Data Feed"},
        {"label": "MF Transaction Order", "type": "Link", "link_to": "MF Transaction Order", "doc_type": "MF Transaction Order"},
        {"label": "NPS CRA Request", "type": "Link", "link_to": "NPS CRA Request", "doc_type": "NPS CRA Request"},
        {"label": "Notification Log", "type": "Link", "link_to": "Notification Log", "doc_type": "Notification Log"},
        {"label": "Integration Request Log", "type": "Link", "link_to": "Integration Request Log", "doc_type": "Integration Request Log"},
    ]
