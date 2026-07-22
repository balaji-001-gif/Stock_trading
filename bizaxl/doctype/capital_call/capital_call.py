# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class CapitalCall(Document):
    """Capital call / drawdown request for AIF, PE, VC funds."""

    def validate(self):
        self.validate_dates()
        self.calculate_totals()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Sent"

    def on_submit(self):
        self.update_commitments()

    def validate_dates(self):
        if self.due_date and self.call_date and self.due_date <= self.call_date:
            frappe.throw(
                "Due Date must be after Call Date.",
                title="Invalid Dates",
            )

    def calculate_totals(self):
        """Calculate total call amount and update summary."""
        self.total_call_amount = sum(
            flt(d.call_amount) for d in self.call_details
        )
        self.total_received_amount = sum(
            flt(d.paid_amount) for d in self.call_details
        )
        self.total_investors = len(self.call_details)
        self.total_responded = sum(
            1 for d in self.call_details if d.status in ("Paid", "Late")
        )
        self.defaults_count = sum(
            1 for d in self.call_details if d.status == "Defaulted"
        )
        self.late_payments_count = sum(
            1 for d in self.call_details if d.status == "Late"
        )
        if self.total_investors:
            self.collection_rate = flt(
                (self.total_responded / self.total_investors) * 100
            )

    def update_commitments(self):
        """Update linked commitment records with drawdown info."""
        for detail in self.call_details:
            if detail.commitment:
                # Use db_set_value to avoid N+1 full document loads
                commitment_doc = frappe.get_doc("Commitment", detail.commitment)
                new_called = flt(commitment_doc.total_called) + flt(detail.call_amount)
                new_paid = flt(commitment_doc.total_paid) + flt(detail.paid_amount)                    commitment_amount = flt(commitment_doc.commitment_amount)
                    remaining = commitment_amount - new_called
                    fulfilled_pct = (new_called / commitment_amount * 100) if commitment_amount else 0

                    frappe.db.set_value(
                        "Commitment",
                        detail.commitment,
                        {
                            "total_called": new_called,
                            "total_paid": new_paid,
                            "last_drawdown_date": self.call_date,
                            "total_outstanding": new_called - new_paid,
                            "remaining_commitment": max(remaining, 0),
                            "commitment_fulfilled_percentage": fulfilled_pct,
                        },
                    )


@frappe.whitelist()
def create_capital_call(fund_series, call_percentage, due_date=None):
    """API: Create a capital call for a fund series."""
    series = frappe.get_doc("Fund Series", fund_series)
    return series.process_capital_call(call_percentage, due_date)


@frappe.whitelist()
def get_capital_calls_by_series(fund_series):
    """API: Get capital calls for a fund series."""
    return frappe.get_all(
        "Capital Call",
        filters={"fund_series": fund_series},
        fields=[
            "name",
            "call_date",
            "due_date",
            "call_percentage",
            "total_call_amount",
            "total_received_amount",
            "collection_rate",
            "status",
        ],
        order_by="call_date desc",
    )


@frappe.whitelist()
def record_payment(capital_call, detail_row, paid_amount, payment_date=None):
    """API: Record a payment against a capital call line item."""
    cc = frappe.get_doc("Capital Call", capital_call)
    for detail in cc.call_details:
        if detail.idx == int(detail_row):
            detail.paid_amount = flt(paid_amount)
            detail.payment_date = payment_date or today()
            if detail.paid_amount >= detail.call_amount:
                detail.status = "Paid"
            elif detail.paid_amount > 0:
                detail.status = "Late"
            break
    cc.save()
    return cc
