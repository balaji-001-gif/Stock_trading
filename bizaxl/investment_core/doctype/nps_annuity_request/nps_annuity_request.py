# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class NPSAnnuityRequest(Document):
    """NPS withdrawal and annuity processing — exit at 60, premature exit, death claims."""

    def validate(self):
        self.fetch_pran()
        self.calculate_lump_sum_and_annuity()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Submitted"

    def fetch_pran(self):
        if self.nps_subscriber and not self.pran_number:
            self.pran_number = frappe.get_value("NPS Subscriber", self.nps_subscriber, "pran_number")

    def calculate_lump_sum_and_annuity(self):
        """Calculate lump sum and annuity amounts based on exit type."""
        corpus = flt(self.total_corpus)
        if not corpus:
            return

        if self.request_type == "Exit at 60 (Normal)":
            # 60% lump sum (tax-free), 40% mandatory annuity
            lump_pct = flt(self.lump_sum_percentage) or 60
            annuity_pct = 100 - lump_pct
            if annuity_pct < 40:
                frappe.msgprint("Minimum 40% of corpus must be used for annuity purchase.", alert=True)
                annuity_pct = 40
                lump_pct = 60

        elif self.request_type == "Premature Exit (Before 60)":
            # Minimum 80% annuity mandatory
            lump_pct = flt(self.lump_sum_percentage) or 20
            annuity_pct = 100 - lump_pct
            if annuity_pct < 80:
                frappe.msgprint("Minimum 80% of corpus must be used for annuity for premature exit.", alert=True)
                annuity_pct = 80
                lump_pct = 20

        elif self.request_type == "Partial Withdrawal (Max 25%)":
            lump_pct = flt(self.lump_sum_percentage) or 25
            annuity_pct = 0
            if lump_pct > 25:
                frappe.msgprint("Partial withdrawal is limited to 25% of corpus.", alert=True)
                lump_pct = 25

        elif self.request_type == "Death Claim":
            lump_pct = 100
            annuity_pct = 0
        else:
            lump_pct = flt(self.lump_sum_percentage) or 60
            annuity_pct = 100 - lump_pct

        self.lump_sum_percentage = lump_pct
        self.annuity_percentage = annuity_pct
        self.lump_sum_amount = corpus * (lump_pct / 100)
        self.annuity_amount = corpus * (annuity_pct / 100)

        # Tax calculation
        if self.request_type == "Exit at 60 (Normal)":
            # Lump sum up to 60% is tax-free
            self.lump_sum_taxable = 0
            self.tax_on_lump_sum = 0
            # Annuity income is taxable as per slab
            self.annuity_taxable = self.annuity_amount
        elif self.request_type == "Premature Exit (Before 60)":
            # 100% of lump sum is taxable
            self.lump_sum_taxable = self.lump_sum_amount
            self.tax_on_lump_sum = self.lump_sum_amount * 0.10  # ~10% avg tax
            self.annuity_taxable = self.annuity_amount


@frappe.whitelist()
def process_exit(nps_subscriber, request_type, **kwargs):
    """API: Process an NPS exit or withdrawal request."""
    doc = frappe.get_doc({
        "doctype": "NPS Annuity Request",
        "nps_subscriber": nps_subscriber,
        "request_type": request_type,
        "request_date": kwargs.get("request_date"),
        "total_corpus": flt(kwargs.get("total_corpus", 0)),
        "subscriber_age": kwargs.get("subscriber_age"),
        "status": "Draft",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_annuity_requests(nps_subscriber):
    """API: Get annuity/withdrawal requests for a subscriber."""
    return frappe.get_all(
        "NPS Annuity Request",
        filters={"nps_subscriber": nps_subscriber},
        fields=[
            "name", "request_type", "request_date", "status",
            "total_corpus", "lump_sum_amount", "annuity_amount",
            "annuity_type", "settlement_date",
        ],
        order_by="request_date desc",
    )
