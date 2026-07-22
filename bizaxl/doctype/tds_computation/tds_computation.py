# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class TDSComputation(Document):
    """TDS/withholding tax computation on fee payments and distributions."""

    def validate(self):
        self.calculate_tds()

    def calculate_tds(self):
        """Calculate TDS, surcharge, education cess, and net amount."""
        gross = flt(self.gross_amount)
        rate = flt(self.tds_rate)
        surcharge_rate = flt(self.surcharge_rate)
        cess_rate = flt(self.cess_rate)

        tds = gross * (rate / 100)
        surcharge = tds * (surcharge_rate / 100) if surcharge_rate > 0 else 0
        cess = (tds + surcharge) * (cess_rate / 100) if cess_rate > 0 else 0

        self.tds_amount = tds
        self.surcharge_amount = surcharge
        self.education_cess = cess
        self.total_tds = tds + surcharge + cess
        self.net_amount = gross - self.total_tds


@frappe.whitelist()
def compute_tds(gross_amount, tds_rate, surcharge_rate=0, cess_rate=4):
    """API: Compute TDS amount without creating a document."""
    from frappe.utils import flt
    gross = flt(gross_amount)
    tds = gross * (flt(tds_rate) / 100)
    surcharge = tds * (flt(surcharge_rate) / 100) if flt(surcharge_rate) > 0 else 0
    cess = (tds + surcharge) * (flt(cess_rate) / 100) if flt(cess_rate) > 0 else 0
    return {
        "gross_amount": gross,
        "tds_amount": tds,
        "surcharge_amount": surcharge,
        "education_cess": cess,
        "total_tds": tds + surcharge + cess,
        "net_amount": gross - (tds + surcharge + cess),
    }


@frappe.whitelist()
def get_tds_summary(fund_master, fiscal_year=None):
    """API: Get TDS summary for a fund."""
    filters = {"fund_master": fund_master}
    result = frappe.get_all(
        "TDS Computation",
        filters=filters,
        fields=[
            "transaction_type",
            "sum(gross_amount) as total_gross",
            "sum(total_tds) as total_tds_deducted",
            "sum(net_amount) as total_net",
        ],
        group_by="transaction_type",
    )
    return result
