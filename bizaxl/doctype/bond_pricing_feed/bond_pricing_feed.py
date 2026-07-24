# Copyright (c) 2026, bizaxl and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class BondPricingFeed(Document):
    """Bond Pricing Feed — tracks bond pricing, credit ratings, and fixed income analytics"""

    def validate(self):
        if not self.pricing_date:
            self.pricing_date = today()
        if not self.valuation_date:
            self.valuation_date = today()
        self.calculate_accrued_interest()

    def calculate_accrued_interest(self):
        """Calculate accrued interest for coupon-bearing bonds"""
        if self.coupon_rate and self.last_price and self.maturity_date:
            from datetime import datetime, date
            from dateutil.relativedelta import relativedelta
            pricing = self.pricing_date or today()
            if isinstance(pricing, str):
                from frappe.utils.data import getdate
                pricing = getdate(pricing)
            days_since_last_coupon = 0
            freq_months = {"Monthly": 1, "Quarterly": 3, "Semi-Annual": 6, "Annual": 12}
            freq = self.pricing_frequency or "Annual"
            months = freq_months.get(freq, 12)
            last_coupon = pricing - relativedelta(months=months)
            if isinstance(last_coupon, date):
                days_since_last_coupon = (pricing - last_coupon).days
            if days_since_last_coupon > 0:
                annual_interest = (self.coupon_rate / 100) * (self.face_value or 1000)
                self.accrued_interest = round(
                    annual_interest * days_since_last_coupon / 365, 2
                )


@frappe.whitelist()
def get_bond_price(isin=None, instrument_type=None, pricing_source=None):
    """Fetch latest bond pricing from the feed"""
    filters = {"status": "Active"}
    if isin:
        filters["isin"] = isin
    if instrument_type:
        filters["instrument_type"] = instrument_type
    if pricing_source:
        filters["pricing_source"] = pricing_source

    prices = frappe.get_all(
        "Bond Pricing Feed",
        filters=filters,
        fields=[
            "name", "isin", "instrument_name", "instrument_type", "issuer",
            "credit_rating", "coupon_rate", "bid_price", "ask_price", "last_price",
            "ytm", "modified_duration", "convexity", "g_spread", "z_spread", "oas",
            "pricing_date", "pricing_source", "maturity_date", "accrued_interest"
        ],
        order_by="pricing_date desc",
        limit=50
    )
    return prices


@frappe.whitelist()
def get_bond_analytics(isin):
    """Get analytics for a specific bond — spread history, duration, convexity"""
    records = frappe.get_all(
        "Bond Pricing Feed",
        filters={"isin": isin, "status": "Active"},
        fields=[
            "name", "isin", "instrument_name", "issuer", "credit_rating",
            "coupon_rate", "ytm", "modified_duration", "convexity",
            "g_spread", "z_spread", "oas", "bid_price", "ask_price",
            "last_price", "pricing_date", "pricing_source", "maturity_date",
            "face_value", "outstanding_amount", "accrued_interest"
        ],
        order_by="pricing_date desc",
        limit=1
    )
    if not records:
        frappe.msgprint(f"No bond found with ISIN: {isin}")
        return None
    return records[0]


@frappe.whitelist()
def get_credit_rating_history(isin, agency=None):
    """Get credit rating history for a bond from the feed"""
    filters = {"isin": isin}
    if agency:
        filters["rating_agency"] = agency
    ratings = frappe.get_all(
        "Bond Pricing Feed",
        filters=filters,
        fields=["name", "credit_rating", "rating_agency", "pricing_date", "modified"],
        order_by="pricing_date desc",
        limit=20
    )
    return ratings
