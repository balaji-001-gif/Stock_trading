# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
NSE / BSE Market Data Connector — Stub-to-Live Integration

Real-time and end-of-day market data from NSE and BSE exchanges.

Supports:
1. Equity Prices — Real-time LTP, bid/ask, volume, day range for equities
2. EOD Data — End-of-day price snapshot with OHLCV (open, high, low, close, volume)
3. F&O Data — Futures and options chain with expiry, strike, open interest
4. Index Values — Live index levels for Nifty 50, Sensex, Bank Nifty, etc.
5. Live Ticker — Simulated streaming price feed for portfolio MTM

Stub mode: Simulates NSE/BSE market data with realistic Indian securities
Live mode: Integrates with actual NSE/BSE market data feeds (WebSocket/REST)
"""

import frappe
import json
import random
import math
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Base prices for stub generation (used as reference for price simulation)
STUB_EQUITIES = {
    "RELIANCE": {"name": "Reliance Industries Ltd", "base_price": 2950, "sector": "Oil & Gas", "isin": "INE040A01034"},
    "TCS": {"name": "Tata Consultancy Services Ltd", "base_price": 3890, "sector": "IT", "isin": "INE030A01027"},
    "INFY": {"name": "Infosys Ltd", "base_price": 1560, "sector": "IT", "isin": "INE009A01021"},
    "HDFC": {"name": "HDFC Bank Ltd", "base_price": 1680, "sector": "Banking", "isin": "INE397D01024"},
    "ICICIBANK": {"name": "ICICI Bank Ltd", "base_price": 1150, "sector": "Banking", "isin": "INE002A01018"},
    "SBIN": {"name": "State Bank of India", "base_price": 780, "sector": "Banking", "isin": "INE467B01029"},
    "HINDUNILVR": {"name": "Hindustan Unilever Ltd", "base_price": 2580, "sector": "FMCG", "isin": "INE759A01021"},
    "ITC": {"name": "ITC Ltd", "base_price": 440, "sector": "FMCG", "isin": "INE154A01025"},
    "BAJFINANCE": {"name": "Bajaj Finance Ltd", "base_price": 7100, "sector": "NBFC", "isin": "INE081A01012"},
    "MARUTI": {"name": "Maruti Suzuki India Ltd", "base_price": 11200, "sector": "Automobile", "isin": "INE660A01013"},
    "TATAMOTORS": {"name": "Tata Motors Ltd", "base_price": 980, "sector": "Automobile", "isin": "INE150A01010"},
    "WIPRO": {"name": "Wipro Ltd", "base_price": 480, "sector": "IT", "isin": "INE075A01022"},
    "HCLTECH": {"name": "HCL Technologies Ltd", "base_price": 1420, "sector": "IT", "isin": "INE860A01027"},
    "AXISBANK": {"name": "Axis Bank Ltd", "base_price": 1100, "sector": "Banking", "isin": "INE238A01034"},
    "KOTAKBANK": {"name": "Kotak Mahindra Bank Ltd", "base_price": 1850, "sector": "Banking", "isin": "INE237A01028"},
    "LT": {"name": "Larsen & Toubro Ltd", "base_price": 3560, "sector": "Infrastructure", "isin": "INE018A01030"},
    "BHARTIARTL": {"name": "Bharti Airtel Ltd", "base_price": 1280, "sector": "Telecom", "isin": "INE397H01017"},
    "ASIANPAINT": {"name": "Asian Paints Ltd", "base_price": 3160, "sector": "Consumer", "isin": "INE021A01026"},
    "NTPC": {"name": "NTPC Ltd", "base_price": 360, "sector": "Power", "isin": "INE733E01010"},
    "POWERGRID": {"name": "Power Grid Corp Ltd", "base_price": 290, "sector": "Power", "isin": "INE752E01010"},
}

STUB_INDICES = {
    "NIFTY 50": {"base": 22350, "change": 0},
    "SENSEX": {"base": 73500, "change": 0},
    "BANK NIFTY": {"base": 47800, "change": 0},
    "NIFTY IT": {"base": 35800, "change": 0},
    "NIFTY MIDCAP 100": {"base": 48200, "change": 0},
    "NIFTY SMALLCAP 100": {"base": 15200, "change": 0},
}


class MarketDataConnector(BaseConnector):
    """NSE/BSE Market Data integration — equities, F&O, indices, EOD data."""

    connector_name = "nse_bse_market"
    label = "NSE / BSE Market Data"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        """Live mode requires NSE/BSE market data subscription."""
        return bool(self._get_api_key() and self._get_api_secret())

    # -------------------------------------------------------------------------
    # Price helpers
    # -------------------------------------------------------------------------

    def _simulate_price(self, base_price, volatility=0.02):
        """Generate a simulated price around base price."""
        change_pct = random.uniform(-volatility, volatility)
        change = base_price * change_pct
        return round(base_price + change, 2)

    # =========================================================================
    # PUBLIC API: Equity Prices
    # =========================================================================

    def get_equity_quote(self, symbol, exchange="NSE"):
        """Get real-time equity quote for a symbol."""
        request = {"symbol": symbol, "exchange": exchange}

        try:
            if self.is_stub:
                result = self._stub_equity_quote(symbol, exchange)
            else:
                result = self._live_equity_quote(symbol, exchange)
            self.log_request("get_equity_quote", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_bulk_quotes(self, symbols, exchange="NSE"):
        """Get quotes for multiple symbols."""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_equity_quote(symbol, exchange)
        return {"status": "Success", "quotes": results, "count": len(results), "mode": "stub"}

    # =========================================================================
    # PUBLIC API: EOD Data
    # =========================================================================

    def get_eod_data(self, symbol, date=None, exchange="NSE"):
        """Get end-of-day OHLCV data for a symbol."""
        date = date or today()
        request = {"symbol": symbol, "date": date, "exchange": exchange}

        try:
            if self.is_stub:
                result = self._stub_eod_data(symbol, date, exchange)
            else:
                result = self._live_eod_data(symbol, date, exchange)
            self.log_request("get_eod_data", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_eod_bulk(self, symbols, date=None, exchange="NSE"):
        """Get EOD data for multiple symbols."""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_eod_data(symbol, date, exchange)
        return {"status": "Success", "eod_data": results, "count": len(results), "mode": "stub"}

    # =========================================================================
    # PUBLIC API: F&O Data
    # =========================================================================

    def get_fo_chain(self, symbol, expiry=None):
        """Get futures and options chain for a symbol."""
        request = {"symbol": symbol, "expiry": expiry}

        try:
            if self.is_stub:
                result = self._stub_fo_chain(symbol, expiry)
            else:
                result = self._live_fo_chain(symbol, expiry)
            self.log_request("get_fo_chain", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Index Values
    # =========================================================================

    def get_index_values(self, indices=None):
        """Get live index values. If None, returns all indices."""
        request = {"indices": indices}

        try:
            if self.is_stub:
                result = self._stub_index_values(indices)
            else:
                result = self._live_index_values(indices)
            self.log_request("get_index_values", request, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Live Ticker
    # =========================================================================

    def get_live_ticker(self, symbols):
        """Get simulated live prices for a watchlist of symbols."""
        request = {"symbols": symbols}

        try:
            if self.is_stub:
                result = self._stub_live_ticker(symbols)
            else:
                result = self._live_live_ticker(symbols)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_equity_quote(self, symbol, exchange):
        """Simulate real-time equity quote."""
        upper = symbol.upper()
        equity = STUB_EQUITIES.get(upper)

        if not equity:
            return {"status": "Not Found", "error": f"Symbol {symbol} not found on {exchange}", "mode": "stub"}

        base = equity["base_price"]
        ltp = self._simulate_price(base)
        open_price = self._simulate_price(base, 0.01)
        day_high = round(max(ltp, open_price) * random.uniform(1.005, 1.02), 2)
        day_low = round(min(ltp, open_price) * random.uniform(0.98, 0.995), 2)
        prev_close = self._simulate_price(base, 0.005)
        change = round(ltp - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2)
        volume = random.randint(500000, 50000000)

        return {
            "status": "Success",
            "mode": "stub",
            "exchange": exchange,
            "symbol": upper,
            "company_name": equity["name"],
            "isin": equity["isin"],
            "sector": equity["sector"],
            "ltp": ltp,
            "open": open_price,
            "high": day_high,
            "low": day_low,
            "close": prev_close,
            "change": change,
            "change_percent": change_pct,
            "volume": volume,
            "bid": round(ltp - random.uniform(0.5, 5), 2),
            "ask": round(ltp + random.uniform(0.5, 5), 2),
            "bid_qty": random.randint(100, 5000),
            "ask_qty": random.randint(100, 5000),
            "total_buy_qty": random.randint(100000, 10000000),
            "total_sell_qty": random.randint(100000, 10000000),
            "week_52_high": round(base * random.uniform(1.10, 1.30), 2),
            "week_52_low": round(base * random.uniform(0.70, 0.90), 2),
            "timestamp": now_datetime().isoformat(),
        }

    def _stub_eod_data(self, symbol, date, exchange):
        """Simulate end-of-day OHLCV data."""
        upper = symbol.upper()
        equity = STUB_EQUITIES.get(upper)
        if not equity:
            return {"status": "Not Found", "error": f"Symbol {symbol} not found", "mode": "stub"}

        base = equity["base_price"]
        open_p = self._simulate_price(base, 0.01)
        high = round(open_p * random.uniform(1.01, 1.04), 2)
        low = round(open_p * random.uniform(0.96, 0.99), 2)
        close = self._simulate_price(base)
        volume = random.randint(1000000, 100000000)

        return {
            "status": "Success",
            "mode": "stub",
            "symbol": upper,
            "exchange": exchange,
            "date": date,
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "value_crores": round((close * volume) / 10000000, 2),
            "delivery_qty": random.randint(100000, volume),
            "delivery_pct": round(random.uniform(20, 60), 2),
        }

    def _stub_fo_chain(self, symbol, expiry):
        """Simulate F&O chain data."""
        upper = symbol.upper()
        equity = STUB_EQUITIES.get(upper)
        if not equity:
            return {"status": "Not Found", "error": f"Symbol {symbol} not found", "mode": "stub"}

        base = equity["base_price"]
        spot = self._simulate_price(base)
        expiry_date = expiry or (datetime.now() + timedelta(days=30 - datetime.now().day)).strftime("%d-%b-%Y")

        # Generate option strikes around spot price
        atm_strike = round(spot / 50) * 50  # Round to nearest 50
        strikes = [atm_strike + (i * 50) for i in range(-5, 6)]

        futures = {
            "expiry": expiry_date,
            "symbol": upper,
            "future_ltp": round(spot * random.uniform(1.001, 1.02), 2),
            "future_volume": random.randint(100000, 5000000),
            "future_oi": random.randint(500000, 10000000),
        }

        options = []
        for strike in strikes:
            call_ltp = round(max(random.uniform(1, spot * 0.05), 0.05), 2)
            put_ltp = round(max(random.uniform(1, spot * 0.05), 0.05), 2)

            options.append({
                "strike": strike,
                "call_ltp": call_ltp if strike < spot + 100 else round(random.uniform(0.05, 5), 2),
                "call_volume": random.randint(1000, 500000),
                "call_oi": random.randint(10000, 2000000),
                "put_ltp": put_ltp if strike > spot - 100 else round(random.uniform(0.05, 5), 2),
                "put_volume": random.randint(1000, 500000),
                "put_oi": random.randint(10000, 2000000),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "symbol": upper,
            "spot_price": spot,
            "expiry": expiry_date,
            "futures": futures,
            "options_count": len(options),
            "options": options,
        }

    def _stub_index_values(self, indices):
        """Simulate index values."""
        target_indices = indices or list(STUB_INDICES.keys())
        results = {}

        for idx_name in target_indices:
            if idx_name not in STUB_INDICES:
                continue
            base = STUB_INDICES[idx_name]["base"]
            current = base + random.uniform(-base * 0.01, base * 0.01)
            change = current - base
            change_pct = (change / base) * 100

            results[idx_name] = {
                "index_name": idx_name,
                "current": round(current, 2),
                "open": round(base * random.uniform(0.995, 1.005), 2),
                "high": round(current * random.uniform(1.002, 1.01), 2),
                "low": round(current * random.uniform(0.99, 0.998), 2),
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "volume": random.randint(10000000, 500000000),
                "advances": random.randint(800, 1500),
                "declines": random.randint(500, 1200),
                "unchanged": random.randint(50, 200),
                "timestamp": now_datetime().isoformat(),
            }

        return {"status": "Success", "mode": "stub", "indices": results}

    def _stub_live_ticker(self, symbols):
        """Simulate live ticker feed for a watchlist."""
        ticker_data = []
        for symbol in symbols:
            upper = symbol.upper()
            equity = STUB_EQUITIES.get(upper)
            if not equity:
                continue
            base = equity["base_price"]
            ltp = self._simulate_price(base)
            change = ltp - base
            ticker_data.append({
                "symbol": upper,
                "name": equity["name"],
                "ltp": ltp,
                "change": round(change, 2),
                "change_percent": round((change / base) * 100, 2),
                "volume": random.randint(100000, 5000000),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "ticker": ticker_data,
            "timestamp": now_datetime().isoformat(),
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_equity_quote(self, symbol, exchange):
        raise NotImplementedError("Live market data requires NSE/BSE data feed credentials.")

    def _live_eod_data(self, symbol, date, exchange):
        raise NotImplementedError("Live EOD data requires NSE/BSE data feed credentials.")

    def _live_fo_chain(self, symbol, expiry):
        raise NotImplementedError("Live F&O data requires NSE/BSE data feed credentials.")

    def _live_index_values(self, indices):
        raise NotImplementedError("Live index data requires NSE/BSE data feed credentials.")

    def _live_live_ticker(self, symbols):
        raise NotImplementedError("Live ticker requires WebSocket connection to exchange.")
