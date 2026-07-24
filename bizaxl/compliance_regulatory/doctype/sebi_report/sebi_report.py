# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff


class SEBIReport(Document):
    """Regulatory filing report for SEBI, RBI, PFRDA, and other regulators."""

    def validate(self):
        self.check_deadline()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "In Progress"

    def check_deadline(self):
        """Alert if filing is approaching or past deadline."""
        if self.filing_deadline:
            days_remaining = date_diff(self.filing_deadline, today())
            if days_remaining < 0:
                frappe.msgprint(
                    f"Warning: Filing deadline was {abs(days_remaining)} days ago!",
                    alert=True,
                    indicator="red",
                )
            elif days_remaining <= 7:
                frappe.msgprint(
                    f"Reminder: Filing deadline is in {days_remaining} days.",
                    alert=True,
                    indicator="orange",
                )


@frappe.whitelist()
def get_pending_filings(fund_master=None, days_ahead=30):
    """API: Get all pending or upcoming filings."""
    from frappe.utils import add_days

    filters = {"status": ["in", ["Draft", "In Progress"]]}
    if fund_master:
        filters["fund_master"] = fund_master

    return frappe.get_all(
        "SEBI Report",
        filters=filters,
        fields=[
            "name", "report_type", "report_category", "regulatory_body",
            "report_date", "filing_deadline", "period_covered", "status",
            "filing_date", "fund_master",
        ],
        order_by="filing_deadline asc",
    )


@frappe.whitelist()
def get_compliance_calendar(fund_master=None, fiscal_year=None):
    """API: Get compliance calendar for a fund."""
    from datetime import date

    today_date = date.today()
    year = fiscal_year or today_date.year

    filings = frappe.get_all(
        "SEBI Report",
        filters={"fund_master": fund_master} if fund_master else {},
        fields=[
            "name", "report_type", "regulatory_body", "report_date",
            "filing_deadline", "period_covered", "status", "filing_date",
        ],
        order_by="filing_deadline asc",
    )

    overdue = [f for f in filings if f["filing_deadline"] and f["filing_deadline"] < today_date and f["status"] not in ("Filed", "Acknowledged")]
    upcoming = [f for f in filings if f["filing_deadline"] and f["filing_deadline"] >= today_date and f["status"] not in ("Filed", "Acknowledged")]

    return {
        "total_filings": len(filings),
        "overdue": overdue,
        "upcoming": upcoming,
        "filed_on_time": [f for f in filings if f["status"] in ("Filed", "Acknowledged")],
    }
