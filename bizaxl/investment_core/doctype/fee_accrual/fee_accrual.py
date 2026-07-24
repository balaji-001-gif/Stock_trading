# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff


class FeeAccrual(Document):
    """Fee accrual tracking for all fee types over specific periods."""

    def validate(self):
        self.calculate_fee_amount()
        self.calculate_waiver()
        self.calculate_net_amount()

    def before_submit(self):
        self.accrual_date = self.accrual_date or self.period_end
        self.status = "Accrued"

    def calculate_fee_amount(self):
        """Calculate fee amount based on fee type and period."""
        if self.fee_type == "Management Fee":
            self.calculate_management_fee()
        elif self.fee_type == "Performance Fee":
            self.performance_fee_component = self.gross_fee_amount
        elif self.fee_type == "Carried Interest":
            self.carried_interest_component = self.gross_fee_amount

        self.total_accrued = (
            flt(self.management_fee_component)
            + flt(self.performance_fee_component)
            + flt(self.carried_interest_component)
            + flt(self.service_fee_component)
            + flt(self.other_fees_component)
        )

    def calculate_management_fee(self):
        """Calculate management fee using daily accrual method."""
        if not self.days_in_period:
            self.days_in_period = date_diff(self.period_end, self.period_start)
        if not self.days_in_period or self.days_in_period <= 0:
            self.days_in_period = 1

        annual_fee = flt(self.aum_for_period) * (flt(self.fee_rate) / 100)
        self.gross_fee_amount = annual_fee * (flt(self.days_in_period) / flt(self.total_days or 365))
        self.management_fee_component = self.gross_fee_amount

    def calculate_waiver(self):
        """Apply fee waiver if applicable."""
        if self.waiver_percentage and self.waiver_percentage > 0:
            self.waiver_amount = flt(self.gross_fee_amount) * (flt(self.waiver_percentage) / 100)
        else:
            self.waiver_amount = 0

    def calculate_net_amount(self):
        """Calculate net fee after waiver."""
        self.net_fee_amount = flt(self.gross_fee_amount) - flt(self.waiver_amount)


@frappe.whitelist()
def calculate_monthly_fee(fund_master, fee_type="Management Fee", year=None, month=None):
    """API: Calculate and accrue fees for a fund for a given month."""
    from frappe.utils import get_first_day, get_last_day, today
    from datetime import date

    today_date = date.today()
    year = year or today_date.year
    month = month or today_date.month

    period_start = get_first_day(date(year, month, 1))
    period_end = get_last_day(date(year, month, 1))

    # Get active fee structure
    fees = frappe.get_all(
        "Fee Structure",
        filters={
            "fund_master": fund_master,
            "fee_type": fee_type,
            "status": "Active",
            "effective_from": ["<=", period_end],
        },
        fields=["name", "management_fee_rate", "management_fee_basis"],
        limit=1,
    )

    if not fees:
        frappe.throw(f"No active {fee_type} found for {fund_master}")

    # Get AUM
    aum = frappe.get_value("Fund Master", fund_master, "aum_current") or 0

    fee_doc = frappe.get_doc({
        "doctype": "Fee Accrual",
        "fund_master": fund_master,
        "fee_structure": fees[0].name,
        "fee_type": fee_type,
        "period_start": period_start,
        "period_end": period_end,
        "aum_for_period": aum,
        "fee_rate": fees[0].management_fee_rate,
        "days_in_period": date_diff(period_end, period_start),
        "status": "Draft",
    })
    fee_doc.insert()
    fee_doc.submit()
    return fee_doc


@frappe.whitelist()
def get_fee_accruals(fund_master, from_date=None, to_date=None):
    """API: Get fee accruals for a fund."""
    filters = {"fund_master": fund_master}
    if from_date and to_date:
        filters["period_start"] = [">=", from_date]
        filters["period_end"] = ["<=", to_date]
    elif from_date:
        filters["period_start"] = [">=", from_date]

    return frappe.get_all(
        "Fee Accrual",
        filters=filters,
        fields=[
            "name", "fee_type", "period_start", "period_end",
            "aum_for_period", "fee_rate", "gross_fee_amount",
            "waiver_amount", "net_fee_amount", "status",
        ],
        order_by="period_start desc",
    )
