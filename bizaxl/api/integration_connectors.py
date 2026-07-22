# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
Centralized API Endpoints — 20 External Integration Connectors

All connectors operate in stub-to-live mode:
- Stub: Fully functional simulation, no credentials needed
- Live: Activates automatically when API keys are configured

Connectors implemented in this file:
1.  UIDAI Aadhaar eKYC — OTP flow, offline XML, verification
2.  NSDL/CDSL Demat — Holdings fetch, BO ID verification, corporate actions
3.  CKYC Registry (CERSAI) — CKYC record fetch, upload, verify, update
4.  CAMS / Karvy KRA — KYC check, CAS import, MF transactions, scheme master
5.  NSE / BSE Market Data — Equity quotes, EOD data, F&O chain, indices, ticker
6.  AMFI NAV & MF Data — Daily NAV, scheme master, NAV history, filing
7.  BSE StarMF / NSE NMF II — Purchase, redemption, switch, order tracking, SIP mandate
"""

import frappe
from frappe.utils import now_datetime, today
from frappe import _


# =============================================================================
# SECTION 1: UIDAI Aadhaar eKYC
# =============================================================================

@frappe.whitelist()
def send_ekyc_otp(investor, aadhaar_number):
    """Send eKYC OTP to Aadhaar-linked mobile number."""
    from bizaxl.bizaxl.doctype.ekyc_request.ekyc_request import send_ekyc_otp as _send
    return _send(investor, aadhaar_number)


@frappe.whitelist()
def verify_ekyc_otp(ekyc_request, otp):
    """Verify eKYC OTP and retrieve KYC data."""
    from bizaxl.bizaxl.doctype.ekyc_request.ekyc_request import verify_ekyc_otp as _verify
    return _verify(ekyc_request, otp)


@frappe.whitelist()
def verify_offline_xml(investor, xml_content, share_code):
    """Verify Aadhaar Offline XML eKYC."""
    from bizaxl.bizaxl.doctype.ekyc_request.ekyc_request import verify_offline_xml as _verify
    return _verify(investor, xml_content, share_code)


@frappe.whitelist()
def get_ekyc_request(ekyc_request):
    """Get eKYC request details."""
    doc = frappe.get_doc("eKYC Request", ekyc_request)
    return {
        "name": doc.name,
        "investor": doc.investor,
        "aadhaar_number": doc.aadhaar_number,
        "ekyc_mode": doc.ekyc_mode,
        "status": doc.status,
        "otp_sent_at": doc.otp_sent_at,
        "otp_valid_until": doc.otp_valid_until,
        "otp_attempts": doc.otp_attempts,
        "kyc_name": doc.kyc_name,
        "kyc_dob": doc.kyc_dob,
        "connector_mode": doc.connector_mode,
        "creation": doc.creation,
    }


@frappe.whitelist()
def list_ekyc_requests(investor=None, status=None):
    """List eKYC requests with optional filters."""
    filters = {}
    if investor:
        filters["investor"] = investor
    if status:
        filters["status"] = status

    return frappe.get_all(
        "eKYC Request",
        filters=filters,
        fields=["name", "investor", "aadhaar_number", "ekyc_mode",
                "status", "otp_sent_at", "kyc_name", "connector_mode"],
        order_by="creation desc",
        limit_page_length=50,
    )


# =============================================================================
# SECTION 2: NSDL/CDSL Demat
# =============================================================================

@frappe.whitelist()
def verify_demat_account(trading_account, bo_id, dp_name="NSDL"):
    """Verify demat BO ID and link to trading account."""
    from bizaxl.bizaxl.doctype.demat_holdings_fetch.demat_holdings_fetch import verify_demat_account as _verify
    return _verify(trading_account, bo_id, dp_name)


@frappe.whitelist()
def fetch_demat_holdings(trading_account, bo_id=None, dp_name="NSDL"):
    """Fetch demat holdings and store results."""
    from bizaxl.bizaxl.doctype.demat_holdings_fetch.demat_holdings_fetch import fetch_demat_holdings as _fetch
    return _fetch(trading_account, bo_id, dp_name)


@frappe.whitelist()
def get_demat_corporate_actions(trading_account=None, from_date=None, to_date=None):
    """Fetch corporate actions for demat holdings."""
    from bizaxl.bizaxl.doctype.demat_holdings_fetch.demat_holdings_fetch import get_demat_corporate_actions as _get
    return _get(trading_account, from_date, to_date)


@frappe.whitelist()
def get_demat_transactions(trading_account, from_date=None, to_date=None):
    """Fetch demat transaction history."""
    from bizaxl.bizaxl.doctype.demat_holdings_fetch.demat_holdings_fetch import get_demat_transactions as _get
    return _get(trading_account, from_date, to_date)


@frappe.whitelist()
def link_demat_holdings_to_portfolio(trading_account):
    """Link fetched demat holdings to the Consolidated Portfolio."""
    from bizaxl.bizaxl.doctype.demat_holdings_fetch.demat_holdings_fetch import link_demat_holdings_to_portfolio as _link
    return _link(trading_account)


@frappe.whitelist()
def list_demat_fetches(trading_account=None):
    """List demat holdings fetch history."""
    filters = {}
    if trading_account:
        filters["trading_account"] = trading_account

    return frappe.get_all(
        "Demat Holdings Fetch",
        filters=filters,
        fields=["name", "trading_account", "bo_id", "depository",
                "status", "total_securities", "total_value",
                "as_of_date", "connector_mode", "fetched_at"],
        order_by="fetched_at desc",
        limit_page_length=20,
    )


# =============================================================================
# SECTION 3: Integration Settings Management
# =============================================================================

@frappe.whitelist()
def get_integration_status(connector_name=None):
    """Get status of all or a specific integration connector."""
    filters = {}
    if connector_name:
        filters["connector_name"] = connector_name

    settings = frappe.get_all(
        "Integration Settings",
        filters=filters,
        fields=["name", "connector_name", "integration_label", "enabled",
                "environment", "connector_status", "last_ping_status",
                "last_ping_at", "error_count"],
        order_by="connector_name asc",
    )

    # Add mode indicator
    for s in settings:
        s["active_mode"] = "live" if s.get("connector_status") in ("Configured", "Active") else "stub"

    return settings


@frappe.whitelist()
def configure_integration(connector_name, integration_label, **kwargs):
    """Configure an integration connector with API credentials."""
    if frappe.db.exists("Integration Settings", connector_name):
        doc = frappe.get_doc("Integration Settings", connector_name)
    else:
        doc = frappe.get_doc({
            "doctype": "Integration Settings",
            "connector_name": connector_name,
        })

    doc.integration_label = integration_label
    doc.api_key = kwargs.get("api_key") or doc.api_key
    doc.api_secret = kwargs.get("api_secret") or doc.api_secret
    doc.endpoint_url = kwargs.get("endpoint_url") or doc.endpoint_url
    doc.environment = kwargs.get("environment", doc.environment or "Production")

    # Update status based on credentials
    if doc.api_key or doc.api_secret:
        doc.connector_status = "Configured"
    else:
        doc.connector_status = "Not Configured"

    doc.save()
    return doc


# =============================================================================
# SECTION 4: Consolidated Integration Dashboard
# =============================================================================

@frappe.whitelist()
def get_integration_dashboard():
    """Get comprehensive integration dashboard with all connector statuses."""
    settings = frappe.get_all(
        "Integration Settings",
        fields=["connector_name", "integration_label", "enabled",
                "environment", "connector_status", "last_ping_status"],
    )

    # Get recent request log
    recent_logs = frappe.get_all(
        "Integration Request Log",
        fields=["integration", "method", "mode", "status", "timestamp", "error"],
        order_by="timestamp desc",
        limit_page_length=20,
    )

    # Count by status
    success_count = frappe.db.count("Integration Request Log", filters={"status": "Success"})
    error_count = frappe.db.count("Integration Request Log", filters={"status": ["in", ("Failed", "Error")]})
    total_requests = success_count + error_count

    # Count by mode
    stub_count = frappe.db.count("Integration Request Log", filters={"mode": "stub"})
    live_count = frappe.db.count("Integration Request Log", filters={"mode": "live"})

    return {
        "connectors": settings,
        "recent_activity": recent_logs,
        "statistics": {
            "total_requests": total_requests,
            "successful": success_count,
            "failed": error_count,
            "stub_mode": stub_count,
            "live_mode": live_count,
            "stub_percentage": round(stub_count / total_requests * 100, 1) if total_requests else 100,
        },
    }


@frappe.whitelist()
def get_connector_logs(integration, limit=50):
    """Get request logs for a specific integration connector."""
    return frappe.get_all(
        "Integration Request Log",
        filters={"integration": ["like", f"%{integration}%"]},
        fields=["name", "method", "mode", "status", "timestamp", "error"],
        order_by="timestamp desc",
        limit_page_length=limit,
    )


# =============================================================================
# SECTION 5: CKYC Registry (CERSAI)
# =============================================================================

@frappe.whitelist()
def fetch_ckyc_record(investor, pan_number):
    """Fetch CKYC record from CERSAI central KYC registry."""
    from bizaxl.bizaxl.doctype.ckyc_record.ckyc_record import fetch_ckyc_record as _fetch
    return _fetch(investor, pan_number)


@frappe.whitelist()
def upload_kyc_to_ckyc(investor, pan_number, kra_name="CAMS KRA"):
    """Upload investor KYC data to CKYC registry."""
    from bizaxl.bizaxl.doctype.ckyc_record.ckyc_record import upload_kyc_to_ckyc as _upload
    return _upload(investor, pan_number, kra_name)


@frappe.whitelist()
def verify_ckyc_status(investor, pan_number):
    """Verify CKYC registration status for a PAN."""
    from bizaxl.bizaxl.doctype.ckyc_record.ckyc_record import verify_ckyc_status as _verify
    return _verify(investor, pan_number)


@frappe.whitelist()
def list_ckyc_records(investor=None):
    """List CKYC records for an investor."""
    from bizaxl.bizaxl.doctype.ckyc_record.ckyc_record import list_ckyc_records as _list
    return _list(investor)


# =============================================================================
# SECTION 6: CAMS / Karvy KRA
# =============================================================================

@frappe.whitelist()
def kra_kyc_check(pan_number, kra_name="CAMS KRA"):
    """Check KYC status across a KRA."""
    from bizaxl.bizaxl.doctype.cas_import.cas_import import kra_kyc_check as _check
    return _check(pan_number, kra_name)


@frappe.whitelist()
def import_cas(investor, pan_number, from_date=None, to_date=None):
    """Import Consolidated Account Statement and link holdings to portfolio."""
    from bizaxl.bizaxl.doctype.cas_import.cas_import import import_cas as _import
    return _import(investor, pan_number, from_date, to_date)


@frappe.whitelist()
def list_cas_imports(investor=None):
    """List CAS imports for an investor."""
    from bizaxl.bizaxl.doctype.cas_import.cas_import import list_cas_imports as _list
    return _list(investor)


@frappe.whitelist()
def fetch_mf_transactions(pan_number, from_date=None, to_date=None):
    """Fetch mutual fund transaction history from CAMS/Karvy."""
    from bizaxl.bizaxl.doctype.cas_import.cas_import import fetch_mf_transactions as _fetch
    return _fetch(pan_number, from_date, to_date)


@frappe.whitelist()
def fetch_scheme_master(amc_code=None, category=None):
    """Fetch mutual fund scheme master data."""
    from bizaxl.bizaxl.doctype.cas_import.cas_import import fetch_scheme_master as _fetch
    return _fetch(amc_code, category)


# =============================================================================
# SECTION 7: NSE / BSE Market Data
# =============================================================================

@frappe.whitelist()
def get_equity_quote(symbol, exchange="NSE"):
    """Get real-time equity quote from NSE/BSE."""
    from bizaxl.bizaxl.doctype.market_data_feed.market_data_feed import get_equity_quote as _quote
    return _quote(symbol, exchange)


@frappe.whitelist()
def get_bulk_quotes(symbols, exchange="NSE"):
    """Get quotes for multiple symbols at once."""
    from bizaxl.bizaxl.doctype.market_data_feed.market_data_feed import get_bulk_quotes as _bulk
    return _bulk(symbols, exchange)


@frappe.whitelist()
def get_index_values(indices=None):
    """Get live index values."""
    from bizaxl.bizaxl.doctype.market_data_feed.market_data_feed import get_index_values as _indices
    return _indices(indices)


@frappe.whitelist()
def get_fo_chain(symbol, expiry=None):
    """Get F&O chain for a symbol."""
    from bizaxl.bizaxl.doctype.market_data_feed.market_data_feed import get_fo_chain as _fo
    return _fo(symbol, expiry)


@frappe.whitelist()
def get_live_ticker(symbols):
    """Get live ticker feed for a watchlist."""
    from bizaxl.bizaxl.doctype.market_data_feed.market_data_feed import get_live_ticker as _ticker
    return _ticker(symbols)


# =============================================================================
# SECTION 8: AMFI NAV & MF Data
# =============================================================================

@frappe.whitelist()
def get_daily_nav(scheme_code=None, amc_code=None):
    """Get latest NAV for a scheme or all schemes."""
    from bizaxl.bizaxl.integrations.amfi_nav import NAVConnector
    connector = NAVConnector()
    return connector.get_daily_nav(scheme_code, amc_code)


@frappe.whitelist()
def get_nav_history(scheme_code, from_date=None, to_date=None):
    """Get historical NAV data for a scheme."""
    from bizaxl.bizaxl.integrations.amfi_nav import NAVConnector
    connector = NAVConnector()
    return connector.get_nav_history(scheme_code, from_date, to_date)


@frappe.whitelist()
def get_scheme_master(amc_code=None, category=None):
    """Get AMFI scheme master data (alias for fetch_scheme_master)."""
    return fetch_scheme_master(amc_code, category)


# =============================================================================
# SECTION 9: BSE StarMF / NSE NMF II
# =============================================================================

@frappe.whitelist()
def place_mf_purchase(investor, pan_number, scheme_code, amount, order_type="Lumpsum", **kwargs):
    """Place a MF purchase order (lumpsum or SIP) via BSE StarMF / NSE NMF II."""
    from bizaxl.bizaxl.doctype.mf_transaction_order.mf_transaction_order import place_mf_purchase as _purchase
    return _purchase(investor, pan_number, scheme_code, amount, order_type, **kwargs)


@frappe.whitelist()
def place_mf_redemption(investor, pan_number, scheme_code, units=None, amount=None, **kwargs):
    """Place a MF redemption order."""
    from bizaxl.bizaxl.doctype.mf_transaction_order.mf_transaction_order import place_mf_redemption as _redeem
    return _redeem(investor, pan_number, scheme_code, units, amount, **kwargs)


@frappe.whitelist()
def place_mf_switch(investor, pan_number, from_scheme, to_scheme, units=None, amount=None):
    """Place a switch order between two schemes."""
    from bizaxl.bizaxl.doctype.mf_transaction_order.mf_transaction_order import place_mf_switch as _switch
    return _switch(investor, pan_number, from_scheme, to_scheme, units, amount)


@frappe.whitelist()
def get_mf_order_status(order_ref):
    """Get MF order status from platform."""
    from bizaxl.bizaxl.doctype.mf_transaction_order.mf_transaction_order import get_mf_order_status as _status
    return _status(order_ref)


@frappe.whitelist()
def register_sip_mandate(investor_pan, bank_account, ifsc_code, amount, frequency="Monthly"):
    """Register SIP auto-debit mandate."""
    from bizaxl.bizaxl.doctype.mf_transaction_order.mf_transaction_order import register_sip_mandate as _mandate
    return _mandate(investor_pan, bank_account, ifsc_code, amount, frequency)


@frappe.whitelist()
def list_mf_orders(investor=None, status=None):
    """List MF transaction orders."""
    from bizaxl.bizaxl.doctype.mf_transaction_order.mf_transaction_order import list_mf_orders as _list
    return _list(investor, status)
