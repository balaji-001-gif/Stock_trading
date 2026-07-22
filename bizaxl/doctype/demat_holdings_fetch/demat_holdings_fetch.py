# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class DematHoldingsFetch(Document):
    """Tracks demat holdings fetch operations from NSDL/CDSL."""

    def after_insert(self):
        """Auto-update linked Trading Account with demat details."""
        if self.trading_account and self.status == "Completed":
            self._update_trading_account()

    def _update_trading_account(self):
        """Update trading account with fetched holdings info."""
        try:
            trading = frappe.get_doc("Trading Account", self.trading_account)
            trading.demat_account_number = self.bo_id
            trading.db_set("demat_account_number", self.bo_id)
        except Exception:
            pass


@frappe.whitelist()
def fetch_demat_holdings(trading_account, bo_id=None, dp_name="NSDL"):
    """API: Fetch demat holdings and store results."""
    from bizaxl.bizaxl.integrations.nsdl_cdsl_demat import DematConnector

    # Get BO ID from trading account if not provided
    if not bo_id:
        trading = frappe.get_doc("Trading Account", trading_account)
        bo_id = trading.demat_account_number

    if not bo_id:
        frappe.throw("BO ID is required. Set demat account number on the Trading Account first.")

    connector = DematConnector()
    result = connector.fetch_holdings(bo_id, dp_name)

    # Create Demat Holdings Fetch record
    fetch = frappe.get_doc({
        "doctype": "Demat Holdings Fetch",
        "trading_account": trading_account,
        "investor": frappe.get_value("Trading Account", trading_account, "investor"),
        "bo_id": bo_id,
        "depository": dp_name,
        "status": "Completed" if result.get("status") == "Success" else "Failed",
        "as_of_date": result.get("as_of_date"),
        "total_securities": result.get("total_securities", 0),
        "total_quantity": result.get("total_quantity", 0),
        "total_value": result.get("total_value", 0),
        "holdings_data": frappe.as_json(result.get("holdings", [])),
        "connector_mode": result.get("mode", "stub"),
        "fetched_at": now_datetime(),
    })
    fetch.insert()

    return result


@frappe.whitelist()
def verify_demat_account(trading_account, bo_id, dp_name="NSDL"):
    """API: Verify demat BO ID and link to trading account."""
    from bizaxl.bizaxl.integrations.nsdl_cdsl_demat import DematConnector

    connector = DematConnector()
    result = connector.verify_bo_id(bo_id, dp_name)

    if result.get("is_valid"):
        # Update trading account
        frappe.db.set_value("Trading Account", trading_account, {
            "demat_account_number": bo_id,
            "dp_name": dp_name,
        })

        return {
            "status": "Success",
            "bo_id": bo_id,
            "holder_name": result.get("holder_name"),
            "depository": dp_name,
            "account_status": result.get("account_status"),
            "mode": result.get("mode"),
        }

    return {"status": "Failed", "error": "BO ID verification failed."}


@frappe.whitelist()
def get_demat_corporate_actions(trading_account=None, from_date=None, to_date=None):
    """API: Fetch corporate actions for demat holdings."""
    from bizaxl.bizaxl.integrations.nsdl_cdsl_demat import DematConnector

    bo_id = None
    if trading_account:
        bo_id = frappe.get_value("Trading Account", trading_account, "demat_account_number")

    connector = DematConnector()
    result = connector.fetch_corporate_actions(bo_id, from_date, to_date)
    return result


@frappe.whitelist()
def get_demat_transactions(trading_account, from_date=None, to_date=None):
    """API: Fetch demat transaction history."""
    from bizaxl.bizaxl.integrations.nsdl_cdsl_demat import DematConnector

    trading = frappe.get_doc("Trading Account", trading_account)
    bo_id = trading.demat_account_number

    if not bo_id:
        frappe.throw("No demat account linked to this trading account.")

    connector = DematConnector()
    result = connector.fetch_transactions(bo_id, from_date, to_date)
    return result


@frappe.whitelist()
def link_demat_holdings_to_portfolio(trading_account):
    """API: Link fetched demat holdings to the Consolidated Portfolio."""
    # Get the latest successful fetch
    fetch = frappe.get_all(
        "Demat Holdings Fetch",
        filters={
            "trading_account": trading_account,
            "status": "Completed",
        },
        fields=["name", "holdings_data", "investor"],
        order_by="fetched_at desc",
        limit=1,
    )

    if not fetch:
        frappe.throw("No completed demat holdings fetch found. Run fetch_demat_holdings first.")

    holdings = frappe.parse_json(fetch[0].holdings_data)

    # Create/update Consolidated Portfolio entries
    # Find or create consolidated portfolio
    portfolio_name = frappe.db.get_value(
        "Consolidated Portfolio",
        {"investor": fetch[0].investor},
        "name",
    )

    if not portfolio_name:
        portfolio = frappe.get_doc({
            "doctype": "Consolidated Portfolio",
            "investor": fetch[0].investor,
            "portfolio_date": frappe.utils.today(),
            "total_value": sum(h.get("market_value", 0) for h in holdings),
        })
        portfolio.insert()
        portfolio_name = portfolio.name

    for h in holdings:
        # Add holding to the Holdings Register
        holding_exists = frappe.db.exists("Holdings Register", {
            "investor": fetch[0].investor,
            "isin": h.get("isin"),
        })

        if not holding_exists:
            frappe.get_doc({
                "doctype": "Holdings Register",
                "investor": fetch[0].investor,
                "instrument_type": "Equity",
                "isin": h.get("isin"),
                "symbol": h.get("symbol"),
                "security_name": h.get("security_name"),
                "quantity": h.get("quantity"),
                "purchase_price": h.get("acp"),
                "current_price": h.get("market_price"),
                "current_value": h.get("market_value"),
                "fund_master": None,
            }).insert()

    return {
        "status": "Success",
        "holdings_linked": len(holdings),
        "portfolio": portfolio_name,
    }
