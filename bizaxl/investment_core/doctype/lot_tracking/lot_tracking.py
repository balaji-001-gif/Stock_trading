# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff, today


class LotTracking(Document):
    """Lot-wise cost basis tracking with FIFO/LIFO/HIFO support."""

    def validate(self):
        self.calculate_values()
        self.validate_quantities()

    def after_save(self):
        """Update holding register quantities after lot is saved to DB."""
        self.update_holding_quantity()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Open"

    def calculate_values(self):
        qty = flt(self.original_quantity)
        self.total_cost = qty * flt(self.unit_cost)
        self.remaining_quantity = flt(self.original_quantity) - flt(self.sold_quantity)

    def validate_quantities(self):
        if self.original_quantity <= 0:
            frappe.throw("Original quantity must be greater than zero.")
        if self.remaining_quantity < 0:
            frappe.throw("Remaining quantity cannot be negative.")

    def update_holding_quantity(self):
        """Sync quantities with holding register."""
        if self.holding:
            total_remaining = frappe.get_all(
                "Lot Tracking",
                filters={"holding": self.holding, "docstatus": 1},
                fields=["sum(remaining_quantity) as total"],
            )[0].total or 0
            frappe.db.set_value(
                "Holdings Register",
                self.holding,
                {"available_quantity": total_remaining, "total_quantity": total_remaining},
            )

    def record_sale(self, sale_quantity, sale_price):
        """Record a partial or full sale from this lot (FIFO basis)."""
        if sale_quantity <= 0:
            frappe.throw("Sale quantity must be greater than zero.")
        if sale_quantity > flt(self.remaining_quantity):
            frappe.throw(
                f"Cannot sell {sale_quantity} units. Only {self.remaining_quantity} remaining in lot."
            )

        sale_value = flt(sale_quantity) * flt(sale_price)
        cost_of_goods = flt(sale_quantity) * flt(self.unit_cost)
        realized_pnl = sale_value - cost_of_goods

        self.sold_quantity = flt(self.sold_quantity) + flt(sale_quantity)
        self.remaining_quantity = flt(self.remaining_quantity) - flt(sale_quantity)
        self.total_sale_value = flt(self.total_sale_value) + sale_value
        self.realized_pnl = flt(self.realized_pnl) + realized_pnl
        self.realized_pnl_percentage = (
            (realized_pnl / cost_of_goods) * 100 if cost_of_goods else 0
        )

        if self.remaining_quantity <= 0:
            self.status = "Closed"

        self.save()

        # Update holding register
        self.update_holding_quantity()

        # Create P&L attribution record
        pnl_data = {
            "doctype": "PNL Attribution",
            "holding": self.holding,
            "lot": self.name,
            "fund_master": self.fund_master or frappe.db.get_value("Holdings Register", self.holding, "fund_master"),
            "security_id": self.security_id,
            "transaction_type": "Sales",
            "quantity": sale_quantity,
            "sale_price": sale_price,
            "cost_price": self.unit_cost,
            "pnl_date": today(),
            "pnl_type": "Realized",
            "gross_realized_pnl": realized_pnl,
            "net_realized_pnl": realized_pnl,
            "cost_basis_method": self.cost_basis_method or "FIFO",
        }
        pnl_doc = frappe.get_doc(pnl_data)
        pnl_doc.insert()
        pnl_doc.submit()

        return realized_pnl


@frappe.whitelist()
def get_lots_by_holding(holding):
    """API: Get all purchase lots for a holding."""
    return frappe.get_all(
        "Lot Tracking",
        filters={"holding": holding},
        fields=[
            "name", "lot_date", "lot_type", "original_quantity",
            "remaining_quantity", "unit_cost", "total_cost",
            "realized_pnl", "status", "tax_lot_status",
        ],
        order_by="lot_date asc",
    )


@frappe.whitelist()
def sell_from_lots(holding, sale_quantity, sale_price, method="FIFO"):
    """API: Sell from lots using specified cost basis method."""
    lots = frappe.get_all(
        "Lot Tracking",
        filters={
            "holding": holding,
            "status": ["in", ["Open", "Partially Closed"]],
            "remaining_quantity": [">", 0],
        },
        fields=["name", "remaining_quantity", "unit_cost", "lot_date"],
        order_by="lot_date asc" if method == "FIFO" else "lot_date desc",
    )

    if not lots:
        frappe.throw("No available lots to sell from.")

    remaining_to_sell = flt(sale_quantity)
    total_pnl = 0
    sale_details = []

    for lot in lots:
        if remaining_to_sell <= 0:
            break

        sell_qty = min(remaining_to_sell, flt(lot["remaining_quantity"]))
        lot_doc = frappe.get_doc("Lot Tracking", lot["name"])
        pnl = lot_doc.record_sale(sell_qty, sale_price)
        total_pnl += pnl
        remaining_to_sell -= sell_qty

        sale_details.append({
            "lot": lot["name"],
            "quantity": sell_qty,
            "cost_price": lot["unit_cost"],
            "realized_pnl": pnl,
        })

    return {
        "total_quantity": flt(sale_quantity) - remaining_to_sell,
        "total_realized_pnl": total_pnl,
        "method": method,
        "details": sale_details,
    }
