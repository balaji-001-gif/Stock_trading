# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class CorporateActions(Document):
    """Corporate action processing — bonus, split, dividend, merger."""

    def validate(self):
        self.validate_ratio()
        self.validate_dates()

    def validate_ratio(self):
        if self.ratio_numerator and self.ratio_numerator <= 0:
            frappe.throw("Ratio numerator must be greater than zero.")
        if self.ratio_denominator and self.ratio_denominator <= 0:
            frappe.throw("Ratio denominator must be greater than zero.")

    def validate_dates(self):
        if self.record_date and self.ex_date and self.ex_date < self.record_date:
            frappe.throw("Ex-date cannot be before record date.")

    def process_action(self):
        """Process the corporate action against all affected holdings."""
        holdings = frappe.get_all(
            "Holdings Register",
            filters={
                "fund_master": self.fund_master,
                "security_id": self.security_id,
                "status": "Active",
            },
        )

        ratio = (
            flt(self.ratio_numerator) / flt(self.ratio_denominator)
            if self.ratio_denominator
            else 0
        )

        success = 0
        errors = []

        for h in holdings:
            try:
                holding = frappe.get_doc("Holdings Register", h.name)
                holding.apply_corporate_action(self.action_type, ratio)
                success += 1
            except Exception as e:
                errors.append(f"Holding {h.name}: {str(e)}")

        self.processed = 1
        self.processed_date = today()
        self.processed_by = frappe.session.user
        self.affected_holdings_count = success
        self.pending_holdings_count = len(holdings) - success

        if errors:
            self.error_log = "\n".join(errors)

        self.save()
        return {"processed": success, "errors": errors, "total": len(holdings)}


@frappe.whitelist()
def apply_corporate_action(corporate_action_name):
    """API: Process a corporate action."""
    ca = frappe.get_doc("Corporate Actions", corporate_action_name)
    return ca.process_action()


@frappe.whitelist()
def get_pending_actions(fund_master):
    """API: Get pending corporate actions for a fund."""
    return frappe.get_all(
        "Corporate Actions",
        filters={
            "fund_master": fund_master,
            "status": ["in", ["Announced", "Approved", "Record Date Passed"]],
            "processed": 0,
        },
        fields=[
            "name", "action_type", "security_id", "security_name",
            "record_date", "ex_date", "ratio_description",
            "dividend_amount", "status",
        ],
        order_by="record_date asc",
    )
