# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
e-Sign / DigiLocker Connector — Stub-to-Live Integration

Aadhaar-based e-Sign for electronic signatures on agreements and documents,
along with DigiLocker integration for document verification and retrieval.

Supports:
1. Aadhaar e-Sign — Digitally sign documents using Aadhaar OTP-based e-Sign
2. DigiLocker Document Fetch — Retrieve verified documents from DigiLocker
3. Agreement Signing — End-to-end workflow for PMS/AIF/subscription agreements
4. Document Verification — Verify authenticity of signed documents

Stub mode: Simulates e-Sign and DigiLocker API responses
Live mode: Integrates with actual e-Sign (CDAC/NSDL/EMudhra) and DigiLocker APIs
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


class ESignConnector(BaseConnector):
    """e-Sign / DigiLocker integration — document signing, verification, document retrieval."""

    connector_name = "esign_digilocker"
    label = "e-Sign / DigiLocker"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Aadhaar e-Sign
    # =========================================================================

    def request_esign(self, investor_name, aadhaar_number, document_hash, signing_purpose):
        """Request Aadhaar e-Sign on a document."""
        request = {"aadhaar": aadhaar_number[-4:], "purpose": signing_purpose}

        try:
            if self.is_stub:
                result = self._stub_request_esign(investor_name, aadhaar_number, document_hash, signing_purpose)
            else:
                result = self._live_request_esign(investor_name, aadhaar_number, document_hash, signing_purpose)
            self.log_request("request_esign", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def verify_esign(self, esign_ref, signed_hash):
        """Verify an e-Signed document's authenticity."""
        try:
            if self.is_stub:
                result = self._stub_verify_esign(esign_ref, signed_hash)
            else:
                result = self._live_verify_esign(esign_ref, signed_hash)
            self.log_request("verify_esign", {"esign_ref": esign_ref}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: DigiLocker
    # =========================================================================

    def fetch_digilocker_document(self, aadhaar_number, document_type):
        """Fetch a verified document from DigiLocker."""
        request = {"aadhaar": aadhaar_number[-4:], "doc_type": document_type}

        try:
            if self.is_stub:
                result = self._stub_fetch_digilocker(aadhaar_number, document_type)
            else:
                result = self._live_fetch_digilocker(aadhaar_number, document_type)
            self.log_request("fetch_digilocker_document", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_digilocker_issued_docs(self, aadhaar_number):
        """Get list of all issued documents in DigiLocker for an Aadhaar."""
        try:
            if self.is_stub:
                result = self._stub_digilocker_issued_docs(aadhaar_number)
            else:
                result = self._live_digilocker_issued_docs(aadhaar_number)
            self.log_request("get_digilocker_issued_docs", {"aadhaar": aadhaar_number[-4:]}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_request_esign(self, investor_name, aadhaar_number, document_hash, signing_purpose):
        """Simulate Aadhaar e-Sign request."""
        esign_ref = f"ESIGN{random_string(16).upper()}"
        signing_hash = f"HASH{random_string(32).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "esign_ref": esign_ref,
            "provider": random.choice(["CDAC", "NSDL e-Sign", "eMudhra", "CAMS e-Sign"]),
            "document_hash": document_hash,
            "signing_hash": signing_hash,
            "aadhaar_ref": f"AUTH{random_string(14).upper()}",
            "signing_purpose": signing_purpose,
            "expiry_datetime": (get_datetime() + timedelta(hours=2)).isoformat(),
            "message": f"e-Sign request created for {investor_name}. OTP sent to Aadhaar-linked mobile.",
        }

    def _stub_verify_esign(self, esign_ref, signed_hash):
        """Simulate e-Sign verification."""
        return {
            "status": "Success",
            "mode": "stub",
            "esign_ref": esign_ref,
            "signature_valid": True,
            "signer_name": "Aarav Sharma",
            "signer_aadhaar_ref": f"AUTH{random_string(14).upper()}",
            "signed_at": (get_datetime() - timedelta(minutes=5)).isoformat(),
            "expires_at": (get_datetime() + timedelta(days=365)).isoformat(),
            "certificate_issuer": "CDAC e-Sign CA",
            "message": "e-Sign verified successfully. Digital signature is valid.",
        }

    def _stub_fetch_digilocker(self, aadhaar_number, document_type):
        """Simulate document fetch from DigiLocker."""
        doc_types = {
            "Aadhaar Card": {"uri": "dglaadhaar", "issuer": "UIDAI"},
            "PAN Card": {"uri": "dglpan", "issuer": "IT Department"},
            "Driving License": {"uri": "dgldl", "issuer": "RTO"},
            "Voter ID": {"uri": "dglvoter", "issuer": "ECI"},
            "Marksheet": {"uri": "dglmarks", "issuer": "CBSE"},
            "Vehicle Registration": {"uri": "dglvehicle", "issuer": "RTO"},
        }

        doc = doc_types.get(document_type, {"uri": "dgldoc", "issuer": "Govt of India"})

        return {
            "status": "Success",
            "mode": "stub",
            "document_type": document_type,
            "document_uri": f"https://digilocker.gov.in/api/v1/documents/{doc['uri']}/{random_string(16).upper()}",
            "issuer": doc["issuer"],
            "document_name": f"{document_type} - {aadhaar_number[-4:]}",
            "format": "PDF",
            "is_verified": True,
            "issued_at": (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d"),
            "message": f"{document_type} fetched successfully from DigiLocker.",
        }

    def _stub_digilocker_issued_docs(self, aadhaar_number):
        """Simulate listing all DigiLocker documents."""
        documents = [
            {"type": "Aadhaar Card", "issuer": "UIDAI", "issued": "2018-05-15"},
            {"type": "PAN Card", "issuer": "IT Department", "issued": "2016-11-20"},
            {"type": "Driving License", "issuer": "RTO", "issued": "2020-03-10"},
            {"type": "Voter ID", "issuer": "ECI", "issued": "2019-08-25"},
            {"type": "10th Marksheet", "issuer": "CBSE", "issued": "2015-06-01"},
        ]

        return {
            "status": "Success",
            "mode": "stub",
            "aadhaar_ref": aadhaar_number[-4:],
            "total_documents": len(documents),
            "documents": documents,
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_request_esign(self, investor_name, aadhaar_number, document_hash, signing_purpose):
        raise NotImplementedError("Live e-Sign requires CDAC/NSDL e-Sign API credentials (ASA/ASP).")

    def _live_verify_esign(self, esign_ref, signed_hash):
        raise NotImplementedError("Live e-Sign verification requires e-Sign provider API access.")

    def _live_fetch_digilocker(self, aadhaar_number, document_type):
        raise NotImplementedError("Live DigiLocker requires DigiLocker API credentials.")

    def _live_digilocker_issued_docs(self, aadhaar_number):
        raise NotImplementedError("Live DigiLocker requires DigiLocker API credentials.")
