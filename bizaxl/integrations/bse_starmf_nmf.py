# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
BSE StarMF / NSE NMF II Connector — Stub-to-Live Integration

Mutual Fund transaction platform for placing orders across all AMCs.
Supports BSE StarMF and NSE NMF II (National Market for Mutual Funds).

Supports:
1. Place Order — Purchase (SIP/lumpsum), redemption, switch between schemes
2. Order Status — Track order lifecycle (pending, confirmed, rejected, settled)
3. Transaction History — Historical orders across all AMCs
4. Mandate Management — NACH/SIP auto-debit mandate setup

Stub mode: Simulates BSE StarMF / NSE NMF II order processing
Live mode: Integrates with actual BSE StarMF / NSE NMF II APIs
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, add_days
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


STUB_AMC_CODES = {
    "SBI": "SBI", "HDFC": "HDFC", "ICICI": "ICICI", "AXIS": "AXIS",
    "KOTAK": "KOTAK", "UTI": "UTI", "NIPPON": "NIPPON", "ADITYA": "ABSL",
    "MIRAE": "MIRAE",
}

STUB_ORDER_STATUSES = ["Pending", "Confirmed", "Allotted", "Rejected", "Settled"]


class MFPlatformConnector(BaseConnector):
    """BSE StarMF / NSE NMF II platform — order placement, tracking, mandate management."""

    connector_name = "bse_starmf_nmf"
    label = "BSE StarMF / NSE NMF II"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        """Live mode requires BSE StarMF / NSE NMF II membership credentials."""
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Place Purchase Order
    # =========================================================================

    def place_purchase_order(self, investor_pan, scheme_code, amount, order_type="Lumpsum",
                             amc_code=None, sip_frequency=None, sip_date=None, folio_number=None):
        """
        Place a purchase order (lumpsum or SIP).

        Args:
            investor_pan (str): PAN of investor
            scheme_code (str): Target scheme code
            amount (float): Investment amount
            order_type (str): 'Lumpsum' or 'SIP'
            amc_code (str, optional): AMC code
            sip_frequency (str, optional): For SIP - Monthly/Quarterly
            sip_date (int, optional): For SIP - Day of month (1-28)
            folio_number (str, optional): Existing folio for additional purchase

        Returns:
            dict: {status, order_ref, transaction_id, message, mode}
        """
        request = {
            "investor_pan": investor_pan, "scheme_code": scheme_code,
            "amount": amount, "order_type": order_type,
        }

        try:
            if self.is_stub:
                result = self._stub_place_order(investor_pan, scheme_code, amount, order_type,
                                                amc_code, sip_frequency, sip_date, folio_number, "Purchase")
            else:
                result = self._live_place_order(investor_pan, scheme_code, amount, order_type,
                                                amc_code, sip_frequency, sip_date, folio_number, "Purchase")
            self.log_request("place_purchase_order", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Place Redemption Order
    # =========================================================================

    def place_redemption_order(self, investor_pan, scheme_code, units=None, amount=None,
                               folio_number=None, all_units=False):
        """
        Place a redemption order.

        Args:
            investor_pan (str): PAN of investor
            scheme_code (str): Scheme code to redeem
            units (float, optional): Number of units to redeem
            amount (float, optional): Amount to redeem (alternative to units)
            folio_number (str, optional): Folio number
            all_units (bool): Redeem entire holding

        Returns:
            dict: {status, order_ref, transaction_id, message, mode}
        """
        request = {
            "investor_pan": investor_pan, "scheme_code": scheme_code,
            "units": units, "amount": amount, "all_units": all_units,
        }

        try:
            if self.is_stub:
                result = self._stub_place_order(investor_pan, scheme_code, units or amount or 0,
                                                "Redemption", None, None, None, folio_number, "Redemption")
            else:
                result = self._live_place_order(investor_pan, scheme_code, units or amount or 0,
                                                "Redemption", None, None, None, folio_number, "Redemption")
            self.log_request("place_redemption_order", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Place Switch Order
    # =========================================================================

    def place_switch_order(self, investor_pan, from_scheme, to_scheme, units=None, amount=None):
        """
        Place a switch order between two schemes.

        Args:
            investor_pan (str): PAN of investor
            from_scheme (str): Source scheme code
            to_scheme (str): Target scheme code
            units (float, optional): Units to switch
            amount (float, optional): Amount to switch

        Returns:
            dict: {status, order_ref, message, mode}
        """
        request = {"investor_pan": investor_pan, "from_scheme": from_scheme, "to_scheme": to_scheme}

        try:
            if self.is_stub:
                result = self._stub_switch_order(investor_pan, from_scheme, to_scheme, units, amount)
            else:
                result = self._live_place_switch(investor_pan, from_scheme, to_scheme, units, amount)
            self.log_request("place_switch_order", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Order Status
    # =========================================================================

    def get_order_status(self, order_ref):
        """Get the current status of an order."""
        request = {"order_ref": order_ref}

        try:
            if self.is_stub:
                result = self._stub_order_status(order_ref)
            else:
                result = self._live_order_status(order_ref)
            self.log_request("get_order_status", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Transaction History
    # =========================================================================

    def get_transaction_history(self, investor_pan, from_date=None, to_date=None):
        """Get transaction history across all AMCs."""
        from_date = from_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        to_date = to_date or today()
        request = {"investor_pan": investor_pan, "from_date": from_date, "to_date": to_date}

        try:
            if self.is_stub:
                result = self._stub_transaction_history(investor_pan, from_date, to_date)
            else:
                result = self._live_transaction_history(investor_pan, from_date, to_date)
            self.log_request("get_transaction_history", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Mandate Management
    # =========================================================================

    def register_sip_mandate(self, investor_pan, bank_account, ifsc_code, amount, frequency="Monthly"):
        """Register NACH/SIP auto-debit mandate."""
        request = {"investor_pan": investor_pan, "bank": bank_account[-4:], "amount": amount}

        try:
            if self.is_stub:
                result = self._stub_register_mandate(investor_pan, bank_account, ifsc_code, amount, frequency)
            else:
                result = self._live_register_mandate(investor_pan, bank_account, ifsc_code, amount, frequency)
            self.log_request("register_sip_mandate", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_place_order(self, investor_pan, scheme_code, amount, order_type,
                          amc_code, sip_frequency, sip_date, folio_number, txn_type):
        """Simulate order placement on BSE StarMF / NSE NMF II."""
        order_ref = f"MF{random_string(12).upper()}"
        txn_id = f"TXN{random_string(16).upper()}"
        nav_applicable = round(random.uniform(50, 500), 2)
        units = round(amount / nav_applicable, 3) if amount > 0 else 0

        statuses = STUB_ORDER_STATUSES
        if order_type == "SIP":
            status = "Confirmed"  # SIP registration confirmed immediately
        else:
            status = "Confirmed"

        return {
            "status": status,
            "mode": "stub",
            "platform": random.choice(["BSE StarMF", "NSE NMF II"]),
            "order_ref": order_ref,
            "transaction_id": txn_id,
            "transaction_type": txn_type,
            "order_type": order_type,
            "scheme_code": scheme_code,
            "investor_pan": investor_pan,
            "amount": amount,
            "units": units if txn_type != "Redemption" else None,
            "nav": nav_applicable,
            "folio_number": folio_number or f"{random.randint(1000000000, 9999999999)}",
            "order_date": today(),
            "expected_settlement": add_days(today(), 2).strftime("%Y-%m-%d") if txn_type == "Purchase" else add_days(today(), 3).strftime("%Y-%m-%d"),
            "brokerage": round(amount * 0.001, 2) if txn_type == "Purchase" else 0,
            "message": f"{txn_type} order placed successfully.",
        }

    def _stub_switch_order(self, investor_pan, from_scheme, to_scheme, units, amount):
        """Simulate switch order between schemes."""
        switch_ref = f"SW{random_string(12).upper()}"
        nav = round(random.uniform(50, 500), 2)

        return {
            "status": "Confirmed",
            "mode": "stub",
            "switch_ref": switch_ref,
            "from_scheme": from_scheme,
            "to_scheme": to_scheme,
            "investor_pan": investor_pan,
            "units": units,
            "amount": amount,
            "nav": nav,
            "order_date": today(),
            "expected_settlement": add_days(today(), 3).strftime("%Y-%m-%d"),
            "message": "Switch order placed successfully.",
        }

    def _stub_order_status(self, order_ref):
        """Simulate order status check."""
        random_stage = random.choice(["Allotted", "Settled"])
        nav = round(random.uniform(50, 500), 2)
        units = round(random.uniform(10, 500), 3)

        return {
            "status": "Success",
            "mode": "stub",
            "order_ref": order_ref,
            "order_stage": random_stage,
            "nav_applicable": nav,
            "units_allotted": units,
            "allotment_date": today(),
            "settlement_date": add_days(datetime.now(), 1).strftime("%Y-%m-%d"),
            "folio_number": f"{random.randint(1000000000, 9999999999)}",
        }

    def _stub_transaction_history(self, investor_pan, from_date, to_date):
        """Simulate transaction history."""
        txn_types = ["Purchase", "SIP Purchase", "Redemption", "Switch In", "Switch Out", "Dividend"]

        transactions = []
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        days = (end - start).days

        for i in range(min(days // 25 + 1, 15)):
            txn_date = start + timedelta(days=random.randint(1, max(days // 15, 1)))
            txn_type = random.choice(txn_types)
            amount = round(random.uniform(1000, 50000), 2)
            nav = round(random.uniform(50, 500), 2)

            transactions.append({
                "transaction_id": f"TXN{random_string(14).upper()}",
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_type": txn_type,
                "scheme_code": f"{random.randint(100000, 999999)}",
                "scheme_name": f"Sample Mutual Fund Scheme - Direct - Growth",
                "amount": amount,
                "nav": nav,
                "units": round(amount / nav, 3) if "Purchase" in txn_type or "SIP" in txn_type else None,
                "folio_number": f"{random.randint(1000000000, 9999999999)}",
                "order_ref": f"MF{random_string(10).upper()}",
            })

        transactions.sort(key=lambda x: x["transaction_date"], reverse=True)

        return {
            "status": "Success",
            "mode": "stub",
            "investor_pan": investor_pan,
            "period": {"from": from_date, "to": to_date},
            "total_transactions": len(transactions),
            "transactions": transactions,
        }

    def _stub_register_mandate(self, investor_pan, bank_account, ifsc_code, amount, frequency):
        """Simulate NACH/SIP mandate registration."""
        mandate_ref = f"NACH{random_string(12).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "mandate_ref": mandate_ref,
            "investor_pan": investor_pan,
            "bank_account_masked": f"XXXXXX{bank_account[-4:]}",
            "amount": amount,
            "frequency": frequency,
            "status": "Active",
            "registration_date": today(),
            "first_debit_date": add_days(datetime.now(), 30).strftime("%Y-%m-%d"),
            "message": "SIP mandate registered successfully. First debit scheduled.",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_place_order(self, investor_pan, scheme_code, amount, order_type, amc_code,
                          sip_frequency, sip_date, folio_number, txn_type):
        raise NotImplementedError("Live order placement requires BSE StarMF/NSE NMF II membership.")

    def _live_place_switch(self, investor_pan, from_scheme, to_scheme, units, amount):
        raise NotImplementedError("Live switch requires BSE StarMF/NMF II credentials.")

    def _live_order_status(self, order_ref):
        raise NotImplementedError("Live order status requires BSE StarMF/NMF II API access.")

    def _live_transaction_history(self, investor_pan, from_date, to_date):
        raise NotImplementedError("Live transaction history requires platform API access.")

    def _live_register_mandate(self, investor_pan, bank_account, ifsc_code, amount, frequency):
        raise NotImplementedError("Live mandate registration requires NACH/ECS API credentials.")
