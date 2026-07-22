# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class AMLComplianceRegister(Document):
    """AML compliance case management and tracking."""

    def validate(self):
        if not self.opened_date:
            self.opened_date = today()


@frappe.whitelist()
def get_aml_summary(fund_master=None):
    """API: Get AML compliance summary."""
    filters = {}
    if fund_master:
        filters["fund_master"] = fund_master

    open_cases = frappe.db.count("AML Compliance Register", filters={"case_status": ["in", ["Open", "Under Review", "Enhanced Monitoring"]]})
    escalated = frappe.db.count("AML Compliance Register", filters={"case_status": ["in", ["Escalated to MLRO", "Reported to FIU-IND"]]})
    high_risk = frappe.db.count("AML Compliance Register", filters={"risk_level": ["in", ["High", "Critical"]]})

    return {
        "open_cases": open_cases,
        "escalated_cases": escalated,
        "high_risk_cases": high_risk,
    }
