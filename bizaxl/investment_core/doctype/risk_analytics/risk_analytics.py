# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class RiskAnalytics(Document):
    """Risk metrics computation — Sharpe, Alpha, Beta, VaR, drawdown analysis."""

    def validate(self):
        self.calculate_risk_metrics()
        self.calculate_var()
        self.validate_values()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Calculated"

    def calculate_risk_metrics(self):
        """Calculate derived risk metrics from input values."""
        port_ret = flt(self.portfolio_return)
        risk_free = flt(self.risk_free_rate)
        port_vol = flt(self.portfolio_volatility)
        bench_ret = flt(self.benchmark_return)
        bench_vol = flt(self.benchmark_volatility)

        # Sharpe Ratio
        if port_vol > 0:
            self.sharpe_ratio = (port_ret - risk_free) / port_vol

        # Sortino Ratio
        downside = flt(self.downside_deviation)
        if downside > 0:
            self.sortino_ratio = (port_ret - risk_free) / downside

        # Tracking Error
        if bench_ret or port_ret:
            self.tracking_error = abs(port_ret - bench_ret)

        # Information Ratio
        te = flt(self.tracking_error)
        if te > 0:
            self.information_ratio = (port_ret - bench_ret) / te

        # Beta
        if bench_vol > 0 and port_vol > 0:
            # Simplified: covariance / variance of market
            # Full calculation would use regression on returns history
            # TODO: compute actual correlation via regression on NAV vs benchmark returns
            correlation = 0.7  # Placeholder — replace with actual correlation
            self.beta = correlation * (port_vol / bench_vol)

        # Alpha (CAPM)
        beta = flt(self.beta)
        if beta:
            expected_return = risk_free + beta * (bench_ret - risk_free)
            self.alpha = port_ret - expected_return

        # R-Squared
        if port_vol > 0 and bench_vol > 0:
            # TODO: compute actual correlation via regression on NAV vs benchmark returns
            correlation = 0.7  # Placeholder
            self.r_squared = (correlation ** 2) * 100

        # Standard Deviation
        self.standard_deviation = port_vol

    def calculate_var(self):
        """Calculate Value at Risk using historical simulation approximation."""
        port_vol = flt(self.portfolio_volatility)
        port_ret = flt(self.portfolio_return)

        if port_vol > 0:
            # VaR(95%) = -(μ - 1.645 * σ)
            self.var_95 = -(port_ret - 1.645 * port_vol)
            # VaR(99%) = -(μ - 2.326 * σ)
            self.var_99 = -(port_ret - 2.326 * port_vol)

    def validate_values(self):
        if self.portfolio_volatility and self.portfolio_volatility < 0:
            frappe.throw("Portfolio volatility cannot be negative.")
        if self.max_drawdown and self.max_drawdown > 0:
            frappe.msgprint("Max drawdown is typically a negative percentage.", alert=True)


@frappe.whitelist()
def compute_risk_metrics(fund_master, calculation_date=None):
    """API: Compute risk metrics for a fund."""
    calculation_date = calculation_date or today()

    # Gather portfolio data
    holdings = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["market_value", "total_cost_value", "unrealized_pnl"],
    )

    # Get NAV returns for vol calculation
    navs = frappe.get_all(
        "NAV History",
        filters={"fund_master": fund_master, "docstatus": 1},
        fields=["nav", "nav_change_percentage"],
        order_by="nav_date asc",
    )

    total_mv = sum(flt(h["market_value"]) for h in holdings)
    total_cost = sum(flt(h["total_cost_value"]) for h in holdings)
    portfolio_return = ((total_mv - total_cost) / total_cost * 100) if total_cost else 0

    # Simple vol estimate from NAV changes
    change_pcts = [flt(n["nav_change_percentage"]) for n in navs if n.get("nav_change_percentage")]
    vol = (sum(c * c for c in change_pcts) / max(len(change_pcts), 1)) ** 0.5 if change_pcts else 0

    ra = frappe.get_doc({
        "doctype": "Risk Analytics",
        "fund_master": fund_master,
        "calculation_date": calculation_date,
        "risk_model": "Historical Simulation",
        "lookback_period": "1 Year",
        "portfolio_return": portfolio_return,
        "portfolio_volatility": vol,
        "status": "Draft",
    })
    ra.insert()
    return ra


@frappe.whitelist()
def get_risk_summary(fund_master):
    """API: Get latest risk metrics summary for dashboards."""
    latest = frappe.get_all(
        "Risk Analytics",
        filters={"fund_master": fund_master, "status": "Calculated"},
        fields=[
            "sharpe_ratio", "sortino_ratio", "alpha", "beta",
            "r_squared", "var_95", "var_99", "max_drawdown",
            "tracking_error", "information_ratio",
            "calculation_date", "portfolio_return", "portfolio_volatility",
        ],
        order_by="calculation_date desc",
        limit=1,
    )

    return latest[0] if latest else None


@frappe.whitelist()
def get_risk_trend(fund_master, metric="sharpe_ratio", limit=12):
    """API: Get trend data for a specific risk metric over time."""
    return frappe.get_all(
        "Risk Analytics",
        filters={"fund_master": fund_master, "status": "Calculated"},
        fields=["calculation_date", metric],
        order_by="calculation_date asc",
        limit_page_length=limit,
    )
