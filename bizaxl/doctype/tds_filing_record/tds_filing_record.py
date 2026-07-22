# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class TDSFilingRecord(Document):
    """Tracks TDS returns, Form 16A generation, and challan status from Tax Portal."""
    pass


@frappe.whitelist()
def file_tds_return(tan_number, return_type, financial_year, quarter, total_tds, total_deductees=0):
    """API: File TDS return with Income Tax Department."""
    from bizaxl.bizaxl.integrations.gstn_tds_portal import TaxPortalConnector

    period = {"fy": financial_year, "quarter": quarter}
    tds_details = {"total_tds": total_tds, "deductees": [{"pan": "TEMP"}] * total_deductees}

    connector = TaxPortalConnector()
    result = connector.file_tds_return(tan_number, return_type, period, tds_details)

    record = frappe.get_doc({
        "doctype": "TDS Filing Record",
        "tan_number": tan_number,
        "return_type": return_type,
        "financial_year": financial_year,
        "quarter": quarter,
        "filing_date": today(),
        "acknowledgment_no": result.get("acknowledgment_no"),
        "token_number": result.get("token_number"),
        "status": "Filed" if result.get("status") == "Success" else "Draft",
        "total_deductees": total_deductees,
        "total_tds_amount": total_tds,
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    record.insert()

    return {"name": record.name, "acknowledgment_no": record.acknowledgment_no, "status": record.status}


@frappe.whitelist()
def generate_form_16a(tan_number, deductee_pan, financial_year, quarter):
    """API: Generate Form 16A TDS certificate via TRACES."""
    from bizaxl.bizaxl.integrations.gstn_tds_portal import TaxPortalConnector

    connector = TaxPortalConnector()
    result = connector.generate_form_16a(tan_number, deductee_pan, financial_year, quarter)

    record = frappe.get_doc({
        "doctype": "TDS Filing Record",
        "tan_number": tan_number,
        "return_type": "Form 16A",
        "financial_year": financial_year,
        "quarter": quarter,
        "status": "Filed",
        "form_16a_ref": result.get("form_16a_ref"),
        "deductee_pan": deductee_pan,
        "generated_at": now_datetime(),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    record.insert()

    return {"name": record.name, "form_16a_ref": result.get("form_16a_ref"), "download_url": result.get("download_url")}


@frappe.whitelist()
def compute_tds(gross_amount, tds_rate, pan_number, section_code="194", surcharge_rate=0, cess_rate=4):
    """API: Compute TDS with surcharge and cess."""
    from bizaxl.bizaxl.integrations.gstn_tds_portal import TaxPortalConnector

    connector = TaxPortalConnector()
    return connector.compute_tds(gross_amount, tds_rate, pan_number, section_code, surcharge_rate, cess_rate)


@frappe.whitelist()
def verify_gstin(gstin):
    """API: Verify GSTIN."""
    from bizaxl.bizaxl.integrations.gstn_tds_portal import TaxPortalConnector

    connector = TaxPortalConnector()
    return connector.verify_gstin(gstin)


@frappe.whitelist()
def verify_tan(tan_number):
    """API: Verify TAN."""
    from bizaxl.bizaxl.integrations.gstn_tds_portal import TaxPortalConnector

    connector = TaxPortalConnector()
    return connector.verify_tan(tan_number)


@frappe.whitelist()
def list_tds_filings(tan_number=None):
    """API: List TDS filing records."""
    filters = {}
    if tan_number:
        filters["tan_number"] = tan_number

    return frappe.get_all(
        "TDS Filing Record",
        filters=filters,
        fields=["name", "tan_number", "return_type", "financial_year", "quarter",
                "filing_date", "acknowledgment_no", "status",
                "total_tds_amount", "connector_mode"],
        order_by="filing_date desc, creation desc",
        limit_page_length=50,
    )
