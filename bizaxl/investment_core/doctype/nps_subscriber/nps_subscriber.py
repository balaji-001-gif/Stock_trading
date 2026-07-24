# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class NPSSubscriber(Document):
    """NPS subscriber with PRAN, Tier I/II accounts, and scheme selection."""

    def validate(self):
        self.update_corpus()

    def update_corpus(self):
        """Calculate total pension corpus from contributions."""
        contributions = frappe.get_all(
            "NPS Contribution",
            filters={
                "nps_subscriber": self.name,
                "docstatus": 1,
            },
            fields=["sum(contribution_amount) as total"],
        )
        self.total_contributions = flt(contributions[0].total) if contributions else 0
        # TODO: Replace hardcoded 8% with actual NAV-based return tracking
        # using NPS Contribution NAV allocation for each scheme (E/C/G/A)
        self.current_pension_corpus = flt(self.total_contributions) * 1.08  # ~8% assumed return


@frappe.whitelist()
def register_subscriber(subscriber_name, pran_number, **kwargs):
    """API: Register a new NPS subscriber."""
    doc = frappe.get_doc({
        "doctype": "NPS Subscriber",
        "subscriber_name": subscriber_name,
        "pran_number": pran_number,
        "date_of_birth": kwargs.get("date_of_birth"),
        "mobile_number": kwargs.get("mobile_number"),
        "email": kwargs.get("email"),
        "pan_number": kwargs.get("pan_number"),
        "scheme_choice": kwargs.get("scheme_choice", "Active Choice"),
        "employment_type": kwargs.get("employment_type"),
        "status": "Active",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_subscriber_summary(pran_number=None, subscriber_name=None):
    """API: Get NPS subscriber summary."""
    filters = {}
    if pran_number:
        filters["pran_number"] = pran_number
    if subscriber_name:
        filters["subscriber_name"] = subscriber_name

    subscribers = frappe.get_all(
        "NPS Subscriber",
        filters=filters,
        fields=[
            "name", "subscriber_name", "pran_number", "scheme_choice",
            "status", "total_contributions", "current_pension_corpus",
            "last_contribution_date", "employment_type",
        ],
        order_by="creation desc",
    )

    return subscribers


@frappe.whitelist()
def get_nps_dashboard():
    """API: Get NPS portfolio dashboard statistics."""
    total_subscribers = frappe.db.count("NPS Subscriber")
    active_subscribers = frappe.db.count("NPS Subscriber", filters={"status": "Active"})
    total_corpus = frappe.get_all(
        "NPS Subscriber",
        fields=["sum(current_pension_corpus) as total"],
    )[0].total or 0
    total_contributions = frappe.get_all(
        "NPS Subscriber",
        fields=["sum(total_contributions) as total"],
    )[0].total or 0

    return {
        "total_subscribers": total_subscribers,
        "active_subscribers": active_subscribers,
        "total_pension_corpus": total_corpus,
        "total_contributions": total_contributions,
    }
