# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class NPSCRARequest(Document):
    """Tracks NPS CRA interactions — PRAN registration, contribution, allocation."""
    pass


@frappe.whitelist()
def register_nps_pran(subscriber_name, **kwargs):
    """API: Register a new NPS subscriber via CRA and generate PRAN."""
    from bizaxl.bizaxl.integrations.nsdl_cra_nps import NPSCRAConnector

    subscriber_data = {
        "name": subscriber_name,
        "pan": kwargs.get("pan_number"),
        "aadhaar": kwargs.get("aadhaar_number"),
        "dob": kwargs.get("date_of_birth"),
        "email": kwargs.get("email"),
        "mobile": kwargs.get("mobile_number"),
        "employment_type": kwargs.get("employment_type"),
    }

    connector = NPSCRAConnector()
    result = connector.register_pran(subscriber_data)

    if result.get("status") == "Success":
        # Create NPS Subscriber
        subscriber = frappe.get_doc({
            "doctype": "NPS Subscriber",
            "subscriber_name": subscriber_name,
            "pran_number": result.get("pran_number"),
            "date_of_birth": kwargs.get("date_of_birth"),
            "mobile_number": kwargs.get("mobile_number"),
            "email": kwargs.get("email"),
            "pan_number": kwargs.get("pan_number"),
            "aadhaar_number": kwargs.get("aadhaar_number"),
            "tier_i_account": result.get("tier_i_account"),
            "tier_ii_account": result.get("tier_ii_account"),
            "cra_name": result.get("cra_name"),
            "cra_reference": result.get("cra_reference"),
            "pran_issue_date": result.get("pran_issue_date"),
            "employment_type": kwargs.get("employment_type", "Self-Employed"),
            "scheme_choice": kwargs.get("scheme_choice", "Active Choice"),
            "status": "Active",
        })
        subscriber.insert()

        # Log CRA request
        frappe.get_doc({
            "doctype": "NPS CRA Request",
            "nps_subscriber": subscriber.name,
            "pran_number": result.get("pran_number"),
            "cra_name": "NSDL",
            "request_type": "PRAN Registration",
            "status": "Success",
            "connector_mode": result.get("mode", "stub"),
            "response_data": frappe.as_json(result),
        }).insert()

        return {
            "subscriber": subscriber.name,
            "pran_number": result.get("pran_number"),
            "tier_i_account": result.get("tier_i_account"),
            "cra_reference": result.get("cra_reference"),
        }

    return {"status": "Failed", "error": result.get("error")}


@frappe.whitelist()
def upload_nps_contribution(nps_subscriber, contribution_amount, **kwargs):
    """API: Upload NPS contribution to CRA for unit allocation."""
    from bizaxl.bizaxl.integrations.nsdl_cra_nps import NPSCRAConnector

    subscriber = frappe.get_doc("NPS Subscriber", nps_subscriber)
    emp_cont = kwargs.get("employee_contribution", contribution_amount)
    empr_cont = kwargs.get("employer_contribution", 0)

    contribution_data = {
        "total_amount": contribution_amount,
        "employee_amount": emp_cont,
        "employer_amount": empr_cont,
        "contribution_date": kwargs.get("contribution_date", today()),
        "scheme_e_pct": kwargs.get("scheme_e_pct", 50),
        "scheme_c_pct": kwargs.get("scheme_c_pct", 15),
        "scheme_g_pct": kwargs.get("scheme_g_pct", 25),
    }

    connector = NPSCRAConnector()
    result = connector.upload_contribution(subscriber.pran_number, contribution_data)

    if result.get("status") == "Success":
        # Create NPS Contribution
        frappe.get_doc({
            "doctype": "NPS Contribution",
            "nps_subscriber": nps_subscriber,
            "pran_number": subscriber.pran_number,
            "contribution_date": kwargs.get("contribution_date", today()),
            "contribution_type": kwargs.get("contribution_type", "Regular"),
            "account_type": kwargs.get("account_type", "Tier I (Pension)"),
            "contribution_amount": contribution_amount,
            "employee_contribution": emp_cont,
            "employer_contribution": empr_cont,
            "total_contribution": contribution_amount,
            "status": "Allocated",
        }).insert()

        # Allocate units
        scheme_allocation = {
            "total_amount": contribution_amount,
            "pfm_code": subscriber.active_scheme_e or "SBI",
            "E": contribution_data["scheme_e_pct"],
            "C": contribution_data["scheme_c_pct"],
            "G": contribution_data["scheme_g_pct"],
            "A": kwargs.get("scheme_a_pct", 10),
        }
        allocation = connector.allocate_units(subscriber.pran_number, result.get("contribution_ref"), scheme_allocation)

        return {
            "contribution_ref": result.get("contribution_ref"),
            "total_amount": contribution_amount,
            "allocation": allocation,
        }

    return {"status": "Failed", "error": result.get("error")}


@frappe.whitelist()
def fetch_pfm_nav(pfm_code=None):
    """API: Fetch latest PFM NAV data."""
    from bizaxl.bizaxl.integrations.nsdl_cra_nps import NPSCRAConnector

    connector = NPSCRAConnector()
    return connector.fetch_pfm_nav(pfm_code)


@frappe.whitelist()
def process_nps_withdrawal(nps_annuity_request):
    """API: Process NPS withdrawal via CRA."""
    from bizaxl.bizaxl.integrations.nsdl_cra_nps import NPSCRAConnector

    annuity = frappe.get_doc("NPS Annuity Request", nps_annuity_request)
    subscriber = frappe.get_doc("NPS Subscriber", annuity.nps_subscriber)

    withdrawal_data = {
        "request_type": annuity.request_type,
        "total_corpus": annuity.total_corpus,
        "lump_sum_pct": annuity.lump_sum_percentage,
        "annuity_pct": annuity.annuity_percentage,
    }

    connector = NPSCRAConnector()
    result = connector.process_withdrawal(subscriber.pran_number, withdrawal_data)

    if result.get("status") == "Success":
        annuity.asp_reference = result.get("asp_reference")
        annuity.settlement_date = result.get("settlement_date")
        annuity.status = "Processed"
        annuity.save()

    return result


@frappe.whitelist()
def list_nps_cra_requests(subscriber=None):
    """API: List NPS CRA requests."""
    filters = {}
    if subscriber:
        filters["nps_subscriber"] = subscriber

    return frappe.get_all(
        "NPS CRA Request",
        filters=filters,
        fields=["name", "pran_number", "request_type", "status",
                "cra_name", "connector_mode", "creation"],
        order_by="creation desc",
        limit_page_length=50,
    )
