# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
NSDL/CDSL Demat Integration Connector — Stub-to-Live Mode

Supports:
1. Demat Account Linkage — Link BO ID (Beneficiary Owner ID) to investor profile
2. Holdings Fetch — Retrieve current portfolio holdings from NSDL/CDSL
3. Corporate Actions — Get corporate action updates (bonus, split, dividend, buyback)
4. Transaction History — Fetch demat transaction history (credits/debits)

Stub mode: Simulates depository responses with realistic Indian securities data
Live mode: Integrates with NSDL/CDSL STS (Straight Through Processing) API
"""

import frappe
import json
import re
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Sample securities for stub data
STUB_SECURITIES = [
    {"isin": "INE040A01034", "symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Oil & Gas"},
    {"isin": "INE009A01021", "symbol": "INFY", "name": "Infosys Ltd", "sector": "IT"},
    {"isin": "INE397D01024", "symbol": "HDFC", "name": "HDFC Bank Ltd", "sector": "Banking"},
    {"isin": "INE030A01027", "symbol": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "IT"},
    {"isin": "INE002A01018", "symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Banking"},
    {"isin": "INE467B01029", "symbol": "SBIN", "name": "State Bank of India", "sector": "Banking"},
    {"isin": "INE759A01021", "symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "FMCG"},
    {"isin": "INE154A01025", "symbol": "ITC", "name": "ITC Ltd", "sector": "FMCG"},
    {"isin": "INE660A01013", "symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile"},
    {"isin": "INE150A01010", "symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Automobile"},
    {"isin": "INE522F01014", "symbol": "HAL", "name": "Hindustan Aeronautics Ltd", "sector": "Defense"},
    {"isin": "INE081A01012", "symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "sector": "NBFC"},
]


class DematConnector(BaseConnector):
    """NSDL/CDSL Demat integration — holdings, corporate actions, transactions."""

    connector_name = "nsdl_cdsl_demat"
    label = "NSDL/CDSL Demat"
    settings_doctype = "Integration Settings"

    # -------------------------------------------------------------------------
    # Credential check
    # -------------------------------------------------------------------------

    def _has_credentials(self):
        """Live mode requires depository participant credentials."""
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Demat Account Linkage
    # =========================================================================

    def verify_bo_id(self, bo_id, dp_name="NSDL"):
        """
        Verify Beneficiary Owner ID (BO ID) format and validity.

        Args:
            bo_id (str): BO ID (e.g., '1201230000123456' for NSDL, '1234567890123456' for CDSL)
            dp_name (str): 'NSDL' or 'CDSL'

        Returns:
            dict: {status, is_valid, depository, bo_id, holder_name, mode}
        """
        request = {"bo_id": bo_id, "dp_name": dp_name}

        try:
            if self.is_stub:
                result = self._stub_verify_bo_id(bo_id, dp_name)
            else:
                result = self._live_verify_bo_id(bo_id, dp_name)

            self.log_request("verify_bo_id", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("verify_bo_id", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Holdings Fetch
    # =========================================================================

    def fetch_holdings(self, bo_id, dp_name="NSDL", as_of_date=None):
        """
        Fetch current demat holdings for a BO ID.

        Args:
            bo_id (str): Beneficiary Owner ID
            dp_name (str): 'NSDL' or 'CDSL'
            as_of_date (str, optional): Date for holdings snapshot

        Returns:
            dict: {status, holdings: [...], total_value, as_of_date, depository, mode}
        """
        as_of_date = as_of_date or today()
        request = {"bo_id": bo_id, "dp_name": dp_name, "as_of_date": as_of_date}

        try:
            if self.is_stub:
                result = self._stub_fetch_holdings(bo_id, dp_name, as_of_date)
            else:
                result = self._live_fetch_holdings(bo_id, dp_name, as_of_date)

            self.log_request("fetch_holdings", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("fetch_holdings", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Corporate Actions
    # =========================================================================

    def fetch_corporate_actions(self, bo_id=None, from_date=None, to_date=None):
        """
        Fetch corporate actions for holdings.

        Args:
            bo_id (str, optional): Filter by BO ID
            from_date (str, optional): Start date
            to_date (str, optional): End date

        Returns:
            dict: {status, corporate_actions: [...], mode}
        """
        from_date = from_date or (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"bo_id": bo_id, "from_date": from_date, "to_date": to_date}

        try:
            if self.is_stub:
                result = self._stub_fetch_corporate_actions(bo_id, from_date, to_date)
            else:
                result = self._live_fetch_corporate_actions(bo_id, from_date, to_date)

            self.log_request("fetch_corporate_actions", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("fetch_corporate_actions", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # PUBLIC API: Transaction History
    # =========================================================================

    def fetch_transactions(self, bo_id, from_date=None, to_date=None):
        """
        Fetch demat transaction history.

        Args:
            bo_id (str): Beneficiary Owner ID
            from_date (str, optional): Start date
            to_date (str, optional): End date

        Returns:
            dict: {status, transactions: [...], mode}
        """
        from_date = from_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"bo_id": bo_id, "from_date": from_date, "to_date": to_date}

        try:
            if self.is_stub:
                result = self._stub_fetch_transactions(bo_id, from_date, to_date)
            else:
                result = self._live_fetch_transactions(bo_id, from_date, to_date)

            self.log_request("fetch_transactions", request, result)
            return result
        except Exception as e:
            error = {"status": "Error", "error": str(e), "mode": self.mode}
            self.log_request("fetch_transactions", request, error, status="Error", error=e)
            return error

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_verify_bo_id(self, bo_id, dp_name):
        """Simulate BO ID verification."""
        self._validate_bo_id(bo_id, dp_name)

        holder_name = random.choice([
            "Aarav Sharma",
            "Priya Patel",
            "Vikram Singh",
            "Ananya Reddy",
            "Rajesh Kumar",
            "Meera Nair",
        ])

        return {
            "status": "Success",
            "is_valid": True,
            "depository": dp_name,
            "bo_id": bo_id,
            "holder_name": holder_name,
            "holder_type": "Individual",
            "account_status": "Active",
            "mode": "stub",
        }

    def _stub_fetch_holdings(self, bo_id, dp_name, as_of_date):
        """Simulate holdings fetch with realistic Indian securities."""
        self._validate_bo_id(bo_id, dp_name)

        # Generate random holdings from stub securities
        num_holdings = random.randint(3, 8)
        selected = random.sample(STUB_SECURITIES, num_holdings)

        holdings = []
        total_value = 0
        quantity_total = 0

        for security in selected:
            quantity = random.randint(10, 500)
            price_per_unit = round(random.uniform(100, 3200), 2)
            value = round(quantity * price_per_unit, 2)
            total_value += value
            quantity_total += quantity
            acp = round(price_per_unit * random.uniform(0.85, 1.15), 2)  # Average Cost Price

            holdings.append({
                "isin": security["isin"],
                "symbol": security["symbol"],
                "security_name": security["name"],
                "sector": security["sector"],
                "quantity": quantity,
                "face_value": 10,
                "acp": acp,
                "cost_value": round(quantity * acp, 2),
                "market_price": price_per_unit,
                "market_value": value,
                "unrealized_pnl": round(value - (quantity * acp), 2),
                "pct_portfolio": 0,  # Will compute below
            })

        # Compute portfolio percentages
        for h in holdings:
            h["pct_portfolio"] = round((h["market_value"] / total_value) * 100, 2) if total_value else 0

        return {
            "status": "Success",
            "depository": dp_name,
            "bo_id": bo_id,
            "holder_name": "Aarav Sharma",
            "as_of_date": as_of_date,
            "total_securities": len(holdings),
            "total_quantity": quantity_total,
            "total_value": round(total_value, 2),
            "holdings": holdings,
            "mode": "stub",
        }

    def _stub_fetch_corporate_actions(self, bo_id, from_date, to_date):
        """Simulate corporate actions data."""
        actions = [
            {
                "isin": "INE040A01034",
                "symbol": "RELIANCE",
                "action_type": "Dividend",
                "description": "Interim Dividend Rs. 10 per share",
                "record_date": "2026-04-15",
                "ex_date": "2026-04-14",
                "ratio": None,
                "amount": 10.00,
            },
            {
                "isin": "INE009A01021",
                "symbol": "INFY",
                "action_type": "Buyback",
                "description": "Buyback 1:5 ratio @ Rs. 1,850/share",
                "record_date": "2026-03-20",
                "ex_date": "2026-03-19",
                "ratio": "1:5",
                "amount": 1850.00,
            },
            {
                "isin": "INE030A01027",
                "symbol": "TCS",
                "action_type": "Bonus",
                "description": "1:1 Bonus Issue",
                "record_date": "2026-02-28",
                "ex_date": "2026-02-27",
                "ratio": "1:1",
                "amount": None,
            },
            {
                "isin": "INE467B01029",
                "symbol": "SBIN",
                "action_type": "Stock Split",
                "description": "Stock Split from Rs. 10 to Rs. 1",
                "record_date": "2026-01-20",
                "ex_date": "2026-01-19",
                "ratio": "10:1",
                "amount": None,
            },
            {
                "isin": "INE154A01025",
                "symbol": "ITC",
                "action_type": "Dividend",
                "description": "Final Dividend Rs. 6.25 per share",
                "record_date": "2026-05-10",
                "ex_date": "2026-05-09",
                "ratio": None,
                "amount": 6.25,
            },
        ]

        return {
            "status": "Success",
            "bo_id": bo_id or "1201230000123456",
            "from_date": from_date,
            "to_date": to_date,
            "total_actions": len(actions),
            "corporate_actions": actions,
            "mode": "stub",
        }

    def _stub_fetch_transactions(self, bo_id, from_date, to_date):
        """Simulate demat transaction history."""
        transaction_types = ["Credit (Buy)", "Debit (Sell)", "Credit (Settlement)", "Debit (Settlement)", "Credit (Bonus)", "Credit (Split)"]

        transactions = []
        current_date = datetime.strptime(from_date, "%Y-%m-%d")
        end_date = datetime.strptime(to_date, "%Y-%m-%d")
        days_diff = (end_date - current_date).days

        for i in range(min(days_diff // 15 + 1, 10)):
            security = random.choice(STUB_SECURITIES)
            txn_type = random.choice(transaction_types)
            quantity = random.randint(5, 100) if "Credit" in txn_type else random.randint(5, 50)
            price = round(random.uniform(100, 3000), 2)

            txn_date = current_date + timedelta(days=random.randint(1, max(days_diff // 10, 1)))
            transactions.append({
                "transaction_id": f"DPTXN{random_string(10).upper()}",
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_type": txn_type,
                "isin": security["isin"],
                "symbol": security["symbol"],
                "security_name": security["name"],
                "quantity": quantity,
                "price": price,
                "value": round(quantity * price, 2),
            })

        # Sort by date descending
        transactions.sort(key=lambda x: x["transaction_date"], reverse=True)

        return {
            "status": "Success",
            "bo_id": bo_id,
            "from_date": from_date,
            "to_date": to_date,
            "total_transactions": len(transactions),
            "transactions": transactions,
            "mode": "stub",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_verify_bo_id(self, bo_id, dp_name):
        """Verify BO ID via depository API."""
        raise NotImplementedError("Live demat verification requires NSDL/CDSL STS API credentials.")

    def _live_fetch_holdings(self, bo_id, dp_name, as_of_date):
        """Fetch holdings via depository API."""
        raise NotImplementedError("Live demat holdings requires NSDL/CDSL CAS API credentials.")

    def _live_fetch_corporate_actions(self, bo_id, from_date, to_date):
        """Fetch corporate actions via depository API."""
        raise NotImplementedError("Live corporate actions require depository API credentials.")

    def _live_fetch_transactions(self, bo_id, from_date, to_date):
        """Fetch transaction history via depository API."""
        raise NotImplementedError("Live demat transactions require NSDL/CDSL API credentials.")

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _validate_bo_id(self, bo_id, dp_name):
        """Validate BO ID format based on depository."""
        if not bo_id:
            frappe.throw(_("BO ID is required"), title=_("Validation Error"))

        if dp_name.upper() == "NSDL":
            # NSDL BO ID: 2-digit DP ID + 8-digit client ID = 10 digits
            if not re.match(r"^\d{10}$", bo_id):
                frappe.throw(
                    _("Invalid NSDL BO ID. Must be 10 digits (2-digit DP ID + 8-digit client ID)."),
                    title=_("Validation Error"),
                )
        elif dp_name.upper() == "CDSL":
            # CDSL BO ID: 16 digits
            if not re.match(r"^\d{16}$", bo_id):
                frappe.throw(
                    _("Invalid CDSL BO ID. Must be 16 digits."),
                    title=_("Validation Error"),
                )
        else:
            frappe.throw(
                _("Invalid depository name. Must be 'NSDL' or 'CDSL'."),
                title=_("Validation Error"),
            )

    def _get_auth_headers(self):
        """Get authentication headers for depository API."""
        return {
            "Content-Type": "application/json",
            "dp_id": self._get_api_key() or "",
            "dp_secret": self._get_api_secret() or "",
        }
