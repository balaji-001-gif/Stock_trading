# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class HoldingsRegister(Document):
    """Multi-asset-class holdings record with lot-wise cost basis."""

    def validate(self):
        self.calculate_values()
        self.calculate_pnl()

    def calculate_values(self):
        """Calculate total cost value and market value."""
        qty = flt(self.total_quantity)
        self.total_cost_value = qty * flt(self.cost_price)
        self.market_value = qty * flt(self.market_price) if self.market_price else 0

    def calculate_pnl(self):
        """Calculate unrealized P&L."""
        if self.total_cost_value:
            self.unrealized_pnl = flt(self.market_value) - flt(self.total_cost_value)

    def apply_corporate_action(self, action_type, ratio, extra_params=None):
        """Apply corporate action to this holding (bonus, split, etc.)."""
        if action_type == "Bonus":
            bonus_qty = flt(self.total_quantity) * flt(ratio)
            self.total_quantity = flt(self.total_quantity) + bonus_qty
            self.available_quantity = flt(self.available_quantity) + bonus_qty
            # Cost price adjusts proportionally
            self.cost_price = flt(self.total_cost_value) / flt(self.total_quantity)

        elif action_type == "Split":
            self.total_quantity = flt(self.total_quantity) * flt(ratio)
            self.available_quantity = flt(self.available_quantity) * flt(ratio)
            self.cost_price = flt(self.cost_price) / flt(ratio)
            if self.market_price:
                self.market_price = flt(self.market_price) / flt(ratio)

        elif action_type == "Consolidation":
            self.total_quantity = flt(self.total_quantity) / flt(ratio)
            self.available_quantity = flt(self.available_quantity) / flt(ratio)
            self.cost_price = flt(self.cost_price) * flt(ratio)
            if self.market_price:
                self.market_price = flt(self.market_price) * flt(ratio)

        self.save()

    def get_lot_summary(self):
        """Get breakdown of all purchase lots for this holding."""
        return frappe.get_all(
            "Lot Tracking",
            filters={"holding": self.name},
            fields=[
                "name", "lot_date", "lot_type", "quantity",
                "cost_per_unit", "total_cost", "remaining_quantity",
                "status",
            ],
            order_by="lot_date asc",
        )


@frappe.whitelist()
def get_portfolio_holdings(fund_master):
    """API: Get all holdings for a fund with valuation."""
    holdings = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=[
            "name", "security_id", "security_name", "security_type",
            "asset_class", "total_quantity", "available_quantity",
            "cost_price", "market_price", "market_value",
            "total_cost_value", "unrealized_pnl", "total_return",
            "sector", "isin", "currency",
        ],
        order_by="market_value desc",
    )

    total_value = sum(flt(h["market_value"]) for h in holdings)
    total_cost = sum(flt(h["total_cost_value"]) for h in holdings)
    total_pnl = sum(flt(h["unrealized_pnl"]) for h in holdings)

    return {
        "holdings": holdings,
        "summary": {
            "total_market_value": total_value,
            "total_cost": total_cost,
            "total_unrealized_pnl": total_pnl,
            "holding_count": len(holdings),
        },
    }


@frappe.whitelist()
def create_holding(fund_master, security_id, security_name, security_type, quantity, cost_price, **kwargs):
    """API: Create a new holding record."""
    hld = frappe.get_doc({
        "doctype": "Holdings Register",
        "fund_master": fund_master,
        "security_id": security_id,
        "security_name": security_name,
        "security_type": security_type,
        "total_quantity": flt(quantity),
        "available_quantity": flt(quantity),
        "cost_price": flt(cost_price),
        "cost_basis_method": "FIFO",
        "status": "Active",
        **kwargs,
    })
    hld.insert()
    hld.submit()
    return hld
