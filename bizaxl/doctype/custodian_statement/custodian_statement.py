# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class CustodianStatement(Document):
    """Tracks custodian statements — MT940/MT950, position/cash reconciliation."""
    pass


@frappe.whitelist()
def fetch_custodian_positions(portfolio_code, as_of_date=None):
    """API: Fetch position statement from custodian (MT950)."""
    from bizaxl.bizaxl.integrations.swift_sftp_custodian import CustodianConnector

    connector = CustodianConnector()
    result = connector.fetch_positions(portfolio_code, as_of_date)

    if result.get("status") != "Success":
        return result

    # Create Custodian Statement record
    doc = frappe.get_doc({
        "doctype": "Custodian Statement",
        "portfolio_code": portfolio_code,
        "custodian_name": "Stub Custodian",
        "statement_type": "Position Statement",
        "message_type": "MT950",
        "statement_date": today(),
        "as_of_date": as_of_date or today(),
        "status": "Received",
        "connector_mode": result.get("mode"),
        "total_securities": result.get("total_securities"),
        "total_market_value": result.get("total_market_value"),
        "closing_balance": result.get("cash_balance"),
        "statement_data_json": frappe.as_json(result.get("positions", [])),
        "custodian_ref": result.get("custodian_ref"),
    })
    doc.insert()

    return {
        "name": doc.name,
        "total_securities": doc.total_securities,
        "portfolio_value": result.get("portfolio_value"),
        "positions": result.get("positions"),
    }


@frappe.whitelist()
def fetch_custodian_transactions(portfolio_code, from_date, to_date):
    """API: Fetch transaction statement from custodian (MT940)."""
    from bizaxl.bizaxl.integrations.swift_sftp_custodian import CustodianConnector

    connector = CustodianConnector()
    result = connector.fetch_transactions(portfolio_code, from_date, to_date)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "Custodian Statement",
        "portfolio_code": portfolio_code,
        "custodian_name": "Stub Custodian",
        "statement_type": "Transaction Statement",
        "message_type": "MT940",
        "statement_date": today(),
        "status": "Received",
        "connector_mode": result.get("mode"),
        "total_credits": result.get("total_credits"),
        "total_debits": result.get("total_debits"),
        "statement_data_json": frappe.as_json(result.get("transactions", [])),
    })
    doc.insert()

    return {
        "name": doc.name,
        "total_transactions": result.get("total_transactions"),
        "net_flow": result.get("net_flow"),
        "transactions": result.get("transactions"),
    }


@frappe.whitelist()
def reconcile_custodian_positions(portfolio_code, as_of_date=None):
    """API: Reconcile custodian positions against internal holdings."""
    from bizaxl.bizaxl.integrations.swift_sftp_custodian import CustodianConnector

    # Fetch internal holdings
    internal_holdings = frappe.get_all(
        "Holdings Register",
        fields=["isin", "quantity", "security_name"],
        limit_page_length=200,
    )

    connector = CustodianConnector()
    result = connector.reconcile_positions(portfolio_code, internal_holdings, as_of_date)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "Custodian Statement",
        "portfolio_code": portfolio_code,
        "custodian_name": "Stub Custodian",
        "statement_type": "Reconciliation Report",
        "statement_date": today(),
        "as_of_date": as_of_date or today(),
        "status": "Partially Reconciled" if result.get("breaks", 0) > 0 else "Fully Reconciled",
        "connector_mode": result.get("mode"),
        "total_securities": result.get("total_positions_checked"),
        "matched_positions": result.get("matched"),
        "break_positions": result.get("breaks"),
        "total_difference_value": result.get("total_difference_value"),
        "reconciliation_status": result.get("reconciliation_status"),
        "reconciliation_notes": f"Matched: {result.get('matched')}, Breaks: {result.get('breaks')}, Total diff: ₹{result.get('total_difference_value'):,.0f}",
        "statement_data_json": frappe.as_json({
            "matched": result.get("matched_positions", []),
            "breaks": result.get("break_positions", []),
        }),
        "custodian_ref": result.get("reconciliation_ref"),
    })
    doc.insert()

    return {
        "name": doc.name,
        "reconciliation_status": doc.reconciliation_status,
        "matched": result.get("matched"),
        "breaks": result.get("breaks"),
        "break_positions": result.get("break_positions"),
    }


@frappe.whitelist()
def fetch_custodian_cash(portfolio_code, as_of_date=None):
    """API: Fetch cash balance from custodian."""
    from bizaxl.bizaxl.integrations.swift_sftp_custodian import CustodianConnector

    connector = CustodianConnector()
    result = connector.fetch_cash_balance(portfolio_code, as_of_date)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "Custodian Statement",
        "portfolio_code": portfolio_code,
        "statement_type": "Cash Statement",
        "statement_date": today(),
        "as_of_date": as_of_date or today(),
        "status": "Received",
        "connector_mode": result.get("mode"),
        "opening_balance": result.get("opening_balance"),
        "closing_balance": result.get("closing_balance"),
        "available_balance": result.get("available_balance"),
        "pending_settlements": result.get("pending_settlements"),
        "currency": result.get("currency"),
    })
    doc.insert()

    return {
        "name": doc.name,
        "closing_balance": result.get("closing_balance"),
        "available_balance": result.get("available_balance"),
    }


@frappe.whitelist()
def list_custodian_statements(portfolio_code=None, statement_type=None):
    """API: List custodian statements."""
    filters = {}
    if portfolio_code:
        filters["portfolio_code"] = portfolio_code
    if statement_type:
        filters["statement_type"] = statement_type

    return frappe.get_all(
        "Custodian Statement",
        filters=filters,
        fields=["name", "portfolio_code", "statement_type", "message_type",
                "statement_date", "status", "reconciliation_status",
                "total_securities", "matched_positions", "break_positions",
                "connector_mode", "custodian_ref"],
        order_by="statement_date desc",
        limit_page_length=50,
    )
