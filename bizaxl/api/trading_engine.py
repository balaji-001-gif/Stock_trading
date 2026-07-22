# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 12 API Endpoints — Stock Broking & Trading Platform."""

import frappe
from frappe.utils import flt, today, now_datetime


# =============================================================================
# TRADING ACCOUNT APIs
# =============================================================================

@frappe.whitelist()
def open_account(investor, **kwargs):
    """Open a new trading and demat account."""
    from bizaxl.bizaxl.doctype.trading_account.trading_account import open_trading_account

    return open_trading_account(investor, **kwargs)


@frappe.whitelist()
def list_trading_accounts(investor=None):
    """List trading accounts."""
    from bizaxl.bizaxl.doctype.trading_account.trading_account import get_trading_accounts

    return get_trading_accounts(investor)


# =============================================================================
# TRADE ORDER APIs
# =============================================================================

@frappe.whitelist()
def place_trade_order(trading_account, symbol, transaction_type, quantity, order_type="Market", **kwargs):
    """Place a new trade order."""
    from bizaxl.bizaxl.doctype.trade_order.trade_order import place_order

    return place_order(trading_account, symbol, transaction_type, quantity, order_type, **kwargs)


@frappe.whitelist()
def get_open_positions(trading_account=None):
    """Get all open orders/positions."""
    from bizaxl.bizaxl.doctype.trade_order.trade_order import get_open_orders

    return get_open_orders(trading_account)


@frappe.whitelist()
def get_trade_history_report(trading_account, limit=50):
    """Get trade history for a trading account."""
    from bizaxl.bizaxl.doctype.trade_order.trade_order import get_trade_history

    return get_trade_history(trading_account, limit)


# =============================================================================
# CONTRACT NOTE APIs
# =============================================================================

@frappe.whitelist()
def generate_contract_note(trading_account, trade_date, **kwargs):
    """Generate a SEBI-compliant contract note."""
    from bizaxl.bizaxl.doctype.contract_note.contract_note import generate_contract_note

    return generate_contract_note(trading_account, trade_date, **kwargs)


@frappe.whitelist()
def get_settlement_report(trading_account, from_date=None, to_date=None):
    """Get settlement report for a trading account."""
    from bizaxl.bizaxl.doctype.contract_note.contract_note import get_settlement_report

    return get_settlement_report(trading_account, from_date, to_date)


# =============================================================================
# MARGIN APIs
# =============================================================================

@frappe.whitelist()
def get_margin_overview(trading_account):
    """Get latest margin status for a trading account."""
    from bizaxl.bizaxl.doctype.margin_account.margin_account import get_margin_status

    return get_margin_status(trading_account)


@frappe.whitelist()
def get_shortfall_alerts(threshold_pct=25):
    """Get margin shortfall alerts above threshold."""
    from bizaxl.bizaxl.doctype.margin_account.margin_account import get_margin_shortfall_alerts

    return get_margin_shortfall_alerts(threshold_pct)


# =============================================================================
# CONSOLIDATED TRADING DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_trading_dashboard(trading_account):
    """Get comprehensive trading dashboard for a trading account."""
    from bizaxl.bizaxl.doctype.margin_account.margin_account import get_margin_status
    from bizaxl.bizaxl.doctype.trade_order.trade_order import get_open_orders

    margin = get_margin_status(trading_account)
    open_orders = get_open_orders(trading_account)

    # Recent trades
    recent_trades = frappe.get_all(
        "Trade Order",
        filters={"trading_account": trading_account},
        fields=["name", "symbol", "order_type", "quantity", "average_price", "total_turnover", "status", "order_date"],
        order_by="order_date desc",
        limit=20,
    )

    # Pending settlements
    pending = frappe.get_all(
        "Contract Note",
        filters={"trading_account": trading_account, "settlement_status": ["in", ("Pending", "Pay-In")]},
        fields=["name", "trade_date", "symbol", "total_turnover", "net_payable", "settlement_date"],
    )

    # Account summary
    account = frappe.get_doc("Trading Account", trading_account)
    client = frappe.get_doc("Investor Profile", account.investor) if account.investor else None

    return {
        "trading_account": trading_account,
        "client_name": client.first_name + " " + (client.last_name or "") if client else "",
        "margin": margin,
        "open_orders_count": len(open_orders),
        "open_orders": open_orders[:5],
        "recent_trades": recent_trades,
        "pending_settlements": pending,
        "pending_settlement_count": len(pending),
        "segments": {
            "equity": account.segment_equity,
            "fno": account.segment_fno,
            "currency": account.segment_currency,
            "commodity": account.segment_commodity,
        },
    }


@frappe.whitelist()
def get_broker_dashboard():
    """Get broker-level dashboard with aggregated trading metrics."""
    total_accounts = frappe.db.count("Trading Account", filters={"status": "Active"})
    total_open_orders = frappe.db.count("Trade Order", filters={"status": ["in", ("Pending", "Open", "Partially Filled")]})

    turnover = frappe.get_all(
        "Contract Note",
        filters={"status": ["in", ("Generated", "Settled")]},
        fields=["sum(total_turnover) as total_turnover", "sum(total_charges) as total_revenue"],
    )

    shortfall_accounts = frappe.db.count(
        "Margin Account",
        filters={"status": ["in", ("Alert", "Square-Off Initiated")]},
    )

    return {
        "total_active_accounts": total_accounts,
        "total_open_orders": total_open_orders,
        "total_turnover": turnover[0].total_turnover if turnover else 0,
        "total_revenue": turnover[0].total_revenue if turnover else 0,
        "margin_shortfall_count": shortfall_accounts,
    }
