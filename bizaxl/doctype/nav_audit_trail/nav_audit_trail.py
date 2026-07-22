# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class NAVAuditTrail(Document):
    """Audit trail for NAV calculations with before/after comparison."""

    def validate(self):
        self.timestamp = now_datetime()
        self.calculate_change_percentage()


    def calculate_change_percentage(self):
        if self.nav_before and self.nav_before > 0:
            self.change_percentage = (
                (self.nav_after - self.nav_before) / self.nav_before
            ) * 100


@frappe.whitelist()
def get_nav_audits(fund_master, from_date=None, to_date=None, limit=50):
    """API: Get NAV audit trail records."""
    filters = {"fund_master": fund_master}
    if from_date and to_date:
        filters["nav_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["nav_date"] = [">=", from_date]
    elif to_date:
        filters["nav_date"] = ["<=", to_date]

    return frappe.get_all(
        "NAV Audit Trail",
        filters=filters,
        fields=[
            "name", "nav_date", "audit_type", "status",
            "nav_before", "nav_after", "change_percentage",
            "calculated_by", "calculation_time", "approved_by",
        ],
        order_by="nav_date desc",
        limit_page_length=limit,
    )
