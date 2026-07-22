# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PerformanceFeeEngine(Document):
    """Performance fee calculation with high watermark, hurdle rate, and crystallization."""

    def validate(self):
        self.fetch_high_watermark()
        self.calculate_excess_return()
        self.calculate_performance_fee()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Calculated"

    def fetch_high_watermark(self):
        """Auto-fetch high watermark NAV from NAV History."""
        if not self.high_watermark_nav and self.share_class:
            peak = frappe.get_all(
                "NAV History",
                filters={
                    "share_class": self.share_class,
                    "docstatus": 1,
                    "nav_date": ["<=", self.crystallization_date or self.creation],
                },
                fields=["max(nav) as peak_nav"],
            )[0].peak_nav

            if peak:
                self.high_watermark_nav = peak

        # Also set peak tracking
        if self.high_watermark_nav:
            self.peak_nav = flt(self.high_watermark_nav)

    def calculate_excess_return(self):
        """Calculate excess return over hurdle rate and benchmark."""
        fund_return = flt(self.fund_return_percentage)
        hurdle = flt(self.hurdle_rate)
        benchmark = flt(self.benchmark_return)

        self.excess_return = fund_return - hurdle

        if not self.calculation_period_end:
            self.calculation_period_end = self.crystallization_date

    def calculate_performance_fee(self):
        """Calculate performance fee with high watermark check."""
        fund_return = flt(self.fund_return_percentage)
        hurdle = flt(self.hurdle_rate)
        rate = flt(self.performance_fee_rate)

        excess = fund_return - hurdle

        if excess <= 0:
            self.gross_performance_fee = 0
            self.crystallized_fee = 0
            self.total_fee_accrued = 0
            return

        # Apply high watermark
        current_nav = flt(self.current_nav)
        high_watermark = flt(self.high_watermark_nav)

        if high_watermark > 0 and current_nav <= high_watermark:
            # Below high watermark — no performance fee
            self.high_watermark_adjusted = 1
            self.gross_performance_fee = 0
            self.crystallized_fee = 0
            self.total_fee_accrued = 0
            return

        # Calculate performance fee
        self.gross_performance_fee = excess * (rate / 100) * (flt(self.current_nav) or 1)
        self.crystallized_fee = self.gross_performance_fee
        self.total_fee_accrued = self.gross_performance_fee

        # Calculate drawdown from peak
        if self.peak_nav and self.peak_nav > 0 and current_nav > 0:
            self.drawdown_from_peak = ((self.peak_nav - current_nav) / self.peak_nav) * 100


@frappe.whitelist()
def crystallize_performance_fee(fund_master, share_class, crystallization_date=None):
    """API: Crystallize performance fee for a fund share class."""
    from frappe.utils import today

    crystallization_date = crystallization_date or today()

    # Get latest NAV
    latest_nav = frappe.get_all(
        "NAV History",
        filters={"fund_master": fund_master, "share_class": share_class, "docstatus": 1},
        fields=["nav", "nav_date"],
        order_by="nav_date desc",
        limit=1,
    )

    if not latest_nav:
        frappe.throw("No NAV history found for this share class.")

    # Get active fee structure
    fee = frappe.get_all(
        "Fee Structure",
        filters={"fund_master": fund_master, "fee_type": "Performance Fee", "status": "Active"},
        fields=["name", "performance_fee_rate", "hurdle_rate"],
        limit=1,
    )

    pfe = frappe.get_doc({
        "doctype": "Performance Fee Engine",
        "fund_master": fund_master,
        "share_class": share_class,
        "fee_structure": fee[0].name if fee else None,
        "crystallization_date": crystallization_date,
        "current_nav": latest_nav[0].nav,
        "performance_fee_rate": fee[0].performance_fee_rate if fee else 0,
        "hurdle_rate": fee[0].hurdle_rate if fee else 0,
        "status": "Draft",
    })
    pfe.insert()
    return pfe


@frappe.whitelist()
def get_performance_fee_history(fund_master, share_class=None):
    """API: Get performance fee history."""
    filters = {"fund_master": fund_master}
    if share_class:
        filters["share_class"] = share_class

    return frappe.get_all(
        "Performance Fee Engine",
        filters=filters,
        fields=[
            "name", "crystallization_date", "fund_return_percentage",
            "hurdle_rate", "excess_return", "high_watermark_nav",
            "current_nav", "gross_performance_fee", "crystallized_fee",
            "status",
        ],
        order_by="crystallization_date desc",
    )
