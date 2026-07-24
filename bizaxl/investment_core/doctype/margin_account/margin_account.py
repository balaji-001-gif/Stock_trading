# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MarginAccount(Document):
    """SPAN margin, MTF tracking, pledge management, and risk monitoring."""

    def validate(self):
        self.set_client_code()
        self.calculate_margin()
        self.check_shortfall()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Adequate"

    def set_client_code(self):
        if self.trading_account and not self.client_code:
            self.client_code = frappe.get_value("Trading Account", self.trading_account, "client_code")

    def calculate_margin(self):
        self.total_margin_required = flt(self.span_margin) + flt(self.exposure_margin)
        self.collateral_value = flt(self.cash_margin) + flt(self.pledged_securities_value)

    def check_shortfall(self):
        available = flt(self.available_margin) + flt(self.collateral_value)
        required = flt(self.total_margin_required)

        if available < required:
            self.margin_shortfall = required - available
            self.shortfall_percentage = ((required - available) / required) * 100 if required else 0
            if self.shortfall_percentage > 25:
                self.status = "Alert"
            if self.shortfall_percentage > 50:
                self.status = "Square-Off Initiated"
        else:
            self.margin_shortfall = 0
            self.shortfall_percentage = 0


@frappe.whitelist()
def get_margin_status(trading_account):
    """API: Get latest margin status for a trading account."""
    margins = frappe.get_all(
        "Margin Account",
        filters={"trading_account": trading_account},
        fields=[
            "name", "margin_date", "margin_type", "available_margin",
            "span_margin", "exposure_margin", "total_margin_required",
            "margin_shortfall", "shortfall_percentage", "status",
            "mtf_available", "mtf_used", "collateral_value",
        ],
        order_by="margin_date desc",
        limit=1,
    )
    return margins[0] if margins else None


@frappe.whitelist()
def get_margin_shortfall_alerts(threshold_pct=25):
    """API: Get all trading accounts with margin shortfall above threshold."""
    return frappe.get_all(
        "Margin Account",
        filters={
            "shortfall_percentage": [">=", threshold_pct],
            "status": ["!=", "Adequate"],
        },
        fields=[
            "name", "trading_account", "margin_date", "available_margin",
            "total_margin_required", "margin_shortfall",
            "shortfall_percentage", "status",
        ],
        order_by="shortfall_percentage desc",
    )
