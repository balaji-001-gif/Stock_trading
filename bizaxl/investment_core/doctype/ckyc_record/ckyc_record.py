# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class CKYCRecord(Document):
    """Tracks CKYC Registry lookups, uploads, and verifications."""

    def after_insert(self):
        """Auto-update investor profile with CKYC data on successful fetch."""
        if self.operation_type == "Fetch Record" and self.status == "Success" and self.investor:
            self._update_investor_ckyc()

    def _update_investor_ckyc(self):
        """Update linked investor profile with fetched CKYC data."""
        try:
            updates = {}
            if self.ckyc_number:
                updates["ckyc_number"] = self.ckyc_number
                updates["ckyc_verified"] = 1

            if updates:
                frappe.db.set_value("Investor Profile", self.investor, updates)
        except Exception:
            pass


@frappe.whitelist()
def fetch_ckyc_record(investor, pan_number):
    """API: Fetch CKYC record from CERSAI registry."""
    from bizaxl.bizaxl.integrations.ckyc_registry import CKYCConnector

    connector = CKYCConnector()
    result = connector.fetch_ckyc(pan_number=pan_number)

    record = frappe.get_doc({
        "doctype": "CKYC Record",
        "investor": investor,
        "pan_number": pan_number,
        "operation_type": "Fetch Record",
        "status": result.get("status", "Failed"),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })

    if result.get("status") == "Success":
        ckyc = result.get("ckyc_data", {})
        record.ckyc_number = ckyc.get("ckyc_number")
        record.kra_name = ckyc.get("kra_name")
        record.matched_name = ckyc.get("full_name")
        record.ckyc_status = ckyc.get("ckyc_status")
        record.is_valid = ckyc.get("ckyc_status") == "Active"
        record.ckyc_last_updated = ckyc.get("ckyc_last_updated")
        record.full_name = ckyc.get("full_name")
        record.father_name = ckyc.get("father_name")
        record.mother_name = ckyc.get("mother_name")
        record.date_of_birth = ckyc.get("date_of_birth")
        record.gender = ckyc.get("gender")
        record.marital_status = ckyc.get("marital_status")
        record.occupation = ckyc.get("occupation")
        record.nationality = ckyc.get("nationality")
        record.residential_status = ckyc.get("residential_status")

        addr = ckyc.get("address_permanent", {})
        record.permanent_address = f"{addr.get('line1', '')}, {addr.get('line2', '')}\n{addr.get('city', '')}, {addr.get('state', '')} - {addr.get('pincode', '')}" if addr else ""

        addr_c = ckyc.get("address_correspondence", {})
        record.correspondence_address = f"{addr_c.get('line1', '')}, {addr_c.get('line2', '')}\n{addr_c.get('city', '')}, {addr_c.get('state', '')} - {addr_c.get('pincode', '')}" if addr_c else ""

        record.email = ckyc.get("email")
        record.mobile = ckyc.get("mobile")
        record.photo_available = ckyc.get("photo_available", 0)
        record.signature_available = ckyc.get("signature_available", 0)
        record.source = result.get("source")

    else:
        record.error_message = result.get("error")

    record.insert()
    return {"name": record.name, "status": record.status, "ckyc_number": record.ckyc_number}


@frappe.whitelist()
def upload_kyc_to_ckyc(investor, pan_number, kra_name="CAMS KRA"):
    """API: Upload investor KYC to CKYC registry."""
    from bizaxl.bizaxl.integrations.ckyc_registry import CKYCConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    investor_data = {
        "pan_number": pan_number,
        "first_name": investor_doc.first_name,
        "last_name": investor_doc.last_name,
        "date_of_birth": investor_doc.date_of_birth,
        "gender": investor_doc.gender,
        "email": investor_doc.email,
        "mobile_number": investor_doc.mobile_number,
    }

    connector = CKYCConnector()
    result = connector.upload_ckyc(investor_data, kra_name)

    record = frappe.get_doc({
        "doctype": "CKYC Record",
        "investor": investor,
        "pan_number": pan_number,
        "operation_type": "Upload KYC",
        "status": result.get("status", "Failed"),
        "ckyc_number": result.get("ckyc_number"),
        "kra_name": kra_name,
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    record.insert()

    return {"name": record.name, "ckyc_number": result.get("ckyc_number"), "status": result.get("status")}


@frappe.whitelist()
def verify_ckyc_status(investor, pan_number):
    """API: Verify CKYC status for an investor."""
    from bizaxl.bizaxl.integrations.ckyc_registry import CKYCConnector

    connector = CKYCConnector()
    result = connector.verify_ckyc(pan_number)

    record = frappe.get_doc({
        "doctype": "CKYC Record",
        "investor": investor,
        "pan_number": pan_number,
        "operation_type": "Verify CKYC",
        "status": "Success",
        "ckyc_number": result.get("ckyc_number"),
        "matched_name": result.get("registered_name"),
        "ckyc_status": result.get("ckyc_status"),
        "is_valid": result.get("is_valid", 0),
        "kra_name": result.get("kra_name"),
        "ckyc_last_updated": result.get("last_updated"),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    record.insert()

    return {
        "name": record.name,
        "is_valid": result.get("is_valid"),
        "ckyc_number": result.get("ckyc_number"),
        "ckyc_status": result.get("ckyc_status"),
    }


@frappe.whitelist()
def list_ckyc_records(investor=None):
    """API: List CKYC records for an investor."""
    filters = {}
    if investor:
        filters["investor"] = investor

    return frappe.get_all(
        "CKYC Record",
        filters=filters,
        fields=["name", "pan_number", "ckyc_number", "operation_type",
                "status", "kra_name", "ckyc_status", "is_valid",
                "connector_mode", "creation"],
        order_by="creation desc",
        limit_page_length=50,
    )
