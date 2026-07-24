# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime


class FundMaster(Document):
    """Master record for an investment fund/portfolio across all 12 verticals."""

    def validate(self):
        self.validate_sebi_registration()
        self.validate_dates()
        self.validate_aum()

    def before_submit(self):
        self.fund_status = "Active"
        if not self.sebi_registration_number:
            frappe.throw(
                "SEBI Registration Number is required before activating a fund.",
                title="Missing Registration",
            )

    def before_cancel(self):
        self.fund_status = "Suspended"

    def validate_sebi_registration(self):
        """Ensure SEBI registration is provided for regulated fund types."""
        regulated_types = [
            "Mutual Fund",
            "PMS",
            "AIF Category I",
            "AIF Category II",
            "AIF Category III",
            "REIT",
            "InvIT",
        ]
        if self.fund_type in regulated_types and not self.sebi_registration_number:
            frappe.throw(
                f"SEBI Registration Number is mandatory for {self.fund_type}.",
                title="Regulatory Requirement",
            )

    def validate_dates(self):
        """Validate inception and close dates."""
        if self.inception_date and self.inception_date > today():
            frappe.throw(
                "Inception Date cannot be in the future.",
                title="Invalid Date",
            )
        if self.close_date and self.inception_date:
            if self.close_date <= self.inception_date:
                frappe.throw(
                    "Close Date must be after Inception Date.",
                    title="Invalid Date Range",
                )

    def validate_aum(self):
        """Ensure AUM is non-negative."""
        if self.aum_current and self.aum_current < 0:
            frappe.throw(
                "AUM cannot be negative.",
                title="Invalid AUM",
            )

    def get_share_classes(self):
        """Return linked share classes."""
        return frappe.get_all(
            "Share Class",
            filters={"fund_master": self.name},
            fields=["name", "class_name", "nav", "expense_ratio"],
        )

    def get_fee_structures(self):
        """Return linked fee structures."""
        return frappe.get_all(
            "Fee Structure",
            filters={"fund_master": self.name},
            fields=["name", "fee_type", "fee_percentage", "fee_frequency"],
        )

    def get_current_nav(self):
        """Get the latest NAV across all share classes."""
        share_classes = self.get_share_classes()
        return {sc["name"]: sc["nav"] for sc in share_classes if sc.get("nav")}


@frappe.whitelist()
def get_fund_summary(fund_name):
    """API endpoint to get a summary of fund details."""
    fund = frappe.get_doc("Fund Master", fund_name)
    return {
        "name": fund.name,
        "fund_name": fund.fund_name,
        "fund_type": fund.fund_type,
        "fund_status": fund.fund_status,
        "aum": fund.aum_current,
        "aum_date": fund.aum_date,
        "share_classes": fund.get_share_classes(),
        "inception_date": fund.inception_date,
        "benchmark": fund.benchmark_index,
        "risk_level": fund.risk_level,
    }


@frappe.whitelist()
def get_funds_by_type(fund_type=None, status="Active"):
    """API endpoint to list funds by type and status."""
    filters = {"fund_status": status}
    if fund_type:
        filters["fund_type"] = fund_type

    return frappe.get_all(
        "Fund Master",
        filters=filters,
        fields=[
            "name",
            "fund_name",
            "fund_code",
            "fund_type",
            "fund_category",
            "aum_current",
            "inception_date",
            "fund_status",
        ],
        order_by="modified desc",
    )
