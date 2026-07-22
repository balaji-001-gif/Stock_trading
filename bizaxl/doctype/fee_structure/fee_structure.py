# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt, cint


class FeeStructure(Document):
    """Fee configuration for funds — management fee, performance fee, carried interest, TDS."""

    def validate(self):
        self.validate_rates()
        self.validate_effective_dates()
        self.validate_waterfall_split()
        self.validate_tds()

    def validate_rates(self):
        if self.management_fee_rate and self.management_fee_rate > 100:
            frappe.throw(
                "Management Fee Rate cannot exceed 100%.",
                title="Invalid Fee Rate",
            )
        if self.performance_fee_rate and self.performance_fee_rate > 100:
            frappe.throw(
                "Performance Fee Rate cannot exceed 100%.",
                title="Invalid Fee Rate",
            )
        if self.carried_interest_rate and self.carried_interest_rate > 100:
            frappe.throw(
                "Carried Interest Rate cannot exceed 100%.",
                title="Invalid Fee Rate",
            )

    def validate_effective_dates(self):
        if self.effective_from and self.effective_to:
            if self.effective_from >= self.effective_to:
                frappe.throw(
                    "Effective To must be after Effective From.",
                    title="Invalid Date Range",
                )

    def validate_waterfall_split(self):
        if self.lp_share_percentage and self.gp_share_percentage:
            total = flt(self.lp_share_percentage) + flt(self.gp_share_percentage)
            if total != 100:
                frappe.throw(
                    f"LP Share ({self.lp_share_percentage}%) + "
                    f"GP Share ({self.gp_share_percentage}%) must equal 100%. "
                    f"Current total: {total}%.",
                    title="Invalid Waterfall Split",
                )

    def validate_tds(self):
        if self.tds_applicable and not self.tds_rate:
            frappe.throw(
                "TDS Rate is required when TDS is applicable.",
                title="Missing TDS Rate",
            )

    def calculate_management_fee(self, aum, days_in_period):
        """
        Calculate management fee for a period.

        Args:
            aum: Average AUM for the period
            days_in_period: Number of days in the fee period

        Returns:
            Calculated fee amount
        """
        if not self.management_fee_rate or not aum:
            return 0

        if self.management_fee_frequency == "Annual":
            annual_fee = aum * (self.management_fee_rate / 100)
            daily_fee = annual_fee / 365
            return daily_fee * days_in_period
        elif self.management_fee_frequency == "Monthly":
            return aum * (self.management_fee_rate / 100)
        elif self.management_fee_frequency == "Quarterly":
            return aum * (self.management_fee_rate / 100)
        else:
            return aum * (self.management_fee_rate / 100) * (days_in_period / 365)

    def calculate_performance_fee(self, fund_return, benchmark_return=None):
        """
        Calculate performance fee based on the configured model.

        Args:
            fund_return: Fund return percentage for the period
            benchmark_return: Benchmark return percentage (if benchmark relative)

        Returns:
            Calculated fee percentage
        """
        if not self.performance_fee_rate:
            return 0

        excess_return = fund_return

        if self.performance_fee_model == "Hurdle Rate":
            excess_return = fund_return - flt(self.hurdle_rate)

        elif self.performance_fee_model == "Benchmark Relative":
            excess_return = fund_return - flt(benchmark_return or 0)

        elif self.performance_fee_model == "High Watermark":
            # High watermark logic is applied externally
            pass

        if excess_return <= 0:
            return 0

        return excess_return * (self.performance_fee_rate / 100)

    def get_tds_amount(self, fee_amount):
        """Calculate TDS on fee payment."""
        if not self.tds_applicable or not self.tds_rate:
            return 0

        if self.tds_threshold and fee_amount <= self.tds_threshold:
            return 0

        tds = fee_amount * (self.tds_rate / 100)
        return tds


@frappe.whitelist()
def get_active_fees_for_fund(fund_master, fee_type=None):
    """API: Get active fee structures for a fund."""
    filters = {
        "fund_master": fund_master,
        "status": "Active",
        "effective_from": ["<=", today()],
    }
    if fee_type:
        filters["fee_type"] = fee_type

    return frappe.get_all(
        "Fee Structure",
        filters=filters,
        fields=[
            "name",
            "fee_name",
            "fee_type",
            "fee_category",
            "management_fee_rate",
            "performance_fee_rate",
            "carried_interest_rate",
            "effective_from",
            "effective_to",
        ],
        order_by="effective_from desc",
    )
