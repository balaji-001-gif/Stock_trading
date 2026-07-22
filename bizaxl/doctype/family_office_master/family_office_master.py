# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FamilyOfficeMaster(Document):
    """Multi-generational family office wealth consolidation entity."""

    def validate(self):
        self.update_member_counts()
        self.update_aggregated_wealth()

    def update_member_counts(self):
        """Count family members and generations tracked."""
        if self.family_members:
            self.total_members = len(self.family_members)
            generations = set()
            for member in self.family_members:
                if member.generation:
                    generations.add(member.generation)
            self.generations_tracked = len(generations)
        else:
            self.total_members = 0
            self.generations_tracked = 0

    def update_aggregated_wealth(self):
        """Calculate total estimated wealth from consolidated portfolios."""
        portfolios = frappe.get_all(
            "Consolidated Portfolio",
            filters={"family_office": self.name, "status": "Active"},
            fields=["total_estimated_value"],
        )
        self.total_estimated_wealth = sum(
            flt(p["total_estimated_value"]) for p in portfolios
        )


@frappe.whitelist()
def get_family_overview(family_office_name):
    """API: Get complete family office overview."""
    fo = frappe.get_doc("Family Office Master", family_office_name)

    portfolios = frappe.get_all(
        "Consolidated Portfolio",
        filters={"family_office": family_office_name},
        fields=["name", "asset_class", "total_estimated_value", "cost_basis", "allocation_percentage"],
        order_by="total_estimated_value desc",
    )

    tax_plans = frappe.get_all(
        "Tax Optimization Plan",
        filters={"family_office": family_office_name},
        fields=["name", "plan_name", "fiscal_year", "estimated_savings", "status"],
        order_by="creation desc",
    )

    succession = frappe.get_all(
        "Succession Plan",
        filters={"family_office": family_office_name},
        fields=["name", "plan_name", "plan_type", "status", "last_review_date"],
    )

    return {
        "family_office": fo.as_dict(),
        "members": fo.family_members,
        "portfolios": portfolios,
        "total_portfolio_value": sum(
            flt(p["total_estimated_value"]) for p in portfolios
        ),
        "tax_plans": tax_plans,
        "succession_plans": succession,
    }


@frappe.whitelist()
def aggregate_all_portfolios(family_office_name):
    """API: Aggregate all family portfolios and calculate total wealth."""
    fo = frappe.get_doc("Family Office Master", family_office_name)
    fo.update_aggregated_wealth()
    fo.wealth_as_of_date = frappe.utils.today()
    fo.last_aggregation_date = frappe.utils.today()
    fo.flags.ignore_permissions = True
    fo.save()
    return {
        "family_office": family_office_name,
        "total_estimated_wealth": fo.total_estimated_wealth,
        "as_of_date": str(fo.wealth_as_of_date),
    }
