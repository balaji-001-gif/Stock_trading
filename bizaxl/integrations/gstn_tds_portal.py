# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
GSTN / TAN / TDS Portal Connector — Stub-to-Live Integration

Tax compliance portal for TDS computation, filing, Form 16A generation,
GST verification, and TRACES integration.

Supports:
1. TDS Computation — Calculate TDS, surcharge, education cess per section
2. TDS Filing — File TDS returns (Form 24Q/26Q) with Income Tax Department
3. Form 16A — Generate Form 16A TDS certificates for deductees
4. TRACES Integration — Retrieve TDS challan status, view filed returns
5. GST Verification — Verify GSTIN of vendors/partners
6. TAN Verification — Verify Tax Deduction and Collection Account Number

Stub mode: Simulates Income Tax Portal and GSTN responses
Live mode: Integrates with actual Income Tax e-Filing portal and GSTN API
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, add_days, add_months
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


class TaxPortalConnector(BaseConnector):
    """GSTN / TAN / TDS Portal — tax compliance, filing, Form 16A, verification."""

    connector_name = "gstn_tds_portal"
    label = "GSTN / TAN / TDS Portal"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: TDS Computation
    # =========================================================================

    def compute_tds(self, gross_amount, tds_rate, pan_number, section_code="194", surcharge_rate=0, cess_rate=4):
        """Compute TDS with surcharge and education cess."""
        try:
            if self.is_stub:
                result = self._stub_compute_tds(gross_amount, tds_rate, pan_number, section_code, surcharge_rate, cess_rate)
            else:
                result = self._live_compute_tds(gross_amount, tds_rate, pan_number, section_code, surcharge_rate, cess_rate)
            self.log_request("compute_tds", {"amount": gross_amount, "rate": tds_rate, "pan": pan_number}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: TDS Filing
    # =========================================================================

    def file_tds_return(self, tan_number, return_type, period, tds_details):
        """File TDS return (Form 24Q/26Q/27Q) with Income Tax Department."""
        request = {"tan": tan_number, "return_type": return_type, "period": period}

        try:
            if self.is_stub:
                result = self._stub_file_tds(tan_number, return_type, period, tds_details)
            else:
                result = self._live_file_tds(tan_number, return_type, period, tds_details)
            self.log_request("file_tds_return", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Form 16A
    # =========================================================================

    def generate_form_16a(self, tan_number, deductee_pan, financial_year, quarter):
        """Generate Form 16A TDS certificate."""
        try:
            if self.is_stub:
                result = self._stub_generate_form_16a(tan_number, deductee_pan, financial_year, quarter)
            else:
                result = self._live_generate_form_16a(tan_number, deductee_pan, financial_year, quarter)
            self.log_request("generate_form_16a", {"tan": tan_number, "pan": deductee_pan, "fy": financial_year}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: TRACES
    # =========================================================================

    def get_tds_challan_status(self, challan_ref, bsr_code):
        """Get TDS challan status from TRACES."""
        try:
            if self.is_stub:
                result = self._stub_challan_status(challan_ref, bsr_code)
            else:
                result = self._live_challan_status(challan_ref, bsr_code)
            self.log_request("get_tds_challan_status", {"challan": challan_ref, "bsr": bsr_code}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: GST Verification
    # =========================================================================

    def verify_gstin(self, gstin):
        """Verify GSTIN and return taxpayer details."""
        try:
            if self.is_stub:
                result = self._stub_verify_gstin(gstin)
            else:
                result = self._live_verify_gstin(gstin)
            self.log_request("verify_gstin", {"gstin": gstin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: TAN Verification
    # =========================================================================

    def verify_tan(self, tan_number):
        """Verify TAN (Tax Deduction and Collection Account Number)."""
        try:
            if self.is_stub:
                result = self._stub_verify_tan(tan_number)
            else:
                result = self._live_verify_tan(tan_number)
            self.log_request("verify_tan", {"tan": tan_number}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_compute_tds(self, gross_amount, tds_rate, pan_number, section_code, surcharge_rate, cess_rate):
        """Simulate TDS computation."""
        tds_amt = round(gross_amount * tds_rate / 100, 2)
        surcharge_amt = round(tds_amt * surcharge_rate / 100, 2) if surcharge_rate else 0
        cess_amt = round((tds_amt + surcharge_amt) * cess_rate / 100, 2)
        total_tds = round(tds_amt + surcharge_amt + cess_amt, 2)
        net_amt = round(gross_amount - total_tds, 2)

        return {
            "status": "Success",
            "mode": "stub",
            "gross_amount": gross_amount,
            "pan": pan_number,
            "section_code": section_code,
            "tds_rate": tds_rate,
            "tds_amount": tds_amt,
            "surcharge_rate": surcharge_rate,
            "surcharge_amount": surcharge_amt,
            "cess_rate": cess_rate,
            "education_cess": cess_amt,
            "total_tds": total_tds,
            "net_amount": net_amt,
            "computation_ref": f"TDS-CALC-{random_string(10).upper()}",
        }

    def _stub_file_tds(self, tan_number, return_type, period, tds_details):
        """Simulate TDS return filing."""
        return {
            "status": "Success",
            "mode": "stub",
            "tan": tan_number,
            "return_type": return_type,
            "financial_year": period.get("fy"),
            "quarter": period.get("quarter"),
            "token_number": f"TOKEN{random_string(16).upper()}",
            "acknowledgment_no": f"ACK{random_string(20).upper()}",
            "filing_date": today(),
            "total_deductees": len(tds_details.get("deductees", [])),
            "total_tds_amount": tds_details.get("total_tds", 0),
            "status": "Filed Successfully",
            "message": f"{return_type} return for Q{period.get('quarter')} FY {period.get('fy')} filed successfully.",
        }

    def _stub_generate_form_16a(self, tan_number, deductee_pan, financial_year, quarter):
        """Simulate Form 16A generation."""
        return {
            "status": "Success",
            "mode": "stub",
            "form_16a_ref": f"16A-{random_string(12).upper()}",
            "tan": tan_number,
            "deductee_pan": deductee_pan,
            "financial_year": financial_year,
            "quarter": quarter,
            "generated_at": now_datetime().isoformat(),
            "total_tds_deducted": round(random.uniform(5000, 500000), 2),
            "download_url": f"https://www.tdscpc.gov.in/form16a/{random_string(20).upper()}",
            "message": "Form 16A generated successfully. Available for download on TRACES.",
        }

    def _stub_challan_status(self, challan_ref, bsr_code):
        """Simulate TDS challan status query."""
        return {
            "status": "Success",
            "mode": "stub",
            "challan_ref": challan_ref,
            "bsr_code": bsr_code,
            "challan_status": random.choice(["Booked", "Matched", "Unmatched"]),
            "amount": round(random.uniform(10000, 500000), 2),
            "deposit_date": add_days(datetime.now(), -random.randint(1, 60)).strftime("%Y-%m-%d"),
            "major_head": "0020",
            "remarks": "TDS deposited and booked successfully." if random.random() > 0.2 else "Challan pending matching with return.",
        }

    def _stub_verify_gstin(self, gstin):
        """Simulate GSTIN verification."""
        return {
            "status": "Success",
            "mode": "stub",
            "gstin": gstin,
            "legal_name": "Bizaxl Optimisations LLP",
            "trade_name": "Bizaxl",
            "gstin_status": "Active",
            "registration_date": "2024-06-01",
            "last_return_filed_date": add_months(today(), -1),
            "taxpayer_type": "Regular",
            "business_type": "LLP",
            "address": "42, MG Road, Indiranagar, Bengaluru - 560038",
            "state": "Karnataka",
            "constitution": "Limited Liability Partnership",
            "valid": True,
        }

    def _stub_verify_tan(self, tan_number):
        """Simulate TAN verification."""
        return {
            "status": "Success",
            "mode": "stub",
            "tan": tan_number,
            "deductor_name": "Bizaxl Optimisations LLP",
            "tan_status": "Active",
            "deductor_type": "LLP",
            "pan": "AAECB1234F",
            "address": "42, MG Road, Indiranagar, Bengaluru - 560038",
            "assessment_officer": "ITO Ward 2(1), Bengaluru",
            "valid": True,
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_compute_tds(self, gross_amount, tds_rate, pan_number, section_code, surcharge_rate, cess_rate):
        raise NotImplementedError("Live TDS computation requires Income Tax portal API access.")

    def _live_file_tds(self, tan_number, return_type, period, tds_details):
        raise NotImplementedError("Live TDS filing requires Income Tax e-Filing API credentials.")

    def _live_generate_form_16a(self, tan_number, deductee_pan, financial_year, quarter):
        raise NotImplementedError("Live Form 16A requires TRACES API credentials.")

    def _live_challan_status(self, challan_ref, bsr_code):
        raise NotImplementedError("Live challan status requires TRACES API access.")

    def _live_verify_gstin(self, gstin):
        raise NotImplementedError("Live GSTIN verification requires GSTN API credentials.")

    def _live_verify_tan(self, tan_number):
        raise NotImplementedError("Live TAN verification requires Income Tax portal access.")
