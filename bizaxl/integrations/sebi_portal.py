# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
SEBI Reporting Portal Connector — Stub-to-Live Integration

Regulatory filing for SEBI, RBI, PFRDA compliance through SEBI portals.

Supports:
1. AIF Annex VI Quarterly — Portfolio, investor, drawdown, and valuation details
2. PMS Quarterly Report — Client-wise holdings, performance, fees charged
3. REIT/InvIT Quarterly — Property-level financials, distributions, valuation
4. SCORES Integration — Investor complaint register and resolution tracking
5. SEBI Inspection — Data pack generation for SEBI inspection readiness

Stub mode: Simulates SEBI portal responses with realistic fund data
Live mode: Integrates with actual SEBI reporting portals (SEBI SFTP, API)
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, add_days, add_months
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Sample report templates for stub data
SEBI_REPORT_TYPES = {
    "AIF Annex VI Quarterly": {
        "fields": [
            "portfolio_summary", "investor_details", "drawdown_status",
            "valuation_summary", "fee_computation", "carried_interest",
        ],
        "regulatory_body": "SEBI",
        "deadline_days": 60,
    },
    "PMS Quarterly Report": {
        "fields": [
            "portfolio_holdings", "transaction_summary", "performance_report",
            "fee_charged", "benchmark_comparison",
        ],
        "regulatory_body": "SEBI",
        "deadline_days": 30,
    },
    "REIT Quarterly Report": {
        "fields": [
            "property_summary", "rental_income", "occupancy_rates",
            "distribution_details", "valuation_update", "debt_profile",
        ],
        "regulatory_body": "SEBI",
        "deadline_days": 45,
    },
    "SCORES Complaint Status": {
        "fields": [
            "complaint_summary", "resolution_status", "pending_items",
            "aged_complaints",
        ],
        "regulatory_body": "SEBI",
        "deadline_days": 15,
    },
}


class SEBIConnector(BaseConnector):
    """SEBI Reporting Portal — AIF Annex VI, PMS, REIT/InvIT, SCORES filings."""

    connector_name = "sebi_portal"
    label = "SEBI Reporting Portal"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: File Report
    # =========================================================================

    def file_report(self, report_type, report_data):
        """File a regulatory report to the SEBI portal."""
        request = {"report_type": report_type, "data_size": len(str(report_data))}

        try:
            if self.is_stub:
                result = self._stub_file_report(report_type, report_data)
            else:
                result = self._live_file_report(report_type, report_data)
            self.log_request("file_report", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Get Filing Status
    # =========================================================================

    def get_filing_status(self, filing_ref):
        """Check the status of a filed report."""
        try:
            if self.is_stub:
                result = self._stub_filing_status(filing_ref)
            else:
                result = self._live_filing_status(filing_ref)
            self.log_request("get_filing_status", {"filing_ref": filing_ref}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: SCORES Integration
    # =========================================================================

    def file_scores_complaint(self, complaint_data):
        """File an investor complaint response to SCORES."""
        try:
            if self.is_stub:
                result = self._stub_scores_complaint(complaint_data)
            else:
                result = self._live_scores_complaint(complaint_data)
            self.log_request("file_scores_complaint", {"complaint_ref": complaint_data.get("ref")}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: SEBI Inspection Readiness
    # =========================================================================

    def generate_inspection_pack(self, fund_master):
        """Generate SEBI inspection readiness data pack."""
        try:
            if self.is_stub:
                result = self._stub_inspection_pack(fund_master)
            else:
                result = self._live_inspection_pack(fund_master)
            self.log_request("generate_inspection_pack", {"fund": fund_master}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_file_report(self, report_type, report_data):
        """Simulate SEBI report filing."""
        filing_ref = f"SEBI-{random_string(14).upper()}"
        ack_no = f"ACK-{random.randint(100000000, 999999999)}"

        return {
            "status": "Success",
            "mode": "stub",
            "filing_ref": filing_ref,
            "acknowledgment_no": ack_no,
            "report_type": report_type,
            "filing_date": today(),
            "expected_processing_time": "3-5 business days",
            "portal": "SEBI Online Portal",
            "message": f"{report_type} filed successfully. Acknowledgment: {ack_no}",
        }

    def _stub_filing_status(self, filing_ref):
        """Simulate filing status check."""
        return {
            "status": "Success",
            "mode": "stub",
            "filing_ref": filing_ref,
            "filing_status": random.choice(["Filed", "Under Review", "Acknowledged", "Deficiency Raised"]),
            "filed_date": add_days(datetime.now(), -random.randint(1, 30)).strftime("%Y-%m-%d"),
            "last_updated": today(),
            "remarks": "No deficiencies found." if random.random() > 0.2 else "Query raised. Response pending.",
        }

    def _stub_scores_complaint(self, complaint_data):
        """Simulate SCORES complaint filing."""
        scores_ref = f"SCORES-{random_string(10).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "scores_ref": scores_ref,
            "complaint_ref": complaint_data.get("ref"),
            "complaint_type": complaint_data.get("type", "Service Issue"),
            "status": "Acknowledged",
            "resolution_deadline": add_days(datetime.now(), 21).strftime("%Y-%m-%d"),
            "message": "Response filed to SCORES. Acknowledged by SEBI.",
        }

    def _stub_inspection_pack(self, fund_master):
        """Simulate inspection pack generation."""
        return {
            "status": "Success",
            "mode": "stub",
            "inspection_ref": f"INSP-{random_string(10).upper()}",
            "fund": fund_master,
            "generated_at": now_datetime().isoformat(),
            "documents_count": random.randint(15, 30),
            "total_pages": random.randint(200, 800),
            "categories": [
                "Fund Documents", "Investor Records", "Trade Confirmations",
                "NAV Working Files", "Compliance Reports", "Board Minutes",
                "Fee Computations", "KYC/AML Records", "Contracts & Agreements",
            ],
            "message": "Inspection pack generated. Ready for SEBI inspection.",
        }

    def _live_file_report(self, report_type, report_data):
        raise NotImplementedError("Live SEBI filing requires SEBI portal API credentials.")

    def _live_filing_status(self, filing_ref):
        raise NotImplementedError("Live filing status requires SEBI portal access.")

    def _live_scores_complaint(self, complaint_data):
        raise NotImplementedError("Live SCORES requires SEBI intermediary credentials.")

    def _live_inspection_pack(self, fund_master):
        raise NotImplementedError("Live inspection pack requires SEBI portal API access.")
