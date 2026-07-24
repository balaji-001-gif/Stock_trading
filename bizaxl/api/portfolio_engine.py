# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 6 API Endpoints — Portfolio & Holdings Management."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# HOLDINGS REGISTER APIs
# =============================================================================

@frappe.whitelist()
def get_portfolio(fund_master):
    """Get complete portfolio holdings with valuation for a fund."""
    from bizaxl.bizaxl.doctype.holdings_register.holdings_register import (
        get_portfolio_holdings,
    )

    return get_portfolio_holdings(fund_master)


@frappe.whitelist()
def add_holding(fund_master, security_id, security_name, security_type, quantity, cost_price, **kwargs):
    """Add a new holding to the portfolio."""
    from bizaxl.bizaxl.doctype.holdings_register.holdings_register import create_holding

    return create_holding(fund_master, security_id, security_name, security_type, quantity, cost_price, **kwargs)


@frappe.whitelist()
def get_holding_detail(holding_name):
    """Get detailed holding information with lot breakdown and P&L."""
    from bizaxl.bizaxl.doctype.holdings_register.holdings_register import HoldingsRegister

    holding = frappe.get_doc("Holdings Register", holding_name)
    lots = holding.get_lot_summary()

    pnl = frappe.get_all(
        "PNL Attribution",
        filters={"holding": holding_name},
        fields=[
            "sum(gross_realized_pnl) as total_realized",
            "sum(net_realized_pnl) as total_net_realized",
        ],
    )

    return {
        "holding": holding.as_dict(),
        "lots": lots,
        "total_lots": len(lots),
        "realized_pnl": pnl[0] if pnl else {"total_realized": 0, "total_net_realized": 0},
        "unrealized_pnl": holding.unrealized_pnl,
    }


# =============================================================================
# LOT TRACKING APIs
# =============================================================================

@frappe.whitelist()
def get_holding_lots(holding):
    """Get all purchase lots for a holding."""
    from bizaxl.bizaxl.doctype.lot_tracking.lot_tracking import get_lots_by_holding

    return get_lots_by_holding(holding)


@frappe.whitelist()
def sell_from_portfolio(holding, sale_quantity, sale_price, method="FIFO"):
    """Sell from holding using specified cost basis method (FIFO/LIFO)."""
    from bizaxl.bizaxl.doctype.lot_tracking.lot_tracking import sell_from_lots

    return sell_from_lots(holding, sale_quantity, sale_price, method)


@frappe.whitelist()
def create_lot(fund_master, holding, security_id, quantity, unit_cost, lot_date=None, **kwargs):
    """Create a new purchase lot."""
    doc = frappe.get_doc({
        "doctype": "Lot Tracking",
        "fund_master": fund_master,
        "holding": holding,
        "security_id": security_id,
        "lot_date": lot_date or today(),
        "original_quantity": flt(quantity),
        "unit_cost": flt(unit_cost),
        "lot_type": kwargs.get("lot_type", "Purchase"),
        "cost_basis_method": kwargs.get("cost_basis_method", "FIFO"),
        "status": "Draft",
    })
    doc.insert()
    doc.submit()
    return doc


# =============================================================================
# CORPORATE ACTIONS APIs
# =============================================================================

@frappe.whitelist()
def process_corporate_action(corporate_action_name):
    """Process a corporate action against all affected holdings."""
    from bizaxl.bizaxl.doctype.corporate_actions.corporate_actions import (
        apply_corporate_action,
    )

    return apply_corporate_action(corporate_action_name)


@frappe.whitelist()
def get_pending_corporate_actions(fund_master):
    """Get pending corporate actions for a fund."""
    from bizaxl.bizaxl.doctype.corporate_actions.corporate_actions import (
        get_pending_actions,
    )

    return get_pending_actions(fund_master)


@frappe.whitelist()
def declare_corporate_action(fund_master, action_type, security_id, security_name, **kwargs):
    """Declare a new corporate action (bonus, split, dividend, merger)."""
    doc = frappe.get_doc({
        "doctype": "Corporate Actions",
        "fund_master": fund_master,
        "action_type": action_type,
        "security_id": security_id,
        "security_name": security_name,
        "status": "Announced",
        "announcement_date": kwargs.get("announcement_date", today()),
        "record_date": kwargs.get("record_date"),
        "ex_date": kwargs.get("ex_date"),
        "ratio_numerator": flt(kwargs.get("ratio_numerator", 1)),
        "ratio_denominator": flt(kwargs.get("ratio_denominator", 1)),
        "dividend_amount": flt(kwargs.get("dividend_amount", 0)),
        "notes": kwargs.get("notes"),
    })
    doc.insert()
    doc.submit()
    return doc


# =============================================================================
# P&L ATTRIBUTION APIs
# =============================================================================

@frappe.whitelist()
def get_pnl_report(fund_master, from_date=None, to_date=None):
    """Get P&L summary report for a fund."""
    from bizaxl.bizaxl.doctype.pnl_attribution.pnl_attribution import get_pnl_summary

    return get_pnl_summary(fund_master, from_date, to_date)


@frappe.whitelist()
def get_pnl_transactions(fund_master, from_date=None, to_date=None, limit=100):
    """Get detailed P&L transactions for a fund."""
    filters = {"fund_master": fund_master}
    if from_date and to_date:
        filters["pnl_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["pnl_date"] = [">=", from_date]
    elif to_date:
        filters["pnl_date"] = ["<=", to_date]

    return frappe.get_all(
        "PNL Attribution",
        filters=filters,
        fields=[
            "name", "pnl_date", "holding", "lot", "security_id",
            "transaction_type", "pnl_type", "quantity",
            "sale_price", "cost_price", "gross_realized_pnl",
            "net_realized_pnl", "brokerage", "taxes",
        ],
        order_by="pnl_date desc",
        limit_page_length=limit,
    )


# =============================================================================
# PORTFOLIO DASHBOARD APIs
# =============================================================================

@frappe.whitelist()
def get_portfolio_dashboard(fund_master):
    """Get comprehensive portfolio dashboard — holdings, lots, actions, P&L."""
    from bizaxl.bizaxl.doctype.holdings_register.holdings_register import (
        get_portfolio_holdings,
    )
    from bizaxl.bizaxl.doctype.corporate_actions.corporate_actions import (
        get_pending_actions,
    )
    from bizaxl.bizaxl.doctype.pnl_attribution.pnl_attribution import get_pnl_summary

    portfolio = get_portfolio_holdings(fund_master)
    pending = get_pending_actions(fund_master)
    pnl = get_pnl_summary(fund_master)

    # Asset class allocation
    asset_allocation = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=[
            "asset_class", "sum(market_value) as total_value",
            "count(*) as count",
        ],
        group_by="asset_class",
        order_by="total_value desc",
    )

    total_value = flt(portfolio.get("summary", {}).get("total_market_value", 0))

    return {
        "fund_master": fund_master,
        "portfolio_summary": portfolio.get("summary"),
        "holdings": portfolio.get("holdings"),
        "asset_allocation": [
            {
                "asset_class": a.get("asset_class", "Unclassified"),
                "market_value": a.get("total_value", 0),
                "allocation_pct": (
                    (flt(a.get("total_value", 0)) / total_value * 100)
                    if total_value else 0
                ),
                "count": a.get("count", 0),
            }
            for a in asset_allocation
        ],
        "pending_corporate_actions": pending,
        "pnl_summary": pnl,
    }


@frappe.whitelist()
def get_portfolio_returns(fund_master):
    """Get portfolio return metrics — realized, unrealized, and total."""
    from bizaxl.bizaxl.doctype.pnl_attribution.pnl_attribution import get_pnl_summary

    pnl = get_pnl_summary(fund_master)

    total_invested = frappe.db.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["sum(total_cost_value) as total_cost"],
    )[0].total_cost or 0

    total_market_value = frappe.db.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["sum(market_value) as total_market"],
    )[0].total_market or 0

    return_percentage = (
        ((total_market_value - total_invested) / total_invested) * 100
        if total_invested else 0
    )

    return {
        "fund_master": fund_master,
        "total_invested": total_invested,
        "total_market_value": total_market_value,
        "realized_pnl": flt(pnl.get("total_realized_pnl", 0)),
        "unrealized_pnl": flt(pnl.get("total_unrealized_pnl", 0)),
        "total_pnl": flt(pnl.get("total_realized_pnl", 0)) + flt(pnl.get("total_unrealized_pnl", 0)),
        "return_percentage": return_percentage,
    }
