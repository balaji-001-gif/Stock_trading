# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SOACAS(Document):
    """Statement of Account / Consolidated Account Statement."""
    pass


@frappe.whitelist()
def get_investor_soa_statements(investor):
    """API: Get SOA/CAS statements for an investor."""
    return frappe.get_all(
        "SOA/CAS",
        filters={"investor": investor},
        fields=[
            "name", "statement_type", "statement_date", "period_from",
            "period_to", "status", "delivery_method", "delivery_status",
            "generated_date",
        ],
        order_by="statement_date desc",
    )
