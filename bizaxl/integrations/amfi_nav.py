# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
AMFI NAV & MF Data Connector — Stub-to-Live Integration

Daily NAV for all mutual fund schemes, scheme master data, NAV history,
and AMFI filing integration for regulatory compliance.

Supports:
1. Daily NAV — Fetch latest NAV for a scheme or all schemes
2. Scheme Master — Search and retrieve scheme metadata
3. NAV History — Historical NAV data for a date range
4. AMFI Filing — Upload NAV data to AMFI for publication

Stub mode: Simulates AMFI data with realistic scheme NAVs across categories
Live mode: Integrates with actual AMFI data feed via AMFI website/API
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated AMC and scheme data
STUB_AMC_NAV = {
    "SBI": [
        {"scheme_code": "119121", "scheme_name": "SBI Bluechip Fund - Direct - Growth", "category": "Equity", "nav": 82.45, "fund_type": "Open Ended"},
        {"scheme_code": "125497", "scheme_name": "SBI Small Cap Fund - Direct - Growth", "category": "Equity", "nav": 65.20, "fund_type": "Open Ended"},
        {"scheme_code": "100873", "scheme_name": "SBI Contra Fund - Direct - Growth", "category": "Equity", "nav": 185.30, "fund_type": "Open Ended"},
        {"scheme_code": "118834", "scheme_name": "SBI Equity Hybrid Fund - Direct - Growth", "category": "Hybrid", "nav": 55.60, "fund_type": "Open Ended"},
        {"scheme_code": "100875", "scheme_name": "SBI Liquid Fund - Direct - Growth", "category": "Liquid", "nav": 4250.80, "fund_type": "Open Ended"},
    ],
    "HDFC": [
        {"scheme_code": "120577", "scheme_name": "HDFC Balanced Advantage Fund - Direct - Growth", "category": "Hybrid", "nav": 315.20, "fund_type": "Open Ended"},
        {"scheme_code": "121078", "scheme_name": "HDFC Mid-Cap Opportunities Fund - Direct - Growth", "category": "Equity", "nav": 134.50, "fund_type": "Open Ended"},
        {"scheme_code": "118690", "scheme_name": "HDFC Flexi Cap Fund - Direct - Growth", "category": "Equity", "nav": 225.80, "fund_type": "Open Ended"},
        {"scheme_code": "113112", "scheme_name": "HDFC Short Term Debt Fund - Direct - Growth", "category": "Debt", "nav": 2250.40, "fund_type": "Open Ended"},
    ],
    "ICICI": [
        {"scheme_code": "116065", "scheme_name": "ICICI Pru Value Discovery Fund - Direct - Growth", "category": "Equity", "nav": 450.80, "fund_type": "Open Ended"},
        {"scheme_code": "113115", "scheme_name": "ICICI Pru Liquid Fund - Direct - Growth", "category": "Liquid", "nav": 3580.65, "fund_type": "Open Ended"},
        {"scheme_code": "118746", "scheme_name": "ICICI Pru Bluechip Fund - Direct - Growth", "category": "Equity", "nav": 92.35, "fund_type": "Open Ended"},
        {"scheme_code": "122639", "scheme_name": "ICICI Pru Small Cap Fund - Direct - Growth", "category": "Equity", "nav": 78.50, "fund_type": "Open Ended"},
    ],
    "AXIS": [
        {"scheme_code": "120716", "scheme_name": "Axis Long Term Equity Fund - Direct - Growth", "category": "Equity", "nav": 68.35, "fund_type": "Open Ended"},
        {"scheme_code": "122170", "scheme_name": "Axis Bluechip Fund - Direct - Growth", "category": "Equity", "nav": 54.80, "fund_type": "Open Ended"},
    ],
    "KOTAK": [
        {"scheme_code": "120275", "scheme_name": "Kotak Standard Multicap Fund - Direct - Growth", "category": "Equity", "nav": 102.15, "fund_type": "Open Ended"},
        {"scheme_code": "113106", "scheme_name": "Kotak Bond Fund - Direct - Growth", "category": "Debt", "nav": 56.80, "fund_type": "Open Ended"},
    ],
    "UTI": [
        {"scheme_code": "100587", "scheme_name": "UTI Nifty 50 Index Fund - Direct - Growth", "category": "Equity", "nav": 156.90, "fund_type": "Open Ended"},
        {"scheme_code": "118722", "scheme_name": "UTI Flexi Cap Fund - Direct - Growth", "category": "Equity", "nav": 98.40, "fund_type": "Open Ended"},
    ],
    "NIPPON": [
        {"scheme_code": "122639", "scheme_name": "Nippon India Small Cap Fund - Direct - Growth", "category": "Equity", "nav": 92.60, "fund_type": "Open Ended"},
        {"scheme_code": "120653", "scheme_name": "Nippon India Liquid Fund - Direct - Growth", "category": "Liquid", "nav": 4210.30, "fund_type": "Open Ended"},
    ],
    "ADITYA": [
        {"scheme_code": "119368", "scheme_name": "ABSL Frontline Equity Fund - Direct - Growth", "category": "Equity", "nav": 278.40, "fund_type": "Open Ended"},
    ],
    "MIRAE": [
        {"scheme_code": "118743", "scheme_name": "Mirae Asset Large Cap Fund - Direct - Growth", "category": "Equity", "nav": 88.75, "fund_type": "Open Ended"},
    ],
}


class NAVConnector(BaseConnector):
    """AMFI NAV & MF Data integration — daily NAV, scheme master, history."""

    connector_name = "amfi_nav"
    label = "AMFI NAV & MF Data"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        """Live mode requires AMFI data access."""
        return bool(self._get_api_key())

    # =========================================================================
    # PUBLIC API: Daily NAV
    # =========================================================================

    def get_daily_nav(self, scheme_code=None, amc_code=None):
        """
        Fetch latest NAV for a scheme or all schemes.

        Args:
            scheme_code (str, optional): Specific scheme code
            amc_code (str, optional): Filter by AMC

        Returns:
            dict: {status, nav_data, date, mode}
        """
        request = {"scheme_code": scheme_code, "amc_code": amc_code}

        try:
            if self.is_stub:
                result = self._stub_daily_nav(scheme_code, amc_code)
            else:
                result = self._live_daily_nav(scheme_code, amc_code)
            self.log_request("get_daily_nav", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Scheme Master
    # =========================================================================

    def get_scheme_master(self, amc_code=None, category=None, search=None):
        """
        Search and retrieve scheme metadata.

        Args:
            amc_code (str, optional): Filter by AMC
            category (str, optional): Filter by category
            search (str, optional): Search by name

        Returns:
            dict: {status, schemes, total_count, mode}
        """
        request = {"amc_code": amc_code, "category": category, "search": search}

        try:
            if self.is_stub:
                result = self._stub_scheme_master(amc_code, category, search)
            else:
                result = self._live_scheme_master(amc_code, category, search)
            self.log_request("get_scheme_master", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: NAV History
    # =========================================================================

    def get_nav_history(self, scheme_code, from_date=None, to_date=None):
        """
        Get historical NAV data for a scheme.

        Args:
            scheme_code (str): Scheme code
            from_date (str, optional): Start date
            to_date (str, optional): End date

        Returns:
            dict: {status, nav_history, scheme, mode}
        """
        from_date = from_date or (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"scheme_code": scheme_code, "from_date": from_date, "to_date": to_date}

        try:
            if self.is_stub:
                result = self._stub_nav_history(scheme_code, from_date, to_date)
            else:
                result = self._live_nav_history(scheme_code, from_date, to_date)
            self.log_request("get_nav_history", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: AMFI Filing
    # =========================================================================

    def file_nav_to_amfi(self, nav_data, scheme_code):
        """
        File NAV to AMFI for publication (fund administrator use).

        Args:
            nav_data (dict): NAV data to file
            scheme_code (str): Scheme code

        Returns:
            dict: {status, filing_ref, message, mode}
        """
        request = {"scheme_code": scheme_code, "nav_value": nav_data.get("nav")}

        try:
            if self.is_stub:
                result = self._stub_file_nav(nav_data, scheme_code)
            else:
                result = self._live_file_nav(nav_data, scheme_code)
            self.log_request("file_nav_to_amfi", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_daily_nav(self, scheme_code, amc_code):
        """Simulate AMFI daily NAV data."""
        nav_date = today()

        if scheme_code:
            # Find specific scheme
            for amc, schemes in STUB_AMC_NAV.items():
                for s in schemes:
                    if s["scheme_code"] == scheme_code:
                        nav = round(s["nav"] * random.uniform(0.995, 1.005), 2)
                        return {
                            "status": "Success",
                            "mode": "stub",
                            "nav_date": nav_date,
                            "scheme": {
                                "amc_code": amc,
                                "scheme_code": s["scheme_code"],
                                "scheme_name": s["scheme_name"],
                                "category": s["category"],
                                "fund_type": s["fund_type"],
                                "nav": nav,
                                "repurchase_price": round(nav * 0.995, 2),
                                "sale_price": round(nav * 1.005, 2),
                            },
                        }
            return {"status": "Not Found", "error": f"Scheme {scheme_code} not found", "mode": "stub"}

        # Return all or filtered by AMC
        nav_data = []
        for amc, schemes in STUB_AMC_NAV.items():
            if amc_code and amc != amc_code.upper():
                continue
            for s in schemes:
                nav = round(s["nav"] * random.uniform(0.995, 1.005), 2)
                nav_data.append({
                    "amc_code": amc,
                    "scheme_code": s["scheme_code"],
                    "scheme_name": s["scheme_name"],
                    "category": s["category"],
                    "nav": nav,
                })

        return {
            "status": "Success",
            "mode": "stub",
            "nav_date": nav_date,
            "total_schemes": len(nav_data),
            "schemes": nav_data,
        }

    def _stub_scheme_master(self, amc_code, category, search):
        """Simulate scheme master data."""
        results = []
        for amc, schemes in STUB_AMC_NAV.items():
            if amc_code and amc != amc_code.upper():
                continue
            for s in schemes:
                if category and s["category"].lower() != category.lower():
                    continue
                if search and search.lower() not in s["scheme_name"].lower():
                    continue
                results.append({
                    "amc_code": amc,
                    "amc_name": f"{amc} Mutual Fund",
                    "scheme_code": s["scheme_code"],
                    "scheme_name": s["scheme_name"],
                    "category": s["category"],
                    "fund_type": s["fund_type"],
                    "nav": s["nav"],
                    "nav_date": today(),
                    "isin_growth": f"INF{random_string(6).upper()}{random.randint(10,99)}",
                    "isin_dividend": f"INF{random_string(6).upper()}{random.randint(10,99)}",
                    "expense_ratio": round(random.uniform(0.5, 2.0), 2),
                    "min_investment": random.choice([500, 1000, 5000]),
                })

        return {
            "status": "Success",
            "mode": "stub",
            "total_count": len(results),
            "schemes": results,
        }

    def _stub_nav_history(self, scheme_code, from_date, to_date):
        """Simulate historical NAV data for a scheme."""
        # Find the scheme
        scheme_found = None
        for amc, schemes in STUB_AMC_NAV.items():
            for s in schemes:
                if s["scheme_code"] == scheme_code:
                    scheme_found = s
                    break

        if not scheme_found:
            return {"status": "Not Found", "error": f"Scheme {scheme_code} not found", "mode": "stub"}

        # Generate historical NAV points
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        days = (end - start).days

        history = []
        base_nav = scheme_found["nav"]
        for i in range(min(days + 1, 365)):
            date = start + timedelta(days=i)
            if date.weekday() >= 5:  # Skip weekends
                continue
            # Simulate daily NAV movement
            daily_change = base_nav * random.uniform(-0.02, 0.02)
            nav_value = round(base_nav + daily_change, 2)

            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "nav": nav_value,
            })

        return {
            "status": "Success",
            "mode": "stub",
            "scheme_code": scheme_code,
            "scheme_name": scheme_found["scheme_name"],
            "period": {"from": from_date, "to": to_date},
            "total_records": len(history),
            "history": history,
        }

    def _stub_file_nav(self, nav_data, scheme_code):
        """Simulate AMFI NAV filing."""
        return {
            "status": "Success",
            "mode": "stub",
            "filing_ref": f"AMFI-NAV-{random_string(10).upper()}",
            "scheme_code": scheme_code,
            "filed_nav": nav_data.get("nav"),
            "filing_date": today(),
            "message": "NAV filed successfully with AMFI.",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_daily_nav(self, scheme_code, amc_code):
        raise NotImplementedError("Live AMFI NAV requires data feed subscription.")

    def _live_scheme_master(self, amc_code, category, search):
        raise NotImplementedError("Live scheme master requires AMFI data access.")

    def _live_nav_history(self, scheme_code, from_date, to_date):
        raise NotImplementedError("Live NAV history requires AMFI data access.")

    def _live_file_nav(self, nav_data, scheme_code):
        raise NotImplementedError("Live AMFI filing requires SEBI intermediary credentials.")
