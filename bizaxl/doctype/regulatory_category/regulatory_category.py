# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class RegulatoryCategory(Document):
    """Regulatory category configuration — SEBI, RBI, PFRDA, IRDAI compliance parameters."""

    def validate(self):
        self.validate_dates()
        self.validate_limits()

    def validate_dates(self):
        if self.effective_from and self.effective_to:
            if self.effective_from >= self.effective_to:
                frappe.throw(
                    "Effective To must be after Effective From.",
                    title="Invalid Date Range",
                )

    def validate_limits(self):
        if (
            self.minimum_investor_count
            and self.maximum_investor_count
            and self.minimum_investor_count > self.maximum_investor_count
        ):
            frappe.throw(
                "Minimum investor count cannot exceed maximum.",
                title="Invalid Limits",
            )

    def get_compliance_summary(self):
        """Get compliance status summary for this category."""
        return {
            "regulatory_body": self.regulatory_body,
            "registration_required": self.registration_required,
            "filing_frequency": self.compliance_filing_frequency,
            "filing_deadline": self.filing_deadline_days,
            "audit_required": self.audit_required,
            "audit_frequency": self.audit_frequency,
            "last_audit": self.last_audit_date,
            "next_audit": self.next_audit_date,
        }


@frappe.whitelist()
def get_categories_by_regulator(regulatory_body=None):
    """API: Get all regulatory categories, optionally filtered by regulator."""
    filters = {"status": "Active"}
    if regulatory_body:
        filters["regulatory_body"] = regulatory_body

    return frappe.get_all(
        "Regulatory Category",
        filters=filters,
        fields=[
            "name",
            "category_name",
            "category_code",
            "regulatory_body",
            "fund_type_applicable",
            "minimum_corpus",
            "minimum_investor_count",
            "maximum_investor_count",
            "minimum_investment_per_investor",
        ],
        order_by="regulatory_body, category_name asc",
    )


@frappe.whitelist()
def check_compliance_calendar():
    """API: Get upcoming compliance deadlines."""
    today_date = today()
    upcoming = frappe.get_all(
        "Regulatory Category",
        filters={"status": "Active", "next_audit_date": [">=", today_date]},
        fields=[
            "name",
            "category_name",
            "regulatory_body",
            "next_audit_date",
            "audit_frequency",
            "compliance_filing_frequency",
            "filing_deadline_days",
        ],
        order_by="next_audit_date asc",
    )
    return upcoming
