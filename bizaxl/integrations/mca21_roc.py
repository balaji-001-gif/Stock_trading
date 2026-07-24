# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
MCA21 / RoC Connector — Stub-to-Live Integration

Ministry of Corporate Affairs (MCA21) and Registrar of Companies (RoC) filings
for PE/VC investments, cap table compliance, and company law submissions.

Supports:
1. Company Search — DIN, CIN, PAN-based company and director search
2. Filing Submission — Form SH-7 (Share Capital), PAS-3 (Allotment), MGT-14 (Resolutions)
3. Director Verification — DIN verification and KYC status
4. RoC Compliances — Annual return, financial statement filing status
5. Charge Management — Register/Modify/Satisfy charges (debentures)

Stub mode: Simulates MCA21 responses with realistic Indian company test data
Live mode: Integrates with MCA21 V3 API via registered DSC/Signature
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated company database
STUB_COMPANIES = [
    {"cin": "L67120MH1995PLC091310", "name": "Reliance Industries Limited", "pan": "AAACR7894D",
     "status": "Active", "roc": "Mumbai", "date_incorporation": "1995-06-24", "authorized_capital": 50000000000},
    {"cin": "L65110MH1994PLC080123", "name": "HDFC Bank Limited", "pan": "AAACH4567F",
     "status": "Active", "roc": "Mumbai", "date_incorporation": "1994-08-30", "authorized_capital": 5000000000},
    {"cin": "U72200KA1999PLC025443", "name": "Infosys Technologies Limited", "pan": "AAACI1234M",
     "status": "Active", "roc": "Bangalore", "date_incorporation": "1999-07-02", "authorized_capital": 2000000000},
    {"cin": "U01100KA2019PTC125678", "name": "Aarav AgriTech Private Limited", "pan": "AACCA5678P",
     "status": "Active", "roc": "Bangalore", "date_incorporation": "2019-08-15", "authorized_capital": 15000000},
    {"cin": "U74999DL2012PTC234567", "name": "BizFin Ventures Private Limited", "pan": "AACFB1234Q",
     "status": "Active", "roc": "Delhi", "date_incorporation": "2012-11-20", "authorized_capital": 50000000},
    {"cin": "U67120TN2008PTC068432", "name": "GreenLeaf Asset Management Private Limited", "pan": "AACGL8765R",
     "status": "Active", "roc": "Chennai", "date_incorporation": "2008-03-12", "authorized_capital": 75000000},
]

# Simulated forms database
STUB_FORMS = ["SH-7 (Change in Share Capital)", "PAS-3 (Return of Allotment)",
              "MGT-14 (Filing of Resolutions)", "CHG-1 (Creation of Charge)",
              "CHG-4 (Satisfaction of Charge)", "DIR-12 (Director Changes)",
              "INC-22 (Notice of Registered Office)", "ACTIVE (Company Status)"]


class MCA21Connector(BaseConnector):
    """MCA21 / RoC integration — company filings, cap table compliance."""

    connector_name = "mca21_roc"
    label = "MCA21 / RoC"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Company Search
    # =========================================================================

    def search_company(self, cin=None, pan=None, name=None):
        """Search for a company by CIN, PAN, or name."""
        try:
            if self.is_stub:
                result = self._stub_search_company(cin, pan, name)
            else:
                result = self._live_search_company(cin, pan, name)
            self.log_request("search_company", {"cin": cin, "pan": pan, "name": name}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def verify_director(self, din, pan=None):
        """Verify Director Identification Number (DIN) status."""
        try:
            if self.is_stub:
                result = self._stub_verify_director(din, pan)
            else:
                result = self._live_verify_director(din, pan)
            self.log_request("verify_director", {"din": din, "pan": pan}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Filings
    # =========================================================================

    def file_mca_form(self, form_type, company_cin, form_data, attachments=None):
        """File a form with MCA21 (SH-7, PAS-3, MGT-14, etc.)."""
        try:
            if self.is_stub:
                result = self._stub_file_form(form_type, company_cin, form_data)
            else:
                result = self._live_file_form(form_type, company_cin, form_data, attachments)
            self.log_request("file_mca_form",
                             {"form_type": form_type, "company": company_cin, "data_fields": list(form_data.keys())}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_filing_status(self, srn):
        """Get filing status by Service Request Number (SRN)."""
        try:
            if self.is_stub:
                result = self._stub_filing_status(srn)
            else:
                result = self._live_filing_status(srn)
            self.log_request("get_filing_status", {"srn": srn}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Compliances
    # =========================================================================

    def get_compliance_status(self, company_cin):
        """Get RoC compliance status — annual returns, financials, filings."""
        try:
            if self.is_stub:
                result = self._stub_compliance_status(company_cin)
            else:
                result = self._live_compliance_status(company_cin)
            self.log_request("get_compliance_status", {"cin": company_cin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_company_master_data(self, company_cin):
        """Get full company master data from MCA21."""
        try:
            if self.is_stub:
                result = self._stub_master_data(company_cin)
            else:
                result = self._live_master_data(company_cin)
            self.log_request("get_company_master_data", {"cin": company_cin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Charges
    # =========================================================================

    def register_charge(self, company_cin, charge_details):
        """Register a charge (CHG-1) against company assets."""
        try:
            if self.is_stub:
                result = self._stub_register_charge(company_cin, charge_details)
            else:
                result = self._live_register_charge(company_cin, charge_details)
            self.log_request("register_charge", {"cin": company_cin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Cap Table Support
    # =========================================================================

    def get_shareholding_pattern(self, company_cin):
        """Get shareholding pattern from MCA21."""
        try:
            if self.is_stub:
                result = self._stub_shareholding(company_cin)
            else:
                result = self._live_shareholding(company_cin)
            self.log_request("get_shareholding_pattern", {"cin": company_cin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_search_company(self, cin, pan, name):
        """Simulate MCA21 company search."""
        results = STUB_COMPANIES
        if cin:
            results = [c for c in results if c["cin"] == cin]
        if pan:
            # Match last 4 chars of PAN
            results = [c for c in results if pan.upper() in c["pan"].upper()]
        if name:
            results = [c for c in results if name.lower() in c["name"].lower()]

        if not results:
            if cin or pan:
                return {"status": "Success", "mode": "stub", "companies_found": 0, "companies": [],
                        "message": "No companies found matching the search criteria."}
            results = STUB_COMPANIES  # Return all if no specific search

        return {
            "status": "Success",
            "mode": "stub",
            "companies_found": len(results),
            "companies": [{
                "cin": c["cin"],
                "company_name": c["name"],
                "pan": c["pan"],
                "status": c["status"],
                "roc": c["roc"],
                "date_of_incorporation": c["date_incorporation"],
                "authorized_capital": c["authorized_capital"],
                "paidup_capital": round(c["authorized_capital"] * random.uniform(0.6, 0.95)),
                "company_class": "Public" if "LTD" in c["name"] else "Private",
                "last_annual_filing": f"FY {random.randint(2023, 2025)}-{random.randint(24, 26)}",
            } for c in results],
        }

    def _stub_verify_director(self, din, pan):
        """Simulate DIN verification."""
        directors = {
            "00123456": {"name": "Ravi Kumar", "din_status": "Active", "dins": 1, "pan": "ABCDE1234F"},
            "00789012": {"name": "Anita Desai", "din_status": "Active", "dins": 3, "pan": "PQRSW5678K"},
            "00543210": {"name": "Suresh Patel", "din_status": "Disqualified", "dins": 5, "pan": "XYZAB9012L"},
            "00987654": {"name": "Meera Nair", "din_status": "Active", "dins": 2, "pan": "LMNOP3456M"},
        }
        director = directors.get(din, {
            "name": "Test Director",
            "din_status": "Active",
            "dins": random.randint(1, 4),
            "pan": pan or f"{random_string(5).upper()}{random.randint(1000, 9999)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
        })

        return {
            "status": "Success",
            "mode": "stub",
            "din": din,
            "director_name": director["name"],
            "din_status": director["din_status"],
            "dins_held": director["dins"],
            "pan": director["pan"],
            "din_activation_date": "2020-06-15" if director["din_status"] == "Active" else "2018-03-10",
            "director_kyc_status": "Compliant" if director["din_status"] == "Active" else "Non-Compliant",
            "number_of_companies": director["dins"],
        }

    def _stub_file_form(self, form_type, company_cin, form_data):
        """Simulate MCA21 form filing."""
        srn = f"MCA-{random_string(12).upper()}-{random.randint(2025, 2026)}"
        fee_amount = random.choice([500, 1000, 2000, 5000, 10000])

        return {
            "status": "Success",
            "mode": "stub",
            "srn": srn,
            "form_type": form_type,
            "company": company_cin,
            "filing_status": "Pending",
            "fee_charged": fee_amount,
            "submitted_at": now_datetime().isoformat(),
            "estimated_processing_time": "3-5 working days",
            "attachments_required": random.randint(1, 3),
            "digital_signature_status": "Verified",
            "message": f"Form {form_type} filed successfully with SRN {srn}.",
        }

    def _stub_filing_status(self, srn):
        """Simulate filing status check."""
        statuses = ["Under Processing", "Under Processing", "Under Processing",
                    "Approved", "Approved", "Resubmission Required", "Rejected"]
        status = random.choice(statuses)
        return {
            "status": "Success",
            "mode": "stub",
            "srn": srn,
            "current_status": status,
            "filing_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "last_updated": now_datetime().isoformat(),
            "processing_office": "RoC Mumbai",
            "remarks": "" if status == "Approved" else random.choice([
                "Additional documents required",
                "Clarification on share valuation needed",
                "Signature mismatch detected",
                "Waiting for DSC verification",
            ]),
        }

    def _stub_compliance_status(self, company_cin):
        """Simulate RoC compliance status."""
        company = next((c for c in STUB_COMPANIES if c["cin"] == company_cin), STUB_COMPANIES[0])
        return {
            "status": "Success",
            "mode": "stub",
            "company": company["name"],
            "cin": company_cin,
            "overall_compliance": "Good" if random.random() < 0.7 else "Action Required",
            "annual_filings": {
                "last_filed_fy": "2024-25",
                "annual_return_status": "Filed",
                "financials_status": "Filed",
                "pending_filings": random.randint(0, 2),
            },
            "board_meetings": {
                "meetings_held_this_fy": random.randint(4, 16),
                "last_meeting_date": (datetime.now() - timedelta(days=random.randint(10, 90))).strftime("%Y-%m-%d"),
                "minutes_filed": True,
            },
            "directors_compliance": {
                "total_directors": random.randint(2, 8),
                "din_active": random.randint(2, 8),
                "din_disqualified": random.randint(0, 1),
                "kyc_compliant": random.randint(2, 7),
            },
            "pending_actions": random.sample([
                "File DIR-3 KYC for directors",
                "Update registered office address",
                "File annual return for FY 2024-25",
                "Satisfy charge CHG-4",
                "Appoint additional director",
            ], k=random.randint(0, 2)),
        }

    def _stub_master_data(self, company_cin):
        """Simulate company master data from MCA21."""
        company = next((c for c in STUB_COMPANIES if c["cin"] == company_cin), STUB_COMPANIES[0])
        return {
            "status": "Success",
            "mode": "stub",
            "corporate_identification_number": company["cin"],
            "company_name": company["name"],
            "status": company["status"],
            "roc": company["roc"],
            "date_of_incorporation": company["date_incorporation"],
            "registered_address": f"{random.randint(1, 500)}, {random.choice(['MG Road', 'Brigade Road', 'Church Street', 'Residency Road'])}, {company['roc']} - {random.randint(560000, 560100)}",
            "email": f"contact@{company['name'].lower().replace(' ', '').replace('limited', '').replace('private', '').strip()}.com",
            "authorized_capital": company["authorized_capital"],
            "paidup_capital": round(company["authorized_capital"] * random.uniform(0.5, 0.95)),
            "company_class": "Public" if "LTD" in company["name"] else "Private",
            "main_division": random.choice(["Financial Services", "Technology", "Manufacturing", "Agriculture", "Consulting"]),
            "registered_office": company["roc"],
            "registrar": f"Registrar of Companies, {company['roc']}",
        }

    def _stub_register_charge(self, company_cin, charge_details):
        """Simulate charge registration."""
        charge_id = f"CHG-{random_string(10).upper()}"
        return {
            "status": "Success",
            "mode": "stub",
            "charge_id": charge_id,
            "srn": f"MCA-CHG-{random_string(10).upper()}-2026",
            "company": company_cin,
            "charge_amount": charge_details.get("amount", random.randint(5000000, 500000000)),
            "charge_creation_date": today(),
            "charge_type": charge_details.get("type", "Debenture"),
            "charge_holder": charge_details.get("holder", "HDFC Bank Limited"),
            "status": "Registered",
            "registration_fee": random.choice([5000, 10000, 25000]),
            "registration_date": today(),
        }

    def _stub_shareholding(self, company_cin):
        """Simulate shareholding pattern from MCA21."""
        company = next((c for c in STUB_COMPANIES if c["cin"] == company_cin), STUB_COMPANIES[0])
        total_shares = company["paidup_capital"] // 10  # Assume face value ₹10

        shareholders = [
            {"name": "Promoter Group", "category": "Promoters", "shares": int(total_shares * 0.52), "percentage": 52.0},
            {"name": "Foreign Institutional Investors", "category": "FII", "shares": int(total_shares * 0.18), "percentage": 18.0},
            {"name": "Domestic Institutional Investors", "category": "DII", "shares": int(total_shares * 0.12), "percentage": 12.0},
            {"name": "Retail Individual Investors", "category": "Retail", "shares": int(total_shares * 0.10), "percentage": 10.0},
            {"name": "Others", "category": "Others", "shares": int(total_shares * 0.08), "percentage": 8.0},
        ]

        return {
            "status": "Success",
            "mode": "stub",
            "company": company["name"],
            "cin": company_cin,
            "total_paidup_capital": company["paidup_capital"],
            "total_shares": total_shares,
            "face_value": 10,
            "shareholders": shareholders,
            "as_on_date": today(),
            "source": "MCA21 Registry",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_search_company(self, cin, pan, name):
        raise NotImplementedError("Live MCA21 search requires MCA21 V3 API credentials with DSC.")

    def _live_verify_director(self, din, pan):
        raise NotImplementedError("Live DIN verification requires MCA21 API credentials.")

    def _live_file_form(self, form_type, company_cin, form_data, attachments):
        raise NotImplementedError("Live MCA21 filing requires registered DSC token.")

    def _live_filing_status(self, srn):
        raise NotImplementedError("Live filing status requires MCA21 API credentials.")

    def _live_compliance_status(self, company_cin):
        raise NotImplementedError("Live compliance check requires MCA21 API credentials.")

    def _live_master_data(self, company_cin):
        raise NotImplementedError("Live company master data requires MCA21 API credentials.")

    def _live_register_charge(self, company_cin, charge_details):
        raise NotImplementedError("Live charge registration requires MCA21 API with DSC.")

    def _live_shareholding(self, company_cin):
        raise NotImplementedError("Live shareholding pattern requires MCA21 API credentials.")
