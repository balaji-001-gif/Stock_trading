# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PerformanceAttribution(Document):
    """Performance attribution with TWRR, MWRR, and Brinson sector attribution."""

    def validate(self):
        self.calculate_excess_return()
        self.calculate_top_contributors()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Calculated"

    def calculate_excess_return(self):
        """Calculate excess return over benchmark."""
        total_ret = flt(self.total_return_percentage)
        bench = flt(self.benchmark_return)
        if total_ret or bench:
            self.excess_return = total_ret - bench

    def calculate_top_contributors(self):
        """Identify top contributors and detractors from P&L data."""
        if not self.fund_master:
            return

        holdings = frappe.get_all(
            "Holdings Register",
            filters={"fund_master": self.fund_master, "status": "Active"},
            fields=["security_name", "unrealized_pnl", "market_value"],
            order_by="unrealized_pnl desc",
            limit=10,
        )

        positive = [h for h in holdings if flt(h.get("unrealized_pnl", 0)) > 0]
        negative = [h for h in holdings if flt(h.get("unrealized_pnl", 0)) < 0]

        if positive:
            self.top_contributors = "\n".join(
                f"{h['security_name']}: {flt(h['unrealized_pnl']):,.2f}"
                for h in positive[:5]
            )
        if negative:
            self.top_detractors = "\n".join(
                f"{h['security_name']}: {flt(h['unrealized_pnl']):,.2f}"
                for h in negative[:5]
            )


@frappe.whitelist()
def calculate_attribution(fund_master, attribution_date=None, period="Monthly", method="TWRR (Time-Weighted)"):
    """API: Calculate performance attribution for a fund."""
    from frappe.utils import today

    attribution_date = attribution_date or today()

    pa = frappe.get_doc({
        "doctype": "Performance Attribution",
        "fund_master": fund_master,
        "attribution_date": attribution_date,
        "attribution_period": period,
        "calculation_method": method,
        "status": "Draft",
        "currency": frappe.get_value("Fund Master", fund_master, "currency") or "INR",
    })
    pa.insert()
    return pa


@frappe.whitelist()
def get_attribution_history(fund_master, limit=12):
    """API: Get attribution history for a fund."""
    return frappe.get_all(
        "Performance Attribution",
        filters={"fund_master": fund_master},
        fields=[
            "name", "attribution_date", "attribution_period", "calculation_method",
            "total_return_percentage", "benchmark_return", "excess_return",
            "twrr", "annualized_return", "sector_allocation_effect",
            "sector_selection_effect", "status",
        ],
        order_by="attribution_date desc",
        limit_page_length=limit,
    )


@frappe.whitelist()
def get_performance_summary(fund_master):
    """API: Get summarized performance metrics for dashboards."""
    latest_pa = frappe.get_all(
        "Performance Attribution",
        filters={"fund_master": fund_master, "status": "Calculated"},
        fields=[
            "total_return_percentage", "benchmark_return", "excess_return",
            "twrr", "annualized_return", "attribution_date",
        ],
        order_by="attribution_date desc",
        limit=1,
    )

    # TWRR trend
    twrr_trend = frappe.get_all(
        "Performance Attribution",
        filters={"fund_master": fund_master, "status": "Calculated"},
        fields=["attribution_date", "twrr"],
        order_by="attribution_date asc",
        limit=24,
    )

    return {
        "latest": latest_pa[0] if latest_pa else None,
        "twrr_trend": twrr_trend,
        "fund_master": fund_master,
    }
