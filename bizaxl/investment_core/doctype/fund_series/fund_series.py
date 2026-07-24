# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt


class FundSeries(Document):
    """Series/tranche for close-ended and drawdown-based funds."""

    def validate(self):
        self.validate_dates()
        self.validate_commitments()
        self.validate_waterfall()

    def validate_dates(self):
        if self.open_date and self.close_date and self.open_date >= self.close_date:
            frappe.throw("Open Date must be before Close Date.", title="Invalid Dates")

    def validate_commitments(self):
        if (
            self.minimum_commitment
            and self.maximum_commitment
            and self.minimum_commitment > self.maximum_commitment
        ):
            frappe.throw(
                "Minimum Commitment cannot exceed Maximum Commitment.",
                title="Invalid Limits",
            )
        if self.series_corpus_committed > self.series_corpus_target:
            frappe.throw(
                "Committed Corpus cannot exceed Corpus Target.",
                title="Over Committed",
            )

    def validate_waterfall(self):
        if (
            self.lp_split_percentage
            and self.gp_split_percentage
            and (self.lp_split_percentage + self.gp_split_percentage != 100)
        ):
            frappe.throw(
                "LP Split + GP Split must equal 100%.",
                title="Invalid Waterfall Split",
            )

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Open for Investment"

    def update_committed_corpus(self):
        """Recalculate total committed corpus from linked commitments."""
        commitments = frappe.get_all(
            "Commitment",
            filters={"fund_series": self.name, "docstatus": 1},
            fields=["sum(commitment_amount) as total"],
        )
        self.series_corpus_committed = flt(commitments[0].total) if commitments else 0
        self.save()

    def process_capital_call(self, call_percentage, due_date=None):
        """Create a capital call for this series."""
        commitments = frappe.get_all(
            "Commitment",
            filters={
                "fund_series": self.name,
                "docstatus": 1,
                "status": ["!=", "Defaulted"],
            },
            fields=["name", "investor", "commitment_amount"],
        )

        if not commitments:
            frappe.throw("No active commitments found for this series.")

        capital_call = frappe.get_doc(
            {
                "doctype": "Capital Call",
                "fund_series": self.name,
                "fund_master": self.fund_master,
                "call_date": today(),
                "due_date": due_date or today(),
                "call_percentage": call_percentage,
                "notes": f"Capital call {call_percentage}% of committed capital.",
            }
        )

        for c in commitments:
            call_amount = flt(c["commitment_amount"]) * (call_percentage / 100)
            capital_call.append(
                "call_details",
                {
                    "investor": c["investor"],
                    "commitment": c["name"],
                    "committed_amount": c["commitment_amount"],
                    "call_amount": call_amount,
                    "status": "Pending",
                },
            )

        capital_call.insert()
        capital_call.submit()

        self.total_capital_call += capital_call.total_call_amount
        self.total_capital_call_percentage = (
            (self.total_capital_call / self.series_corpus_target) * 100
            if self.series_corpus_target
            else 0
        )
        self.save()

        return capital_call


@frappe.whitelist()
def get_series_by_fund(fund_master):
    """API: Get all series for a fund."""
    return frappe.get_all(
        "Fund Series",
        filters={"fund_master": fund_master},
        fields=[
            "name",
            "series_name",
            "series_code",
            "series_type",
            "status",
            "series_corpus_target",
            "series_corpus_committed",
            "total_capital_call",
            "open_date",
            "close_date",
        ],
        order_by="open_date desc",
    )
