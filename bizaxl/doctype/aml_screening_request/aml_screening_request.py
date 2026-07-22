# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class AMLScreeningRequest(Document):
    """Tracks AML/sanctions screening connector requests and results."""
    pass


@frappe.whitelist()
def run_full_aml_screening(investor):
    """API: Run full AML screening (PEP + Sanctions + Adverse Media) for an investor."""
    from bizaxl.bizaxl.integrations.aml_screening import AMLScreeningConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    full_name = f"{investor_doc.first_name} {investor_doc.last_name or ''}".strip()

    connector = AMLScreeningConnector()
    result = connector.full_screen(full_name, investor_doc.pan_number)

    # Create/update AML Screening record
    screening = frappe.get_doc({
        "doctype": "AML Screening",
        "investor": investor,
        "screening_type": "Initial Onboarding",
        "screening_status": result.get("overall_status", "Cleared"),
        "screening_date": today(),
        "screening_method": "Automated API",
        "pep_check": result.get("pep", {}).get("conclusion", "Clear"),
        "ofac_check": result.get("sanctions", {}).get("conclusion", "Clear"),
        "sanctions_check": result.get("sanctions", {}).get("conclusion", "Clear"),
        "adverse_media_check": result.get("adverse_media", {}).get("conclusion", "Clear"),
        "risk_score": result.get("risk_score", {}).get("score", 0),
        "risk_level": result.get("risk_score", {}).get("level", "Low"),
    })
    screening.insert()
    screening.submit()

    # Log the connector request
    frappe.get_doc({
        "doctype": "AML Screening Request",
        "investor": investor,
        "screening_reference": result.get("screening_ref"),
        "check_type": "Full Screen",
        "status": result.get("overall_status", "Cleared"),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    }).insert()

    return {
        "screening_ref": result.get("screening_ref"),
        "overall_status": result.get("overall_status"),
        "risk_score": result.get("risk_score", {}).get("score"),
        "risk_level": result.get("risk_score", {}).get("level"),
        "pep_matches": result.get("pep", {}).get("matches_found", 0),
        "sanctions_matches": result.get("sanctions", {}).get("matches_found", 0),
        "adverse_media_matches": result.get("adverse_media", {}).get("matches_found", 0),
    }


@frappe.whitelist()
def screen_pep_only(investor):
    """API: Screen investor against PEP database only."""
    from bizaxl.bizaxl.integrations.aml_screening import AMLScreeningConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    full_name = f"{investor_doc.first_name} {investor_doc.last_name or ''}".strip()

    connector = AMLScreeningConnector()
    result = connector.screen_pep(full_name)
    return result


@frappe.whitelist()
def list_aml_requests(investor=None):
    """API: List AML screening requests."""
    filters = {}
    if investor:
        filters["investor"] = investor

    return frappe.get_all(
        "AML Screening Request",
        filters=filters,
        fields=["name", "investor", "check_type", "status", "connector_mode", "creation"],
        order_by="creation desc",
        limit_page_length=50,
    )
