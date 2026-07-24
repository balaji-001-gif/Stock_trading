# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class SubscriptionRequest(Document):
    """Investor subscription application with NAV-based pricing and allotment."""

    def validate(self):
        self.validate_amounts()
        self.calculate_total_investment()
        self.validate_kyc()

    def before_submit(self):
        if self.allotment_status == "Pending":
            self.allotment_status = "Allotted"
            self.allotment_date = today()

    def validate_amounts(self):
        if self.investment_amount <= 0:
            frappe.throw(
                "Investment amount must be greater than zero.",
                title="Invalid Amount",
            )

    def calculate_total_investment(self):
        """Calculate total investment including any entry loads."""
        entry_load = 0
        if self.share_class:
            sc = frappe.get_cached_value(
                "Share Class", self.share_class, "entry_load"
            )
            entry_load = flt(sc) if sc else 0
        self.total_investment = flt(self.investment_amount) * (1 + entry_load / 100)

    def validate_kyc(self):
        """Ensure investor KYC is completed."""
        kyc = frappe.get_cached_value(
            "Investor Profile", self.investor, "kyc_status"
        )
        if kyc not in ("Verified",):
            frappe.throw(
                f"Investor KYC is not verified. Current status: {kyc}",
                title="KYC Required",
            )

    def calculate_units(self, nav):
        """Calculate units to allot based on NAV."""
        if not nav or nav <= 0:
            frappe.throw("Invalid NAV value for unit calculation.")
        self.applicable_nav = nav
        self.units_allotted = flt(self.total_investment) / flt(nav)

    def process_allotment(self, nav):
        """Process full allotment with NAV."""
        # Get units before
        self.units_before = self.get_existing_units()

        # Calculate and allot
        self.calculate_units(nav)
        self.allotment_status = "Allotted"
        self.allotment_date = today()

        # Get units after
        self.units_after = flt(self.units_before) + flt(self.units_allotted)
        self.save()

        # Create allotment record
        allotment = frappe.get_doc({
            "doctype": "Allotment Detail",
            "investor": self.investor,
            "fund_master": self.fund_master,
            "share_class": self.share_class,
            "subscription_request": self.name,
            "units": self.units_allotted,
            "nav": nav,
            "amount": self.total_investment,
            "allotment_date": today(),
        })
        allotment.insert()
        allotment.submit()

        return allotment

    def get_existing_units(self):
        """Get total units held by this investor in this fund/share class."""
        units = frappe.get_all(
            "Allotment Detail",
            filters={
                "investor": self.investor,
                "fund_master": self.fund_master,
                "share_class": self.share_class,
                "docstatus": 1,
            },
            fields=["sum(units) as total_units", "sum(amount) as total_amount"],
        )
        return flt(units[0].total_units) if units else 0


@frappe.whitelist()
def create_subscription(investor, fund_master, share_class, investment_amount, **kwargs):
    """API: Create a new subscription request."""
    sub = frappe.get_doc({
        "doctype": "Subscription Request",
        "investor": investor,
        "fund_master": fund_master,
        "share_class": share_class,
        "subscription_date": today(),
        "application_date": today(),
        "investment_amount": flt(investment_amount),
        "subscription_type": kwargs.get("subscription_type", "Lump Sum"),
        "allotment_status": "Pending",
        "payment_status": "Pending",
        "approval_status": "Pending",
    })
    for key, value in kwargs.items():
        if hasattr(sub, key) and not sub.get(key):
            try:
                sub.set(key, value)
            except Exception:
                pass
    sub.insert()
    return sub


@frappe.whitelist()
def get_investor_subscriptions(investor):
    """API: Get all subscriptions for an investor."""
    return frappe.get_all(
        "Subscription Request",
        filters={"investor": investor},
        fields=[
            "name",
            "fund_master",
            "share_class",
            "subscription_type",
            "investment_amount",
            "units_allotted",
            "applicable_nav",
            "allotment_status",
            "payment_status",
            "subscription_date",
        ],
        order_by="subscription_date desc",
    )
