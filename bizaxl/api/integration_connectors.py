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
8.  NSDL CRA (NPS) — PRAN registration, contribution upload, allocation, withdrawal
9.  NACH / UPI AutoPay — eNACH mandate, UPI AutoPay, mandates, debit processing
10. SMS / WhatsApp / Email — Templated notifications, OTP, bulk alerts
11. AML / Sanctions Screening — PEP, OFAC, UN sanctions, adverse media, risk scoring
12. e-Sign / DigiLocker — Aadhaar e-Sign, DigiLocker document fetch, agreement signing
13. GSTN / TAN / TDS Portal — TDS computation, filing, Form 16A, GST/TAN verification
14. SEBI Reporting Portal — AIF Annex VI, PMS quarterly, REIT/InvIT, SCORES
15. Bloomberg / Refinitiv / ICRA — Bond pricing, credit ratings, fixed income analytics
16. FATCA / CRS Filing — Form 61B, US FATCA XML, foreign investor reporting
17. Video KYC — Agent queue, session recording, frame capture, liveness detection
18. AI / ML Analytics Engine — Risk analytics, tax harvesting, rebalancing, attribution
19. MCA21 / RoC — Company filings, director verification, cap table compliance
20. SWIFT / SFTP Custodian — MT940/MT950, position/cash reconciliation, file exchange
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


# =============================================================================
# SECTION 10: NSDL CRA (NPS)
# =============================================================================

@frappe.whitelist()
def register_nps_pran(subscriber_name, **kwargs):
    """Register NPS subscriber via CRA and generate PRAN."""
    from bizaxl.bizaxl.doctype.nps_cra_request.nps_cra_request import register_nps_pran as _reg
    return _reg(subscriber_name, **kwargs)


@frappe.whitelist()
def upload_nps_contribution(nps_subscriber, contribution_amount, **kwargs):
    """Upload NPS contribution to CRA."""
    from bizaxl.bizaxl.doctype.nps_cra_request.nps_cra_request import upload_nps_contribution as _upload
    return _upload(nps_subscriber, contribution_amount, **kwargs)


@frappe.whitelist()
def fetch_pfm_nav(pfm_code=None):
    """Fetch latest Pension Fund Manager NAV data."""
    from bizaxl.bizaxl.doctype.nps_cra_request.nps_cra_request import fetch_pfm_nav as _nav
    return _nav(pfm_code)


@frappe.whitelist()
def process_nps_withdrawal(nps_annuity_request):
    """Process NPS withdrawal via CRA."""
    from bizaxl.bizaxl.doctype.nps_cra_request.nps_cra_request import process_nps_withdrawal as _wd
    return _wd(nps_annuity_request)


@frappe.whitelist()
def list_nps_cra_requests(subscriber=None):
    """List NPS CRA requests."""
    from bizaxl.bizaxl.doctype.nps_cra_request.nps_cra_request import list_nps_cra_requests as _list
    return _list(subscriber)


# =============================================================================
# SECTION 11: NACH / UPI AutoPay
# =============================================================================

@frappe.whitelist()
def register_nach_mandate(bank_account, ifsc_code, amount, **kwargs):
    """Register eNACH mandate for SIP auto-debit."""
    from bizaxl.bizaxl.integrations.nach_upi_autopay import AutoPayConnector
    connector = AutoPayConnector()
    result = connector.register_nach_mandate({
        "bank_account": bank_account,
        "ifsc": ifsc_code,
        "amount": amount,
        "frequency": kwargs.get("frequency", "Monthly"),
        "pan": kwargs.get("pan"),
    })
    return result


@frappe.whitelist()
def register_upi_autopay(vpa, amount, frequency="Monthly"):
    """Register UPI AutoPay mandate."""
    from bizaxl.bizaxl.integrations.nach_upi_autopay import AutoPayConnector
    connector = AutoPayConnector()
    return connector.register_upi_autopay(vpa, amount, frequency)


@frappe.whitelist()
def get_mandate_status(mandate_ref):
    """Get mandate status."""
    from bizaxl.bizaxl.integrations.nach_upi_autopay import AutoPayConnector
    connector = AutoPayConnector()
    return connector.get_mandate_status(mandate_ref)


@frappe.whitelist()
def process_auto_debit(mandate_ref, amount):
    """Process automated debit against a mandate."""
    from bizaxl.bizaxl.integrations.nach_upi_autopay import AutoPayConnector
    connector = AutoPayConnector()
    return connector.process_debit(mandate_ref, amount)


@frappe.whitelist()
def get_bounce_report(from_date=None, to_date=None):
    """Get bounced debit report."""
    from bizaxl.bizaxl.integrations.nach_upi_autopay import AutoPayConnector
    connector = AutoPayConnector()
    return connector.get_bounce_report(from_date, to_date)


# =============================================================================
# SECTION 12: SMS / WhatsApp / Email Notifications
# =============================================================================

@frappe.whitelist()
def send_notification(channel, recipient, template_key, **kwargs):
    """Send templated notification via SMS, WhatsApp, or Email."""
    from bizaxl.bizaxl.doctype.notification_log.notification_log import send_notification as _send
    return _send(channel, recipient, template_key, **kwargs)


@frappe.whitelist()
def send_bulk_notification(channel, recipients, template_key, template_vars, **kwargs):
    """Send bulk notifications to multiple recipients."""
    from bizaxl.bizaxl.doctype.notification_log.notification_log import send_bulk_notification as _bulk
    return _bulk(channel, recipients, template_key, template_vars, **kwargs)


@frappe.whitelist()
def get_notification_logs(reference_doctype=None, reference_name=None, channel=None):
    """Get notification logs with filters."""
    from bizaxl.bizaxl.doctype.notification_log.notification_log import get_notification_logs as _logs
    return _logs(reference_doctype, reference_name, channel)


# =============================================================================
# SECTION 13: AML / Sanctions Screening
# =============================================================================

@frappe.whitelist()
def run_full_aml_screening(investor):
    """Run full AML screening (PEP + Sanctions + Adverse Media + Risk Score)."""
    from bizaxl.bizaxl.doctype.aml_screening_request.aml_screening_request import run_full_aml_screening as _screen
    return _screen(investor)


@frappe.whitelist()
def screen_pep_only(investor):
    """Screen investor against PEP database only."""
    from bizaxl.bizaxl.doctype.aml_screening_request.aml_screening_request import screen_pep_only as _pep
    return _pep(investor)


@frappe.whitelist()
def list_aml_requests(investor=None):
    """List AML screening requests."""
    from bizaxl.bizaxl.doctype.aml_screening_request.aml_screening_request import list_aml_requests as _list
    return _list(investor)


# =============================================================================
# SECTION 14: e-Sign / DigiLocker
# =============================================================================

@frappe.whitelist()
def request_esign(investor, document_type, document_hash, signing_purpose):
    """Request Aadhaar e-Sign for a document."""
    from bizaxl.bizaxl.integrations.esign_digilocker import ESignConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    connector = ESignConnector()
    result = connector.request_esign(
        f"{investor_doc.first_name} {investor_doc.last_name or ''}",
        investor_doc.aadhaar_number,
        document_hash,
        signing_purpose,
    )
    return result


@frappe.whitelist()
def fetch_digilocker_document(investor, document_type):
    """Fetch a verified document from DigiLocker."""
    from bizaxl.bizaxl.integrations.esign_digilocker import ESignConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    connector = ESignConnector()
    return connector.fetch_digilocker_document(investor_doc.aadhaar_number, document_type)


@frappe.whitelist()
def get_digilocker_issued_docs(investor):
    """Get list of all issued documents in DigiLocker."""
    from bizaxl.bizaxl.integrations.esign_digilocker import ESignConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    connector = ESignConnector()
    return connector.get_digilocker_issued_docs(investor_doc.aadhaar_number)


# =============================================================================
# SECTION 15: GSTN / TAN / TDS Portal
# =============================================================================

@frappe.whitelist()
def compute_tds(gross_amount, tds_rate, pan_number, section_code="194", **kwargs):
    """Compute TDS with surcharge and education cess."""
    from bizaxl.bizaxl.doctype.tds_filing_record.tds_filing_record import compute_tds as _compute
    return _compute(gross_amount, tds_rate, pan_number, section_code, **kwargs)


@frappe.whitelist()
def file_tds_return(tan_number, return_type, financial_year, quarter, total_tds, **kwargs):
    """File TDS return with Income Tax Department."""
    from bizaxl.bizaxl.doctype.tds_filing_record.tds_filing_record import file_tds_return as _file
    return _file(tan_number, return_type, financial_year, quarter, total_tds, **kwargs)


@frappe.whitelist()
def generate_form_16a(tan_number, deductee_pan, financial_year, quarter):
    """Generate Form 16A TDS certificate via TRACES."""
    from bizaxl.bizaxl.doctype.tds_filing_record.tds_filing_record import generate_form_16a as _form
    return _form(tan_number, deductee_pan, financial_year, quarter)


@frappe.whitelist()
def verify_gstin(gstin):
    """Verify GSTIN."""
    from bizaxl.bizaxl.doctype.tds_filing_record.tds_filing_record import verify_gstin as _gst
    return _gst(gstin)


@frappe.whitelist()
def verify_tan(tan_number):
    """Verify TAN."""
    from bizaxl.bizaxl.doctype.tds_filing_record.tds_filing_record import verify_tan as _tan
    return _tan(tan_number)


@frappe.whitelist()
def list_tds_filings(tan_number=None):
    """List TDS filing records."""
    from bizaxl.bizaxl.doctype.tds_filing_record.tds_filing_record import list_tds_filings as _list
    return _list(tan_number)


# =============================================================================
# SECTION 16: SEBI Reporting Portal
# =============================================================================

@frappe.whitelist()
def generate_sebi_report(report_type, fund, **kwargs):
    """Generate SEBI compliance report (AIF Annex VI, PMS quarterly, REIT/InvIT, etc.)."""
    from bizaxl.bizaxl.integrations.sebi_portal import SEBIConnector
    connector = SEBIConnector()
    result = connector.generate_report(report_type, fund, **kwargs)

    # Create SEBI Report record
    sebi_report = frappe.get_doc({
        "doctype": "SEBI Report",
        "report_type": report_type,
        "fund_master": fund,
        "period_covered": kwargs.get("period", "Quarterly"),
        "status": "Draft",
        "regulatory_body": "SEBI",
        "report_data_json": frappe.as_json(result.get("report_data", {})),
        "report_summary": result.get("summary", ""),
        "report_date": today(),
    })
    sebi_report.insert()
    return {
        "name": sebi_report.name,
        "report_type": report_type,
        "summary": result.get("summary"),
        "period": result.get("period"),
        "report_data": result.get("report_data"),
        "submission_status": sebi_report.status,
    }


@frappe.whitelist()
def submit_sebi_report(report_name):
    """Submit SEBI report to SEBI portal."""
    from bizaxl.bizaxl.integrations.sebi_portal import SEBIConnector
    doc = frappe.get_doc("SEBI Report", report_name)
    connector = SEBIConnector()
    result = connector.submit_report(doc)

    doc.db_set("status", "Filed")
    doc.db_set("filing_reference", result.get("submission_ref"))
    doc.db_set("acknowledgment_number", result.get("acknowledgment_number", ""))
    doc.db_set("filing_date", today())

    return {
        "name": doc.name,
        "status": "Filed",
        "filing_reference": result.get("submission_ref"),
        "message": result.get("message"),
    }


@frappe.whitelist()
def get_sebi_compliance_calendar(regulatory_category=None):
    """Get SEBI compliance calendar with filing deadlines."""
    from bizaxl.bizaxl.integrations.sebi_portal import SEBIConnector
    connector = SEBIConnector()
    return connector.get_compliance_calendar(regulatory_category)


@frappe.whitelist()
def get_sebi_annex_vi(report_name):
    """Get SEBI AIF Annex VI report data."""
    from bizaxl.bizaxl.integrations.sebi_portal import SEBIConnector
    connector = SEBIConnector()
    return connector.get_annex_vi(report_name)


@frappe.whitelist()
def list_sebi_reports(fund=None, report_type=None):
    """List SEBI reports with optional filters."""
    filters = {}
    if fund:
        filters["fund_master"] = fund
    if report_type:
        filters["report_type"] = report_type

    return frappe.get_all(
        "SEBI Report",
        filters=filters,
        fields=["name", "report_type", "fund_master", "status",
                "period_covered", "filing_reference", "acknowledgment_number",
                "creation", "modified"],
        order_by="creation desc",
        limit_page_length=50,
    )


# =============================================================================
# SECTION 17: Bloomberg / Refinitiv / ICRA Bond Pricing
# =============================================================================

@frappe.whitelist()
def get_bond_price(isin=None, instrument_type=None, pricing_source=None):
    """Fetch latest bond pricing from Bloomberg/Refinitiv/ICRA."""
    from bizaxl.bizaxl.doctype.bond_pricing_feed.bond_pricing_feed import get_bond_price as _price
    return _price(isin, instrument_type, pricing_source)


@frappe.whitelist()
def get_bond_analytics(isin):
    """Get analytics for a specific bond — YTM, duration, convexity, spreads."""
    from bizaxl.bizaxl.doctype.bond_pricing_feed.bond_pricing_feed import get_bond_analytics as _analytics
    return _analytics(isin)


@frappe.whitelist()
def get_credit_rating_history(isin, agency=None):
    """Get credit rating history for a bond from rating agencies."""
    from bizaxl.bizaxl.doctype.bond_pricing_feed.bond_pricing_feed import get_credit_rating_history as _rating
    return _rating(isin, agency)


@frappe.whitelist()
def fetch_bond_pricing_from_source(isin, pricing_source="Bloomberg"):
    """Fetch bond pricing directly from a pricing source and store in feed."""
    from bizaxl.bizaxl.integrations.bloomberg_refinitiv import BondPricingConnector

    connector = BondPricingConnector()
    result = connector.get_bond_price(isin, pricing_source)

    if result.get("success"):
        feed = frappe.get_doc({
            "doctype": "Bond Pricing Feed",
            "isin": isin,
            "instrument_name": result.get("instrument_name", ""),
            "instrument_type": result.get("instrument_type", "Corporate Bond"),
            "issuer": result.get("issuer", ""),
            "credit_rating": result.get("credit_rating", ""),
            "rating_agency": result.get("rating_agency", ""),
            "coupon_rate": result.get("coupon_rate"),
            "bid_price": result.get("bid_price"),
            "ask_price": result.get("ask_price"),
            "last_price": result.get("last_price"),
            "ytm": result.get("ytm"),
            "modified_duration": result.get("modified_duration"),
            "convexity": result.get("convexity"),
            "g_spread": result.get("g_spread"),
            "z_spread": result.get("z_spread"),
            "pricing_date": result.get("pricing_date", today()),
            "pricing_source": pricing_source,
            "status": "Active",
        })
        feed.insert()

    return result


@frappe.whitelist()
def list_bond_pricing(isin=None, pricing_source=None):
    """List bond pricing feed records."""
    filters = {}
    if isin:
        filters["isin"] = isin
    if pricing_source:
        filters["pricing_source"] = pricing_source

    return frappe.get_all(
        "Bond Pricing Feed",
        filters=filters,
        fields=["name", "isin", "instrument_name", "instrument_type", "issuer",
                "credit_rating", "coupon_rate", "bid_price", "ask_price",
                "last_price", "ytm", "pricing_date", "pricing_source", "status"],
        order_by="pricing_date desc",
        limit_page_length=50,
    )


# =============================================================================
# SECTION 18: FATCA / CRS Filing
# =============================================================================

@frappe.whitelist()
def submit_fatca_filing(filing_type, filing_year, reporting_year, entity_name, entity_pan):
    """Submit FATCA/CRS filing to Income Tax Department."""
    from bizaxl.bizaxl.doctype.fatca_filing_record.fatca_filing_record import submit_fatca_filing as _submit
    return _submit(filing_type, filing_year, reporting_year, entity_name, entity_pan)


@frappe.whitelist()
def generate_fatca_report(filing_type, reporting_year, **kwargs):
    """Generate FATCA/CRS report with account data."""
    from bizaxl.bizaxl.integrations.fatca_crs_filing import FATCAConnector
    connector = FATCAConnector()
    return connector.generate_report(filing_type, reporting_year, **kwargs)


@frappe.whitelist()
def submit_fatca_to_income_tax(filing_record_name):
    """Submit FATCA/CRS filing to Income Tax Department portal."""
    from bizaxl.bizaxl.integrations.fatca_crs_filing import FATCAConnector
    doc = frappe.get_doc("FATCA Filing Record", filing_record_name)
    connector = FATCAConnector()
    result = connector.submit_filing(doc)

    doc.db_set("status", "Submitted")
    doc.db_set("submission_ref", result.get("submission_ref"))
    doc.db_set("submission_date", today())
    doc.db_set("response_data", frappe.as_json(result))

    return {
        "name": doc.name,
        "status": "Submitted",
        "submission_ref": result.get("submission_ref"),
        "acknowledgment_ref": result.get("acknowledgment_ref"),
    }


@frappe.whitelist()
def generate_fatca_xml(filing_type, reporting_year, **kwargs):
    """Generate FATCA/CRS XML for filing."""
    from bizaxl.bizaxl.integrations.fatca_crs_filing import FATCAConnector
    connector = FATCAConnector()
    return connector.generate_xml(filing_type, reporting_year, **kwargs)


@frappe.whitelist()
def get_filing_status(name):
    """Get the status of a FATCA/CRS filing record."""
    from bizaxl.bizaxl.doctype.fatca_filing_record.fatca_filing_record import get_filing_status as _status
    return _status(name)


@frappe.whitelist()
def list_fatca_filings(filing_type=None, status=None, year=None):
    """List FATCA/CRS filings."""
    from bizaxl.bizaxl.doctype.fatca_filing_record.fatca_filing_record import list_fatca_filings as _list
    return _list(filing_type, status, year)


# =============================================================================
# SECTION 19: Video KYC
# =============================================================================

@frappe.whitelist()
def start_video_kyc(investor, pan_number, preferred_language="English", investor_type="Individual"):
    """Start a video KYC session for remote investor onboarding."""
    from bizaxl.bizaxl.doctype.video_kyc_session.video_kyc_session import start_video_kyc as _start
    return _start(investor, pan_number, preferred_language, investor_type)


@frappe.whitelist()
def complete_video_kyc(vkyc_session, agent_notes=None):
    """Complete a video KYC session with verification result."""
    from bizaxl.bizaxl.doctype.video_kyc_session.video_kyc_session import complete_video_kyc as _complete
    return _complete(vkyc_session, agent_notes)


@frappe.whitelist()
def get_agent_queue(status=None):
    """Get available KYC agents and queue status."""
    from bizaxl.bizaxl.doctype.video_kyc_session.video_kyc_session import get_agent_queue as _queue
    return _queue(status)


@frappe.whitelist()
def list_vkyc_sessions(investor=None, status=None):
    """List video KYC sessions."""
    from bizaxl.bizaxl.doctype.video_kyc_session.video_kyc_session import list_vkyc_sessions as _list
    return _list(investor, status)


# =============================================================================
# SECTION 20: AI / ML Analytics Engine
# =============================================================================

@frappe.whitelist()
def run_risk_analysis(fund_master=None, investor=None, lookback_months=12, risk_free_rate=6.5):
    """Run comprehensive risk metrics analysis (Sharpe, Alpha, Beta, VaR)."""
    from bizaxl.bizaxl.doctype.ai_analytics_result.ai_analytics_result import run_risk_analysis as _run
    return _run(fund_master, investor, lookback_months, risk_free_rate)


@frappe.whitelist()
def run_tax_harvest_analysis(investor, portfolio_value=None, tax_slab="30%"):
    """Find tax-loss harvesting opportunities across holdings."""
    from bizaxl.bizaxl.doctype.ai_analytics_result.ai_analytics_result import run_tax_harvest_analysis as _run
    return _run(investor, portfolio_value, tax_slab)


@frappe.whitelist()
def run_rebalancing_analysis(fund_master=None, investor=None, drift_threshold=5.0):
    """Run portfolio rebalancing analysis."""
    from bizaxl.bizaxl.doctype.ai_analytics_result.ai_analytics_result import run_rebalancing_analysis as _run
    return _run(fund_master, investor, drift_threshold)


@frappe.whitelist()
def run_performance_attribution(fund_master, sectors=None):
    """Run performance attribution analysis (Brinson)."""
    from bizaxl.bizaxl.doctype.ai_analytics_result.ai_analytics_result import run_performance_attribution as _run
    return _run(fund_master, sectors)


@frappe.whitelist()
def run_market_regime_analysis():
    """Detect current market regime (bull/bear/sideways)."""
    from bizaxl.bizaxl.doctype.ai_analytics_result.ai_analytics_result import run_market_regime_analysis as _run
    return _run()


@frappe.whitelist()
def list_ai_analyses(analysis_type=None):
    """List AI analytics results."""
    from bizaxl.bizaxl.doctype.ai_analytics_result.ai_analytics_result import list_ai_analyses as _list
    return _list(analysis_type)


# =============================================================================
# SECTION 21: MCA21 / RoC
# =============================================================================

@frappe.whitelist()
def search_mca_company(cin=None, pan=None, name=None):
    """Search for a company on MCA21 by CIN, PAN, or name."""
    from bizaxl.bizaxl.integrations.mca21_roc import MCA21Connector
    connector = MCA21Connector()
    return connector.search_company(cin, pan, name)


@frappe.whitelist()
def verify_din(din, pan=None):
    """Verify Director Identification Number (DIN)."""
    from bizaxl.bizaxl.integrations.mca21_roc import MCA21Connector
    connector = MCA21Connector()
    return connector.verify_director(din, pan)


@frappe.whitelist()
def file_mca_form(form_type, company_cin, form_data):
    """File MCA21 form (SH-7, PAS-3, MGT-14, CHG-1, etc.)."""
    from bizaxl.bizaxl.integrations.mca21_roc import MCA21Connector
    connector = MCA21Connector()
    return connector.file_mca_form(form_type, company_cin, form_data)


@frappe.whitelist()
def get_mca_filing_status(srn):
    """Get MCA21 filing status by SRN."""
    from bizaxl.bizaxl.integrations.mca21_roc import MCA21Connector
    connector = MCA21Connector()
    return connector.get_filing_status(srn)


@frappe.whitelist()
def get_mca_company_master(cin):
    """Get full company master data from MCA21."""
    from bizaxl.bizaxl.integrations.mca21_roc import MCA21Connector
    connector = MCA21Connector()
    return connector.get_company_master_data(cin)


@frappe.whitelist()
def get_shareholding_pattern(cin):
    """Get shareholding pattern from MCA21."""
    from bizaxl.bizaxl.integrations.mca21_roc import MCA21Connector
    connector = MCA21Connector()
    return connector.get_shareholding_pattern(cin)


# =============================================================================
# SECTION 22: SWIFT / SFTP Custodian
# =============================================================================

@frappe.whitelist()
def fetch_custodian_positions(portfolio_code, as_of_date=None):
    """Fetch position statement (MT950) from custodian."""
    from bizaxl.bizaxl.doctype.custodian_statement.custodian_statement import fetch_custodian_positions as _fetch
    return _fetch(portfolio_code, as_of_date)


@frappe.whitelist()
def fetch_custodian_transactions(portfolio_code, from_date, to_date):
    """Fetch transaction statement (MT940) from custodian."""
    from bizaxl.bizaxl.doctype.custodian_statement.custodian_statement import fetch_custodian_transactions as _fetch
    return _fetch(portfolio_code, from_date, to_date)


@frappe.whitelist()
def reconcile_custodian_positions(portfolio_code, as_of_date=None):
    """Reconcile custodian positions against internal holdings."""
    from bizaxl.bizaxl.doctype.custodian_statement.custodian_statement import reconcile_custodian_positions as _recon
    return _recon(portfolio_code, as_of_date)


@frappe.whitelist()
def fetch_custodian_cash(portfolio_code, as_of_date=None):
    """Fetch cash balance from custodian."""
    from bizaxl.bizaxl.doctype.custodian_statement.custodian_statement import fetch_custodian_cash as _cash
    return _cash(portfolio_code, as_of_date)


@frappe.whitelist()
def list_custodian_statements(portfolio_code=None, statement_type=None):
    """List custodian statements."""
    from bizaxl.bizaxl.doctype.custodian_statement.custodian_statement import list_custodian_statements as _list
    return _list(portfolio_code, statement_type)
