# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class TaxOptimizationPlan(Document):
    """Tax planning with STCG/LTCG tracking, harvesting, and grandfathering."""

    def validate(self):
        self.calculate_tax_liability()

    def calculate_tax_liability(self):
        """Estimate total tax liability from realized gains."""
        stcg = flt(self.stcg_realized)
        ltcg = flt(self.ltcg_realized)
        # Simplified: STCG 15%, LTCG 10% on equity above Rs. 1L
        stcg_tax = stcg * 0.15
        ltcg_exempt = 100000  # Rs. 1L LTCG exemption
        ltcg_taxable = max(0, ltcg - ltcg_exempt)
        ltcg_tax = ltcg_taxable * 0.10
        self.total_tax_liability = stcg_tax + ltcg_tax


@frappe.whitelist()
def get_tax_summary(family_office_name, fiscal_year=None):
    """API: Get tax optimization summary for a family office."""
    filters = {"family_office": family_office_name}
    if fiscal_year:
        filters["fiscal_year"] = fiscal_year

    plans = frappe.get_all(
        "Tax Optimization Plan",
        filters=filters,
        fields=[
            "name", "plan_name", "fiscal_year", "plan_type",
            "stcg_realized", "ltcg_realized", "total_tax_liability",
            "estimated_savings", "harvested_losses", "status",
        ],
        order_by="fiscal_year desc",
    )

    total_tax = sum(flt(p["total_tax_liability"]) for p in plans)
    total_savings = sum(flt(p["estimated_savings"]) for p in plans)
    total_harvested = sum(flt(p["harvested_losses"]) for p in plans)

    return {
        "plans": plans,
        "total_tax_liability": total_tax,
        "total_estimated_savings": total_savings,
        "total_losses_harvested": total_harvested,
    }
