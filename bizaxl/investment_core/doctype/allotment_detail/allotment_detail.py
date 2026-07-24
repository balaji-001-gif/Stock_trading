# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class AllotmentDetail(Document):
    """Unit allotment record for subscription processing."""

    def validate(self):
        self.validate_amounts()

    def before_submit(self):
        self.allotted_by = frappe.session.user

    def validate_amounts(self):
        if self.units <= 0:
            frappe.throw("Units allotted must be greater than zero.", title="Invalid Units")
        if self.nav <= 0:
            frappe.throw("NAV must be greater than zero.", title="Invalid NAV")
        if self.amount <= 0:
            frappe.throw("Amount must be greater than zero.", title="Invalid Amount")


@frappe.whitelist()
def get_holdings(investor, fund_master=None):
    """API: Get all holdings for an investor."""
    filters = {"investor": investor, "docstatus": 1}
    if fund_master:
        filters["fund_master"] = fund_master

    return frappe.get_all(
        "Allotment Detail",
        filters=filters,
        fields=[
            "name",
            "fund_master",
            "share_class",
            "sum(units) as total_units",
            "sum(amount) as total_amount",
            "allotment_date",
        ],
        group_by="fund_master, share_class",
        order_by="allotment_date desc",
    )
