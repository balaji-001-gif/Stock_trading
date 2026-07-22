# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class SuccessionPlan(Document):
    """Estate and succession planning — will, trust, nomination tracking."""

    def validate(self):
        self.validate_review_dates()

    def validate_review_dates(self):
        if self.next_review_date and self.next_review_date < today():
            frappe.msgprint(
                "Next review date is in the past. Please update it.",
                alert=True,
                indicator="orange",
            )


@frappe.whitelist()
def get_succession_summary(family_office_name):
    """API: Get succession planning summary for a family office."""
    plans = frappe.get_all(
        "Succession Plan",
        filters={"family_office": family_office_name},
        fields=[
            "name", "plan_name", "plan_type", "plan_status",
            "effective_date", "last_review_date", "next_review_date",
            "estimated_estate_value",
        ],
        order_by="creation desc",
    )

    overdue = [
        p for p in plans
        if p.get("next_review_date") and p["next_review_date"] < today()
    ]

    return {
        "total_plans": len(plans),
        "plans": plans,
        "overdue_reviews": overdue,
        "total_estate_value": sum(
            p.get("estimated_estate_value", 0) or 0 for p in plans
        ),
    }
