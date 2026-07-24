# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 7 API Endpoints — Compliance & Regulatory Reporting."""

import frappe
from frappe.utils import today


# =============================================================================
# SEBI REPORT APIs
# =============================================================================

@frappe.whitelist()
def get_pending_regulatory_filings(fund_master=None, days_ahead=30):
    """Get all pending or upcoming regulatory filings."""
    from bizaxl.bizaxl.doctype.sebi_report.sebi_report import get_pending_filings

    return get_pending_filings(fund_master, days_ahead)


@frappe.whitelist()
def get_regulatory_calendar(fund_master=None, fiscal_year=None):
    """Get compliance calendar with overdue/upcoming/filed breakdown."""
    from bizaxl.bizaxl.doctype.sebi_report.sebi_report import get_compliance_calendar

    return get_compliance_calendar(fund_master, fiscal_year)


@frappe.whitelist()
def create_regulatory_filing(fund_master, report_type, report_category, regulatory_body, **kwargs):
    """Create a new regulatory filing record."""
    doc = frappe.get_doc({
        "doctype": "SEBI Report",
        "fund_master": fund_master,
        "report_type": report_type,
        "report_category": report_category,
        "regulatory_body": regulatory_body,
        "report_date": kwargs.get("report_date", today()),
        "filing_deadline": kwargs.get("filing_deadline"),
        "period_covered": kwargs.get("period_covered"),
        "filing_portal": kwargs.get("filing_portal"),
        "status": "Draft",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def submit_regulatory_filing(filing_name, filing_date=None, acknowledgment_no=None):
    """Mark a regulatory filing as submitted."""
    doc = frappe.get_doc("SEBI Report", filing_name)
    doc.status = "Filed"
    doc.filing_date = filing_date or today()
    if acknowledgment_no:
        doc.acknowledgment_no = acknowledgment_no
    doc.flags.ignore_permissions = True
    doc.save()
    return {"status": "filed", "filing": filing_name, "filing_date": str(doc.filing_date)}


# =============================================================================
# FATCA/CRS APIs
# =============================================================================

@frappe.whitelist()
def get_fatca_crs_status(fund_master):
    """Get FATCA/CRS filing status for a fund."""
    from bizaxl.bizaxl.doctype.fatca_crs_filing.fatca_crs_filing import get_fatca_status

    return get_fatca_status(fund_master)


@frappe.whitelist()
def record_fatca_filing(fund_master, filing_type, fiscal_year, **kwargs):
    """Record a new FATCA/CRS filing."""
    doc = frappe.get_doc({
        "doctype": "FATCA CRS Filing",
        "fund_master": fund_master,
        "filing_type": filing_type,
        "fiscal_year": fiscal_year,
        "due_date": kwargs.get("due_date"),
        "nil_report": kwargs.get("nil_report", 0),
        "reportable_accounts": kwargs.get("reportable_accounts", 0),
        "status": kwargs.get("status", "Draft"),
    })
    doc.insert()
    return doc


# =============================================================================
# AML COMPLIANCE APIs
# =============================================================================

@frappe.whitelist()
def get_aml_dashboard(fund_master=None):
    """Get AML compliance summary with case counts."""
    from bizaxl.bizaxl.doctype.aml_compliance_register.aml_compliance_register import get_aml_summary

    return get_aml_summary(fund_master)


@frappe.whitelist()
def create_aml_case(investor, case_type, risk_level, **kwargs):
    """Create a new AML compliance case."""
    doc = frappe.get_doc({
        "doctype": "AML Compliance Register",
        "investor": investor,
        "case_type": case_type,
        "risk_level": risk_level,
        "case_status": "Open",
        "opened_date": today(),
        "trigger_event": kwargs.get("trigger_event", "Manual Review"),
        "assigned_to": kwargs.get("assigned_to"),
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_aml_cases(fund_master=None, case_status=None):
    """Get AML cases with optional filters."""
    filters = {}
    if fund_master:
        filters["fund_master"] = fund_master
    if case_status:
        filters["case_status"] = case_status

    return frappe.get_all(
        "AML Compliance Register",
        filters=filters,
        fields=[
            "name", "investor", "case_type", "risk_level", "case_status",
            "opened_date", "review_date", "assigned_to",
        ],
        order_by="opened_date desc",
    )


# =============================================================================
# BOARD PACK APIs
# =============================================================================

@frappe.whitelist()
def get_board_schedule(fund_master):
    """Get board meeting schedule for a fund."""
    from bizaxl.bizaxl.doctype.board_pack.board_pack import get_board_meeting_schedule

    return get_board_meeting_schedule(fund_master)


@frappe.whitelist()
def create_board_pack(fund_master, meeting_title, meeting_type, meeting_date, **kwargs):
    """Create a new board meeting pack."""
    doc = frappe.get_doc({
        "doctype": "Board Pack",
        "fund_master": fund_master,
        "meeting_title": meeting_title,
        "meeting_type": meeting_type,
        "meeting_date": meeting_date,
        "status": "Draft",
        "next_meeting_date": kwargs.get("next_meeting_date"),
    })
    doc.insert()
    return doc


# =============================================================================
# CONSOLIDATED COMPLIANCE DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_compliance_dashboard(fund_master):
    """Get comprehensive compliance dashboard for a fund."""
    from bizaxl.bizaxl.doctype.sebi_report.sebi_report import get_pending_filings, get_compliance_calendar
    from bizaxl.bizaxl.doctype.fatca_crs_filing.fatca_crs_filing import get_fatca_status
    from bizaxl.bizaxl.doctype.aml_compliance_register.aml_compliance_register import get_aml_summary
    from bizaxl.bizaxl.doctype.board_pack.board_pack import get_board_meeting_schedule

    return {
        "fund_master": fund_master,
        "compliance_calendar": get_compliance_calendar(fund_master),
        "pending_filings": get_pending_filings(fund_master),
        "fatca_crs": get_fatca_status(fund_master),
        "aml_summary": get_aml_summary(fund_master),
        "board_schedule": get_board_meeting_schedule(fund_master),
        "total_aml_cases": frappe.db.count(
            "AML Compliance Register",
            filters={"case_status": ["in", ("Open", "Under Review", "Enhanced Monitoring")]},
        ),
    }


@frappe.whitelist()
def get_due_diligence_dashboard(fund_master):
    """Get due diligence tracking view for compliance officers."""
    calendar = frappe.get_all(
        "SEBI Report",
        filters={"fund_master": fund_master},
        fields=["name", "report_type", "filing_deadline", "status"],
        order_by="filing_deadline asc",
    )

    aml = frappe.get_all(
        "AML Compliance Register",
        filters={"case_status": ["!=", "Closed"]},
        fields=["name", "investor", "case_type", "risk_level", "case_status", "opened_date"],
        order_by="risk_level desc",
    )

    return {
        "upcoming_deadlines": [f for f in calendar if f["status"] not in ("Filed", "Acknowledged")][:10],
        "open_aml_cases": aml[:10],
        "total_pending_filings": len([f for f in calendar if f["status"] not in ("Filed", "Acknowledged")]),
    }
