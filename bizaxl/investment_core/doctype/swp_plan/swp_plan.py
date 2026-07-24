# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SWPPlan(Document):
    """Systematic Withdrawal Plan."""
    pass


@frappe.whitelist()
def create_swp(investor, fund_master, share_class, **kwargs):
    """API: Create a new SWP plan."""
    swp = frappe.get_doc({
        "doctype": "SWP Plan",
        "investor": investor,
        "fund_master": fund_master,
        "share_class": share_class,
        "status": "Active",
        **kwargs,
    })
    swp.insert()
    return swp
