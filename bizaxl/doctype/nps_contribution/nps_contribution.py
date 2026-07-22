# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class NPSContribution(Document):
    """NPS contribution with employee/employer split and scheme-wise NAV allocation."""

    def validate(self):
        self.calculate_total()
        self.allocate_to_schemes()
        self.update_subscriber()

    def calculate_total(self):
        self.total_contribution = flt(self.contribution_amount)
        if self.employee_contribution or self.employer_contribution:
            self.total_contribution = flt(self.employee_contribution) + flt(self.employer_contribution)

    def allocate_to_schemes(self):
        """Allocate contribution based on scheme percentages using per-scheme NAVs."""
        total = flt(self.total_contribution)
        if total and not self.units_allocated:
            scheme_e_pct = flt(self.scheme_e_percentage) / 100
            scheme_c_pct = flt(self.scheme_c_percentage) / 100
            scheme_g_pct = flt(self.scheme_g_percentage) / 100
            scheme_a_pct = flt(self.scheme_a_percentage) / 100

            # Allocate per scheme using each scheme's own NAV
            nav_e = flt(self.nav_e) or 1
            nav_c = flt(self.nav_c) or 1
            nav_g = flt(self.nav_g) or 1
            nav_a = flt(self.nav_a) or 1

            amount_e = total * scheme_e_pct
            amount_c = total * scheme_c_pct
            amount_g = total * scheme_g_pct
            amount_a = total * scheme_a_pct

            self.pfm_e_units = amount_e / nav_e
            self.pfm_c_units = amount_c / nav_c
            self.pfm_g_units = amount_g / nav_g
            self.pfm_a_units = amount_a / nav_a

            self.units_allocated = (
                self.pfm_e_units + self.pfm_c_units
                + self.pfm_g_units + self.pfm_a_units
            )
            self.total_invested = total

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Allocated"
        if not self.pran_number:
            self.pran_number = frappe.get_value("NPS Subscriber", self.nps_subscriber, "pran_number")

    def update_subscriber(self):
        """Update the subscriber's last contribution date."""
        if self.contribution_date:
            frappe.db.set_value(
                "NPS Subscriber",
                self.nps_subscriber,
                "last_contribution_date",
                self.contribution_date,
            )


@frappe.whitelist()
def record_contribution(nps_subscriber, contribution_date, contribution_amount, **kwargs):
    """API: Record an NPS contribution."""
    doc = frappe.get_doc({
        "doctype": "NPS Contribution",
        "nps_subscriber": nps_subscriber,
        "contribution_date": contribution_date,
        "contribution_amount": flt(contribution_amount),
        "employee_contribution": flt(kwargs.get("employee_contribution", 0)),
        "employer_contribution": flt(kwargs.get("employer_contribution", 0)),
        "account_type": kwargs.get("account_type", "Tier I (Pension)"),
        "contribution_type": kwargs.get("contribution_type", "Regular"),
        "status": "Pending",
    })
    doc.insert()
    doc.submit()
    return doc


@frappe.whitelist()
def get_contribution_history(nps_subscriber, limit=24):
    """API: Get contribution history for an NPS subscriber."""
    return frappe.get_all(
        "NPS Contribution",
        filters={"nps_subscriber": nps_subscriber, "docstatus": 1},
        fields=[
            "name", "contribution_date", "contribution_amount",
            "employee_contribution", "employer_contribution",
            "account_type", "units_allocated", "applicable_nav", "status",
        ],
        order_by="contribution_date desc",
        limit_page_length=limit,
    )
