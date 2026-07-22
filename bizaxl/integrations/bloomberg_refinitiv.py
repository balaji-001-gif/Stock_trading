# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
Bloomberg / Refinitiv / ICRA Connector — Stub-to-Live Integration

Bond pricing, credit rating feeds, and valuation for unlisted debt securities
and fixed income analytics.

Supports:
1. Bond Pricing — Get latest prices, yields, spreads for corporate/government bonds
2. Credit Ratings — Fetch credit ratings from ICRA, CRISIL, CARE, Fitch
3. Fixed Income Analytics — Yield-to-maturity, duration, convexity calculations
4. Unlisted Debt Valuation — Fair value assessment for unlisted debt securities
5. Bond Master — Corporate bond/NCD master data with ISIN, coupon, maturity

Stub mode: Simulates Bloomberg/Refinitiv/ICRA data with realistic Indian bond data
Live mode: Integrates with actual Bloomberg Terminal API, Refinitiv Eikon, ICRA API
"""

import frappe
import json
import random
import math
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt, add_days, add_months
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Realistic Indian bond stub data
STUB_BONDS = [
    {"isin": "INE148I09KU1", "issuer": "HDFC Bank Ltd", "type": "Bond", "coupon": 7.85, "maturity": "2030-06-15", "rating": "AAA", "agency": "CRISIL", "face_value": 1000000, "sector": "Banking"},
    {"isin": "INE009A08CK1", "issuer": "Infosys Ltd", "type": "NCD", "coupon": 7.50, "maturity": "2028-03-20", "rating": "AAA", "agency": "ICRA", "face_value": 1000000, "sector": "IT"},
    {"isin": "INE040A09ZR1", "issuer": "Reliance Industries Ltd", "type": "NCD", "coupon": 7.95, "maturity": "2032-09-30", "rating": "AAA", "agency": "CARE", "face_value": 1000000, "sector": "Oil & Gas"},
    {"isin": "INE397D08HQ1", "issuer": "HDFC Ltd", "type": "Bond", "coupon": 8.10, "maturity": "2029-12-31", "rating": "AAA", "agency": "CRISIL", "face_value": 1000000, "sector": "Housing Finance"},
    {"isin": "INE002A08DH6", "issuer": "ICICI Bank Ltd", "type": "Bond", "coupon": 7.65, "maturity": "2027-08-15", "rating": "AAA", "agency": "ICRA", "face_value": 1000000, "sector": "Banking"},
    {"isin": "INE064A08AE7", "issuer": "LIC Housing Finance", "type": "Bond", "coupon": 8.35, "maturity": "2031-05-10", "rating": "AAA", "agency": "CRISIL", "face_value": 1000000, "sector": "Housing Finance"},
    {"isin": "INE237A08FF1", "issuer": "Kotak Mahindra Bank", "type": "Bond", "coupon": 7.55, "maturity": "2026-11-30", "rating": "AA+", "agency": "CARE", "face_value": 1000000, "sector": "Banking"},
    {"isin": "INE133A08SA3", "issuer": "ONGC", "type": "Bond", "coupon": 7.40, "maturity": "2028-04-25", "rating": "AAA", "agency": "CRISIL", "face_value": 1000000, "sector": "Oil & Gas"},
    {"isin": "INE438A08DE1", "issuer": "Power Finance Corp", "type": "Bond", "coupon": 8.50, "maturity": "2033-07-30", "rating": "AAA", "agency": "ICRA", "face_value": 1000000, "sector": "Power"},
    {"isin": "INE397H08LG1", "issuer": "Bharti Airtel Ltd", "type": "NCD", "coupon": 8.25, "maturity": "2029-12-15", "rating": "AA+", "agency": "CARE", "face_value": 1000000, "sector": "Telecom"},
]


class BondPricingConnector(BaseConnector):
    """Bloomberg/Refinitiv/ICRA — bond pricing, credit ratings, fixed income analytics."""

    connector_name = "bloomberg_refinitiv"
    label = "Bloomberg / Refinitiv / ICRA"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Bond Pricing
    # =========================================================================

    def get_bond_price(self, isin):
        """Get latest bond price, yield, and spread for a security."""
        try:
            if self.is_stub:
                result = self._stub_bond_price(isin)
            else:
                result = self._live_bond_price(isin)
            self.log_request("get_bond_price", {"isin": isin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Bulk Bond Pricing
    # =========================================================================

    def get_bulk_bond_prices(self, isins):
        """Get pricing for multiple bonds at once."""
        results = {}
        for isin in isins:
            results[isin] = self.get_bond_price(isin)
        return {"status": "Success", "bonds": results, "count": len(results), "mode": "stub"}

    # =========================================================================
    # PUBLIC API: Credit Ratings
    # =========================================================================

    def get_credit_rating(self, isin):
        """Fetch credit rating and outlook for a security."""
        try:
            if self.is_stub:
                result = self._stub_credit_rating(isin)
            else:
                result = self._live_credit_rating(isin)
            self.log_request("get_credit_rating", {"isin": isin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Fixed Income Analytics
    # =========================================================================

    def calculate_fi_analytics(self, isin, price=None):
        """Calculate YTM, duration, convexity for a bond."""
        try:
            if self.is_stub:
                result = self._stub_fi_analytics(isin, price)
            else:
                result = self._live_fi_analytics(isin, price)
            self.log_request("calculate_fi_analytics", {"isin": isin}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Bond Master Search
    # =========================================================================

    def search_bond_master(self, query, sector=None, rating=None):
        """Search bond master by issuer, ISIN, sector, or rating."""
        try:
            if self.is_stub:
                result = self._stub_search_bond_master(query, sector, rating)
            else:
                result = self._live_search_bond_master(query, sector, rating)
            self.log_request("search_bond_master", {"query": query}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_bond_price(self, isin):
        """Simulate bond pricing from Bloomberg/Refinitiv."""
        bond = next((b for b in STUB_BONDS if b["isin"] == isin), None)
        if not bond:
            return {"status": "Not Found", "error": f"ISIN {isin} not found", "mode": "stub"}

        years_to_maturity = max((datetime.strptime(bond["maturity"], "%Y-%m-%d") - datetime.now()).days / 365, 0.1)
        clean_price = round(100 - (years_to_maturity * random.uniform(0, 2)) + random.uniform(-1, 1), 2)
        accrued_interest = round(bond["coupon"] * random.randint(30, 120) / 365, 2)
        dirty_price = round(clean_price + accrued_interest, 2)
        ytm = round(bond["coupon"] + (100 - clean_price) / years_to_maturity / 10 + random.uniform(-0.25, 0.25), 2)
        spread = round(ytm - 7.10, 2)  # Spread over 10-year G-sec

        return {
            "status": "Success",
            "mode": "stub",
            "source": random.choice(["Bloomberg", "Refinitiv Eikon", "NSE BOND"]),
            "isin": isin,
            "issuer": bond["issuer"],
            "coupon": bond["coupon"],
            "maturity": bond["maturity"],
            "clean_price": clean_price,
            "accrued_interest": accrued_interest,
            "dirty_price": dirty_price,
            "ytm": ytm,
            "spread_vs_gsec": spread,
            "modified_duration": round(years_to_maturity / (1 + ytm / 100), 2),
            "rating": bond["rating"],
            "rating_agency": bond["agency"],
            "pricing_date": today(),
            "bid_yield": round(ytm + random.uniform(-0.05, 0), 2),
            "ask_yield": round(ytm + random.uniform(0, 0.05), 2),
            "last_traded_price": round(clean_price + random.uniform(-0.5, 0.5), 2),
        }

    def _stub_credit_rating(self, isin):
        """Simulate credit rating data."""
        bond = next((b for b in STUB_BONDS if b["isin"] == isin), None)
        if not bond:
            return {"status": "Not Found", "error": f"ISIN {isin} not found", "mode": "stub"}

        return {
            "status": "Success",
            "mode": "stub",
            "source": random.choice(["ICRA", "CRISIL", "CARE", "Fitch"]),
            "isin": isin,
            "issuer": bond["issuer"],
            "instrument_type": bond["type"],
            "current_rating": bond["rating"],
            "rating_agency": bond["agency"],
            "rating_outlook": random.choice(["Stable", "Stable", "Positive", "Negative"]),
            "rating_date": add_days(datetime.now(), -random.randint(30, 180)).strftime("%Y-%m-%d"),
            "previous_rating": bond["rating"] if random.random() > 0.1 else f"{bond['rating'][:-1]}{chr(ord(bond['rating'][-1])-1)}",
            "rating_action": "Confirmed" if random.random() > 0.1 else "Upgraded",
            "watch_status": "Rating Watch with Negative Implications" if random.random() < 0.05 else "No Watch",
        }

    def _stub_fi_analytics(self, isin, price):
        """Calculate fixed income analytics."""
        bond = next((b for b in STUB_BONDS if b["isin"] == isin), None)
        if not bond:
            return {"status": "Not Found", "error": f"ISIN {isin} not found", "mode": "stub"}

        clean_price = price or 100.0
        years_to_maturity = max((datetime.strptime(bond["maturity"], "%Y-%m-%d") - datetime.now()).days / 365, 0.1)
        ytm = round(bond["coupon"] + (100 - clean_price) / years_to_maturity / 10, 2)
        duration = round(years_to_maturity / (1 + ytm / 100), 2)
        mod_duration = round(duration / (1 + ytm / 100), 2)
        convexity = round((years_to_maturity ** 2 + years_to_maturity) / (1 + ytm / 100) ** 2, 2)

        return {
            "status": "Success",
            "mode": "stub",
            "isin": isin,
            "issuer": bond["issuer"],
            "coupon": bond["coupon"],
            "maturity": bond["maturity"],
            "years_to_maturity": round(years_to_maturity, 2),
            "ytm": ytm,
            "macaulay_duration": duration,
            "modified_duration": mod_duration,
            "convexity": convexity,
            "dv01": round(mod_duration * 0.01 * 1000000 / 100, 2),
            "price_value_of_basis_point": round((mod_duration * 0.0001 * clean_price), 4),
        }

    def _stub_search_bond_master(self, query, sector, rating):
        """Simulate bond master search."""
        results = STUB_BONDS
        if query:
            results = [b for b in results if query.lower() in b["issuer"].lower() or query.upper() in b["isin"]]
        if sector:
            results = [b for b in results if b["sector"].lower() == sector.lower()]
        if rating:
            results = [b for b in results if b["rating"] == rating.upper()]

        return {
            "status": "Success",
            "mode": "stub",
            "total_results": len(results),
            "results": results,
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholder)
    # =========================================================================

    def _live_bond_price(self, isin):
        raise NotImplementedError("Live bond pricing requires Bloomberg/Refinitiv API subscription.")

    def _live_credit_rating(self, isin):
        raise NotImplementedError("Live credit ratings require ICRA/CRISIL API subscription.")

    def _live_fi_analytics(self, isin, price):
        raise NotImplementedError("Live FI analytics requires Bloomberg Terminal API.")

    def _live_search_bond_master(self, query, sector, rating):
        raise NotImplementedError("Live bond master requires Bloomberg/Refinitiv data feed.")
