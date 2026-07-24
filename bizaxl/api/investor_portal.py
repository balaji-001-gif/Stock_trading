# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 8 API Endpoints — Investor Portal & Communications."""

import frappe
from frappe.utils import today


# =============================================================================
# CAPITAL ACCOUNT STATEMENT APIs
# =============================================================================

@frappe.whitelist()
def get_investor_capital_statements(investor):
    """Get capital account statements for an investor."""
    from bizaxl.bizaxl.doctype.capital_account_statement.capital_account_statement import (
        get_investor_statements,
    )

    return get_investor_statements(investor)


@frappe.whitelist()
def generate_capital_statement(investor, fund_master, statement_type="Periodic", **kwargs):
    """Generate a capital account statement for an investor."""
    doc = frappe.get_doc({
        "doctype": "Capital Account Statement",
        "investor": investor,
        "fund_master": fund_master,
        "share_class": kwargs.get("share_class"),
        "statement_type": statement_type,
        "statement_date": kwargs.get("statement_date", today()),
        "period_start": kwargs.get("period_start"),
        "period_end": kwargs.get("period_end"),
        "opening_capital": kwargs.get("opening_capital", 0),
        "contributions": kwargs.get("contributions", 0),
        "distributions": kwargs.get("distributions", 0),
        "status": "Draft",
    })
    doc.insert()
    doc.submit()
    return doc


# =============================================================================
# SOA/CAS APIs
# =============================================================================

@frappe.whitelist()
def get_investor_soa(investor):
    """Get SOA/CAS statements for an investor."""
    from bizaxl.bizaxl.doctype.soa_cas.soa_cas import get_investor_soa_statements

    return get_investor_soa_statements(investor)


@frappe.whitelist()
def generate_soa(investor, fund_master, statement_type="SOA", **kwargs):
    """Generate a Statement of Account / CAS for an investor."""
    doc = frappe.get_doc({
        "doctype": "SOA CAS",
        "investor": investor,
        "fund_master": fund_master,
        "statement_type": statement_type,
        "statement_date": kwargs.get("statement_date", today()),
        "period_from": kwargs.get("period_from"),
        "period_to": kwargs.get("period_to"),
        "status": "Draft",
        "delivery_method": kwargs.get("delivery_method", "Email"),
    })
    doc.insert()
    doc.submit()
    return doc


@frappe.whitelist()
def get_investor_portfolio_summary(investor):
    """Get consolidated portfolio summary for investor portal."""
    # Holdings from Allotment Detail
    holdings = frappe.get_all(
        "Allotment Detail",
        filters={"investor": investor, "docstatus": 1},
        fields=[
            "fund_master", "share_class", "sum(units) as total_units",
            "sum(amount) as total_cost",
        ],
        group_by="fund_master, share_class",
    )

    # Capital account statements
    statements = frappe.get_all(
        "Capital Account Statement",
        filters={"investor": investor},
        fields=["name", "fund_master", "statement_date", "closing_capital", "return_percentage"],
        order_by="statement_date desc",
        limit=5,
    )

    # Recent correspondence
    correspondence = frappe.get_all(
        "Auto Correspondence",
        filters={"investor": investor},
        fields=["name", "correspondence_type", "subject", "sent_date", "status"],
        order_by="sent_date desc",
        limit=10,
    )

    return {
        "investor": investor,
        "holdings": holdings,
        "total_invested": sum(h.get("total_cost", 0) or 0 for h in holdings),
        "recent_statements": statements,
        "recent_correspondence": correspondence,
    }


# =============================================================================
# AUTO CORRESPONDENCE APIs
# =============================================================================

@frappe.whitelist()
def dispatch_notification(correspondence_name):
    """Dispatch a correspondence to the investor."""
    from bizaxl.bizaxl.doctype.auto_correspondence.auto_correspondence import (
        dispatch_correspondence,
    )

    return dispatch_correspondence(correspondence_name)


@frappe.whitelist()
def get_investor_messages(investor, limit=20):
    """Get recent correspondence for an investor."""
    from bizaxl.bizaxl.doctype.auto_correspondence.auto_correspondence import (
        get_investor_correspondence,
    )

    return get_investor_correspondence(investor, limit)


@frappe.whitelist()
def get_pending_notifications():
    """Get all pending correspondence awaiting dispatch."""
    from bizaxl.bizaxl.doctype.auto_correspondence.auto_correspondence import (
        get_pending_correspondence,
    )

    return get_pending_correspondence()


@frappe.whitelist()
def send_investor_notification(investor, correspondence_type, subject, body_text, **kwargs):
    """Create and dispatch an investor notification."""
    doc = frappe.get_doc({
        "doctype": "Auto Correspondence",
        "investor": investor,
        "correspondence_type": correspondence_type,
        "trigger_event": kwargs.get("trigger_event", "Manual"),
        "subject": subject,
        "body_text": body_text,
        "channel": kwargs.get("channel", "Email"),
        "status": "Draft",
    })
    doc.insert()
    # Auto-dispatch if requested
    if kwargs.get("dispatch_now"):
        from bizaxl.bizaxl.doctype.auto_correspondence.auto_correspondence import (
            dispatch_correspondence,
        )
        return dispatch_correspondence(doc.name)
    return doc


# =============================================================================
# E-SIGN APIs
# =============================================================================

@frappe.whitelist()
def request_esign(investor, document_type, **kwargs):
    """Create a new e-Sign request for an investor."""
    doc = frappe.get_doc({
        "doctype": "eSign Request",
        "investor": investor,
        "document_type": document_type,
        "document_reference": kwargs.get("document_reference"),
        "esign_method": kwargs.get("esign_method", "Aadhaar e-Sign (OTP)"),
        "request_date": today(),
        "expiry_date": kwargs.get("expiry_date"),
        "status": "Draft",
    })
    doc.insert()
    doc.submit()
    return doc


@frappe.whitelist()
def sign_document(esign_name, signed_document=None):
    """Mark an e-Sign request as completed/signed."""
    from bizaxl.bizaxl.doctype.esign_request.esign_request import complete_esign

    return complete_esign(esign_name, signed_document)


@frappe.whitelist()
def verify_signed_document(esign_name):
    """Verify a completed e-Sign request."""
    from bizaxl.bizaxl.doctype.esign_request.esign_request import verify_esign

    return verify_esign(esign_name)


@frappe.whitelist()
def get_pending_esigns(investor=None):
    """Get pending e-Sign requests."""
    from bizaxl.bizaxl.doctype.esign_request.esign_request import get_pending_esign_requests

    return get_pending_esign_requests(investor)


# =============================================================================
# INVESTOR DASHBOARD APIS
# =============================================================================

@frappe.whitelist()
def get_investor_dashboard(investor):
    """Get comprehensive investor portal dashboard."""
    from bizaxl.bizaxl.doctype.capital_account_statement.capital_account_statement import (
        get_investor_statements,
    )
    from bizaxl.bizaxl.doctype.auto_correspondence.auto_correspondence import (
        get_investor_correspondence,
    )
    from bizaxl.bizaxl.doctype.esign_request.esign_request import get_pending_esign_requests

    # Holdings
    allotments = frappe.get_all(
        "Allotment Detail",
        filters={"investor": investor, "docstatus": 1},
        fields=["fund_master", "share_class", "sum(units) as units", "sum(amount) as cost"],
        group_by="fund_master, share_class",
    )

    # SIP/Plans
    sips = frappe.get_all(
        "SIP Plan",
        filters={"investor": investor},
        fields=["name", "fund_master", "sip_amount", "sip_frequency", "status", "next_sip_date"],
    )

    return {
        "investor": investor,
        "portfolio": {
            "holdings": allotments,
            "total_invested": sum(a.get("cost", 0) or 0 for a in allotments),
        },
        "statements": get_investor_statements(investor),
        "correspondence": get_investor_correspondence(investor),
        "pending_esigns": get_pending_esign_requests(investor),
        "active_plans": sips,
    }


@frappe.whitelist()
def get_investor_activity_feed(investor, limit=20):
    """Get recent activity feed for an investor across all communications."""
    correspondence = frappe.get_all(
        "Auto Correspondence",
        filters={"investor": investor},
        fields=[
            "'correspondence' as activity_type", "name as reference",
            "correspondence_type", "subject", "sent_date as activity_date", "status",
        ],
        order_by="sent_date desc",
        limit=limit,
    )

    esigns = frappe.get_all(
        "eSign Request",
        filters={"investor": investor},
        fields=[
            "'esign' as activity_type", "name as reference",
            "document_type as correspondence_type", "signing_purpose as subject",
            "signed_date as activity_date", "status",
        ],
        order_by="signed_date desc",
        limit=limit,
    )

    statements = frappe.get_all(
        "Capital Account Statement",
        filters={"investor": investor},
        fields=[
            "'statement' as activity_type", "name as reference",
            "statement_type as correspondence_type", "'Statement' as subject",
            "statement_date as activity_date", "status",
        ],
        order_by="statement_date desc",
        limit=limit,
    )

    # Merge and sort all activities
    activities = correspondence + esigns + statements
    activities.sort(key=lambda x: x.get("activity_date") or "", reverse=True)

    return activities[:limit]
