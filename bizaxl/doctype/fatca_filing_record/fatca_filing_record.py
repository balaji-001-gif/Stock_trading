# Copyright (c) 2026, bizaxl and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today


class FATCAFilingRecord(Document):
    """FATCA Filing Record — tracks FATCA/CRS filing submissions and acknowledgments"""

    def validate(self):
        if not self.submission_date and self.status == "Submitted":
            self.submission_date = today()


@frappe.whitelist()
def submit_fatca_filing(filing_type, filing_year, reporting_year, entity_name, entity_pan):
    """Create a new FATCA/CRS filing record"""
    record = frappe.get_doc({
        "doctype": "FATCA Filing Record",
        "filing_type": filing_type,
        "filing_year": filing_year,
        "reporting_year": reporting_year,
        "entity_name": entity_name,
        "entity_pan": entity_pan,
        "status": "Pending Submission"
    })
    record.insert()
    return record


@frappe.whitelist()
def get_filing_status(name):
    """Get the status of a filing record"""
    record = frappe.get_doc("FATCA Filing Record", name)
    return {
        "name": record.name,
        "status": record.status,
        "filing_type": record.filing_type,
        "submission_ref": record.submission_ref,
        "acknowledgment_ref": record.acknowledgment_ref,
        "submission_date": record.submission_date
    }


@frappe.whitelist()
def list_fatca_filings(filing_type=None, status=None, year=None):
    """List FATCA/CRS filings with optional filters"""
    filters = {}
    if filing_type:
        filters["filing_type"] = filing_type
    if status:
        filters["status"] = status
    if year:
        filters["filing_year"] = year

    filings = frappe.get_all(
        "FATCA Filing Record",
        filters=filters,
        fields=[
            "name", "filing_type", "filing_year", "reporting_year",
            "entity_name", "entity_pan", "status", "submission_date",
            "submission_ref", "acknowledgment_ref", "total_accounts_reported"
        ],
        order_by="creation desc",
        limit=50
    )
    return filings
