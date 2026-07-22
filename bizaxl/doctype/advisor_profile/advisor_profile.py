# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class AdvisorProfile(Document):
    """RIA/MFD advisor profile with SEBI/AMFI registration and compliance tracking."""

    def validate(self):
        self.validate_registration()
        self.update_client_count()

    def validate_registration(self):
        if self.valid_until and self.valid_until < frappe.utils.today():
            frappe.msgprint("Advisor registration has expired. Please renew.", alert=True)

    def update_client_count(self):
        if self.name:
            self.total_clients = frappe.db.count("Client Plan", filters={"advisor": self.name})


@frappe.whitelist()
def register_advisor(advisor_name, registration_type, **kwargs):
    """API: Register a new advisor (RIA/MFD)."""
    doc = frappe.get_doc({
        "doctype": "Advisor Profile",
        "advisor_name": advisor_name,
        "registration_type": registration_type,
        "arn_number": kwargs.get("arn_number"),
        "ria_number": kwargs.get("ria_number"),
        "email": kwargs.get("email"),
        "mobile": kwargs.get("mobile"),
        "status": "Active",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_advisor_dashboard(advisor_name):
    """API: Get advisor dashboard with AUM, clients, and income."""
    advisor = frappe.get_doc("Advisor Profile", advisor_name)

    clients = frappe.get_all(
        "Client Plan",
        filters={"advisor": advisor_name},
        fields=["name", "client_name", "total_invested", "goal_amount", "status"],
        order_by="creation desc",
    )

    commissions = frappe.get_all(
        "Advisor Commission",
        filters={"advisor": advisor_name},
        fields=["commission_type", "sum(commission_amount) as total"],
        group_by="commission_type",
    )

    compliance = frappe.get_all(
        "Advisor Compliance",
        filters={"advisor": advisor_name, "status": ["!=", "Completed"]},
        fields=["name", "compliance_type", "due_date", "status"],
        order_by="due_date asc",
    )

    return {
        "advisor": advisor.as_dict(),
        "total_clients": len(clients),
        "total_aum": flt(advisor.total_aum),
        "clients": clients,
        "commissions": commissions,
        "pending_compliance": compliance,
    }
