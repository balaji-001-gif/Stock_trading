# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff


class ClientPlan(Document):
    """Goal-based financial planning with SIP calculator and proposal tracking."""

    def validate(self):
        self.calculate_shortfall()

    def calculate_shortfall(self):
        """Calculate projected shortfall using compound growth assumptions.

        Uses FV = PV * (1 + r)^n for existing savings and
        FV of annuity formula for SIP contributions.
        Rate of return varies by risk profile.
        """
        goal = flt(self.goal_amount)
        current = flt(self.current_savings)
        sip = flt(self.monthly_sip_required)
        lump = flt(self.lump_sum_required)

        if not goal:
            return

        # Determine assumed annual return based on risk profile
        risk_returns = {
            "Conservative": 0.06,
            "Moderately Conservative": 0.08,
            "Moderate": 0.10,
            "Moderately Aggressive": 0.12,
            "Aggressive": 0.14,
        }
        rate = risk_returns.get(self.risk_profile, 0.10)

        # Assume 10-year horizon if target not set
        years = 10
        if self.target_date and self.investment_horizon:
            horizon_map = {
                "Short Term (< 1 Year)": 1,
                "Medium Term (1-3 Years)": 3,
                "Long Term (3-7 Years)": 7,
                "Very Long Term (7+ Years)": 15,
            }
            years = horizon_map.get(self.investment_horizon, 10)

        # Future value of current savings: FV = PV * (1 + r)^n
        fv_savings = current * ((1 + rate) ** years)

        # Future value of lump sum added now
        fv_lump = lump * ((1 + rate) ** years)

        # Future value of SIP annuity: FV = P * [((1 + r)^n - 1) / r]
        monthly_rate = rate / 12
        months = years * 12
        if monthly_rate > 0:
            fv_sip = sip * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            fv_sip = sip * months

        projected = fv_savings + fv_lump + fv_sip
        self.projected_shortfall = max(0, goal - projected)


@frappe.whitelist()
def create_client_plan(advisor, client_name, goal_type, goal_amount, **kwargs):
    """API: Create a new client financial plan."""
    doc = frappe.get_doc({
        "doctype": "Client Plan",
        "advisor": advisor,
        "client_name": client_name,
        "goal_type": goal_type,
        "goal_amount": flt(goal_amount),
        "risk_profile": kwargs.get("risk_profile", "Moderate"),
        "investment_horizon": kwargs.get("investment_horizon", "Long Term (3-7 Years)"),
        "status": "Lead",
        "email": kwargs.get("email"),
        "mobile": kwargs.get("mobile"),
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_clients_by_advisor(advisor):
    """API: Get all clients for an advisor."""
    return frappe.get_all(
        "Client Plan",
        filters={"advisor": advisor},
        fields=[
            "name", "client_name", "goal_type", "goal_amount",
            "total_invested", "current_value", "risk_profile",
            "status", "proposal_generated", "proposal_accepted",
        ],
        order_by="creation desc",
    )
