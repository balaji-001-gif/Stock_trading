# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
UIDAI Aadhaar eKYC Connector — Stub-to-Live Integration

Supports:
1. OTP-based eKYC — Send OTP to Aadhaar-linked mobile, verify OTP, retrieve KYC data
2. Offline XML eKYC — Upload Aadhaar Offline XML + share code, decrypt & verify
3. eKYC Status — Check verification status and retrieve investor details

Stub mode: Simulates UIDAI responses with realistic Indian test data
Live mode: Integrates with actual UIDAI Aadhaar eKYC API via registered AUA/KUA
"""

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


class UIDAIConnector(BaseConnector):
    """UIDAI Aadhaar eKYC integration — OTP flow, offline XML, verification."""

    connector_name = "uidai_ekyc"
    label = "UIDAI Aadhaar eKYC"
    settings_doctype = "Integration Settings"

    # -------------------------------------------------------------------------
    # Credential check
    # -------------------------------------------------------------------------

    def _has_credentials(self):
        """Live mode requires AUA/KUA credentials from UIDAI."""
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: OTP-based eKYC
    # =========================================================================

    def send_otp(self, aadhaar_number, consent_text=None):
        """
        Send OTP to Aadhaar-linked mobile number.

        Args:
            aadhaar_number (str): 12-digit Aadhaar number
            consent_text (str, optional): Consent text from investor

        Returns:
            dict: {status, txn_id, message, mode, timestamp}
        """
        request = {
            "aadhaar_number": self._mask_aadhaar(aadhaar_number),
            "consent": consent_text or "I consent to eKYC verification via Aadhaar.",
            "timestamp": now_datetime().isoformat(),
        }

        try:
            if self.is_stub:
                result = self._stub_send_otp(aadhaar_number)
            else:
                result = self._live_send_otp(aadhaar_number, consent_text)

            self.log_request("send_otp", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("send_otp", request, error, status="Error", error=e)
            return error

    def verify_otp(self, txn_id, otp):
        """
        Verify OTP and retrieve eKYC data.

        Args:
            txn_id (str): Transaction ID from send_otp()
            otp (str): 6-digit OTP received by investor

        Returns:
            dict: {status, kyc_data, investor_details, xml_data, mode}
        """
        request = {"txn_id": txn_id, "otp": otp}

        try:
            if self.is_stub:
                result = self._stub_verify_otp(txn_id, otp)
            else:
                result = self._live_verify_otp(txn_id, otp)

            self.log_request("verify_otp", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("verify_otp", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Offline XML eKYC
    # =========================================================================

    def verify_offline_xml(self, xml_content, share_code):
        """
        Verify Aadhaar Offline XML with share code.

        Args:
            xml_content (str): Aadhaar Offline XML content (signed)
            share_code (str): Share code set by Aadhaar holder

        Returns:
            dict: {status, kyc_data, investor_details, mode}
        """
        request = {
            "xml_length": len(xml_content) if xml_content else 0,
            "share_code_provided": bool(share_code),
        }

        try:
            if self.is_stub:
                result = self._stub_verify_offline_xml(xml_content, share_code)
            else:
                result = self._live_verify_offline_xml(xml_content, share_code)

            self.log_request("verify_offline_xml", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("verify_offline_xml", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Status & Details
    # =========================================================================

    def get_ekyc_status(self, txn_id):
        """Check eKYC transaction status."""
        request = {"txn_id": txn_id}

        try:
            if self.is_stub:
                result = self._stub_get_status(txn_id)
            else:
                result = self._live_get_status(txn_id)

            self.log_request("get_ekyc_status", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_investor_details(self, aadhaar_number):
        """Get masked investor details from Aadhaar."""
        request = {"aadhaar_number": self._mask_aadhaar(aadhaar_number)}

        try:
            if self.is_stub:
                result = self._stub_get_details(aadhaar_number)
            else:
                result = self._live_get_details(aadhaar_number)

            self.log_request("get_investor_details", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_send_otp(self, aadhaar_number):
        """Simulate UIDAI OTP send with realistic test data."""
        self._validate_aadhaar_stub(aadhaar_number)

        txn_id = f"UIDAI-OTP-{random_string(12).upper()}"
        return {
            "status": "Success",
            "txn_id": txn_id,
            "message": "OTP sent to registered mobile number (masked: XXXXXX9834)",
            "otp_ref": f"REF{random_string(8).upper()}",
            "valid_until": (get_datetime() + timedelta(minutes=10)).isoformat(),
            "mode": "stub",
            "timestamp": now_datetime().isoformat(),
        }

    def _stub_verify_otp(self, txn_id, otp):
        """Simulate UIDAI OTP verification and KYC data retrieval."""
        # In stub mode, the valid OTP is always "123456" or "000000"
        if otp not in ("123456", "000000"):
            return {
                "status": "Failed",
                "error": "Invalid OTP. Please request a new OTP.",
                "mode": "stub",
            }

        # Simulated eKYC data
        return {
            "status": "Success",
            "mode": "stub",
            "kyc_data": {
                "aadhaar_number": "XXXX-XXXX-1234",
                "name": "Aarav Sharma",
                "dob": "15/08/1990",
                "gender": "Male",
                "phone": "XXXXXX9834",
                "email": "aarav.s@example.com",
                "address": {
                    "line1": "42, MG Road",
                    "line2": "Indiranagar",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "pincode": "560038",
                    "country": "India",
                },
                "photo": None,  # Base64 encoded photo in real flow
            },
            "txn_id": txn_id,
            "verification_method": "Aadhaar OTP",
            "timestamp": now_datetime().isoformat(),
        }

    def _stub_verify_offline_xml(self, xml_content, share_code):
        """Simulate Offline XML eKYC verification."""
        # In stub mode, valid share_code is always "1234"
        if share_code != "1234":
            return {
                "status": "Failed",
                "error": "Invalid share code. XML could not be decrypted.",
                "mode": "stub",
            }

        return {
            "status": "Success",
            "mode": "stub",
            "kyc_data": {
                "aadhaar_number": "XXXX-XXXX-5678",
                "name": "Priya Patel",
                "dob": "22/03/1985",
                "gender": "Female",
                "phone": "XXXXXX7890",
                "email": "priya.p@example.com",
                "address": {
                    "line1": "15, Lake View Apartments",
                    "line2": "Koramangala",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "pincode": "560034",
                    "country": "India",
                },
                "photo": None,
            },
            "verification_method": "Offline XML",
            "timestamp": now_datetime().isoformat(),
        }

    def _stub_get_status(self, txn_id):
        """Simulate eKYC status check."""
        return {
            "status": "Completed",
            "txn_id": txn_id,
            "verified_at": (get_datetime() - timedelta(minutes=2)).isoformat(),
            "mode": "stub",
        }

    def _stub_get_details(self, aadhaar_number):
        """Simulate masked investor details lookup."""
        return {
            "status": "Success",
            "mode": "stub",
            "aadhaar_reference": f"REF{random_string(14).upper()}",
            "last_verified": today(),
            "kyc_available": True,
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders — activated when credentials exist)
    # =========================================================================

    def _live_send_otp(self, aadhaar_number, consent_text=None):
        """Make actual UIDAI eKYC API call to send OTP."""
        endpoint = self._get_endpoint() or "https://ekyc.uidai.gov.in/otp"
        # Real implementation:
        # response = requests.post(
        #     f"{endpoint}/sendOtp",
        #     json={"uid": aadhaar_number, "consent": consent_text},
        #     headers=self._get_auth_headers(),
        # )
        # return self._parse_response(response)
        raise NotImplementedError("Live UIDAI eKYC requires production API credentials.")

    def _live_verify_otp(self, txn_id, otp):
        """Make actual UIDAI eKYC API call to verify OTP."""
        raise NotImplementedError("Live UIDAI eKYC requires production API credentials.")

    def _live_verify_offline_xml(self, xml_content, share_code):
        """Decrypt and verify Aadhaar Offline XML."""
        raise NotImplementedError("Live offline XML verification requires UIDAI public key setup.")

    def _live_get_status(self, txn_id):
        """Check eKYC status via UIDAI API."""
        raise NotImplementedError("Live UIDAI eKYC requires production API credentials.")

    def _live_get_details(self, aadhaar_number):
        """Get investor details via UIDAI API."""
        raise NotImplementedError("Live UIDAI eKYC requires production API credentials.")

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _validate_aadhaar_stub(self, aadhaar_number):
        """Validate Aadhaar number format in stub mode."""
        if not aadhaar_number or not re.match(r"^\d{12}$", aadhaar_number):
            frappe.throw(_("Invalid Aadhaar number. Must be 12 digits."), title=_("Validation Error"))

    def _mask_aadhaar(self, aadhaar_number):
        """Mask Aadhaar for logging: XXXX-XXXX-1234."""
        if aadhaar_number and len(aadhaar_number) == 12:
            return f"XXXX-XXXX-{aadhaar_number[-4:]}"
        return aadhaar_number

    def _get_auth_headers(self):
        """Get authentication headers for UIDAI API."""
        return {
            "Content-Type": "application/json",
            "api_key": self._get_api_key() or "",
            "api_secret": self._get_api_secret() or "",
        }
