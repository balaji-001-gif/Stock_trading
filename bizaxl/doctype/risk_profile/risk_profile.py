# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt


class RiskProfile(Document):
    """Investor risk assessment with scoring, classification, and suggested allocations."""

    def validate(self):
        self.validate_assessment_date()
        self.calculate_completion()
        self.calculate_derived_score()
        self.set_suggested_classification()
        self.set_validity()

    def before_submit(self):
        if not self.approval_status:
            self.approval_status = "Pending"
        self.link_to_investor()

    def validate_assessment_date(self):
        if not self.assessment_date:
            self.assessment_date = today()

    def calculate_completion(self):
        """Calculate questionnaire completion percentage."""
        if self.total_questions and self.total_questions > 0:
            self.completion_percentage = flt(
                (self.answered_questions or 0) / self.total_questions * 100
            )
        else:
            self.completion_percentage = 0

    def calculate_derived_score(self):
        """Calculate derived risk score from questionnaire responses."""
        score_map = {
            "investment_knowledge": {
                "None": 5,
                "Limited": 20,
                "Basic": 40,
                "Good": 60,
                "Advanced": 80,
                "Expert": 90,
            },
            "investment_experience": {
                "Less than 1 Year": 10,
                "1-3 Years": 30,
                "3-5 Years": 50,
                "5-10 Years": 70,
                "10+ Years": 85,
            },
            "risk_appetite": {
                "Avoid Risk": 5,
                "Low Risk Tolerance": 20,
                "Moderate Risk Tolerance": 50,
                "High Risk Tolerance": 75,
                "Very High Risk Tolerance": 95,
            },
            "investment_horizon": {
                "Short Term (< 1 Year)": 10,
                "Medium Term (1-3 Years)": 35,
                "Long Term (3-7 Years)": 65,
                "Very Long Term (7+ Years)": 85,
            },
            "loss_tolerance": {
                "Cannot Accept Any Loss": 5,
                "Up to 5% Loss": 20,
                "Up to 10% Loss": 45,
                "Up to 20% Loss": 70,
                "Above 20% Loss": 90,
            },
            "liquidity_needs": {
                "Very High (Need access within 3 months)": 10,
                "High (Need access within 6 months)": 25,
                "Moderate (Need access within 1 year)": 45,
                "Low (1-3 years)": 70,
                "Very Low (3+ years)": 85,
            },
        }

        scores = []
        for field, mapping in score_map.items():
            value = getattr(self, field, None)
            if value and value in mapping:
                scores.append(mapping[value])

        if scores:
            self.derived_risk_score = round(sum(scores) / len(scores))
            self.risk_score = self.risk_score or self.derived_risk_score

    def set_suggested_classification(self):
        """Set suggested portfolio type and asset allocation based on risk score."""
        score = self.risk_score or self.derived_risk_score or 50

        if score <= 15:
            self.risk_level = "Very Low"
            self.risk_category = "Conservative"
            self.suggested_portfolio_type = "Capital Preservation"
            self.suggested_asset_allocation = "Equity: 5-10%, Debt: 70-80%, Cash: 10-20%"
            self.max_equity_exposure = 10
            self.max_debt_exposure = 80
        elif score <= 30:
            self.risk_level = "Low"
            self.risk_category = "Moderately Conservative"
            self.suggested_portfolio_type = "Income"
            self.suggested_asset_allocation = "Equity: 15-25%, Debt: 60-70%, Cash: 5-15%"
            self.max_equity_exposure = 25
            self.max_debt_exposure = 70
        elif score <= 50:
            self.risk_level = "Moderate"
            self.risk_category = "Balanced"
            self.suggested_portfolio_type = "Balanced"
            self.suggested_asset_allocation = "Equity: 40-60%, Debt: 30-50%, Cash: 5-10%"
            self.max_equity_exposure = 60
            self.max_debt_exposure = 50
        elif score <= 70:
            self.risk_level = "Moderately High"
            self.risk_category = "Moderately Aggressive"
            self.suggested_portfolio_type = "Growth"
            self.suggested_asset_allocation = "Equity: 60-75%, Debt: 20-30%, Cash: 2-5%"
            self.max_equity_exposure = 75
            self.max_debt_exposure = 30
        elif score <= 85:
            self.risk_level = "High"
            self.risk_category = "Aggressive"
            self.suggested_portfolio_type = "Aggressive Growth"
            self.suggested_asset_allocation = "Equity: 75-90%, Debt: 5-15%, Cash: 2-5%"
            self.max_equity_exposure = 90
            self.max_debt_exposure = 15
        else:
            self.risk_level = "Very High"
            self.risk_category = "Aggressive"
            self.suggested_portfolio_type = "Aggressive Growth"
            self.suggested_asset_allocation = "Equity: 85-100%, Alternatives: 0-10%, Cash: 0-5%"
            self.max_equity_exposure = 100
            self.max_debt_exposure = 10

    def set_validity(self):
        """Set validity and next reassessment date."""
        if self.approval_status == "Approved" and not self.valid_until:
            # Risk profiles valid for 1 year
            from frappe.utils import add_days, add_years
            self.valid_until = add_years(today(), 1)
            self.next_reassessment_date = add_days(self.valid_until, -30)

    def link_to_investor(self):
        """Link this risk profile to the investor profile."""
        if self.investor:
            frappe.db.set_value(
                "Investor Profile",
                self.investor,
                "risk_profile_link",
                self.name,
            )


@frappe.whitelist()
def assess_risk(investor, responses=None):
    """API: Create a risk assessment for an investor with optional responses."""
    profile = frappe.get_doc({
        "doctype": "Risk Profile",
        "investor": investor,
        "assessment_date": today(),
        "assessment_method": "Online Questionnaire",
        "approval_status": "Pending",
    })
    if responses:
        profile.responses_json = responses
    profile.insert()
    return profile


@frappe.whitelist()
def get_investor_risk_profile(investor):
    """API: Get the latest risk profile for an investor."""
    profiles = frappe.get_all(
        "Risk Profile",
        filters={"investor": investor},
        fields=[
            "name",
            "risk_score",
            "risk_level",
            "risk_category",
            "assessment_date",
            "valid_until",
            "suggested_portfolio_type",
            "suggested_asset_allocation",
            "approval_status",
        ],
        order_by="assessment_date desc",
        limit=1,
    )
    return profiles[0] if profiles else None
