# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 13 API Endpoints — Advisor Portal (RIA/MFD)."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# ADVISOR PROFILE APIs
# =============================================================================

@frappe.whitelist()
def register_new_advisor(advisor_name, registration_type, **kwargs):
    """Register a new advisor (RIA/MFD)."""
    from bizaxl.bizaxl.doctype.advisor_profile.advisor_profile import register_advisor

    return register_advisor(advisor_name, registration_type, **kwargs)


@frappe.whitelist()
def get_advisor_summary(advisor_name):
    """Get advisor dashboard with all metrics."""
    from bizaxl.bizaxl.doctype.advisor_profile.advisor_profile import get_advisor_dashboard

    return get_advisor_dashboard(advisor_name)


@frappe.whitelist()
def list_advisors():
    """List all advisors."""
    return frappe.get_all(
        "Advisor Profile",
        fields=["name", "advisor_name", "registration_type", "arn_number", "ria_number", "status", "total_aum"],
        order_by="advisor_name asc",
    )


# =============================================================================
# CLIENT PLAN APIs
# =============================================================================

@frappe.whitelist()
def create_client_financial_plan(advisor, client_name, goal_type, goal_amount, **kwargs):
    """Create a new client financial plan."""
    from bizaxl.bizaxl.doctype.client_plan.client_plan import create_client_plan

    return create_client_plan(advisor, client_name, goal_type, goal_amount, **kwargs)


@frappe.whitelist()
def get_advisor_clients(advisor):
    """Get all clients for an advisor."""
    from bizaxl.bizaxl.doctype.client_plan.client_plan import get_clients_by_advisor

    return get_clients_by_advisor(advisor)


# =============================================================================
# COMMISSION APIs
# =============================================================================

@frappe.whitelist()
def get_commission_report(advisor, from_date=None, to_date=None):
    """Get commission summary for an advisor."""
    from bizaxl.bizaxl.doctype.advisor_commission.advisor_commission import get_commission_summary

    return get_commission_summary(advisor, from_date, to_date)


@frappe.whitelist()
def get_revenue_report(advisor):
    """Get revenue dashboard with monthly breakdown."""
    from bizaxl.bizaxl.doctype.advisor_commission.advisor_commission import get_revenue_dashboard

    return get_revenue_dashboard(advisor)


@frappe.whitelist()
def record_commission(advisor, commission_type, commission_amount, **kwargs):
    """Record an advisor commission."""
    doc = frappe.get_doc({
        "doctype": "Advisor Commission",
        "advisor": advisor,
        "commission_type": commission_type,
        "commission_amount": flt(commission_amount),
        "gross_commission": flt(kwargs.get("gross_commission", commission_amount)),
        "commission_date": kwargs.get("commission_date", today()),
        "fund_master": kwargs.get("fund_master"),
        "investor": kwargs.get("investor"),
        "status": "Calculated",
    })
    doc.insert()
    return doc


# =============================================================================
# COMPLIANCE APIs
# =============================================================================

@frappe.whitelist()
def get_advisor_compliance(advisor):
    """Get compliance calendar for an advisor."""
    from bizaxl.bizaxl.doctype.advisor_compliance.advisor_compliance import (
        get_advisor_compliance_calendar,
    )

    return get_advisor_compliance_calendar(advisor)


@frappe.whitelist()
def record_advisor_compliance(advisor, compliance_type, due_date, **kwargs):
    """Record a compliance item for an advisor."""
    from bizaxl.bizaxl.doctype.advisor_compliance.advisor_compliance import record_compliance

    return record_compliance(advisor, compliance_type, due_date, **kwargs)


# =============================================================================
# CONSOLIDATED ADVISOR DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_advisor_full_dashboard(advisor_name):
    """Get comprehensive advisor portal dashboard."""
    advisor = frappe.get_doc("Advisor Profile", advisor_name)

    clients = frappe.get_all(
        "Client Plan",
        filters={"advisor": advisor_name},
        fields=["goal_type", "count(*) as count", "sum(total_invested) as total"],
        group_by="goal_type",
    )

    commissions = frappe.get_all(
        "Advisor Commission",
        filters={"advisor": advisor_name},
        fields=[
            "commission_type",
            "sum(gross_commission) as total_gross",
            "sum(net_commission) as total_net",
        ],
        group_by="commission_type",
    )

    compliance = frappe.get_all(
        "Advisor Compliance",
        filters={"advisor": advisor_name, "status": ["!=", "Completed"]},
        fields=["name", "compliance_type", "due_date", "status"],
        order_by="due_date asc",
    )

    total_aum = frappe.db.get_all(
        "Client Plan",
        filters={"advisor": advisor_name},
        fields=["sum(current_value) as total_aum"],
    )[0].total_aum or 0

    return {
        "advisor_name": advisor_name,
        "advisor_type": advisor.registration_type,
        "arn": advisor.arn_number,
        "status": advisor.status,
        "clients_by_goal": clients,
        "total_clients": sum(c["count"] for c in clients),
        "total_aum": total_aum,
        "commission_breakdown": commissions,
        "total_net_commission": sum(c["total_net"] for c in commissions),
        "pending_compliance": len(compliance),
        "compliance_items": compliance,
    }


@frappe.whitelist()
def get_advisor_activity_feed(advisor_name, limit=20):
    """Get recent activity feed for an advisor."""
    new_clients = frappe.get_all(
        "Client Plan",
        filters={"advisor": advisor_name},
        fields=["'new_client' as activity_type", "name as reference", "client_name as description", "creation as activity_date"],
        order_by="creation desc",
        limit=limit,
    )

    commissions = frappe.get_all(
        "Advisor Commission",
        filters={"advisor": advisor_name},
        fields=["'commission' as activity_type", "name as reference", "commission_type as description", "commission_date as activity_date"],
        order_by="commission_date desc",
        limit=limit,
    )

    compliance = frappe.get_all(
        "Advisor Compliance",
        filters={"advisor": advisor_name},
        fields=["'compliance' as activity_type", "name as reference", "compliance_type as description", "submission_date as activity_date"],
        order_by="submission_date desc",
        limit=limit,
    )

    activities = new_clients + commissions + compliance
    activities.sort(key=lambda x: x.get("activity_date") or "", reverse=True)
    return activities[:limit]
