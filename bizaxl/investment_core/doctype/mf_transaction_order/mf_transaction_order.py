# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class MFTransactionOrder(Document):
    """Tracks mutual fund orders placed via BSE StarMF or NSE NMF II platforms."""
    pass


@frappe.whitelist()
def place_mf_purchase(investor, pan_number, scheme_code, amount, order_type="Lumpsum",
                       amc_code=None, sip_frequency=None, sip_date=None, folio_number=None):
    """API: Place a purchase order (lumpsum or SIP) via BSE StarMF / NSE NMF II."""
    from bizaxl.bizaxl.integrations.bse_starmf_nmf import MFPlatformConnector

    connector = MFPlatformConnector()
    result = connector.place_purchase_order(
        pan_number, scheme_code, amount, order_type,
        amc_code, sip_frequency, sip_date, folio_number,
    )

    order = frappe.get_doc({
        "doctype": "MF Transaction Order",
        "investor": investor,
        "pan_number": pan_number,
        "transaction_type": "SIP Purchase" if order_type == "SIP" else "Purchase",
        "order_type": order_type,
        "platform": result.get("platform", "BSE StarMF"),
        "order_ref": result.get("order_ref"),
        "transaction_id": result.get("transaction_id"),
        "status": result.get("status", "Pending"),
        "scheme_code": scheme_code,
        "folio_number": result.get("folio_number"),
        "amount": amount,
        "units": result.get("units"),
        "nav_applicable": result.get("nav"),
        "sip_frequency": sip_frequency if order_type == "SIP" else None,
        "sip_date": sip_date if order_type == "SIP" else None,
        "mandate_ref": result.get("mandate_ref"),
        "expected_settlement": result.get("expected_settlement"),
        "brokerage": result.get("brokerage"),
        "order_date": result.get("order_date"),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    order.insert()

    return {
        "name": order.name,
        "order_ref": order.order_ref,
        "status": order.status,
        "folio_number": order.folio_number,
        "amount": order.amount,
        "units": order.units,
    }


@frappe.whitelist()
def place_mf_redemption(investor, pan_number, scheme_code, units=None, amount=None,
                         folio_number=None, all_units=False):
    """API: Place a redemption order."""
    from bizaxl.bizaxl.integrations.bse_starmf_nmf import MFPlatformConnector

    connector = MFPlatformConnector()
    result = connector.place_redemption_order(
        pan_number, scheme_code, units, amount, folio_number, all_units,
    )

    order = frappe.get_doc({
        "doctype": "MF Transaction Order",
        "investor": investor,
        "pan_number": pan_number,
        "transaction_type": "Redemption",
        "order_type": "Lumpsum",
        "platform": result.get("platform", "BSE StarMF"),
        "order_ref": result.get("order_ref"),
        "transaction_id": result.get("transaction_id"),
        "status": result.get("status", "Pending"),
        "scheme_code": scheme_code,
        "folio_number": result.get("folio_number"),
        "amount": amount,
        "units": units,
        "nav_applicable": result.get("nav"),
        "expected_settlement": result.get("expected_settlement"),
        "order_date": result.get("order_date"),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    order.insert()

    return {"name": order.name, "order_ref": order.order_ref, "status": order.status}


@frappe.whitelist()
def place_mf_switch(investor, pan_number, from_scheme, to_scheme, units=None, amount=None):
    """API: Place a switch order between two schemes."""
    from bizaxl.bizaxl.integrations.bse_starmf_nmf import MFPlatformConnector

    connector = MFPlatformConnector()
    result = connector.place_switch_order(pan_number, from_scheme, to_scheme, units, amount)

    order = frappe.get_doc({
        "doctype": "MF Transaction Order",
        "investor": investor,
        "pan_number": pan_number,
        "transaction_type": "Switch Out",
        "order_type": "Switch",
        "platform": result.get("platform", "NSE NMF II"),
        "order_ref": result.get("switch_ref"),
        "status": result.get("status", "Pending"),
        "from_scheme": from_scheme,
        "to_scheme": to_scheme,
        "amount": amount,
        "units": units,
        "nav_applicable": result.get("nav"),
        "expected_settlement": result.get("expected_settlement"),
        "order_date": result.get("order_date"),
        "connector_mode": result.get("mode", "stub"),
        "response_data": frappe.as_json(result),
    })
    order.insert()

    return {"name": order.name, "switch_ref": order.order_ref, "status": order.status}


@frappe.whitelist()
def get_mf_order_status(order_ref):
    """API: Get MF order status."""
    from bizaxl.bizaxl.integrations.bse_starmf_nmf import MFPlatformConnector

    connector = MFPlatformConnector()
    return connector.get_order_status(order_ref)


@frappe.whitelist()
def register_sip_mandate(investor_pan, bank_account, ifsc_code, amount, frequency="Monthly"):
    """API: Register SIP auto-debit mandate."""
    from bizaxl.bizaxl.integrations.bse_starmf_nmf import MFPlatformConnector

    connector = MFPlatformConnector()
    return connector.register_sip_mandate(investor_pan, bank_account, ifsc_code, amount, frequency)


@frappe.whitelist()
def get_mf_transaction_history(pan_number, from_date=None, to_date=None):
    """API: Get MF transaction history across all AMCs."""
    from bizaxl.bizaxl.integrations.bse_starmf_nmf import MFPlatformConnector

    connector = MFPlatformConnector()
    return connector.get_transaction_history(pan_number, from_date, to_date)


@frappe.whitelist()
def list_mf_orders(investor=None, status=None):
    """API: List MF transaction orders."""
    filters = {}
    if investor:
        filters["investor"] = investor
    if status:
        filters["status"] = status

    return frappe.get_all(
        "MF Transaction Order",
        filters=filters,
        fields=["name", "pan_number", "transaction_type", "order_type",
                "scheme_code", "amount", "units", "status", "order_ref",
                "order_date", "folio_number", "platform", "connector_mode"],
        order_by="order_date desc, creation desc",
        limit_page_length=50,
    )
