# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 1 API Endpoints — Fund Configuration & Master Setup."""

import frappe
from frappe.utils import today, flt


# =============================================================================
# FUND MASTER APIs
# =============================================================================

@frappe.whitelist()
def create_fund(**kwargs):
    """Create a new fund master record."""
    doc = frappe.get_doc({
        "doctype": "Fund Master",
        "fund_name": kwargs.get("fund_name"),
        "fund_code": kwargs.get("fund_code"),
        "fund_type": kwargs.get("fund_type"),
        "fund_category": kwargs.get("fund_category"),
        "fund_status": "Draft",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_fund_overview(fund_name):
    """Get complete fund overview with all linked data."""
    fund = frappe.get_doc("Fund Master", fund_name)
    return {
        "fund": fund.as_dict(),
        "share_classes": fund.get_share_classes(),
        "fee_structures": fund.get_fee_structures(),
        "configuration": fund.get_current_nav(),
    }


@frappe.whitelist()
def list_all_funds(fund_type=None, status="Active"):
    """List all funds with optional filters."""
    filters = {}
    if fund_type:
        filters["fund_type"] = fund_type
    if status:
        filters["fund_status"] = status

    return frappe.get_all(
        "Fund Master",
        filters=filters,
        fields=[
            "name",
            "fund_name",
            "fund_code",
            "fund_type",
            "fund_category",
            "fund_status",
            "aum_current",
            "aum_date",
            "inception_date",
            "sebi_registration_number",
            "risk_level",
        ],
        order_by="modified desc",
    )


# =============================================================================
# SHARE CLASS APIs
# =============================================================================

@frappe.whitelist()
def create_share_class(fund_master, class_name, class_code, class_type, **kwargs):
    """Create a new share class for a fund."""
    doc = frappe.get_doc({
        "doctype": "Share Class",
        "fund_master": fund_master,
        "class_name": class_name,
        "class_code": class_code,
        "class_type": class_type,
        "status": "Active",
    })
    for key, value in kwargs.items():
        if hasattr(doc, key):
            doc.set(key, value)
    doc.insert()
    return doc


# =============================================================================
# FUND SERIES APIs
# =============================================================================

@frappe.whitelist()
def create_series(fund_master, series_name, series_code, **kwargs):
    """Create a new fund series."""
    doc = frappe.get_doc({
        "doctype": "Fund Series",
        "fund_master": fund_master,
        "series_name": series_name,
        "series_code": series_code,
        "status": "Draft",
    })
    for key, value in kwargs.items():
        if hasattr(doc, key):
            doc.set(key, value)
    doc.insert()
    return doc


# =============================================================================
# FEE STRUCTURE APIs
# =============================================================================

@frappe.whitelist()
def calculate_management_fee(fund_name, aum, days_in_period=30):
    """Calculate management fee for a fund based on active fee structure."""
    fees = frappe.get_all(
        "Fee Structure",
        filters={
            "fund_master": fund_name,
            "fee_type": "Management Fee",
            "status": "Active",
            "effective_from": ["<=", today()],
        },
        limit=1,
    )
    if not fees:
        return {"error": "No active management fee structure found"}

    fee_doc = frappe.get_doc("Fee Structure", fees[0].name)
    fee_amount = fee_doc.calculate_management_fee(flt(aum), days_in_period)
    return {
        "fee_structure": fee_doc.name,
        "fee_name": fee_doc.fee_name,
        "aum": aum,
        "days": days_in_period,
        "calculated_fee": fee_amount,
        "fee_rate": fee_doc.management_fee_rate,
    }


# =============================================================================
# FUND CONFIGURATION APIs
# =============================================================================

@frappe.whitelist()
def setup_fund_configuration(fund_master, **kwargs):
    """Create or update the fund configuration."""
    existing = frappe.get_all(
        "Fund Configuration",
        filters={"fund_master": fund_master, "status": "Active"},
        limit=1,
    )

    if existing:
        config = frappe.get_doc("Fund Configuration", existing[0].name)
    else:
        config = frappe.get_doc({
            "doctype": "Fund Configuration",
            "fund_master": fund_master,
            "status": "Active",
        })

    for key, value in kwargs.items():
        if hasattr(config, key):
            config.set(key, value)

    config.save()
    return config


# =============================================================================
# DASHBOARD / SUMMARY APIs
# =============================================================================

@frappe.whitelist()
def get_fund_dashboard_data():
    """Get aggregated data for the main fund dashboard."""
    total_funds = frappe.db.count("Fund Master", filters={"fund_status": "Active"})
    total_aum = frappe.db.get_all(
        "Fund Master",
        filters={"fund_status": "Active"},
        fields=["sum(aum_current) as total_aum"],
    )[0].total_aum or 0

    fund_types = frappe.get_all(
        "Fund Master",
        filters={"fund_status": "Active"},
        fields=["fund_type", "count(*) as count"],
        group_by="fund_type",
    )

    recent_funds = frappe.get_all(
        "Fund Master",
        fields=[
            "name",
            "fund_name",
            "fund_type",
            "fund_status",
            "aum_current",
            "modified",
        ],
        order_by="modified desc",
        limit=10,
    )

    return {
        "total_funds": total_funds,
        "total_aum": total_aum,
        "fund_by_type": fund_types,
        "recent_funds": recent_funds,
    }
