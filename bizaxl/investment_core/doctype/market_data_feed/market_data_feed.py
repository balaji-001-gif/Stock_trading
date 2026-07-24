# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MarketDataFeed(Document):
    """Tracks market data price/quote fetches from NSE/BSE connectors."""
    pass


@frappe.whitelist()
def get_equity_quote(symbol, exchange="NSE"):
    """API: Get real-time equity quote."""
    from bizaxl.bizaxl.integrations.nse_bse_market import MarketDataConnector

    connector = MarketDataConnector()
    result = connector.get_equity_quote(symbol, exchange)

    if result.get("status") == "Success":
        feed = frappe.get_doc({
            "doctype": "Market Data Feed",
            "feed_type": "Equity Quote",
            "symbol": symbol.upper(),
            "exchange": exchange,
            "status": "Success",
            "ltp": result.get("ltp"),
            "open_price": result.get("open"),
            "day_high": result.get("high"),
            "day_low": result.get("low"),
            "previous_close": result.get("close"),
            "change": result.get("change"),
            "change_percent": result.get("change_percent"),
            "volume": result.get("volume"),
            "bid": result.get("bid"),
            "ask": result.get("ask"),
            "week_52_high": result.get("week_52_high"),
            "week_52_low": result.get("week_52_low"),
            "fetched_at": frappe.utils.now_datetime(),
            "connector_mode": result.get("mode", "stub"),
            "raw_data": frappe.as_json(result),
        })
        feed.insert()

    return result


@frappe.whitelist()
def get_bulk_quotes(symbols, exchange="NSE"):
    """API: Get quotes for multiple symbols."""
    from bizaxl.bizaxl.integrations.nse_bse_market import MarketDataConnector

    symbols_list = [s.strip() for s in symbols.split(",") if s.strip()]
    connector = MarketDataConnector()
    return connector.get_bulk_quotes(symbols_list, exchange)


@frappe.whitelist()
def get_index_values(indices=None):
    """API: Get live index values."""
    from bizaxl.bizaxl.integrations.nse_bse_market import MarketDataConnector

    indices_list = [i.strip() for i in indices.split(",") if i.strip()] if indices else None
    connector = MarketDataConnector()
    return connector.get_index_values(indices_list)


@frappe.whitelist()
def get_fo_chain(symbol, expiry=None):
    """API: Get F&O chain for a symbol."""
    from bizaxl.bizaxl.integrations.nse_bse_market import MarketDataConnector

    connector = MarketDataConnector()
    return connector.get_fo_chain(symbol, expiry)


@frappe.whitelist()
def get_live_ticker(symbols):
    """API: Get live ticker for a watchlist."""
    from bizaxl.bizaxl.integrations.nse_bse_market import MarketDataConnector

    symbols_list = [s.strip() for s in symbols.split(",") if s.strip()]
    connector = MarketDataConnector()
    return connector.get_live_ticker(symbols_list)
