# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff


class AdvisorCompliance(Document):
    """SEBI IA/AMFI compliance tracking for advisors."""

    def validate(self):
        self.check_overdue()

    def check_overdue(self):
        if self.due_date and self.due_date < today() and self.status not in ("Completed", "Waived"):
            self.status = "Overdue"


@frappe.whitelist()
def get_advisor_compliance_calendar(advisor):
    """API: Get compliance calendar for an advisor."""
    items = frappe.get_all(
        "Advisor Compliance",
        filters={"advisor": advisor},
        fields=["name", "compliance_type", "due_date", "status", "submission_date"],
        order_by="due_date asc",
    )

    overdue = [i for i in items if i["status"] == "Overdue"]
    pending = [i for i in items if i["status"] in ("Pending", "In Progress")]
    completed = [i for i in items if i["status"] == "Completed"]

    return {
        "total": len(items),
        "overdue": overdue,
        "pending": pending,
        "completed": completed,
    }


@frappe.whitelist()
def record_compliance(advisor, compliance_type, due_date, **kwargs):
    """API: Record an advisor compliance item."""
    doc = frappe.get_doc({
        "doctype": "Advisor Compliance",
        "advisor": advisor,
        "compliance_type": compliance_type,
        "due_date": due_date,
        "description": kwargs.get("description"),
        "status": "Pending",
    })
    doc.insert()
    return doc
