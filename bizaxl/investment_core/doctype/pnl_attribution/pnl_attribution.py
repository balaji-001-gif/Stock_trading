# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PNLAttribution(Document):
    """Profit and loss attribution by security, lot, and transaction."""

    def validate(self):
        self.calculate_pnl()

    def calculate_pnl(self):
        qty = flt(self.quantity)
        if self.transaction_type in ("Sales", "Redemption", "Maturity"):
            sale_value = qty * flt(self.sale_price)
            cost_value = qty * flt(self.cost_price)
            self.gross_realized_pnl = sale_value - cost_value
            charges = flt(self.brokerage) + flt(self.taxes) + flt(self.other_charges)
            self.net_realized_pnl = self.gross_realized_pnl - charges


@frappe.whitelist()
def get_pnl_summary(fund_master, from_date=None, to_date=None):
    """API: Get P&L summary for a fund."""
    filters = {"fund_master": fund_master}
    if from_date and to_date:
        filters["pnl_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["pnl_date"] = [">=", from_date]
    elif to_date:
        filters["pnl_date"] = ["<=", to_date]

    realized = frappe.get_all(
        "PNL Attribution",
        filters={"fund_master": fund_master, "pnl_type": ["in", ("Realized", "Both")]},
        fields=["sum(gross_realized_pnl) as total_realized", "sum(net_realized_pnl) as total_net"],
    )

    unrealized = frappe.db.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["sum(unrealized_pnl) as total_unrealized"],
    )

    return {
        "total_realized_pnl": realized[0].total_realized if realized else 0,
        "total_net_realized_pnl": realized[0].total_net if realized else 0,
        "total_unrealized_pnl": unrealized[0].total_unrealized if unrealized else 0,
    }
