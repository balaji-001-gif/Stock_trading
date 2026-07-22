# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MTMValuation(Document):
    """Mark-to-market valuation of individual securities/holdings."""

    def validate(self):
        self.calculate_values()
        self.calculate_pnl()

    def before_submit(self):
        self.verification_status = "Pending"

    def calculate_values(self):
        """Calculate market value and cost value."""
        qty = flt(self.quantity)
        self.market_value = qty * flt(self.market_price)
        self.cost_value = qty * flt(self.cost_price)

    def calculate_pnl(self):
        """Calculate unrealized P&L and day change."""
        if self.cost_value and self.cost_value > 0:
            self.unrealized_pnl = flt(self.market_value) - flt(self.cost_value)
            self.unrealized_pnl_percentage = (
                flt(self.unrealized_pnl) / flt(self.cost_value)
            ) * 100
        else:
            self.unrealized_pnl = self.market_value
            self.unrealized_pnl_percentage = 100

        # Day change calculation
        yesterday_price = self.get_yesterday_price()
        if yesterday_price and yesterday_price > 0:
            self.day_change = flt(self.market_price) - flt(yesterday_price)
            self.day_change_percentage = (
                flt(self.day_change) / flt(yesterday_price)
            ) * 100

    def get_yesterday_price(self):
        """Get the previous day's market price for this security."""
        from frappe.utils import add_days

        yesterday = frappe.get_all(
            "MTM Valuation",
            filters={
                "fund_master": self.fund_master,
                "security_id": self.security_id,
                "valuation_date": ["<", self.valuation_date],
                "docstatus": 1,
                "name": ["!=", self.name],
            },
            fields=["market_price"],
            order_by="valuation_date desc",
            limit=1,
        )
        return flt(yesterday[0].market_price) if yesterday else None


@frappe.whitelist()
def get_portfolio_valuation(fund_master, valuation_date=None):
    """API: Get portfolio valuation for a fund on a given date."""
    from frappe.utils import today as _today

    valuation_date = valuation_date or _today()

    holdings = frappe.get_all(
        "MTM Valuation",
        filters={
            "fund_master": fund_master,
            "valuation_date": valuation_date,
            "docstatus": 1,
        },
        fields=[
            "security_id",
            "security_name",
            "security_type",
            "quantity",
            "market_price",
            "cost_price",
            "market_value",
            "cost_value",
            "unrealized_pnl",
            "unrealized_pnl_percentage",
            "valuation_method",
        ],
        order_by="market_value desc",
    )

    total_market_value = sum(flt(h["market_value"]) for h in holdings)
    total_cost = sum(flt(h["cost_value"]) for h in holdings)
    total_pnl = sum(flt(h["unrealized_pnl"]) for h in holdings)

    return {
        "date": valuation_date,
        "holdings": holdings,
        "summary": {
            "total_market_value": total_market_value,
            "total_cost": total_cost,
            "total_unrealized_pnl": total_pnl,
            "return_percentage": (
                (total_pnl / total_cost) * 100 if total_cost else 0
            ),
        },
    }
