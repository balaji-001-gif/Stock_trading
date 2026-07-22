# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 3 API Endpoints — Subscription & Redemption."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# SUBSCRIPTION APIs
# =============================================================================

@frappe.whitelist()
def process_subscription_and_allot(investor, fund_master, share_class, investment_amount, nav=None):
    """API: Complete subscription with instant allotment at given NAV."""
    from bizaxl.bizaxl.doctype.subscription_request.subscription_request import (
        create_subscription,
    )

    sub = create_subscription(investor, fund_master, share_class, investment_amount)
    sub_doc = frappe.get_doc("Subscription Request", sub.name)
    sub_doc.submit()

    if nav:
        allotment = sub_doc.process_allotment(flt(nav))
        return {
            "subscription": sub.name,
            "allotment": allotment.name,
            "units": allotment.units,
            "nav": allotment.nav,
            "amount": allotment.amount,
        }
    return {"subscription": sub.name, "status": "Pending NAV"}


@frappe.whitelist()
def get_holdings_summary(investor):
    """API: Get complete holdings summary for an investor across all funds."""
    holdings = frappe.get_all(
        "Allotment Detail",
        filters={"investor": investor, "docstatus": 1},
        fields=[
            "fund_master",
            "share_class",
            "sum(units) as total_units",
            "sum(amount) as total_cost",
        ],
        group_by="fund_master, share_class",
    )

    subscriptions = frappe.get_all(
        "Subscription Request",
        filters={"investor": investor, "docstatus": 1},
        fields=["sum(investment_amount) as total_invested"],
    )

    redemptions = frappe.get_all(
        "Redemption Request",
        filters={"investor": investor, "settlement_status": ["!=", "Cancelled"]},
        fields=["sum(redemption_amount) as total_redeemed"],
    )

    return {
        "holdings": holdings,
        "total_invested": subscriptions[0].total_invested if subscriptions else 0,
        "total_redeemed": redemptions[0].total_redeemed if redemptions else 0,
        "current_value": sum(
            flt(h["total_units"]) * 100 for h in holdings
        ),  # Placeholder - requires NAV engine
    }


# =============================================================================
# CAPITAL CALL APIs
# =============================================================================

@frappe.whitelist()
def get_drawdown_status(fund_series):
    """API: Get drawdown status for a fund series."""
    series = frappe.get_doc("Fund Series", fund_series)
    calls = frappe.get_all(
        "Capital Call",
        filters={"fund_series": fund_series},
        fields=[
            "name",
            "call_date",
            "call_percentage",
            "total_call_amount",
            "collection_rate",
            "status",
        ],
        order_by="call_date desc",
    )
    return {
        "series": series.name,
        "total_committed": series.series_corpus_committed,
        "total_called": series.total_capital_call,
        "capital_call_percentage": series.total_capital_call_percentage,
        "calls": calls,
    }


# =============================================================================
# SYSTEMATIC PLAN APIs
# =============================================================================

@frappe.whitelist()
def get_investor_plans(investor):
    """API: Get all systematic plans for an investor."""
    sips = frappe.get_all(
        "SIP Plan",
        filters={"investor": investor},
        fields=["name", "fund_master", "sip_amount", "sip_frequency", "status", "next_sip_date"],
        order_by="creation desc",
    )
    swps = frappe.get_all(
        "SWP Plan",
        filters={"investor": investor},
        fields=["name", "fund_master", "withdrawal_amount", "swp_frequency", "status"],
        order_by="creation desc",
    )
    stps = frappe.get_all(
        "STP Plan",
        filters={"investor": investor},
        fields=["name", "from_fund", "to_fund", "transfer_amount", "status"],
        order_by="creation desc",
    )
    return {"sips": sips, "swps": swps, "stps": stps}


@frappe.whitelist()
def get_subscription_dashboard():
    """API: Get subscription dashboard statistics."""
    total_subs = frappe.db.count("Subscription Request")
    pending_allotment = frappe.db.count(
        "Subscription Request", filters={"allotment_status": "Pending"}
    )
    total_investment = frappe.get_all(
        "Subscription Request",
        filters={"docstatus": 1},
        fields=["sum(investment_amount) as total"],
    )[0].total or 0

    return {
        "total_subscriptions": total_subs,
        "pending_allotment": pending_allotment,
        "total_investment_processed": total_investment,
    }
