# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 11 API Endpoints — Pension Funds & NPS."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# NPS SUBSCRIBER APIs
# =============================================================================

@frappe.whitelist()
def register_nps_subscriber(subscriber_name, pran_number, **kwargs):
    """Register a new NPS subscriber."""
    from bizaxl.bizaxl.doctype.nps_subscriber.nps_subscriber import register_subscriber

    return register_subscriber(subscriber_name, pran_number, **kwargs)


@frappe.whitelist()
def get_nps_subscribers(pran_number=None, subscriber_name=None):
    """Get NPS subscriber details."""
    from bizaxl.bizaxl.doctype.nps_subscriber.nps_subscriber import get_subscriber_summary

    return get_subscriber_summary(pran_number, subscriber_name)


@frappe.whitelist()
def get_nps_dashboard_stats():
    """Get NPS dashboard statistics."""
    from bizaxl.bizaxl.doctype.nps_subscriber.nps_subscriber import get_nps_dashboard

    return get_nps_dashboard()


# =============================================================================
# NPS CONTRIBUTION APIs
# =============================================================================

@frappe.whitelist()
def record_nps_contribution(nps_subscriber, contribution_date, contribution_amount, **kwargs):
    """Record an NPS contribution."""
    from bizaxl.bizaxl.doctype.nps_contribution.nps_contribution import record_contribution

    return record_contribution(nps_subscriber, contribution_date, contribution_amount, **kwargs)


@frappe.whitelist()
def get_nps_contribution_history(nps_subscriber, limit=24):
    """Get contribution history for an NPS subscriber."""
    from bizaxl.bizaxl.doctype.nps_contribution.nps_contribution import get_contribution_history

    return get_contribution_history(nps_subscriber, limit)


# =============================================================================
# NPS ANNUITY & EXIT APIs
# =============================================================================

@frappe.whitelist()
def process_nps_exit(nps_subscriber, request_type, **kwargs):
    """Process an NPS exit or withdrawal request."""
    from bizaxl.bizaxl.doctype.nps_annuity_request.nps_annuity_request import process_exit

    return process_exit(nps_subscriber, request_type, **kwargs)


@frappe.whitelist()
def get_nps_annuity_requests(nps_subscriber):
    """Get annuity/withdrawal requests for a subscriber."""
    from bizaxl.bizaxl.doctype.nps_annuity_request.nps_annuity_request import get_annuity_requests

    return get_annuity_requests(nps_subscriber)


# =============================================================================
# PENSION FUND MANAGER APIs
# =============================================================================

@frappe.whitelist()
def list_pension_fund_managers():
    """List all pension fund managers."""
    return frappe.get_all(
        "Pension Fund Manager",
        fields=["name", "pfm_name", "pfm_code", "pfm_short_name", "status"],
        order_by="pfm_name asc",
    )


@frappe.whitelist()
def create_pension_fund_manager(pfm_name, pfm_code, **kwargs):
    """Register a new pension fund manager."""
    doc = frappe.get_doc({
        "doctype": "Pension Fund Manager",
        "pfm_name": pfm_name,
        "pfm_code": pfm_code,
        "pfm_short_name": kwargs.get("pfm_short_name"),
        "status": kwargs.get("status", "Active"),
    })
    doc.insert()
    return doc


# =============================================================================
# CONSOLIDATED NPS DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_nps_full_dashboard():
    """Get comprehensive NPS dashboard with all metrics."""
    from bizaxl.bizaxl.doctype.nps_subscriber.nps_subscriber import get_nps_dashboard

    dashboard = get_nps_dashboard()

    # Breakdown by employment type
    by_employment = frappe.get_all(
        "NPS Subscriber",
        fields=["employment_type", "count(*) as count"],
        group_by="employment_type",
    )

    # Breakdown by scheme choice
    by_scheme = frappe.get_all(
        "NPS Subscriber",
        fields=["scheme_choice", "count(*) as count"],
        group_by="scheme_choice",
    )

    # Recent contributions
    recent = frappe.get_all(
        "NPS Contribution",
        filters={"docstatus": 1},
        fields=["nps_subscriber", "contribution_date", "total_contribution"],
        order_by="creation desc",
        limit=10,
    )

    # Pending annuity requests
    pending = frappe.db.count(
        "NPS Annuity Request",
        filters={"status": ["in", ("Draft", "Submitted")]},
    )

    return {
        **dashboard,
        "by_employment_type": by_employment,
        "by_scheme_choice": by_scheme,
        "recent_contributions": recent,
        "pending_annuity_requests": pending,
        "total_pfm_count": frappe.db.count("Pension Fund Manager", filters={"status": "Active"}),
    }
