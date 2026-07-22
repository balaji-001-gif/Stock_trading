# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class TradeOrder(Document):
    """Order management with order types, execution, and status tracking."""

    def validate(self):
        self.set_client_code()
        self.calculate_turnover()
        self.validate_order()

    def before_submit(self):
        if self.status == "Pending":
            self.status = "Open"

    def set_client_code(self):
        if self.trading_account and not self.client_code:
            self.client_code = frappe.get_value("Trading Account", self.trading_account, "client_code")

    def calculate_turnover(self):
        qty = flt(self.filled_quantity) or flt(self.quantity)
        price = flt(self.average_price) or flt(self.limit_price)
        self.total_turnover = qty * price

    def validate_order(self):
        if not self.transaction_type:
            frappe.throw("Transaction type (Buy/Sell) is required.")
        if self.order_type in ("Limit", "Stop Loss (SL)") and not self.limit_price:
            frappe.throw("Limit price is required for Limit and SL orders.")
        if self.order_type in ("Cover Order (CO)", "Bracket Order (BO)") and not self.stop_loss_price:
            frappe.msgprint("Stop loss price recommended for CO/BO orders.", alert=True)


@frappe.whitelist()
def place_order(trading_account, symbol, transaction_type, quantity, order_type="Market", **kwargs):
    """API: Place a new trade order."""
    doc = frappe.get_doc({
        "doctype": "Trade Order",
        "trading_account": trading_account,
        "transaction_type": transaction_type,
        "order_date": now_datetime(),
        "order_type": order_type,
        "symbol": symbol,
        "quantity": int(quantity),
        "exchange": kwargs.get("exchange", "NSE"),
        "segment": kwargs.get("segment", "Equity Cash"),
        "instrument_type": kwargs.get("instrument_type", "Equity"),
        "limit_price": flt(kwargs.get("limit_price", 0)),
        "trigger_price": flt(kwargs.get("trigger_price", 0)),
        "validity": kwargs.get("validity", "Day"),
        "status": "Pending",
    })
    doc.insert()
    doc.submit()
    return doc


@frappe.whitelist()
def get_open_orders(trading_account=None):
    """API: Get all open orders."""
    filters = {"status": ["in", ("Pending", "Open", "Partially Filled")]}
    if trading_account:
        filters["trading_account"] = trading_account
    return frappe.get_all(
        "Trade Order",
        filters=filters,
        fields=[
            "name", "trading_account", "symbol", "order_type",
            "quantity", "filled_quantity", "limit_price",
            "average_price", "status", "order_date", "exchange",
        ],
        order_by="order_date desc",
    )


@frappe.whitelist()
def get_trade_history(trading_account, limit=50):
    """API: Get trade history for a trading account."""
    return frappe.get_all(
        "Trade Order",
        filters={"trading_account": trading_account},
        fields=[
            "name", "symbol", "order_type", "quantity", "filled_quantity",
            "average_price", "total_turnover", "status", "order_date",
            "filled_date", "exchange", "segment",
        ],
        order_by="order_date desc",
        limit_page_length=limit,
    )
