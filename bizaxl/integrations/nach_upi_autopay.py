# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
NACH / UPI AutoPay Connector — Stub-to-Live Integration

eNACH mandate for SIP auto-debit and UPI AutoPay for recurring investments.

Supports:
1. eNACH Mandate — Register, modify, revoke NACH mandates for SIP auto-debit
2. UPI AutoPay — Register UPI AutoPay mandates via VPA (Virtual Payment Address)
3. Mandate Status — Check mandate status, history, and upcoming debits
4. Debit Processing — Process actual debit against active mandates
5. Bounce/Reconciliation — Track failed debits and reconciliation

Stub mode: Simulates NPCI NACH and UPI AutoPay responses
Live mode: Integrates with actual NPCI NACH/UPI AutoPay API via bank/sponsor bank
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, add_days, add_months
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


class AutoPayConnector(BaseConnector):
    """NACH / UPI AutoPay integration — mandates, debits, reconciliation."""

    connector_name = "nach_upi_autopay"
    label = "NACH / UPI AutoPay"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: eNACH Mandate
    # =========================================================================

    def register_nach_mandate(self, mandate_data):
        """Register eNACH mandate for SIP auto-debit."""
        request = {
            "pan": mandate_data.get("pan"),
            "bank": mandate_data.get("bank_account")[-4:],
            "amount": mandate_data.get("amount"),
        }

        try:
            if self.is_stub:
                result = self._stub_register_nach(mandate_data)
            else:
                result = self._live_register_nach(mandate_data)
            self.log_request("register_nach_mandate", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def revoke_nach_mandate(self, mandate_ref):
        """Revoke an existing NACH mandate."""
        try:
            if self.is_stub:
                result = self._stub_revoke_nach(mandate_ref)
            else:
                result = self._live_revoke_nach(mandate_ref)
            self.log_request("revoke_nach_mandate", {"mandate": mandate_ref}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: UPI AutoPay
    # =========================================================================

    def register_upi_autopay(self, vpa, amount, frequency="Monthly"):
        """Register UPI AutoPay mandate via VPA."""
        request = {"vpa": vpa, "amount": amount, "frequency": frequency}

        try:
            if self.is_stub:
                result = self._stub_register_upi(vpa, amount, frequency)
            else:
                result = self._live_register_upi(vpa, amount, frequency)
            self.log_request("register_upi_autopay", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Mandate Status
    # =========================================================================

    def get_mandate_status(self, mandate_ref):
        """Get status of any mandate (NACH or UPI)."""
        try:
            if self.is_stub:
                result = self._stub_mandate_status(mandate_ref)
            else:
                result = self._live_mandate_status(mandate_ref)
            self.log_request("get_mandate_status", {"mandate": mandate_ref}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_mandate_history(self, pan_number=None, vpa=None):
        """Get mandate history for a PAN or VPA."""
        request = {"pan": pan_number, "vpa": vpa}

        try:
            if self.is_stub:
                result = self._stub_mandate_history(pan_number, vpa)
            else:
                result = self._live_mandate_history(pan_number, vpa)
            self.log_request("get_mandate_history", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Debit Processing
    # =========================================================================

    def process_debit(self, mandate_ref, amount):
        """Process a debit against an active mandate."""
        try:
            if self.is_stub:
                result = self._stub_process_debit(mandate_ref, amount)
            else:
                result = self._live_process_debit(mandate_ref, amount)
            self.log_request("process_debit", {"mandate": mandate_ref, "amount": amount}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_bounce_report(self, from_date=None, to_date=None):
        """Get bounced debit report."""
        from_date = from_date or add_months(today(), -1)
        to_date = to_date or today()
        request = {"from": from_date, "to": to_date}

        try:
            if self.is_stub:
                result = self._stub_bounce_report(from_date, to_date)
            else:
                result = self._live_bounce_report(from_date, to_date)
            self.log_request("get_bounce_report", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_register_nach(self, mandate_data):
        """Simulate eNACH mandate registration."""
        mandate_ref = f"NACH{random_string(14).upper()}"
        umrn = f"{random.randint(100000000001, 999999999999)}"

        return {
            "status": "Success",
            "mode": "stub",
            "mandate_ref": mandate_ref,
            "umrn": umrn,
            "type": "eNACH",
            "amount": mandate_data.get("amount"),
            "frequency": mandate_data.get("frequency", "Monthly"),
            "start_date": mandate_data.get("start_date", today()),
            "end_date": mandate_data.get("end_date") or add_months(today(), 60),
            "max_amount": mandate_data.get("max_amount", mandate_data.get("amount")),
            "bank_account_masked": f"XXXXXX{mandate_data.get('bank_account', '')[-4:]}",
            "ifsc": mandate_data.get("ifsc"),
            "status": "Active",
            "registered_at": now_datetime().isoformat(),
            "first_debit_date": add_days(datetime.now(), 30).strftime("%Y-%m-%d"),
            "message": "eNACH mandate registered successfully. UMRN generated.",
        }

    def _stub_revoke_nach(self, mandate_ref):
        """Simulate mandate revocation."""
        return {
            "status": "Success",
            "mode": "stub",
            "mandate_ref": mandate_ref,
            "revoked_at": now_datetime().isoformat(),
            "status": "Revoked",
            "message": "eNACH mandate revoked successfully.",
        }

    def _stub_register_upi(self, vpa, amount, frequency):
        """Simulate UPI AutoPay registration."""
        mandate_ref = f"UPI{random_string(14).upper()}"

        return {
            "status": "Success",
            "mode": "stub",
            "mandate_ref": mandate_ref,
            "type": "UPI AutoPay",
            "vpa": vpa,
            "amount": amount,
            "frequency": frequency,
            "status": "Active",
            "registered_at": now_datetime().isoformat(),
            "first_debit_date": add_days(datetime.now(), 1).strftime("%Y-%m-%d"),
            "message": "UPI AutoPay mandate registered at NPCI. First debit scheduled.",
        }

    def _stub_mandate_status(self, mandate_ref):
        """Simulate mandate status check."""
        return {
            "status": "Success",
            "mode": "stub",
            "mandate_ref": mandate_ref,
            "type": "eNACH" if mandate_ref.startswith("NACH") else "UPI AutoPay",
            "mandate_status": "Active",
            "total_debits": random.randint(3, 24),
            "successful_debits": random.randint(2, 22),
            "failed_debits": random.randint(0, 2),
            "last_debit_date": add_days(datetime.now(), -random.randint(5, 30)).strftime("%Y-%m-%d"),
            "last_debit_amount": round(random.uniform(1000, 10000), 2),
            "next_debit_date": add_days(datetime.now(), random.randint(1, 28)).strftime("%Y-%m-%d"),
        }

    def _stub_mandate_history(self, pan_number, vpa):
        """Simulate mandate history."""
        mandates = []
        for i in range(random.randint(1, 5)):
            is_nach = random.choice([True, False])
            amt = round(random.uniform(1000, 25000), 2)
            mandates.append({
                "mandate_ref": f"{'NACH' if is_nach else 'UPI'}{random_string(10).upper()}",
                "type": "eNACH" if is_nach else "UPI AutoPay",
                "amount": amt,
                "frequency": random.choice(["Monthly", "Quarterly"]),
                "status": random.choice(["Active", "Active", "Active", "Revoked"]),
                "created_date": add_days(datetime.now(), -random.randint(30, 365)).strftime("%Y-%m-%d"),
                "last_debit": add_days(datetime.now(), -random.randint(5, 30)).strftime("%Y-%m-%d"),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "pan": pan_number,
            "vpa": vpa,
            "total_mandates": len(mandates),
            "active_mandates": sum(1 for m in mandates if m["status"] == "Active"),
            "mandates": mandates,
        }

    def _stub_process_debit(self, mandate_ref, amount):
        """Simulate debit processing."""
        success = random.random() > 0.1  # 90% success rate
        if success:
            return {
                "status": "Success",
                "mode": "stub",
                "mandate_ref": mandate_ref,
                "debit_ref": f"DB-{random_string(14).upper()}",
                "amount": amount,
                "debit_date": today(),
                "status": "Settled",
                "utr": f"UTR{random_string(12).upper()}",
                "message": "Debit processed successfully.",
            }
        return {
            "status": "Failed",
            "mode": "stub",
            "mandate_ref": mandate_ref,
            "amount": amount,
            "debit_date": today(),
            "status": "Bounced",
            "bounce_reason": random.choice([
                "Insufficient Funds", "Account Closed",
                "Mandate Revoked", "Technical Issue", "Limit Exceeded",
            ]),
            "message": "Debit failed. Reason: Insufficient Funds.",
        }

    def _stub_bounce_report(self, from_date, to_date):
        """Simulate bounce report."""
        bounces = []
        for i in range(random.randint(0, 5)):
            bounces.append({
                "mandate_ref": f"NACH{random_string(10).upper()}",
                "debit_ref": f"DB{random_string(12).upper()}",
                "amount": round(random.uniform(1000, 15000), 2),
                "attempt_date": add_days(datetime.now(), -random.randint(1, 30)).strftime("%Y-%m-%d"),
                "bounce_reason": random.choice([
                    "Insufficient Funds", "Account Closed", "Technical Issue",
                ]),
                "retry_status": random.choice(["Not Retried", "Retried - Success", "Retried - Failed"]),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "period": {"from": from_date, "to": to_date},
            "total_bounces": len(bounces),
            "total_bounce_amount": round(sum(b["amount"] for b in bounces), 2),
            "bounces": bounces,
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_register_nach(self, mandate_data):
        raise NotImplementedError("Live eNACH requires NPCI NACH API credentials via sponsor bank.")

    def _live_revoke_nach(self, mandate_ref):
        raise NotImplementedError("Live NACH revocation requires bank API credentials.")

    def _live_register_upi(self, vpa, amount, frequency):
        raise NotImplementedError("Live UPI AutoPay requires NPCI UPI API credentials.")

    def _live_mandate_status(self, mandate_ref):
        raise NotImplementedError("Live mandate status requires NPCI API access.")

    def _live_mandate_history(self, pan_number, vpa):
        raise NotImplementedError("Live mandate history requires NPCI API access.")

    def _live_process_debit(self, mandate_ref, amount):
        raise NotImplementedError("Live debit requires bank/NPCI API credentials.")

    def _live_bounce_report(self, from_date, to_date):
        raise NotImplementedError("Live bounce report requires bank API access.")
