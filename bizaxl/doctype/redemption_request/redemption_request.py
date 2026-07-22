# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff, today


class RedemptionRequest(Document):
    """Investor redemption request with exit load, TDS, and settlement tracking."""

    def validate(self):
        self.validate_amounts()
        self.calculate_holding_period()
        self.calculate_exit_load()
        self.calculate_net_amount()

    def validate_amounts(self):
        if self.units_requested and self.units_requested <= 0:
            frappe.throw("Units requested must be greater than zero.")
        if self.amount_requested and self.amount_requested <= 0:
            frappe.throw("Amount requested must be greater than zero.")
        self.validate_sufficient_units()

    def validate_sufficient_units(self):
        """Check investor has enough units to redeem."""
        if not self.units_requested or not self.investor or not self.fund_master:
            return
        total_units = frappe.get_all(
            "Allotment Detail",
            filters={
                "investor": self.investor,
                "fund_master": self.fund_master,
                "share_class": self.share_class,
                "docstatus": 1,
            },
            fields=["sum(units) as total"],
        )[0].total or 0

        # Subtract already redeemed
        redeemed_units = frappe.get_all(
            "Redemption Request",
            filters={
                "investor": self.investor,
                "fund_master": self.fund_master,
                "share_class": self.share_class,
                "docstatus": 1,
                "name": ["!=", self.name],
            },
            fields=["sum(units_redeemed) as total"],
        )[0].total or 0

        available = flt(total_units) - flt(redeemed_units)
        if self.units_requested > available:
            frappe.throw(
                f"Insufficient units. Available: {available}, Requested: {self.units_requested}",
                title="Insufficient Holdings",
            )

    def calculate_holding_period(self):
        """Calculate holding period from earliest allotment to redemption date."""
        if not self.investor or not self.fund_master:
            return
        earliest_allotment = frappe.get_all(
            "Allotment Detail",
            filters={
                "investor": self.investor,
                "fund_master": self.fund_master,
                "share_class": self.share_class,
                "docstatus": 1,
            },
            fields=["min(allotment_date) as earliest_date"],
        )[0].earliest_date

        if earliest_allotment:
            ref_date = self.redemption_date or self.request_date or today()
            self.holding_period_days = date_diff(ref_date, earliest_allotment)

    def calculate_exit_load(self):
        """Calculate exit load based on holding period."""
        self.exit_load_applicable = 0
        self.exit_load_percentage = 0
        self.exit_load_amount = 0

        if not self.share_class or not self.redemption_amount:
            return

        # Check exit load matrix from share class
        sc = frappe.get_doc("Share Class", self.share_class)
        if sc.exit_load_matrix:
            for row in sc.exit_load_matrix:
                if self.holding_period_days >= row.from_days and (
                    not row.to_days or self.holding_period_days <= row.to_days
                ):
                    if row.exit_load_percentage > 0:
                        self.exit_load_applicable = 1
                        self.exit_load_percentage = row.exit_load_percentage
                        self.exit_load_amount = flt(self.redemption_amount) * (
                            row.exit_load_percentage / 100
                        )
                    break

    def calculate_net_amount(self):
        """Calculate net payable after exit load and TDS."""
        gross = flt(self.redemption_amount)
        self.net_amount_payable = gross - flt(self.exit_load_amount) - flt(self.tds_deducted)
        if not self.settlement_amount:
            self.settlement_amount = self.net_amount_payable


@frappe.whitelist()
def create_redemption(investor, fund_master, share_class, **kwargs):
    """API: Create a redemption request."""
    red = frappe.get_doc({
        "doctype": "Redemption Request",
        "investor": investor,
        "fund_master": fund_master,
        "share_class": share_class,
        "request_date": today(),
        "redemption_type": kwargs.get("redemption_type", "Partial Redemption"),
        "units_requested": flt(kwargs.get("units_requested", 0)),
        "amount_requested": flt(kwargs.get("amount_requested", 0)),
        "settlement_status": "Pending",
        "approval_status": "Pending",
    })
    red.insert()
    return red


@frappe.whitelist()
def get_investor_redemptions(investor):
    """API: Get all redemptions for an investor."""
    return frappe.get_all(
        "Redemption Request",
        filters={"investor": investor},
        fields=[
            "name", "fund_master", "share_class", "redemption_type",
            "units_requested", "redemption_amount", "exit_load_amount",
            "net_amount_payable", "settlement_status", "request_date",
        ],
        order_by="request_date desc",
    )
