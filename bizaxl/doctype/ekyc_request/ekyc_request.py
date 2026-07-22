# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class eKYCRequest(Document):
    """Tracks Aadhaar eKYC OTP sessions, verification, and KYC data retrieval."""

    def validate(self):
        if self.status == "eKYC Completed" and self.kyc_name:
            self._populate_investor_kyc()

    def after_insert(self):
        self._update_investor()

    def _populate_investor_kyc(self):
        """Auto-populate investor profile with KYC data from Aadhaar."""
        if not self.investor:
            return

        investor = frappe.get_doc("Investor Profile", self.investor)

        # Update investor with KYC data only if fields are empty
        updated = False

        if self.kyc_name and not investor.first_name:
            name_parts = self.kyc_name.strip().split(" ", 1)
            investor.first_name = name_parts[0]
            if len(name_parts) > 1:
                investor.last_name = name_parts[1]
            updated = True

        if self.kyc_dob and not investor.date_of_birth:
            investor.date_of_birth = self.kyc_dob
            updated = True

        if self.kyc_gender and not investor.gender:
            gender_map = {"M": "Male", "F": "Female", "T": "Other"}
            investor.gender = gender_map.get(self.kyc_gender, self.kyc_gender)
            updated = True

        if self.kyc_phone and not investor.mobile_number:
            investor.mobile_number = self.kyc_phone
            updated = True

        if self.kyc_address_line1 and not investor.address_line_1:
            investor.address_line_1 = self.kyc_address_line1
            investor.address_line_2 = self.kyc_address_line2 or investor.address_line_2
            investor.city = self.kyc_city or investor.city
            investor.state = self.kyc_state or investor.state
            investor.pincode = self.kyc_pincode or investor.pincode
            updated = True

        if updated:
            investor.save(ignore_permissions=True)

    def _update_investor(self):
        """Update linked investor profile with eKYC status."""
        if self.investor and self.status in ("OTP Sent", "OTP Verified", "eKYC Completed"):
            investor = frappe.get_doc("Investor Profile", self.investor)
            if investor.kyc_status == "Not Started":
                investor.db_set("kyc_status", "In Progress")


@frappe.whitelist()
def send_ekyc_otp(investor, aadhaar_number):
    """API: Send eKYC OTP to Aadhaar-linked mobile number."""
    from bizaxl.bizaxl.integrations.uidai_ekyc import UIDAIConnector

    connector = UIDAIConnector()
    result = connector.send_otp(aadhaar_number)

    if result.get("status") == "Success":
        # Create eKYC Request record
        ekyc = frappe.get_doc({
            "doctype": "eKYC Request",
            "investor": investor,
            "aadhaar_number": aadhaar_number,
            "ekyc_mode": "Aadhaar OTP",
            "transaction_id": result.get("txn_id"),
            "status": "OTP Sent",
            "otp_sent_at": now_datetime(),
            "otp_valid_until": result.get("valid_until"),
            "connector_mode": result.get("mode", "stub"),
            "response_data": frappe.as_json(result),
        })
        ekyc.insert()

        return {
            "ekyc_request": ekyc.name,
            "txn_id": result.get("txn_id"),
            "message": result.get("message"),
            "valid_until": result.get("valid_until"),
            "mode": result.get("mode"),
        }

    return {"status": "Error", "error": result.get("error")}


@frappe.whitelist()
def verify_ekyc_otp(ekyc_request, otp):
    """API: Verify eKYC OTP and retrieve KYC data."""
    from bizaxl.bizaxl.integrations.uidai_ekyc import UIDAIConnector

    ekyc = frappe.get_doc("eKYC Request", ekyc_request)

    connector = UIDAIConnector()
    result = connector.verify_otp(ekyc.transaction_id, otp)

    if result.get("status") == "Success":
        kyc = result.get("kyc_data", {})

        # Update eKYC Request record
        ekyc.status = "eKYC Completed"
        ekyc.otp_verified_at = now_datetime()
        ekyc.kyc_name = kyc.get("name")
        ekyc.kyc_dob = kyc.get("dob")
        ekyc.kyc_gender = kyc.get("gender")
        ekyc.kyc_phone = kyc.get("phone")
        ekyc.kyc_email = kyc.get("email")

        addr = kyc.get("address", {})
        ekyc.kyc_address_line1 = addr.get("line1")
        ekyc.kyc_address_line2 = addr.get("line2")
        ekyc.kyc_city = addr.get("city")
        ekyc.kyc_state = addr.get("state")
        ekyc.kyc_pincode = addr.get("pincode")

        ekyc.connector_mode = result.get("mode", "stub")
        ekyc.response_data = frappe.as_json(result)
        ekyc.save(ignore_permissions=True)

        # Create KYC Document
        kyc_doc = frappe.get_doc({
            "doctype": "KYC Document",
            "investor": ekyc.investor,
            "document_type": "Aadhaar Card",
            "document_number": ekyc.aadhaar_number,
            "verification_status": "Verified",
            "verification_method": "eKYC (Aadhaar OTP)",
            "ekyc_reference": ekyc.transaction_id,
            "ekyc_mode": "Aadhaar OTP",
            "ekyc_consent": 1,
        })
        kyc_doc.insert()

        return {
            "status": "Success",
            "ekyc_request": ekyc.name,
            "kyc_document": kyc_doc.name,
            "investor_name": kyc.get("name"),
            "dob": kyc.get("dob"),
            "mode": result.get("mode"),
        }

    # Failed OTP
    ekyc.otp_attempts = (ekyc.otp_attempts or 0) + 1
    if ekyc.otp_attempts >= 5:
        ekyc.status = "Failed"
    ekyc.error_message = result.get("error")
    ekyc.response_data = frappe.as_json(result)
    ekyc.save(ignore_permissions=True)

    return {"status": "Failed", "error": result.get("error"), "attempts": ekyc.otp_attempts}


@frappe.whitelist()
def verify_offline_xml(investor, xml_content, share_code):
    """API: Verify Aadhaar Offline XML eKYC."""
    from bizaxl.bizaxl.integrations.uidai_ekyc import UIDAIConnector

    connector = UIDAIConnector()
    result = connector.verify_offline_xml(xml_content, share_code)

    if result.get("status") == "Success":
        kyc = result.get("kyc_data", {})

        ekyc = frappe.get_doc({
            "doctype": "eKYC Request",
            "investor": investor,
            "aadhaar_number": kyc.get("aadhaar_number", "XXXX-XXXX-5678"),
            "ekyc_mode": "Offline XML",
            "status": "eKYC Completed",
            "connector_mode": result.get("mode", "stub"),
            "response_data": frappe.as_json(result),
        })
        ekyc.insert()

        return {
            "status": "Success",
            "ekyc_request": ekyc.name,
            "investor_name": kyc.get("name"),
            "mode": result.get("mode"),
        }

    return {"status": "Failed", "error": result.get("error")}
