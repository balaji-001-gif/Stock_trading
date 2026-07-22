# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CapitalAccountStatement(Document):
    """Investor capital account statement with activity and returns."""

    def validate(self):
        self.calculate_closing_capital()
        self.calculate_total_return()
        self.calculate_excess_return()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Generated"

    def calculate_closing_capital(self):
        self.closing_capital = (
            flt(self.opening_capital)
            + flt(self.contributions)
            - flt(self.distributions)
            + flt(self.accrued_income)
            + flt(self.unrealized_pnl)
            + flt(self.realized_pnl)
        )

    def calculate_total_return(self):
        if self.closing_capital and self.opening_capital:
            self.total_return = flt(self.closing_capital) - flt(self.opening_capital)

    def calculate_excess_return(self):
        if self.return_percentage is not None and self.benchmark_return is not None:
            self.excess_return = flt(self.return_percentage) - flt(self.benchmark_return)


@frappe.whitelist()
def get_investor_statements(investor):
    """API: Get capital account statements for an investor."""
    return frappe.get_all(
        "Capital Account Statement",
        filters={"investor": investor},
        fields=[
            "name", "fund_master", "share_class", "statement_date",
            "statement_type", "opening_capital", "closing_capital",
            "total_return", "return_percentage", "status",
        ],
        order_by="statement_date desc",
    )
