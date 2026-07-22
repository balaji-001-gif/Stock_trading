# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, now_datetime


class NAVHistory(Document):
    """NAV record for a fund share class with change tracking and audit."""

    def validate(self):
        self.calculate_previous_nav()
        self.calculate_change()
        self.calculate_net_assets()
        self.calculate_nav_per_unit()

    def before_submit(self):
        self.calculated_by = frappe.session.user
        self.calculation_time = now_datetime()
        self.update_share_class_nav()

    def calculate_previous_nav(self):
        """Fetch and set the previous NAV for this fund/share class."""
        if not self.previous_nav:
            last_nav = frappe.get_all(
                "NAV History",
                filters={
                    "fund_master": self.fund_master,
                    "share_class": self.share_class,
                    "nav_date": ["<", self.nav_date],
                    "docstatus": 1,
                    "name": ["!=", self.name],
                },
                fields=["nav"],
                order_by="nav_date desc",
                limit=1,
            )
            if last_nav:
                self.previous_nav = flt(last_nav[0].nav)

    def calculate_change(self):
        """Calculate NAV change and percentage from previous NAV."""
        if self.previous_nav and self.previous_nav > 0:
            self.nav_change = flt(self.nav) - flt(self.previous_nav)
            self.nav_change_percentage = (
                flt(self.nav_change) / flt(self.previous_nav)
            ) * 100
        else:
            self.nav_change = 0
            self.nav_change_percentage = 0

    def calculate_net_assets(self):
        """Calculate net assets = total assets - total liabilities."""
        if self.total_assets or self.total_liabilities:
            self.net_assets = flt(self.total_assets) - flt(self.total_liabilities)

    def calculate_nav_per_unit(self):
        """Calculate NAV per unit from net assets or total AUM."""
        if self.units_outstanding and self.units_outstanding > 0:
            if self.net_assets:
                self.nav_per_unit = flt(self.net_assets) / flt(self.units_outstanding)
            elif self.total_aum:
                self.nav_per_unit = flt(self.total_aum) / flt(self.units_outstanding)
            else:
                self.nav_per_unit = self.nav

    def update_share_class_nav(self):
        """Push the latest NAV to the linked Share Class record."""
        frappe.db.set_value(
            "Share Class",
            self.share_class,
            {"nav": self.nav, "nav_date": self.nav_date},
        )

    def after_submit(self):
        """Create NAV audit trail entry."""
        frappe.get_doc({
            "doctype": "NAV Audit Trail",
            "nav_history": self.name,
            "fund_master": self.fund_master,
            "share_class": self.share_class,
            "nav_date": self.nav_date,
            "nav_before": self.previous_nav,
            "nav_after": self.nav,
            "change_percentage": self.nav_change_percentage,
            "calculated_by": self.calculated_by,
            "calculation_time": self.calculation_time,
            "audit_type": "NAV Calculation",
            "status": "Published",
        }).insert()


@frappe.whitelist()
def calculate_nav(fund_master, share_class, nav_date=None, nav_value=None):
    """API: Calculate and record NAV for a fund share class."""
    from frappe.utils import today as _today

    nav_date = nav_date or _today()

    # Create NAV record
    nav_doc = frappe.get_doc({
        "doctype": "NAV History",
        "fund_master": fund_master,
        "share_class": share_class,
        "nav_date": nav_date,
        "nav_type": "Daily",
        "nav": flt(nav_value or 0),
        "calculation_method": "Automated",
    })
    nav_doc.insert()
    nav_doc.submit()
    return nav_doc


@frappe.whitelist()
def get_nav_history(fund_master, share_class=None, from_date=None, to_date=None, limit=100):
    """API: Get NAV history for a fund, optionally filtered by share class and date range."""
    filters = {"fund_master": fund_master, "docstatus": 1}
    if share_class:
        filters["share_class"] = share_class
    if from_date:
        filters["nav_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("nav_date", [])
        filters["nav_date"].append(["<=", to_date])

    return frappe.get_all(
        "NAV History",
        filters=filters,
        fields=[
            "name",
            "nav_date",
            "nav",
            "previous_nav",
            "nav_change",
            "nav_change_percentage",
            "total_aum",
            "units_outstanding",
            "nav_type",
        ],
        order_by="nav_date desc",
        limit_page_length=limit,
    )


@frappe.whitelist()
def get_latest_nav(fund_master, share_class):
    """API: Get the latest NAV for a fund share class."""
    navs = frappe.get_all(
        "NAV History",
        filters={
            "fund_master": fund_master,
            "share_class": share_class,
            "docstatus": 1,
        },
        fields=["name", "nav", "nav_date", "nav_change_percentage", "total_aum"],
        order_by="nav_date desc",
        limit=1,
    )
    return navs[0] if navs else None
