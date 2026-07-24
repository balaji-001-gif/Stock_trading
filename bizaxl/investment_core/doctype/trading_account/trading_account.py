# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TradingAccount(Document):
    """Client trading and demat account with segment activation and limits."""
    pass


@frappe.whitelist()
def open_trading_account(investor, **kwargs):
    """API: Open a new trading account for an investor."""
    doc = frappe.get_doc({
        "doctype": "Trading Account",
        "investor": investor,
        "client_code": kwargs.get("client_code"),
        "account_type": kwargs.get("account_type", "Individual"),
        "trading_account_number": kwargs.get("trading_account_number"),
        "demat_account_number": kwargs.get("demat_account_number"),
        "dp_name": kwargs.get("dp_name", "NSDL"),
        "status": "Active",
        "segment_equity": kwargs.get("segment_equity", 1),
        "exposure_limit": kwargs.get("exposure_limit"),
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_trading_accounts(investor=None):
    """API: Get trading accounts."""
    filters = {}
    if investor:
        filters["investor"] = investor
    return frappe.get_all(
        "Trading Account",
        filters=filters,
        fields=[
            "name", "investor", "client_code", "account_type",
            "trading_account_number", "demat_account_number",
            "dp_name", "segment_equity", "segment_fno",
            "segment_currency", "segment_commodity",
            "kyc_status", "status", "exposure_limit",
        ],
        order_by="creation desc",
    )
