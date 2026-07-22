# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 2 API Endpoints — Investor Onboarding & KYC."""

import frappe
from frappe.utils import today


# =============================================================================
# ONBOARDING WORKFLOW APIs
# =============================================================================

@frappe.whitelist()
def onboard_investor(**kwargs):
    """Complete investor onboarding with KYC documents, AML screening, and risk assessment."""
    required = ["first_name", "pan_number", "email", "mobile_number", "investor_category"]
    missing = [f for f in required if not kwargs.get(f)]
    if missing:
        frappe.throw(
            f"Missing required fields: {', '.join(m.replace('_', ' ').title() for m in missing)}"
        )

    # Known safe fields for Investor Profile
    safe_fields = [
        "first_name", "last_name", "pan_number", "aadhaar_number",
        "email", "mobile_number", "phone_number", "date_of_birth", "gender",
        "nationality", "investor_category", "investor_type", "investor_sub_type",
        "occupation", "employer_name", "designation",
        "address_line_1", "address_line_2", "city", "state", "pincode", "country",
        "annual_income_range", "source_of_funds",
        "bank_name", "bank_account_number", "ifsc_code",
        "tax_residency_country_1", "tin_number_1",
        "tax_residency_country_2", "tin_number_2", "us_person", "us_tin_number",
    ]

    # 1. Create investor profile with only known fields
    investor_data = {
        "doctype": "Investor Profile",
        "kyc_status": "Not Started",
        "status": "Active",
        "fatca_status": "Pending",
    }
    for field in safe_fields:
        if kwargs.get(field) is not None:
            investor_data[field] = kwargs.get(field)

    investor = frappe.get_doc(investor_data)
    investor.insert()

    # 2. Create initial AML screening
    aml = frappe.get_doc({
        "doctype": "AML Screening",
        "investor": investor.name,
        "screening_type": "Initial Onboarding",
        "screening_status": "Pending",
        "screening_date": today(),
        "screening_method": "Automated API",
    })
    aml.insert()

    return {
        "investor": investor.name,
        "investor_name": investor.first_name + " " + (investor.last_name or ""),
        "aml_screening": aml.name,
        "status": "Onboarding Initiated",
        "next_steps": [
            "Upload KYC documents",
            "Complete risk assessment",
            "Initiate AML screening",
            "Verify KYC",
        ],
    }


@frappe.whitelist()
def get_onboarding_status(investor):
    """API: Get complete onboarding status for an investor."""
    investor_doc = frappe.get_doc("Investor Profile", investor)

    kyc_docs = frappe.get_all(
        "KYC Document",
        filters={"investor": investor},
        fields=["document_type", "verification_status"],
    )

    aml = frappe.get_all(
        "AML Screening",
        filters={"investor": investor},
        fields=["screening_status", "risk_level", "review_status"],
        order_by="screening_date desc",
        limit=1,
    )

    risk = frappe.get_all(
        "Risk Profile",
        filters={"investor": investor},
        fields=["risk_level", "risk_category", "approval_status"],
        order_by="assessment_date desc",
        limit=1,
    )

    return {
        "investor": investor,
        "kyc_status": investor_doc.kyc_status,
        "kyc_documents": kyc_docs,
        "aml_screening": aml[0] if aml else None,
        "risk_profile": risk[0] if risk else None,
        "onboarding_complete": (
            investor_doc.kyc_status == "Verified"
            and aml
            and aml[0].screening_status == "Cleared"
            and risk
            and risk[0].approval_status == "Approved"
        ),
    }


@frappe.whitelist()
def get_dashboard_stats():
    """API: Get investor onboarding dashboard statistics."""
    total = frappe.db.count("Investor Profile")
    kyc_stats = frappe.db.get_all(
        "Investor Profile",
        fields=["kyc_status", "count(*) as count"],
        group_by="kyc_status",
    )
    category_stats = frappe.db.get_all(
        "Investor Profile",
        fields=["investor_category", "count(*) as count"],
        group_by="investor_category",
    )

    aml_pending = frappe.db.count(
        "AML Screening",
        filters={"screening_status": ["in", ["Pending", "In Progress"]]},
    )

    return {
        "total_investors": total,
        "kyc_breakdown": kyc_stats,
        "category_breakdown": category_stats,
        "pending_aml_screenings": aml_pending,
    }


@frappe.whitelist()
def upload_kyc_document(investor, document_type, document_number=None):
    """API: Upload a KYC document for an investor."""
    doc = frappe.get_doc({
        "doctype": "KYC Document",
        "investor": investor,
        "document_type": document_type,
        "document_number": document_number,
        "verification_status": "Pending",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_fatca_declaration(investor):
    """API: Get FATCA declaration details for an investor."""
    investor_doc = frappe.get_doc("Investor Profile", investor)
    return {
        "tax_residency_1": investor_doc.tax_residency_country_1,
        "tin_1": investor_doc.tin_number_1,
        "tax_residency_2": investor_doc.tax_residency_country_2,
        "tin_2": investor_doc.tin_number_2,
        "fatca_status": investor_doc.fatca_status,
        "us_person": investor_doc.us_person,
        "us_tin": investor_doc.us_tin_number,
    }
