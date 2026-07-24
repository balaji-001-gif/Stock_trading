# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FATCCRSFiling(Document):
    """FATCA/CRS tax reporting for foreign investors."""

    def validate(self):
        if not self.fiscal_year:
            frappe.throw("Fiscal Year is required.")
        if not self.nil_report and not self.reportable_accounts:
            frappe.msgprint(
                "Please specify reportable accounts count or mark as nil report.",
                alert=True,
            )


@frappe.whitelist()
def get_fatca_status(fund_master):
    """API: Get FATCA/CRS filing status for a fund."""
    filings = frappe.get_all(
        "FATCA/CRS Filing",
        filters={"fund_master": fund_master},
        fields=[
            "name", "filing_type", "fiscal_year", "status",
            "due_date", "filing_date", "reportable_accounts",
            "nil_report", "acknowledgment_no",
        ],
        order_by="fiscal_year desc",
    )
    return filings
