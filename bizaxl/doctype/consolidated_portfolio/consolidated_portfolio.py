# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ConsolidatedPortfolio(Document):
    """Multi-asset class portfolio aggregation for family office."""

    def validate(self):
        self.calculate_unrealized_gain()
        self.calculate_yield()

    def calculate_unrealized_gain(self):
        self.unrealized_gain_loss = flt(self.total_estimated_value) - flt(self.cost_basis)

    def calculate_yield(self):
        if self.total_estimated_value and self.total_estimated_value > 0:
            self.yield_percentage = (flt(self.annual_income) / flt(self.total_estimated_value)) * 100


@frappe.whitelist()
def get_wealth_allocation(family_office_name):
    """API: Get wealth allocation by asset class."""
    portfolios = frappe.get_all(
        "Consolidated Portfolio",
        filters={"family_office": family_office_name, "status": "Active"},
        fields=["asset_class", "sum(total_estimated_value) as total_value"],
        group_by="asset_class",
        order_by="total_value desc",
    )
    total = sum(flt(p["total_value"]) for p in portfolios)
    return {
        "allocation": [
            {
                "asset_class": p["asset_class"],
                "value": p["total_value"],
                "percentage": (flt(p["total_value"]) / total * 100) if total else 0,
            }
            for p in portfolios
        ],
        "total_wealth": total,
    }


@frappe.whitelist()
def add_portfolio_item(family_office, asset_class, security_name, estimated_value, **kwargs):
    """API: Add a new asset to the consolidated portfolio."""
    doc = frappe.get_doc({
        "doctype": "Consolidated Portfolio",
        "family_office": family_office,
        "asset_class": asset_class,
        "security_name": security_name,
        "total_estimated_value": flt(estimated_value),
        "cost_basis": flt(kwargs.get("cost_basis", 0)),
        "status": "Active",
        "holding_entity": kwargs.get("holding_entity"),
        "beneficial_owner": kwargs.get("beneficial_owner"),
        "valuation_method": kwargs.get("valuation_method", "Estimated"),
        "source_type": kwargs.get("source_type", "Manual Entry"),
    })
    doc.insert()
    return doc
