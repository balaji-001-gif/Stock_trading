# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DynamicRatios(Document):
    """Ratio configuration for NAV calculations — expense ratios, accruals, distributions."""
    pass


@frappe.whitelist()
def get_active_ratios(fund_master, ratio_type=None, as_on_date=None):
    """API: Get active ratios for a fund."""
    from frappe.utils import today

    as_on_date = as_on_date or today()
    filters = {
        "fund_master": fund_master,
        "status": "Active",
        "effective_from": ["<=", as_on_date],
    }
    if ratio_type:
        filters["ratio_type"] = ratio_type

    return frappe.get_all(
        "Dynamic Ratios",
        filters=filters,
        fields=[
            "name", "ratio_type", "ratio_name", "ratio_value",
            "ratio_frequency", "calculation_method", "applicable_on",
            "priority_order",
        ],
        order_by="priority_order asc",
    )
