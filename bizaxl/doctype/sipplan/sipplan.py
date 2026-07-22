# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, add_days, add_months


class SIPPlan(Document):
    """Systematic Investment Plan with NACH/UPI mandate."""

    def validate(self):
        self.validate_amount()
        self.set_next_sip_date()

    def validate_amount(self):
        if self.sip_amount <= 0:
            frappe.throw("SIP amount must be greater than zero.")

    def set_next_sip_date(self):
        if not self.next_sip_date and self.start_date:
            self.next_sip_date = self.start_date

    def process_installment(self):
        """Process a single SIP installment (creates subscription request)."""
        if self.status != "Active":
            frappe.throw("SIP plan is not active.")

        sub = frappe.get_doc({
            "doctype": "Subscription Request",
            "investor": self.investor,
            "fund_master": self.fund_master,
            "share_class": self.share_class,
            "subscription_type": "SIP Installment",
            "investment_amount": self.sip_amount,
            "subscription_date": today(),
            "application_date": today(),
            "allotment_status": "Pending",
            "payment_status": "Received",
            "payment_mode": "NACH Auto Debit",
        })
        sub.insert()
        sub.submit()

        self.installments_done = (self.installments_done or 0) + 1
        self.total_invested = flt(self.total_invested) + flt(self.sip_amount)
        self.last_sip_date = today()
        self.last_sip_status = "Processed"

        # Calculate next SIP date
        if self.sip_frequency == "Monthly":
            self.next_sip_date = add_months(today(), 1)
        elif self.sip_frequency == "Quarterly":
            self.next_sip_date = add_months(today(), 3)
        elif self.sip_frequency == "Weekly":
            self.next_sip_date = add_days(today(), 7)
        else:
            self.next_sip_date = add_days(today(), 1)

        # Check if completed
        if self.total_installments and self.installments_done >= self.total_installments:
            self.status = "Completed"

        self.save()
        return sub


@frappe.whitelist()
def create_sip(investor, fund_master, share_class, sip_amount, sip_frequency="Monthly", **kwargs):
    """API: Create a new SIP plan."""
    sip = frappe.get_doc({
        "doctype": "SIP Plan",
        "investor": investor,
        "fund_master": fund_master,
        "share_class": share_class,
        "sip_amount": flt(sip_amount),
        "sip_frequency": sip_frequency,
        "status": "Active",
        "start_date": today(),
    })
    for key, value in kwargs.items():
        if hasattr(sip, key) and not sip.get(key):
            try:
                sip.set(key, value)
            except Exception:
                pass
    sip.insert()
    return sip
