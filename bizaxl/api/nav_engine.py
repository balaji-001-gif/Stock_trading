# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 4 API Endpoints — NAV Calculation Engine."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# NAV HISTORY APIs
# =============================================================================

@frappe.whitelist()
def compute_and_record_nav(fund_master, share_class, nav_value, nav_date=None):
    """Compute and record a NAV entry for a fund share class."""
    from bizaxl.bizaxl.doctype.nav_history.nav_history import calculate_nav

    return calculate_nav(fund_master, share_class, nav_date, nav_value)


@frappe.whitelist()
def get_nav_timeline(fund_master, share_class=None, from_date=None, to_date=None, limit=100):
    """Get NAV history timeline with change tracking."""
    from bizaxl.bizaxl.doctype.nav_history.nav_history import get_nav_history

    return get_nav_history(fund_master, share_class, from_date, to_date, limit)


@frappe.whitelist()
def get_nav_snapshot(fund_master, share_class):
    """Get latest NAV snapshot for a share class."""
    from bizaxl.bizaxl.doctype.nav_history.nav_history import get_latest_nav

    return get_latest_nav(fund_master, share_class)


# =============================================================================
# MTM VALUATION APIs
# =============================================================================

@frappe.whitelist()
def get_valuation_snapshot(fund_master, valuation_date=None):
    """Get portfolio MTM valuation snapshot for a given date."""
    from bizaxl.bizaxl.doctype.mtm_valuation.mtm_valuation import get_portfolio_valuation

    return get_portfolio_valuation(fund_master, valuation_date)


@frappe.whitelist()
def run_daily_valuation(fund_master, valuation_date=None):
    """Run daily MTM valuation for all active holdings in a fund."""
    from bizaxl.bizaxl.doctype.mtm_valuation.mtm_valuation import get_portfolio_valuation

    valuation_date = valuation_date or today()

    holdings = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=[
            "name", "security_id", "security_name", "security_type",
            "total_quantity", "cost_price", "market_price",
        ],
    )

    created = 0
    for h in holdings:
        existing = frappe.get_all(
            "MTM Valuation",
            filters={
                "fund_master": fund_master,
                "security_id": h["security_id"],
                "valuation_date": valuation_date,
            },
            limit=1,
        )
        if existing:
            continue

        mtm = frappe.get_doc({
            "doctype": "MTM Valuation",
            "fund_master": fund_master,
            "holding": h["name"],
            "security_id": h["security_id"],
            "security_name": h["security_name"],
            "security_type": h["security_type"],
            "quantity": h["total_quantity"],
            "market_price": flt(h["market_price"]),
            "cost_price": flt(h["cost_price"]),
            "valuation_date": valuation_date,
            "valuation_method": "Mark-to-Market",
        })
        mtm.insert()
        mtm.submit()
        created += 1

    return {
        "fund_master": fund_master,
        "valuation_date": valuation_date,
        "holdings_processed": created,
        "portfolio": get_portfolio_valuation(fund_master, valuation_date),
    }


# =============================================================================
# DYNAMIC RATIOS APIs
# =============================================================================

@frappe.whitelist()
def get_applicable_ratios(fund_master, ratio_type=None, as_on_date=None):
    """Get all active ratio configurations applicable for a fund."""
    from bizaxl.bizaxl.doctype.dynamic_ratios.dynamic_ratios import get_active_ratios

    return get_active_ratios(fund_master, ratio_type, as_on_date)


# =============================================================================
# NAV AUDIT TRAIL APIs
# =============================================================================

@frappe.whitelist()
def get_nav_audit_log(fund_master, from_date=None, to_date=None, limit=50):
    """Get NAV audit trail with before/after comparison."""
    from bizaxl.bizaxl.doctype.nav_audit_trail.nav_audit_trail import get_nav_audits

    return get_nav_audits(fund_master, from_date, to_date, limit)


@frappe.whitelist()
def get_nav_audit_summary(fund_master, from_date=None, to_date=None):
    """Get aggregated NAV audit summary with statistics."""
    audits = frappe.get_all(
        "NAV Audit Trail",
        filters={"fund_master": fund_master},
        fields=[
            "audit_type", "count(*) as count",
            "avg(ifnull(change_percentage, 0)) as avg_change",
        ],
        group_by="audit_type",
    )

    total_entries = frappe.db.count("NAV Audit Trail", filters={"fund_master": fund_master})
    pending_approvals = frappe.db.count(
        "NAV Audit Trail",
        filters={"fund_master": fund_master, "status": ["!=", "Approved"]},
    )

    return {
        "fund_master": fund_master,
        "total_audit_entries": total_entries,
        "pending_approvals": pending_approvals,
        "breakdown_by_type": audits,
    }


# =============================================================================
# NAV DASHBOARD APIs
# =============================================================================

@frappe.whitelist()
def get_nav_dashboard(fund_master):
    """Get comprehensive NAV dashboard for a fund."""
    latest_navs = frappe.get_all(
        "NAV History",
        filters={"fund_master": fund_master, "docstatus": 1},
        fields=[
            "share_class", "nav", "nav_date", "nav_change_percentage",
            "total_aum", "units_outstanding",
        ],
        order_by="nav_date desc",
        limit=1,
    )

    share_classes = frappe.get_all(
        "NAV History",
        filters={"fund_master": fund_master, "docstatus": 1},
        fields=[
            "share_class", "max(nav_date) as latest_date",
        ],
        group_by="share_class",
    )

    total_aum = sum(flt(n.get("total_aum", 0)) for n in latest_navs) if latest_navs else 0

    return {
        "fund_master": fund_master,
        "current_nav": latest_navs[0] if latest_navs else None,
        "total_aum": total_aum,
        "share_classes": share_classes,
        "nav_history": frappe.get_all(
            "NAV History",
            filters={"fund_master": fund_master, "docstatus": 1},
            fields=["nav_date", "nav", "nav_change_percentage", "total_aum"],
            order_by="nav_date desc",
            limit=30,
        ),
    }


@frappe.whitelist()
def get_nav_calendar(fund_master, month=None, year=None):
    """Get NAV calendar showing which dates have NAV calculated."""
    from datetime import date

    today_date = date.today()
    year = year or today_date.year
    month = month or today_date.month

    navs = frappe.get_all(
        "NAV History",
        filters={
            "fund_master": fund_master,
            "docstatus": 1,
            "nav_date": ["between", [date(year, month, 1), date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)]],
        },
        fields=["nav_date", "count(*) as count"],
        group_by="nav_date",
    )

    return {
        "year": year,
        "month": month,
        "nav_dates": navs,
        "total_days": len(navs),
    }
