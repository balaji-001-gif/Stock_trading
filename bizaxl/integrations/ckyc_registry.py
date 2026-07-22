# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
CKYC Registry (CERSAI) Connector — Stub-to-Live Integration

Central KYC record management via CERSAI (Central Registry of Securitisation
Asset Reconstruction and Security Interest of India) for the CKYC registry.

Supports:
1. Fetch CKYC Record — Retrieve KYC data using PAN or CKYC number
2. Upload CKYC Data — Submit new KYC record to the registry
3. Verify CKYC — Check CKYC validity and status
4. Update CKYC — Update existing CKYC record with latest information

Stub mode: Simulates CERSAI responses with realistic Indian test data
Live mode: Integrates with actual CERSAI CKYC API via registered KRA
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated CKYC records keyed by PAN
STUB_CKYC_RECORDS = {
    "ABCDE1234F": {
        "ckyc_number": "CKYC1234567890",
        "full_name": "Aarav Sharma",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "middle_name": "",
        "father_name": "Rajesh Sharma",
        "mother_name": "Sunita Sharma",
        "spouse_name": "",
        "date_of_birth": "15/08/1990",
        "gender": "Male",
        "marital_status": "Single",
        "occupation": "Software Engineer",
        "nationality": "Indian",
        "residential_status": "Resident Individual",
        "pan": "ABCDE1234F",
        "aadhaar": "XXXX-XXXX-1234",
        "email": "aarav.s@example.com",
        "mobile": "9876543210",
        "address_permanent": {
            "line1": "42, MG Road",
            "line2": "Indiranagar",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560038",
            "country": "India",
        },
        "address_correspondence": {
            "line1": "42, MG Road",
            "line2": "Indiranagar",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560038",
            "country": "India",
        },
        "photo_available": False,
        "signature_available": False,
        "ckyc_status": "Active",
        "ckyc_last_updated": "2025-12-15",
        "kra_name": "CAMS KRA",
    },
    "PQRS5678W": {
        "ckyc_number": "CKYC9876543210",
        "full_name": "Priya Patel",
        "first_name": "Priya",
        "last_name": "Patel",
        "father_name": "Rakesh Patel",
        "mother_name": "Meena Patel",
        "spouse_name": "",
        "date_of_birth": "22/03/1985",
        "gender": "Female",
        "marital_status": "Married",
        "occupation": "Chartered Accountant",
        "nationality": "Indian",
        "residential_status": "Resident Individual",
        "pan": "PQRS5678W",
        "aadhaar": "XXXX-XXXX-5678",
        "email": "priya.p@example.com",
        "mobile": "9988776655",
        "address_permanent": {
            "line1": "15, Lake View Apartments",
            "line2": "Koramangala",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560034",
            "country": "India",
        },
        "address_correspondence": {
            "line1": "15, Lake View Apartments",
            "line2": "Koramangala",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560034",
            "country": "India",
        },
        "photo_available": False,
        "signature_available": False,
        "ckyc_status": "Active",
        "ckyc_last_updated": "2026-01-10",
        "kra_name": "Karvy KRA",
    },
    "XYZ1234A": {
        "ckyc_number": "CKYC5678901234",
        "full_name": "Vikram Singh",
        "first_name": "Vikram",
        "last_name": "Singh",
        "father_name": "Ajay Singh",
        "mother_name": "Deepa Singh",
        "spouse_name": "Anita Singh",
        "date_of_birth": "10/11/1978",
        "gender": "Male",
        "marital_status": "Married",
        "occupation": "Business Owner",
        "nationality": "Indian",
        "residential_status": "Resident Individual",
        "pan": "XYZ1234A",
        "aadhaar": "XXXX-XXXX-9012",
        "email": "vikram.s@example.com",
        "mobile": "8765432109",
        "address_permanent": {
            "line1": "7, Palm Grove Society",
            "line2": "Andheri West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400053",
            "country": "India",
        },
        "address_correspondence": {
            "line1": "7, Palm Grove Society",
            "line2": "Andheri West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400053",
            "country": "India",
        },
        "photo_available": True,
        "signature_available": True,
        "ckyc_status": "Active",
        "ckyc_last_updated": "2026-02-20",
        "kra_name": "CDSL Ventures",
    },
    "NEWKYC00E1A": {
        "ckyc_number": None,
        "full_name": "New Investor",
        "pan": "NEWKYC00E1A",
        "ckyc_status": "Not Registered",
    },
}


class CKYCConnector(BaseConnector):
    """CKYC Registry (CERSAI) integration — fetch, upload, verify, update KYC records."""

    connector_name = "ckyc_registry"
    label = "CKYC Registry (CERSAI)"
    settings_doctype = "Integration Settings"

    # -------------------------------------------------------------------------
    # Credential check
    # -------------------------------------------------------------------------

    def _has_credentials(self):
        """Live mode requires CERSAI KRA credentials."""
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Fetch CKYC Record
    # =========================================================================

    def fetch_ckyc(self, pan_number=None, ckyc_number=None):
        """
        Fetch CKYC record from central registry.

        Args:
            pan_number (str, optional): PAN number to look up
            ckyc_number (str, optional): CKYC number to look up

        Returns:
            dict: {status, ckyc_data, source, mode}
        """
        request = {"pan": pan_number, "ckyc_number": ckyc_number}

        if not pan_number and not ckyc_number:
            frappe.throw(_("Either PAN number or CKYC number is required."))

        try:
            if self.is_stub:
                result = self._stub_fetch_ckyc(pan_number, ckyc_number)
            else:
                result = self._live_fetch_ckyc(pan_number, ckyc_number)

            self.log_request("fetch_ckyc", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("fetch_ckyc", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Upload CKYC Data
    # =========================================================================

    def upload_ckyc(self, investor_data, kra_name="CAMS KRA"):
        """
        Upload KYC data to CKYC registry.

        Args:
            investor_data (dict): Investor KYC details
            kra_name (str): KRA through which to upload

        Returns:
            dict: {status, ckyc_number, message, mode}
        """
        request = {"kra": kra_name, "pan": investor_data.get("pan_number")}

        try:
            if self.is_stub:
                result = self._stub_upload_ckyc(investor_data, kra_name)
            else:
                result = self._live_upload_ckyc(investor_data, kra_name)

            self.log_request("upload_ckyc", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("upload_ckyc", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Verify CKYC
    # =========================================================================

    def verify_ckyc(self, pan_number):
        """
        Verify CKYC status for a PAN.

        Args:
            pan_number (str): PAN number to verify

        Returns:
            dict: {status, is_valid, ckyc_number, ckyc_status, mode}
        """
        request = {"pan": pan_number}

        try:
            if self.is_stub:
                result = self._stub_verify_ckyc(pan_number)
            else:
                result = self._live_verify_ckyc(pan_number)

            self.log_request("verify_ckyc", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("verify_ckyc", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Update CKYC
    # =========================================================================

    def update_ckyc(self, ckyc_number, updated_fields):
        """
        Update existing CKYC record.

        Args:
            ckyc_number (str): Existing CKYC number
            updated_fields (dict): Fields to update

        Returns:
            dict: {status, ckyc_number, updated_fields, mode}
        """
        request = {"ckyc_number": ckyc_number, "updates": list(updated_fields.keys())}

        try:
            if self.is_stub:
                result = self._stub_update_ckyc(ckyc_number, updated_fields)
            else:
                result = self._live_update_ckyc(ckyc_number, updated_fields)

            self.log_request("update_ckyc", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("update_ckyc", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_fetch_ckyc(self, pan_number, ckyc_number):
        """Simulate CKYC record fetch from CERSAI registry."""
        identifier = pan_number or ckyc_number

        if pan_number and pan_number.upper() in STUB_CKYC_RECORDS:
            record = STUB_CKYC_RECORDS[pan_number.upper()]
        elif ckyc_number:
            # Search by CKYC number
            record = None
            for pan, data in STUB_CKYC_RECORDS.items():
                if data.get("ckyc_number") == ckyc_number:
                    record = data
                    break
            if not record:
                return {
                    "status": "Not Found",
                    "error": f"No CKYC record found for ID: {ckyc_number}",
                    "mode": "stub",
                }
        else:
            # Simulate a generic fetch by generating based on PAN pattern
            if pan_number and len(pan_number) == 10:
                return {
                    "status": "Success",
                    "mode": "stub",
                    "source": "CERSAI CKYC Registry",
                    "ckyc_data": {
                        "ckyc_number": f"CKYC{random_string(10).upper()}",
                        "full_name": f"Investor {pan_number[:5]}",
                        "pan": pan_number.upper(),
                        "date_of_birth": "01/01/1990",
                        "gender": "Male",
                        "nationality": "Indian",
                        "ckyc_status": "Active",
                        "ckyc_last_updated": today(),
                    },
                }
            return {
                "status": "Not Found",
                "error": f"No CKYC record found for: {identifier}",
                "mode": "stub",
            }

        # Record found
        return {
            "status": "Success",
            "mode": "stub",
            "source": "CERSAI CKYC Registry",
            "searched_by": "PAN" if pan_number else "CKYC Number",
            "ckyc_data": {
                "ckyc_number": record.get("ckyc_number"),
                "full_name": record.get("full_name"),
                "first_name": record.get("first_name"),
                "last_name": record.get("last_name"),
                "father_name": record.get("father_name"),
                "mother_name": record.get("mother_name"),
                "spouse_name": record.get("spouse_name"),
                "date_of_birth": record.get("date_of_birth"),
                "gender": record.get("gender"),
                "marital_status": record.get("marital_status"),
                "occupation": record.get("occupation"),
                "nationality": record.get("nationality"),
                "residential_status": record.get("residential_status"),
                "pan": record.get("pan"),
                "aadhaar": record.get("aadhaar"),
                "email": record.get("email"),
                "mobile": record.get("mobile"),
                "address_permanent": record.get("address_permanent"),
                "address_correspondence": record.get("address_correspondence"),
                "photo_available": record.get("photo_available"),
                "signature_available": record.get("signature_available"),
                "ckyc_status": record.get("ckyc_status"),
                "ckyc_last_updated": record.get("ckyc_last_updated"),
                "kra_name": record.get("kra_name"),
            },
        }

    def _stub_upload_ckyc(self, investor_data, kra_name):
        """Simulate CKYC upload to CERSAI registry."""
        pan = (investor_data.get("pan_number") or "").upper()
        if not pan or len(pan) != 10:
            return {"status": "Failed", "error": "Valid PAN number is required for CKYC upload."}

        ckyc_number = f"CKYC{random_string(10).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "ckyc_number": ckyc_number,
            "message": f"KYC data uploaded successfully via {kra_name}. CKYC number generated.",
            "kra_name": kra_name,
            "registration_date": today(),
            "ckyc_status": "Active",
        }

    def _stub_verify_ckyc(self, pan_number):
        """Simulate CKYC verification."""
        pan = pan_number.upper() if pan_number else ""

        if pan in STUB_CKYC_RECORDS:
            record = STUB_CKYC_RECORDS[pan]
            return {
                "status": "Success",
                "is_valid": record.get("ckyc_status") == "Active",
                "ckyc_number": record.get("ckyc_number"),
                "registered_name": record.get("full_name"),
                "ckyc_status": record.get("ckyc_status"),
                "kra_name": record.get("kra_name"),
                "last_updated": record.get("ckyc_last_updated"),
                "mode": "stub",
            }

        return {
            "status": "Success",
            "is_valid": False,
            "ckyc_number": None,
            "ckyc_status": "Not Registered",
            "message": "No CKYC record found for this PAN.",
            "mode": "stub",
        }

    def _stub_update_ckyc(self, ckyc_number, updated_fields):
        """Simulate CKYC record update."""
        return {
            "status": "Success",
            "mode": "stub",
            "ckyc_number": ckyc_number,
            "updated_fields": list(updated_fields.keys()),
            "update_date": today(),
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_fetch_ckyc(self, pan_number, ckyc_number):
        """Fetch CKYC record via CERSAI KRA API."""
        raise NotImplementedError("Live CKYC fetch requires CERSAI KRA API credentials.")

    def _live_upload_ckyc(self, investor_data, kra_name):
        """Upload KYC data via CERSAI KRA API."""
        raise NotImplementedError("Live CKYC upload requires KRA API credentials.")

    def _live_verify_ckyc(self, pan_number):
        """Verify CKYC status via CERSAI KRA API."""
        raise NotImplementedError("Live CKYC verification requires KRA API credentials.")

    def _live_update_ckyc(self, ckyc_number, updated_fields):
        """Update CKYC record via CERSAI KRA API."""
        raise NotImplementedError("Live CKYC update requires KRA API credentials.")
