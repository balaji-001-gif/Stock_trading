# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
SWIFT / SFTP Custodian Connector — Stub-to-Live Integration

Daily position and cash reconciliation feeds from custodians.
Processes MT940/MT950 message formats and SFTP file exchange.

Supports:
1. MT940 — Customer Statement Message (cash transactions)
2. MT950 — Statement of Holdings (position statement)
3. SFTP File Exchange — Automated file pick up from custodian SFTP
4. Position Reconciliation — Compare custodian vs internal positions
5. Cash Reconciliation — Compare custodian vs internal cash balances
6. Corporate Actions Feed — Automated corporate action updates from custodian

Stub mode: Generates realistic MT940/MT950 messages and reconciliation reports
Live mode: Connects to custodian SFTP servers and processes SWIFT messages
"""

import frappe
import json
import random
import io
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated holdings by security type
STUB_HOLDINGS = [
    {"isin": "INE002A01018", "name": "Reliance Industries", "quantity": random.randint(500, 5000), "asset_class": "Equity"},
    {"isin": "INE040A01034", "name": "HDFC Bank", "quantity": random.randint(1000, 10000), "asset_class": "Equity"},
    {"isin": "INE009A01021", "name": "Infosys", "quantity": random.randint(800, 8000), "asset_class": "Equity"},
    {"isin": "INE030A01027", "name": "ICICI Bank", "quantity": random.randint(1200, 12000), "asset_class": "Equity"},
    {"isin": "INE397D01024", "name": "LTIMindtree", "quantity": random.randint(200, 2000), "asset_class": "Equity"},
    {"isin": "IN0020230101", "name": "7.18% GS 2033", "quantity": 500000, "asset_class": "Government Bond"},
    {"isin": "INE103A01014", "name": "6.79% GS 2029", "quantity": 350000, "asset_class": "Government Bond"},
    {"isin": "INE113F23014", "name": "9.50% NCD Tata Capital", "quantity": 100000, "asset_class": "Corporate Bond"},
    {"isin": "INE454A05010", "name": "SBI Magnum Midcap Fund", "quantity": 25000, "asset_class": "Mutual Fund"},
    {"isin": "INE064J01018", "name": "HDFC Balanced Advantage Fund", "quantity": 18000, "asset_class": "Mutual Fund"},
]


class CustodianConnector(BaseConnector):
    """SWIFT / SFTP Custodian integration — MT940/MT950, reconciliation, file exchange."""

    connector_name = "swift_sftp_custodian"
    label = "SWIFT / SFTP Custodian"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Holdings & Positions
    # =========================================================================

    def fetch_positions(self, portfolio_code, as_of_date=None):
        """Fetch position statement (MT950 equivalent) from custodian."""
        try:
            if self.is_stub:
                result = self._stub_fetch_positions(portfolio_code, as_of_date)
            else:
                result = self._live_fetch_positions(portfolio_code, as_of_date)
            self.log_request("fetch_positions", {"portfolio": portfolio_code, "as_of_date": as_of_date or today()}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def fetch_transactions(self, portfolio_code, from_date, to_date):
        """Fetch cash/security transactions (MT940 equivalent) from custodian."""
        try:
            if self.is_stub:
                result = self._stub_fetch_transactions(portfolio_code, from_date, to_date)
            else:
                result = self._live_fetch_transactions(portfolio_code, from_date, to_date)
            self.log_request("fetch_transactions",
                             {"portfolio": portfolio_code, "from": from_date, "to": to_date}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def fetch_cash_balance(self, portfolio_code, as_of_date=None):
        """Fetch cash balance from custodian."""
        try:
            if self.is_stub:
                result = self._stub_cash_balance(portfolio_code, as_of_date)
            else:
                result = self._live_cash_balance(portfolio_code, as_of_date)
            self.log_request("fetch_cash_balance", {"portfolio": portfolio_code}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Reconciliation
    # =========================================================================

    def reconcile_positions(self, portfolio_code, internal_holdings, as_of_date=None):
        """Compare custodian positions against internal holdings record."""
        try:
            if self.is_stub:
                result = self._stub_reconcile_positions(portfolio_code, internal_holdings, as_of_date)
            else:
                result = self._live_reconcile_positions(portfolio_code, internal_holdings, as_of_date)
            self.log_request("reconcile_positions",
                             {"portfolio": portfolio_code, "internal_count": len(internal_holdings or [])}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def reconcile_cash(self, portfolio_code, internal_balance, as_of_date=None):
        """Reconcile custodian cash balance against internal records."""
        try:
            if self.is_stub:
                result = self._stub_reconcile_cash(portfolio_code, internal_balance, as_of_date)
            else:
                result = self._live_reconcile_cash(portfolio_code, internal_balance, as_of_date)
            self.log_request("reconcile_cash", {"portfolio": portfolio_code, "internal_balance": internal_balance}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: File Exchange
    # =========================================================================

    def fetch_sftp_files(self, remote_path, file_pattern=None):
        """List and fetch files from custodian SFTP server."""
        try:
            if self.is_stub:
                result = self._stub_sftp_files(remote_path, file_pattern)
            else:
                result = self._live_sftp_files(remote_path, file_pattern)
            self.log_request("fetch_sftp_files", {"remote_path": remote_path, "pattern": file_pattern}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def process_mt940_message(self, message_text):
        """Parse and process an MT940 SWIFT message."""
        try:
            if self.is_stub:
                result = self._stub_process_mt940(message_text)
            else:
                result = self._live_process_mt940(message_text)
            self.log_request("process_mt940", {"message_length": len(message_text)}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_fetch_positions(self, portfolio_code, as_of_date):
        """Simulate MT950 position statement."""
        positions = []
        for h in STUB_HOLDINGS:
            price = random.uniform(50, 3500)
            positions.append({
                "isin": h["isin"],
                "security_name": h["name"],
                "asset_class": h["asset_class"],
                "quantity": h["quantity"],
                "price": round(price, 2),
                "market_value": round(h["quantity"] * price, 2),
                "accrued_interest": round(random.uniform(0, h["quantity"] * 0.02), 2) if "Bond" in h["asset_class"] else 0,
                "cost_basis": round(h["quantity"] * price * random.uniform(0.7, 1.1), 2),
                "unrealized_pnl": round(h["quantity"] * price * random.uniform(-0.15, 0.20), 2),
                "currency": "INR",
                "custodian_code": f"CUS-{random_string(6).upper()}",
                "pricing_date": as_of_date or today(),
            })

        total_value = sum(p["market_value"] for p in positions)
        cash_balance = random.uniform(100000, 20000000)

        return {
            "status": "Success",
            "mode": "stub",
            "portfolio_code": portfolio_code,
            "as_of_date": as_of_date or today(),
            "total_securities": len(positions),
            "total_market_value": round(total_value, 2),
            "cash_balance": round(cash_balance, 2),
            "portfolio_value": round(total_value + cash_balance, 2),
            "positions": positions,
            "message_type": "MT950",
            "custodian_ref": f"CUST-{random_string(14).upper()}",
        }

    def _stub_fetch_transactions(self, portfolio_code, from_date, to_date):
        """Simulate MT940 cash transactions."""
        txn_types = [
            ("Dividend Received", "CREDIT"), ("Interest Received", "CREDIT"),
            ("Redemption Proceeds", "CREDIT"), ("Coupon Payment", "CREDIT"),
            ("Equity Purchase", "DEBIT"), ("Bond Purchase", "DEBIT"),
            ("Management Fee", "DEBIT"), ("Custody Fee", "DEBIT"),
            ("Subscription", "CREDIT"), ("Withdrawal", "DEBIT"),
        ]
        transactions = []
        days_range = (get_datetime(to_date) - get_datetime(from_date)).days or 30
        num_txns = min(random.randint(5, 15), max(1, days_range))

        for i in range(num_txns):
            txn_type, direction = random.choice(txn_types)
            amount = round(random.uniform(10000, 5000000), 2)
            transactions.append({
                "transaction_ref": f"TXN-{random_string(12).upper()}",
                "type": txn_type,
                "direction": direction,
                "amount": amount if direction == "CREDIT" else -amount,
                "currency": "INR",
                "value_date": (get_datetime(from_date) + timedelta(days=random.randint(0, days_range))).strftime("%Y-%m-%d"),
                "trade_date": (get_datetime(from_date) + timedelta(days=random.randint(0, days_range))).strftime("%Y-%m-%d"),
                "description": f"{txn_type} - {random.choice(['HDFC Bank', 'Reliance', 'ICICI', 'SBI', 'Axis'])}",
                "status": random.choice(["Settled", "Settled", "Settled", "Pending"]),
                "beneficiary": portfolio_code,
            })

        # Sort by value_date
        transactions.sort(key=lambda t: t["value_date"])

        return {
            "status": "Success",
            "mode": "stub",
            "portfolio_code": portfolio_code,
            "from_date": from_date,
            "to_date": to_date,
            "total_transactions": len(transactions),
            "total_credits": round(sum(t["amount"] for t in transactions if t["direction"] == "CREDIT"), 2),
            "total_debits": round(abs(sum(t["amount"] for t in transactions if t["direction"] == "DEBIT")), 2),
            "net_flow": round(sum(t["amount"] for t in transactions), 2),
            "transactions": transactions,
            "message_type": "MT940",
        }

    def _stub_cash_balance(self, portfolio_code, as_of_date):
        """Simulate cash balance from custodian."""
        return {
            "status": "Success",
            "mode": "stub",
            "portfolio_code": portfolio_code,
            "as_of_date": as_of_date or today(),
            "currency": "INR",
            "opening_balance": round(random.uniform(500000, 10000000), 2),
            "credits": round(random.uniform(100000, 5000000), 2),
            "debits": round(random.uniform(100000, 4000000), 2),
            "closing_balance": round(random.uniform(500000, 12000000), 2),
            "available_balance": round(random.uniform(400000, 11000000), 2),
            "pending_settlements": round(random.uniform(0, 2000000), 2),
            "account_number": f"CASH-{random_string(10).upper()}",
            "account_type": "Custody Cash Account",
        }

    def _stub_reconcile_positions(self, portfolio_code, internal_holdings, as_of_date):
        """Simulate position reconciliation."""
        custodian_positions = self._stub_fetch_positions(portfolio_code, as_of_date)["positions"]
        matches = []
        breaks = []

        internal_map = {h.get("isin"): h for h in (internal_holdings or [])}

        for cp in custodian_positions:
            ih = internal_map.get(cp["isin"])
            if ih:
                diff = abs(cp["quantity"] - ih.get("quantity", 0))
                if diff > 0:
                    breaks.append({
                        "isin": cp["isin"],
                        "security_name": cp["security_name"],
                        "custodian_qty": cp["quantity"],
                        "internal_qty": ih.get("quantity", 0),
                        "difference": cp["quantity"] - ih.get("quantity", 0),
                        "difference_value": round(diff * cp["price"], 2),
                        "break_type": "Quantity Mismatch",
                    })
                else:
                    matches.append({
                        "isin": cp["isin"],
                        "security_name": cp["security_name"],
                        "quantity": cp["quantity"],
                        "status": "Matched",
                    })
            else:
                breaks.append({
                    "isin": cp["isin"],
                    "security_name": cp["security_name"],
                    "custodian_qty": cp["quantity"],
                    "internal_qty": 0,
                    "difference": cp["quantity"],
                    "difference_value": round(cp["quantity"] * cp["price"], 2),
                    "break_type": "Missing in Internal Records",
                })

        total_diff_value = sum(b["difference_value"] for b in breaks)
        return {
            "status": "Success",
            "mode": "stub",
            "portfolio_code": portfolio_code,
            "as_of_date": as_of_date or today(),
            "total_positions_checked": len(custodian_positions),
            "matched": len(matches),
            "breaks": len(breaks),
            "total_difference_value": round(total_diff_value, 2),
            "reconciliation_status": "Matched" if len(breaks) == 0 else "Breaks Found",
            "matched_positions": matches,
            "break_positions": breaks,
            "reconciliation_ref": f"RECON-{random_string(10).upper()}",
        }

    def _stub_reconcile_cash(self, portfolio_code, internal_balance, as_of_date):
        """Simulate cash reconciliation."""
        custodian_balance = self._stub_cash_balance(portfolio_code, as_of_date)
        custodian_closing = custodian_balance["closing_balance"]
        internal_closing = internal_balance or random.uniform(500000, 10000000)
        diff = round(custodian_closing - internal_closing, 2)

        return {
            "status": "Success",
            "mode": "stub",
            "portfolio_code": portfolio_code,
            "as_of_date": as_of_date or today(),
            "custodian_balance": custodian_closing,
            "internal_balance": internal_closing,
            "difference": diff,
            "reconciled": abs(diff) < 100,
            "pending_items": [] if abs(diff) < 100 else [
                {"type": random.choice(["Uncleared Cheque", "Pending Transfer", "Fee Deduction"]),
                 "amount": round(abs(diff) * random.uniform(0.3, 0.7), 2),
                 "description": "Still in settlement cycle"}
            ],
        }

    def _stub_sftp_files(self, remote_path, file_pattern):
        """Simulate SFTP file listing."""
        file_types = {
            "MT940": {"prefix": "STMT", "extension": "940"},
            "MT950": {"prefix": "POS", "extension": "950"},
            "CORP_ACTION": {"prefix": "CA", "extension": "csv"},
            "TRADE_CONFIRM": {"prefix": "TC", "extension": "csv"},
        }

        files = []
        for ftype, config in file_types.items():
            for i in range(random.randint(0, 3)):
                file_date = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y%m%d")
                files.append({
                    "filename": f"{config['prefix']}_{file_date}_{random_string(6).upper()}.{config['extension']}",
                    "file_type": ftype,
                    "file_size_bytes": random.randint(5000, 500000),
                    "last_modified": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    "remote_path": f"{remote_path}/{ftype.lower()}",
                    "downloaded": random.choice([True, False]),
                })

        # Apply file_pattern filter
        if file_pattern:
            files = [f for f in files if file_pattern.lower() in f["filename"].lower()]

        return {
            "status": "Success",
            "mode": "stub",
            "remote_path": remote_path,
            "files_found": len(files),
            "files": sorted(files, key=lambda f: f["last_modified"], reverse=True),
        }

    def _stub_process_mt940(self, message_text):
        """Simulate MT940 message parsing."""
        # Parse basic SWIFT MT940 structure
        parsed = {
            "sender": message_text[message_text.find(":20:")+4:message_text.find(":20:")+20] if ":20:" in message_text else "CUSTODIAN_BANK",
            "account_number": message_text[message_text.find(":25:")+4:message_text.find(":25:")+20] if ":25:" in message_text else "ACC-001",
            "currency": "INR",
            "statement_number": random.randint(1, 999),
            "opening_balance": round(random.uniform(500000, 5000000), 2),
            "closing_balance": round(random.uniform(500000, 5500000), 2),
            "transactions_extracted": random.randint(3, 12),
            "parsing_success": True,
        }
        return {
            "status": "Success",
            "mode": "stub",
            "message_type": "MT940",
            "parsed_data": parsed,
            "message_format": "SWIFT FIN",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_fetch_positions(self, portfolio_code, as_of_date):
        raise NotImplementedError("Live custodian positions require SFTP/custodian API credentials.")

    def _live_fetch_transactions(self, portfolio_code, from_date, to_date):
        raise NotImplementedError("Live custodian transactions require SFTP/custodian API credentials.")

    def _live_cash_balance(self, portfolio_code, as_of_date):
        raise NotImplementedError("Live custodian cash balance requires API credentials.")

    def _live_reconcile_positions(self, portfolio_code, internal_holdings, as_of_date):
        raise NotImplementedError("Live reconciliation requires both custodian and internal data feeds.")

    def _live_reconcile_cash(self, portfolio_code, internal_balance, as_of_date):
        raise NotImplementedError("Live cash reconciliation requires custodian API credentials.")

    def _live_sftp_files(self, remote_path, file_pattern):
        raise NotImplementedError("Live SFTP requires SSH key credentials and server configuration.")

    def _live_process_mt940(self, message_text):
        raise NotImplementedError("Live MT940 parsing requires SWIFT message validation setup.")
