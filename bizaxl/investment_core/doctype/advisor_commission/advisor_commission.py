# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class AdvisorCommission(Document):
    """Trail commission, upfront fees, and revenue tracking for advisors."""

    def validate(self):
        self.calculate_net_commission()

    def calculate_net_commission(self):
        gross = flt(self.gross_commission) or flt(self.commission_amount)
        tds = flt(self.tds_deducted)
        self.net_commission = gross - tds


@frappe.whitelist()
def get_commission_summary(advisor, from_date=None, to_date=None):
    """API: Get commission summary for an advisor."""
    filters = {"advisor": advisor}
    return frappe.get_all(
        "Advisor Commission",
        filters=filters,
        fields=[
            "commission_type",
            "sum(gross_commission) as total_gross",
            "sum(tds_deducted) as total_tds",
            "sum(net_commission) as total_net",
        ],
        group_by="commission_type",
    )


@frappe.whitelist()
def get_revenue_dashboard(advisor):
    """API: Get revenue dashboard with monthly breakdown."""
    monthly = frappe.get_all(
        "Advisor Commission",
        filters={"advisor": advisor},
        fields=[
            "monthname(commission_date) as month",
            "year(commission_date) as year",
            "sum(net_commission) as total_commission",
        ],
        group_by="monthname(commission_date), year(commission_date)",
        order_by="year desc, month desc",
    )

    totals = frappe.get_all(
        "Advisor Commission",
        filters={"advisor": advisor},
        fields=[
            "sum(gross_commission) as total_gross",
            "sum(net_commission) as total_net",
            "sum(tds_deducted) as total_tds",
        ],
    )

    return {
        "monthly_breakdown": monthly,
        "totals": totals[0] if totals else {"total_gross": 0, "total_net": 0, "total_tds": 0},
    }
