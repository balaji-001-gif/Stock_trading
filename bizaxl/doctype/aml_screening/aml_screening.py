# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class AMLScreening(Document):
    """Anti-Money Laundering screening record with PEP, OFAC, sanctions checks."""

    def validate(self):
        self.validate_screening_date()
        self.calculate_risk_level()

    def before_submit(self):
        if self.screening_status == "Pending":
            self.screening_status = "In Progress"

    def validate_screening_date(self):
        if not self.screening_date:
            self.screening_date = today()

    def calculate_risk_level(self):
        """Calculate overall risk level based on individual checks."""
        risk_factors = []

        if self.pep_check == "Match Found":
            risk_factors.append("PEP Match")
        if self.ofac_check == "Match Found":
            risk_factors.append("OFAC Match")
        if self.sanctions_check == "Match Found":
            risk_factors.append("Sanctions Match")
        if self.adverse_media_check == "Match Found":
            risk_factors.append("Adverse Media Match")
        if self.country_risk in ("High", "FATF Grey List", "FATF Black List"):
            risk_factors.append(f"Country Risk: {self.country_risk}")

        if self.risk_score:
            if self.risk_score >= 75:
                self.risk_level = "Critical"
            elif self.risk_score >= 50:
                self.risk_level = "High"
            elif self.risk_score >= 25:
                self.risk_level = "Medium"
            else:
                self.risk_level = "Low"

        if risk_factors:
            self.risk_factors = "; ".join(risk_factors)

    def clear_screening(self):
        """Mark screening as cleared."""
        self.screening_status = "Cleared"
        self.review_status = "Cleared - Low Risk"
        self.review_date = today()
        self.reviewed_by = frappe.session.user
        self.save()

    def flag_for_review(self, reason):
        """Flag screening for manual review."""
        self.screening_status = "Flagged"
        self.review_status = "Under Review"
        self.review_notes = reason
        self.save()

    def escalate_to_mlro(self, reason):
        """Escalate to Money Laundering Reporting Officer."""
        self.screening_status = "Escalated"
        self.review_status = "Escalated to MLRO"
        self.review_notes = reason
        self.action_taken = "Suspicious Activity Report (SAR)"
        self.save()


@frappe.whitelist()
def perform_screening(investor, screening_type="Initial Onboarding"):
    """API: Initiate an AML screening for an investor."""
    screening = frappe.get_doc({
        "doctype": "AML Screening",
        "investor": investor,
        "screening_type": screening_type,
        "screening_status": "In Progress",
        "screening_date": today(),
        "screening_method": "Automated API",
    })
    screening.insert()
    screening.submit()
    return screening


@frappe.whitelist()
def get_investor_screening_status(investor):
    """API: Get latest AML screening status for an investor."""
    screenings = frappe.get_all(
        "AML Screening",
        filters={"investor": investor},
        fields=[
            "name",
            "screening_type",
            "screening_status",
            "risk_level",
            "screening_date",
            "review_status",
            "next_review_date",
        ],
        order_by="screening_date desc",
        limit=5,
    )
    return screenings
