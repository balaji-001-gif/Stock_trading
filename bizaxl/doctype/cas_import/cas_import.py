# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CASImport(Document):
    """Tracks Consolidated Account Statement imports from CAMS/Karvy."""

    def after_insert(self):
        """Auto-link imported folios to the Holdings Register."""
        if self.status == "Imported" and self.folio_data:
            self._link_to_holdings()

    def _link_to_holdings(self):
        """Create Holdings Register entries for each imported folio."""
        if not self.investor:
            return

        try:
            folios = frappe.parse_json(self.folio_data)
        except Exception:
            return

        linked = 0
        for folio in folios:
            # Dedup by investor + ISIN (scheme_code). Holdings Register has no folio_number field.
            existing = frappe.db.exists("Holdings Register", {
                "investor": self.investor,
                "isin": folio.get("scheme_code"),
            })
            if existing:
                continue

            try:
                frappe.get_doc({
                    "doctype": "Holdings Register",
                    "investor": self.investor,
                    "instrument_type": "Mutual Fund",
                    "isin": folio.get("scheme_code"),
                    "symbol": folio.get("scheme_code"),
                    "security_name": folio.get("scheme_name"),
                    "folio_number": folio.get("folio_number"),
                    "quantity": folio.get("units"),
                    "purchase_price": folio.get("cost_price"),
                    "current_price": folio.get("nav"),
                    "current_value": folio.get("current_value"),
                    "fund_master": None,
                }).insert()
                linked += 1
            except Exception:
                continue

        if linked > 0:
            frappe.msgprint(f"{linked} holdings linked to portfolio from CAS import.")


@frappe.whitelist()
def import_cas(investor, pan_number, from_date=None, to_date=None):
    """API: Fetch Consolidated Account Statement and import holdings."""
    from bizaxl.bizaxl.integrations.cams_karvy_kra import KRAConnector

    connector = KRAConnector()
    result = connector.fetch_cas(pan_number, from_date, to_date)

    if result.get("status") != "Success":
        return {"status": "Failed", "error": result.get("error")}

    cas = frappe.get_doc({
        "doctype": "CAS Import",
        "investor": investor,
        "pan_number": pan_number,
        "source": "CAMS/Karvy CAS",
        "reporting_from": result.get("reporting_period", {}).get("from"),
        "reporting_to": result.get("reporting_period", {}).get("to"),
        "status": "Imported",
        "total_folios": result.get("total_folios", 0),
        "total_investment": result.get("total_investment", 0),
        "total_current_value": result.get("total_current_value", 0),
        "total_unrealized_gain": result.get("total_unrealized_gain", 0),
        "total_return_pct": result.get("total_return_pct", 0),
        "folio_data": frappe.as_json(result.get("folios", [])),
        "connector_mode": result.get("mode", "stub"),
        "imported_at": now_datetime(),
    })
    cas.insert()

    return {
        "cas_import": cas.name,
        "total_folios": result.get("total_folios"),
        "total_investment": result.get("total_investment"),
        "total_current_value": result.get("total_current_value"),
        "total_unrealized_gain": result.get("total_unrealized_gain"),
    }


@frappe.whitelist()
def list_cas_imports(investor=None):
    """API: List CAS imports for an investor."""
    filters = {}
    if investor:
        filters["investor"] = investor

    return frappe.get_all(
        "CAS Import",
        filters=filters,
        fields=["name", "pan_number", "source", "status",
                "total_folios", "total_investment", "total_current_value",
                "total_unrealized_gain", "total_return_pct",
                "connector_mode", "imported_at"],
        order_by="imported_at desc",
        limit_page_length=50,
    )


@frappe.whitelist()
def fetch_mf_transactions(pan_number, from_date=None, to_date=None):
    """API: Fetch MF transaction history from CAMS/Karvy."""
    from bizaxl.bizaxl.integrations.cams_karvy_kra import KRAConnector

    connector = KRAConnector()
    result = connector.fetch_mf_transactions(pan_number, None, from_date, to_date)
    return result


@frappe.whitelist()
def kra_kyc_check(pan_number, kra_name="CAMS KRA"):
    """API: Check KYC status across a KRA."""
    from bizaxl.bizaxl.integrations.cams_karvy_kra import KRAConnector

    connector = KRAConnector()
    result = connector.kra_kyc_check(pan_number, kra_name)
    return result


@frappe.whitelist()
def fetch_scheme_master(amc_code=None, category=None):
    """API: Fetch scheme master data."""
    from bizaxl.bizaxl.integrations.cams_karvy_kra import KRAConnector

    connector = KRAConnector()
    result = connector.fetch_scheme_master(amc_code, category)
    return result
