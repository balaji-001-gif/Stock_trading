# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
NSDL CRA (NPS) Connector — Stub-to-Live Integration

NPS Central Record-keeping Agency (CRA) via NSDL for NPS subscriber
management, contribution processing, unit allocation, and annuity.

Supports:
1. PRAN Registration — Generate PRAN, create Tier I/II accounts, link Aadhaar/PAN
2. Contribution Upload — Upload monthly contributions, allocate to schemes (E/C/G/A)
3. Scheme Choice — Active choice (E/C/G/A %) or Auto choice (lifecycle-based)
4. Unit Allocation — Fetch PFM NAV, allocate units per scheme
5. Withdrawal Processing — Partial withdrawal, exit at 60, annuity purchase

Stub mode: Simulates NSDL CRA responses with realistic NPS data
Live mode: Integrates with actual NSDL CRA API via registered PoP
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, add_days
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Realistic stub PFM NAV data
STUB_PFM_NAV = {
    "SBI": {"scheme_e": 85.40, "scheme_c": 62.30, "scheme_g": 48.20, "scheme_a": 55.10},
    "LIC": {"scheme_e": 78.60, "scheme_c": 58.90, "scheme_g": 45.80, "scheme_a": 52.40},
    "UTI": {"scheme_e": 82.10, "scheme_c": 60.50, "scheme_g": 47.30, "scheme_a": 53.80},
    "HDFC": {"scheme_e": 88.30, "scheme_c": 63.70, "scheme_g": 49.10, "scheme_a": 56.60},
    "ICICI": {"scheme_e": 80.90, "scheme_c": 61.20, "scheme_g": 46.50, "scheme_a": 54.20},
}


class NPSCRAConnector(BaseConnector):
    """NSDL CRA (NPS) integration — subscriber management, contributions, allocations."""

    connector_name = "nsdl_cra_nps"
    label = "NSDL CRA (NPS)"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: PRAN Registration
    # =========================================================================

    def register_pran(self, subscriber_data):
        """Register a new NPS subscriber and generate PRAN."""
        request = {"pan": subscriber_data.get("pan")}

        try:
            if self.is_stub:
                result = self._stub_register_pran(subscriber_data)
            else:
                result = self._live_register_pran(subscriber_data)
            self.log_request("register_pran", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_pran_status(self, pran_number):
        """Get PRAN account status and details."""
        try:
            if self.is_stub:
                result = self._stub_pran_status(pran_number)
            else:
                result = self._live_pran_status(pran_number)
            self.log_request("get_pran_status", {"pran": pran_number}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Contribution Upload
    # =========================================================================

    def upload_contribution(self, pran_number, contribution_data):
        """Upload a contribution to CRA for unit allocation."""
        request = {"pran": pran_number, "amount": contribution_data.get("total_amount")}

        try:
            if self.is_stub:
                result = self._stub_upload_contribution(pran_number, contribution_data)
            else:
                result = self._live_upload_contribution(pran_number, contribution_data)
            self.log_request("upload_contribution", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_contribution_statement(self, pran_number, from_date=None, to_date=None):
        """Get contribution statement for a PRAN."""
        from_date = from_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"pran": pran_number, "from": from_date, "to": to_date}

        try:
            if self.is_stub:
                result = self._stub_contribution_statement(pran_number, from_date, to_date)
            else:
                result = self._live_contribution_statement(pran_number, from_date, to_date)
            self.log_request("get_contribution_statement", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: NAV & Unit Allocation
    # =========================================================================

    def fetch_pfm_nav(self, pfm_code=None):
        """Fetch latest NAV from Pension Fund Managers."""
        try:
            if self.is_stub:
                result = self._stub_fetch_pfm_nav(pfm_code)
            else:
                result = self._live_fetch_pfm_nav(pfm_code)
            self.log_request("fetch_pfm_nav", {"pfm": pfm_code}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def allocate_units(self, pran_number, contribution_ref, scheme_allocation):
        """Allocate units based on scheme choice and PFM NAV."""
        request = {"pran": pran_number, "contribution_ref": contribution_ref}

        try:
            if self.is_stub:
                result = self._stub_allocate_units(pran_number, contribution_ref, scheme_allocation)
            else:
                result = self._live_allocate_units(pran_number, contribution_ref, scheme_allocation)
            self.log_request("allocate_units", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Withdrawal / Annuity
    # =========================================================================

    def process_withdrawal(self, pran_number, withdrawal_data):
        """Process partial withdrawal, exit, or death claim."""
        request = {"pran": pran_number, "type": withdrawal_data.get("request_type")}

        try:
            if self.is_stub:
                result = self._stub_process_withdrawal(pran_number, withdrawal_data)
            else:
                result = self._live_process_withdrawal(pran_number, withdrawal_data)
            self.log_request("process_withdrawal", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_register_pran(self, subscriber_data):
        """Simulate PRAN registration."""
        pran = f"PRAN{random_string(12).upper()}"
        tier_i = f"TIER1{random_string(10).upper()}"
        tier_ii = f"TIER2{random_string(10).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "pran_number": pran,
            "tier_i_account": tier_i,
            "tier_ii_account": tier_ii,
            "cra_name": "NSDL",
            "cra_reference": f"CRA-REF-{random_string(10).upper()}",
            "pran_issue_date": today(),
            "subscriber_name": subscriber_data.get("name", ""),
            "message": "PRAN generated successfully. Tier I and Tier II accounts created.",
        }

    def _stub_pran_status(self, pran_number):
        """Simulate PRAN status check."""
        return {
            "status": "Success",
            "mode": "stub",
            "pran_number": pran_number,
            "account_status": "Active",
            "tier_i_balance": round(random.uniform(50000, 500000), 2),
            "tier_ii_balance": round(random.uniform(10000, 100000), 2),
            "total_corpus": round(random.uniform(60000, 600000), 2),
            "last_contribution_date": add_days(datetime.now(), -random.randint(1, 60)).strftime("%Y-%m-%d"),
            "scheme_choice": "Active Choice",
            "pfm_name": random.choice(["SBI", "LIC", "UTI", "HDFC", "ICICI"]),
        }

    def _stub_upload_contribution(self, pran_number, contribution_data):
        """Simulate contribution upload to CRA."""
        total = contribution_data.get("total_amount", 0)
        emp = contribution_data.get("employee_amount", total)
        empr = contribution_data.get("employer_amount", 0)

        return {
            "status": "Success",
            "mode": "stub",
            "contribution_ref": f"CRA-CONT-{random_string(12).upper()}",
            "pran_number": pran_number,
            "transaction_id": f"TXN{random_string(16).upper()}",
            "total_amount": total,
            "employee_amount": emp,
            "employer_amount": empr,
            "contribution_date": today(),
            "allocated": True,
            "message": "Contribution uploaded and allocated to schemes.",
        }

    def _stub_contribution_statement(self, pran_number, from_date, to_date):
        """Simulate contribution statement."""
        contributions = []
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")

        for i in range(min((end - start).days // 30 + 1, 12)):
            date = start + timedelta(days=30 * i)
            total = random.randint(5000, 50000)
            emp = round(total * random.uniform(0.5, 0.7))
            empr = total - emp

            contributions.append({
                "date": date.strftime("%Y-%m-%d"),
                "total": total,
                "employee": emp,
                "employer": empr,
                "ref": f"CONT{random_string(10).upper()}",
                "scheme_e_pct": round(random.uniform(40, 60), 1),
                "scheme_c_pct": round(random.uniform(10, 20), 1),
                "scheme_g_pct": round(random.uniform(15, 30), 1),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "pran_number": pran_number,
            "period": {"from": from_date, "to": to_date},
            "total_contributions": len(contributions),
            "total_amount": sum(c["total"] for c in contributions),
            "contributions": contributions,
        }

    def _stub_fetch_pfm_nav(self, pfm_code):
        """Simulate PFM NAV data."""
        if pfm_code and pfm_code.upper() in STUB_PFM_NAV:
            pfms = {pfm_code.upper(): STUB_PFM_NAV[pfm_code.upper()]}
        else:
            pfms = STUB_PFM_NAV

        nav_data = []
        for code, schemes in pfms.items():
            nav_data.append({
                "pfm_code": code,
                "scheme_e_nav": round(schemes["scheme_e"] * random.uniform(0.995, 1.005), 4),
                "scheme_c_nav": round(schemes["scheme_c"] * random.uniform(0.995, 1.005), 4),
                "scheme_g_nav": round(schemes["scheme_g"] * random.uniform(0.995, 1.005), 4),
                "scheme_a_nav": round(schemes["scheme_a"] * random.uniform(0.995, 1.005), 4),
                "nav_date": today(),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "total_pfms": len(nav_data),
            "pfms": nav_data,
        }

    def _stub_allocate_units(self, pran_number, contribution_ref, scheme_allocation):
        """Simulate unit allocation based on scheme choice."""
        schemes = scheme_allocation or {"E": 50, "C": 15, "G": 25, "A": 10}
        total_amount = scheme_allocation.get("total_amount", 0)
        pfm = scheme_allocation.get("pfm_code", "SBI")

        # Use stub NAVs with slight variation
        navs = STUB_PFM_NAV.get(pfm, STUB_PFM_NAV["SBI"])
        allocations = {}
        total_units = 0

        for scheme, pct in [("E", schemes.get("E", 0)), ("C", schemes.get("C", 0)),
                            ("G", schemes.get("G", 0)), ("A", schemes.get("A", 0))]:
            if pct and total_amount:
                scheme_amount = total_amount * pct / 100
                nav_key = f"scheme_{scheme.lower()}"
                nav = navs.get(nav_key, 50)
                units = round(scheme_amount / nav, 4)
                allocations[f"scheme_{scheme.lower()}_units"] = units
                allocations[f"scheme_{scheme.lower()}_nav"] = nav
                allocations[f"scheme_{scheme.lower()}_amount"] = round(scheme_amount, 2)
                total_units += units

        return {
            "status": "Success",
            "mode": "stub",
            "pran_number": pran_number,
            "contribution_ref": contribution_ref,
            "pfm_code": pfm,
            "total_units": round(total_units, 4),
            "allocations": allocations,
            "allocation_date": today(),
        }

    def _stub_process_withdrawal(self, pran_number, withdrawal_data):
        """Simulate withdrawal/annuity processing."""
        req_type = withdrawal_data.get("request_type", "Exit at 60")
        corpus = withdrawal_data.get("total_corpus", 500000)

        lump_sum_pct = 60 if "60" in req_type else (25 if "Partial" in req_type else 0)
        annuity_pct = 100 - lump_sum_pct

        return {
            "status": "Success",
            "mode": "stub",
            "pran_number": pran_number,
            "request_type": req_type,
            "total_corpus": corpus,
            "lump_sum_amount": round(corpus * lump_sum_pct / 100, 2),
            "annuity_amount": round(corpus * annuity_pct / 100, 2),
            "annuity_mandatory": annuity_pct >= 40,
            "withdrawal_ref": f"WD-{random_string(12).upper()}",
            "asp_reference": f"ASP-{random_string(10).upper()}" if annuity_pct > 0 else None,
            "settlement_date": add_days(datetime.now(), 15).strftime("%Y-%m-%d"),
            "message": f"{req_type} processed. Lump sum and annuity instructions forwarded to ASP.",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_register_pran(self, subscriber_data):
        raise NotImplementedError("Live PRAN registration requires NSDL CRA API credentials.")

    def _live_pran_status(self, pran_number):
        raise NotImplementedError("Live PRAN status requires CRA API access.")

    def _live_upload_contribution(self, pran_number, contribution_data):
        raise NotImplementedError("Live contribution upload requires CRA API credentials.")

    def _live_contribution_statement(self, pran_number, from_date, to_date):
        raise NotImplementedError("Live contribution statement requires CRA API access.")

    def _live_fetch_pfm_nav(self, pfm_code):
        raise NotImplementedError("Live PFM NAV requires CRA API credentials.")

    def _live_allocate_units(self, pran_number, contribution_ref, scheme_allocation):
        raise NotImplementedError("Live unit allocation requires CRA API access.")

    def _live_process_withdrawal(self, pran_number, withdrawal_data):
        raise NotImplementedError("Live withdrawal requires CRA API credentials.")
