# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class ShareClass(Document):
    """Share class within a fund — Growth/Dividend/Direct/Regular/Institutional."""

    def validate(self):
        self.validate_nav()
        self.validate_expense_ratio()
        self.validate_minimum_investment()

    def validate_nav(self):
        if self.nav and self.nav <= 0:
            frappe.throw("NAV must be greater than zero.", title="Invalid NAV")

    def validate_expense_ratio(self):
        if self.expense_ratio and (self.expense_ratio < 0 or self.expense_ratio > 100):
            frappe.throw(
                "Expense Ratio must be between 0 and 100.",
                title="Invalid Expense Ratio",
            )
        if self.ter and (self.ter < 0 or self.ter > 100):
            frappe.throw(
                "Total Expense Ratio must be between 0 and 100.",
                title="Invalid TER",
            )

    def validate_minimum_investment(self):
        if (
            self.minimum_investment
            and self.maximum_investment_per_investor
            and self.minimum_investment > self.maximum_investment_per_investor
        ):
            frappe.throw(
                "Minimum Investment cannot exceed Maximum Investment per Investor.",
                title="Invalid Limits",
            )

    def update_nav(self, new_nav, nav_date=None):
        """Update NAV with audit trail."""
        old_nav = self.nav
        self.nav = new_nav
        self.nav_date = nav_date or today()
        self.save()

        # Log NAV change
        nav_log = frappe.get_doc(
            {
                "doctype": "NAV History",
                "share_class": self.name,
                "fund_master": self.fund_master,
                "nav": new_nav,
                "previous_nav": old_nav,
                "nav_date": self.nav_date,
                "nav_change_percentage": (
                    ((new_nav - old_nav) / old_nav) * 100 if old_nav else 0
                ),
            }
        )
        nav_log.insert()
        return nav_log


@frappe.whitelist()
def get_share_classes_by_fund(fund_master):
    """API: Get all share classes for a fund."""
    return frappe.get_all(
        "Share Class",
        filters={"fund_master": fund_master},
        fields=[
            "name",
            "class_name",
            "class_code",
            "class_type",
            "plan_type",
            "nav",
            "nav_date",
            "expense_ratio",
            "ter",
            "minimum_investment",
            "status",
        ],
        order_by="class_name asc",
    )


@frappe.whitelist()
def get_share_class_summary(share_class_name):
    """API: Get detailed summary of a share class."""
    sc = frappe.get_doc("Share Class", share_class_name)
    return {
        "name": sc.name,
        "class_name": sc.class_name,
        "class_type": sc.class_type,
        "plan_type": sc.plan_type,
        "fund": sc.fund_master,
        "nav": sc.nav,
        "nav_date": sc.nav_date,
        "expense_ratio": sc.expense_ratio,
        "ter": sc.ter,
        "minimum_investment": sc.minimum_investment,
        "isin": sc.isin,
        "status": sc.status,
    }
