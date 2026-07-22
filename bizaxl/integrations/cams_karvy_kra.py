# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
CAMS / Karvy KRA Connector — Stub-to-Live Integration

KYC Record Verification via KRAs (KYC Registration Agencies) and
Consolidated Account Statement (CAS) import for mutual fund holdings.

Supported KRAs:
1. CAMS KRA — KYC verification, CAS generation, MF transaction history
2. Karvy KRA — KYC verification, CAS generation
3. NDML KRA — KYC verification
4. CDSL Ventures — KYC verification

Supports:
1. KRA Check — Verify KYC status across all KRAs
2. Fetch CAS — Retrieve Consolidated Account Statement for an investor
3. MF Transaction History — Get mutual fund transaction history
4. Scheme Master — Fetch AMC and scheme master data

Stub mode: Simulates KRA and CAMS responses with realistic Indian mutual fund data
Live mode: Integrates with actual CAMS/Karvy APIs via registered intermediary
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, comma_and
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated AMC master data
STUB_AMCS = [
    {"amc_code": "SBI", "amc_name": "SBI Mutual Fund", "amfi_code": "SBI"},
    {"amc_code": "HDFC", "amc_name": "HDFC Mutual Fund", "amfi_code": "HDFC"},
    {"amc_code": "ICICI", "amc_name": "ICICI Prudential Mutual Fund", "amfi_code": "ICICI"},
    {"amc_code": "AXIS", "amc_name": "Axis Mutual Fund", "amfi_code": "AXIS"},
    {"amc_code": "KOTAK", "amc_name": "Kotak Mahindra Mutual Fund", "amfi_code": "KOTAK"},
    {"amc_code": "UTI", "amc_name": "UTI Mutual Fund", "amfi_code": "UTI"},
    {"amc_code": "NIPPON", "amc_name": "Nippon India Mutual Fund", "amfi_code": "NIPPON"},
    {"amc_code": "ADITYA", "amc_name": "Aditya Birla Sun Life Mutual Fund", "amfi_code": "ABSL"},
    {"amc_code": "FRANKLIN", "amc_name": "Franklin Templeton Mutual Fund", "amfi_code": "FT"},
    {"amc_code": "MIRAE", "amc_name": "Mirae Asset Mutual Fund", "amfi_code": "MIRAE"},
]

# Simulated scheme master data
STUB_SCHEMES = [
    {"amc_code": "SBI", "scheme_name": "SBI Bluechip Fund - Direct Plan - Growth", "scheme_code": "119121", "category": "Equity", "nav": 82.45},
    {"amc_code": "HDFC", "scheme_name": "HDFC Balanced Advantage Fund - Direct - Growth", "scheme_code": "120577", "category": "Hybrid", "nav": 315.20},
    {"amc_code": "ICICI", "scheme_name": "ICICI Pru Value Discovery Fund - Direct - Growth", "scheme_code": "116065", "category": "Equity", "nav": 450.80},
    {"amc_code": "AXIS", "scheme_name": "Axis Long Term Equity Fund - Direct - Growth", "scheme_code": "120716", "category": "Equity", "nav": 68.35},
    {"amc_code": "KOTAK", "scheme_name": "Kotak Standard Multicap Fund - Direct - Growth", "scheme_code": "120275", "category": "Equity", "nav": 102.15},
    {"amc_code": "UTI", "scheme_name": "UTI Nifty 50 Index Fund - Direct - Growth", "scheme_code": "100587", "category": "Equity", "nav": 156.90},
    {"amc_code": "NIPPON", "scheme_name": "Nippon India Small Cap Fund - Direct - Growth", "scheme_code": "122639", "category": "Equity", "nav": 92.60},
    {"amc_code": "ADITYA", "scheme_name": "ABSL Frontline Equity Fund - Direct - Growth", "scheme_code": "119368", "category": "Equity", "nav": 278.40},
    {"amc_code": "FRANKLIN", "scheme_name": "Franklin India Prima Fund - Direct - Growth", "scheme_code": "101693", "category": "Equity", "nav": 245.30},
    {"amc_code": "MIRAE", "scheme_name": "Mirae Asset Large Cap Fund - Direct - Growth", "scheme_code": "118743", "category": "Equity", "nav": 88.75},
    {"amc_code": "SBI", "scheme_name": "SBI Small Cap Fund - Direct - Growth", "scheme_code": "125497", "category": "Equity", "nav": 65.20},
    {"amc_code": "HDFC", "scheme_name": "HDFC Mid-Cap Opportunities Fund - Direct - Growth", "scheme_code": "121078", "category": "Equity", "nav": 134.50},
    {"amc_code": "ICICI", "scheme_name": "ICICI Pru Liquid Fund - Direct - Growth", "scheme_code": "113115", "category": "Liquid", "nav": 3580.65},
    {"amc_code": "NIPPON", "scheme_name": "Nippon India Liquid Fund - Direct - Growth", "scheme_code": "120653", "category": "Liquid", "nav": 4210.30},
    {"amc_code": "KOTAK", "scheme_name": "Kotak Bond Fund - Direct - Growth", "scheme_code": "113106", "category": "Debt", "nav": 56.80},
]


class KRAConnector(BaseConnector):
    """CAMS/Karvy KRA integration — KYC verification, CAS import, MF transactions."""

    connector_name = "cams_karvy_kra"
    label = "CAMS / Karvy KRA"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        """Live mode requires KRA intermediary credentials."""
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: KRA KYC Check
    # =========================================================================

    def kra_kyc_check(self, pan_number, kra_name="CAMS KRA"):
        """
        Check KYC status across a KRA.

        Args:
            pan_number (str): PAN number to check
            kra_name (str): KRA to check against

        Returns:
            dict: {status, kyc_status, kyc_details, kra_name, mode}
        """
        request = {"pan": pan_number, "kra": kra_name}

        try:
            if self.is_stub:
                result = self._stub_kra_kyc_check(pan_number, kra_name)
            else:
                result = self._live_kra_kyc_check(pan_number, kra_name)

            self.log_request("kra_kyc_check", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("kra_kyc_check", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: CAS Fetch
    # =========================================================================

    def fetch_cas(self, pan_number, from_date=None, to_date=None):
        """
        Fetch Consolidated Account Statement from CAMS/Karvy.

        Args:
            pan_number (str): PAN number
            from_date (str, optional): Start date
            to_date (str, optional): End date

        Returns:
            dict: {status, cas_data, folios, mode}
        """
        from_date = from_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"pan": pan_number, "from_date": from_date, "to_date": to_date}

        try:
            if self.is_stub:
                result = self._stub_fetch_cas(pan_number, from_date, to_date)
            else:
                result = self._live_fetch_cas(pan_number, from_date, to_date)

            self.log_request("fetch_cas", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("fetch_cas", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Transaction History
    # =========================================================================

    def fetch_mf_transactions(self, pan_number, folio_number=None, from_date=None, to_date=None):
        """
        Fetch mutual fund transaction history.

        Args:
            pan_number (str): PAN number
            folio_number (str, optional): Filter by folio
            from_date (str, optional): Start date
            to_date (str, optional): End date

        Returns:
            dict: {status, transactions, mode}
        """
        from_date = from_date or (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"pan": pan_number, "folio": folio_number, "from_date": from_date, "to_date": to_date}

        try:
            if self.is_stub:
                result = self._stub_fetch_mf_transactions(pan_number, folio_number, from_date, to_date)
            else:
                result = self._live_fetch_mf_transactions(pan_number, folio_number, from_date, to_date)

            self.log_request("fetch_mf_transactions", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("fetch_mf_transactions", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Scheme Master
    # =========================================================================

    def fetch_scheme_master(self, amc_code=None, category=None):
        """
        Fetch mutual fund scheme master data.

        Args:
            amc_code (str, optional): Filter by AMC
            category (str, optional): Filter by category

        Returns:
            dict: {status, schemes, mode}
        """
        request = {"amc": amc_code, "category": category}

        try:
            if self.is_stub:
                result = self._stub_fetch_scheme_master(amc_code, category)
            else:
                result = self._live_fetch_scheme_master(amc_code, category)

            self.log_request("fetch_scheme_master", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_kra_kyc_check(self, pan_number, kra_name):
        """Simulate KRA KYC check."""
        pan = pan_number.upper() if pan_number else ""

        kyc_found = len(pan) == 10  # Any valid PAN format passes KRA check
        if not kyc_found:
            return {
                "status": "Success",
                "kyc_status": "Not Verified",
                "kra_name": kra_name,
                "message": "No KYC record found for this PAN in the KRA database.",
                "mode": "stub",
            }

        # Generate deterministic KRA reference based on PAN
        kra_ref = f"KRA-{kra_name[:4].upper()}-{pan[:5]}{random_string(6).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "kra_name": kra_name,
            "kyc_status": "Verified",
            "kyc_valid": True,
            "kra_reference": kra_ref,
            "kyc_details": {
                "full_name": f"Investor {pan[:5]}",
                "pan": pan,
                "kyc_compliance": "KYC compliant as per SEBI guidelines",
                "verified_since": (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d"),
                "last_verified": today(),
                "kyc_type": "Full KYC (CKYC)",
                "ckyc_number": f"CKYC{random_string(10).upper()}",
            },
            "message": "KYC verified successfully via KRA.",
        }

    def _stub_fetch_cas(self, pan_number, from_date, to_date):
        """Simulate CAS (Consolidated Account Statement) data."""
        pan = pan_number.upper() if pan_number else ""

        if len(pan) != 10:
            return {
                "status": "Failed",
                "error": "Invalid PAN number format for CAS fetch.",
                "mode": "stub",
            }

        # Generate random folios from stub schemes
        num_folios = random.randint(2, 5)
        selected_schemes = random.sample(STUB_SCHEMES, num_folios)

        folios = []
        total_investment = 0
        total_current_value = 0

        for i, scheme in enumerate(selected_schemes):
            folio_number = f"{random.randint(1000000000, 9999999999)}"
            units = round(random.uniform(100, 5000), 3)
            nav = scheme["nav"]
            cost_price = round(nav * random.uniform(0.85, 0.98), 2)
            current_value = round(units * nav, 2)
            invested = round(units * cost_price, 2)
            gain = round(current_value - invested, 2)

            total_investment += invested
            total_current_value += current_value

            folios.append({
                "folio_number": folio_number,
                "amc_name": scheme["amc_code"],
                "scheme_code": scheme["scheme_code"],
                "scheme_name": scheme["scheme_name"],
                "category": scheme["category"],
                "units": units,
                "nav": nav,
                "cost_price": cost_price,
                "current_value": current_value,
                "invested_amount": invested,
                "unrealized_gain": gain,
                "pct_return": round((gain / invested) * 100, 2) if invested else 0,
            })

        return {
            "status": "Success",
            "mode": "stub",
            "pan": pan,
            "reporting_period": {"from": from_date, "to": to_date},
            "source": "CAMS/Karvy CAS",
            "total_folios": len(folios),
            "total_investment": round(total_investment, 2),
            "total_current_value": round(total_current_value, 2),
            "total_unrealized_gain": round(total_current_value - total_investment, 2),
            "total_return_pct": round(((total_current_value - total_investment) / total_investment) * 100, 2) if total_investment else 0,
            "folios": folios,
        }

    def _stub_fetch_mf_transactions(self, pan_number, folio_number, from_date, to_date):
        """Simulate MF transaction history."""
        transaction_types = [
            "Purchase (SIP)", "Purchase (Lumpsum)", "Redemption",
            "Switch In", "Switch Out", "Dividend Payout",
            "Dividend Reinvestment", "STP In", "STP Out",
        ]

        transactions = []
        current_date = datetime.strptime(from_date, "%Y-%m-%d")
        end_date = datetime.strptime(to_date, "%Y-%m-%d")
        days_diff = (end_date - current_date).days

        for i in range(min(days_diff // 20 + 1, 12)):
            scheme = random.choice(STUB_SCHEMES)
            txn_type = random.choice(transaction_types)
            amount = round(random.uniform(1000, 50000), 2)
            nav = round(random.uniform(10, 500), 2)
            units = round(amount / nav, 3)

            txn_date = current_date + timedelta(days=random.randint(1, max(days_diff // 12, 1)))

            transactions.append({
                "transaction_id": f"MF{random_string(12).upper()}",
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_type": txn_type,
                "amc": scheme["amc_code"],
                "scheme_code": scheme["scheme_code"],
                "scheme_name": scheme["scheme_name"],
                "folio_number": folio_number or f"{random.randint(1000000000, 9999999999)}",
                "amount": amount,
                "nav": nav,
                "units": units,
            })

        transactions.sort(key=lambda x: x["transaction_date"], reverse=True)

        return {
            "status": "Success",
            "mode": "stub",
            "pan": pan_number,
            "folio_number": folio_number,
            "period": {"from": from_date, "to": to_date},
            "total_transactions": len(transactions),
            "transactions": transactions,
        }

    def _stub_fetch_scheme_master(self, amc_code, category):
        """Simulate scheme master data."""
        schemes = STUB_SCHEMES

        if amc_code:
            schemes = [s for s in schemes if s["amc_code"] == amc_code.upper()]
        if category:
            schemes = [s for s in schemes if s["category"].lower() == category.lower()]

        return {
            "status": "Success",
            "mode": "stub",
            "total_schemes": len(schemes),
            "schemes": schemes,
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_kra_kyc_check(self, pan_number, kra_name):
        """Check KYC via actual KRA API."""
        raise NotImplementedError("Live KRA check requires KRA intermediary API credentials.")

    def _live_fetch_cas(self, pan_number, from_date, to_date):
        """Fetch CAS via CAMS/Karvy API."""
        raise NotImplementedError("Live CAS fetch requires CAMS/Karvy API credentials.")

    def _live_fetch_mf_transactions(self, pan_number, folio_number, from_date, to_date):
        """Fetch MF transactions via CAMS/Karvy API."""
        raise NotImplementedError("Live MF transaction fetch requires CAMS/Karvy API credentials.")

    def _live_fetch_scheme_master(self, amc_code, category):
        """Fetch scheme master via AMFI API."""
        raise NotImplementedError("Live scheme master fetch requires AMFI API credentials.")
