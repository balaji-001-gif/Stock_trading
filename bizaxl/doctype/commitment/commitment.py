# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Commitment(Document):
    """Investor capital commitment to a fund series for drawdown-based funds."""

    def validate(self):
        self.validate_amounts()
        self.set_remaining()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Active"

    def validate_amounts(self):
        if self.commitment_amount <= 0:
            frappe.throw(
                "Commitment amount must be greater than zero.",
                title="Invalid Amount",
            )

    def set_remaining(self):
        self.remaining_commitment = flt(self.commitment_amount) - flt(self.total_called)
        if self.commitment_amount:
            self.commitment_fulfilled_percentage = flt(
                (flt(self.total_called) / flt(self.commitment_amount)) * 100
            )
        self.total_outstanding = flt(self.total_called) - flt(self.total_paid)

    def record_drawdown(self, call_amount, paid_amount=0):
        """Record a drawdown against this commitment."""
        self.total_called = flt(self.total_called) + flt(call_amount)
        if paid_amount:
            self.total_paid = flt(self.total_paid) + flt(paid_amount)
        self.set_remaining()
        self.save()


@frappe.whitelist()
def get_commitments_by_series(fund_series, status=None):
    """API: Get commitments for a fund series."""
    filters = {"fund_series": fund_series}
    if status:
        filters["status"] = status

    return frappe.get_all(
        "Commitment",
        filters=filters,
        fields=[
            "name",
            "investor",
            "commitment_amount",
            "total_called",
            "total_paid",
            "remaining_commitment",
            "commitment_fulfilled_percentage",
            "status",
        ],
        order_by="commitment_date desc",
    )


@frappe.whitelist()
def get_investor_commitments(investor):
    """API: Get all commitments for an investor."""
    return frappe.get_all(
        "Commitment",
        filters={"investor": investor, "docstatus": 1},
        fields=[
            "name",
            "fund_master",
            "fund_series",
            "commitment_amount",
            "remaining_commitment",
            "status",
        ],
        order_by="commitment_date desc",
    )
