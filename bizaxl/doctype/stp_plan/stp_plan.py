# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class STPPlan(Document):
    """Systematic Transfer Plan between funds."""

    def validate(self):
        if self.from_fund == self.to_fund:
            frappe.throw(
                "Source and target funds must be different.",
                title="Same Fund",
            )


@frappe.whitelist()
def create_stp(investor, from_fund, to_fund, **kwargs):
    """API: Create a new STP plan."""
    stp = frappe.get_doc({
        "doctype": "STP Plan",
        "investor": investor,
        "from_fund": from_fund,
        "to_fund": to_fund,
        "status": "Active",
        **kwargs,
    })
    stp.insert()
    return stp
