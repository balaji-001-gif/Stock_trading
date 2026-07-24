# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CurrencySettings(Document):
    """Multi-currency exchange rate configuration for cross-border investments."""

    def validate(self):
        self.validate_exchange_rate()
        self.validate_currency_pair()
        self.validate_dates()

    def validate_exchange_rate(self):
        if self.exchange_rate and self.exchange_rate <= 0:
            frappe.throw(
                "Exchange rate must be greater than zero.",
                title="Invalid Rate",
            )

    def validate_currency_pair(self):
        if self.base_currency == self.target_currency:
            frappe.throw(
                "Base and Target currencies must be different.",
                title="Same Currency",
            )

    def validate_dates(self):
        if self.valid_from and self.valid_to:
            if self.valid_from >= self.valid_to:
                frappe.throw(
                    "Valid To must be after Valid From.",
                    title="Invalid Date Range",
                )

    def convert_amount(self, amount, reverse=False):
        """
        Convert amount between currencies.

        Args:
            amount: Amount to convert
            reverse: If True, converts from target to base currency

        Returns:
            Converted amount
        """
        if reverse:
            return flt(amount) / flt(self.exchange_rate)
        return flt(amount) * flt(self.exchange_rate)


@frappe.whitelist()
def get_exchange_rate(base_currency, target_currency, fund_master=None):
    """API: Get current exchange rate for a currency pair."""
    filters = {
        "base_currency": base_currency,
        "target_currency": target_currency,
        "status": "Active",
    }
    if fund_master:
        filters["fund_master"] = fund_master

    rate = frappe.get_value(
        "Currency Settings",
        filters,
        ["name", "exchange_rate", "exchange_rate_date", "rate_source"],
        as_dict=True,
    )
    return rate


@frappe.whitelist()
def convert_currency(amount, from_currency, to_currency, fund_master=None):
    """API: Convert amount between currencies using active exchange rate."""
    rate_doc = get_exchange_rate(from_currency, to_currency, fund_master)
    if not rate_doc:
        frappe.throw(
            f"No active exchange rate found for {from_currency}->{to_currency}",
            title="Rate Not Found",
        )
    cs = frappe.get_doc("Currency Settings", rate_doc.name)
    converted = cs.convert_amount(flt(amount))
    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "original_amount": amount,
        "converted_amount": converted,
        "exchange_rate": cs.exchange_rate,
        "rate_date": cs.exchange_rate_date,
    }
