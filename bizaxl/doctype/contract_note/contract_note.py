# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ContractNote(Document):
    """SEBI-compliant contract note with brokerage, STT, GST, stamp duty charges."""

    def validate(self):
        self.set_client_code()
        self.calculate_charges()
        self.calculate_net()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Generated"

    def set_client_code(self):
        if self.trading_account and not self.client_code:
            self.client_code = frappe.get_value("Trading Account", self.trading_account, "client_code")

    def calculate_charges(self):
        """Calculate all charges per SEBI contract note format."""
        turnover = flt(self.total_turnover)
        if not turnover:
            return

        # Brokerage (typically 0.01% to 0.5% for retail)
        brokerage_rate = flt(self.brokerage_rate) / 100 if self.brokerage_rate else 0
        self.brokerage = turnover * brokerage_rate

        # STT (0.1% delivery, 0.025% intraday equity, varies for F&O)
        stt_rate = flt(self.stt_rate) / 100 if self.stt_rate else 0
        self.stt = turnover * stt_rate

        # GST 18% on brokerage
        self.gst = flt(self.brokerage) * 0.18

        # SEBI turnover fees (Rs. 10 per crore approximately)
        self.sebi_fees = turnover * 0.000001  # ~0.0001%

        # Stamp duty (varies by state, ~0.005% to 0.015%)
        stamp_rate = 0.0001
        self.stamp_duty = turnover * stamp_rate

    def calculate_net(self):
        """Calculate total charges and net payable/receivable."""
        turnover = flt(self.total_turnover)
        self.total_charges = (
            flt(self.brokerage)
            + flt(self.stt)
            + flt(self.gst)
            + flt(self.sebi_fees)
            + flt(self.stamp_duty)
            + flt(self.other_charges)
        )
        self.net_amount = flt(self.sell_value) - flt(self.buy_value)
        self.net_payable = self.net_amount - self.total_charges


@frappe.whitelist()
def generate_contract_note(trading_account, trade_date, **kwargs):
    """API: Generate a contract note from trade data."""
    doc = frappe.get_doc({
        "doctype": "Contract Note",
        "trading_account": trading_account,
        "trade_date": trade_date,
        "exchange": kwargs.get("exchange", "NSE"),
        "segment": kwargs.get("segment", "Equity Cash"),
        "symbol": kwargs.get("symbol"),
        "quantity": int(kwargs.get("quantity", 0)),
        "trade_price": flt(kwargs.get("trade_price", 0)),
        "total_turnover": flt(kwargs.get("total_turnover", 0)),
        "buy_value": flt(kwargs.get("buy_value", 0)),
        "sell_value": flt(kwargs.get("sell_value", 0)),
        "settlement_type": kwargs.get("settlement_type", "T+1"),
        "status": "Draft",
    })
    doc.insert()
    doc.submit()
    return doc


@frappe.whitelist()
def get_settlement_report(trading_account, from_date=None, to_date=None):
    """API: Get settlement report for a trading account."""
    filters = {"trading_account": trading_account}
    if from_date:
        filters["trade_date"] = [">=", from_date]
    if to_date:
        filters["trade_date"] = ["<=", to_date]

    return frappe.get_all(
        "Contract Note",
        filters=filters,
        fields=[
            "name", "trade_date", "settlement_date", "symbol",
            "quantity", "total_turnover", "brokerage", "stt",
            "gst", "total_charges", "net_amount", "net_payable",
            "settlement_status", "status",
        ],
        order_by="trade_date desc",
    )
