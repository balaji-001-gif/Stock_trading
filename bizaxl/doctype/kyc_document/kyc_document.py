# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff


class KYCDocument(Document):
    """Identity document record for investor KYC verification."""

    def validate(self):
        self.validate_expiry()
        self.validate_document_number()
        self.update_investor_kyc_status()

    def validate_expiry(self):
        """Warn if document is expired or expiring soon."""
        if self.date_of_expiry:
            days_remaining = date_diff(self.date_of_expiry, today())
            if days_remaining < 0:
                frappe.throw(
                    f"This document has expired {abs(days_remaining)} days ago.",
                    title="Expired Document",
                )
            elif days_remaining < 30:
                frappe.msgprint(
                    f"Warning: Document expires in {days_remaining} days.",
                    alert=True,
                )

    def validate_document_number(self):
        """Basic format validation based on document type."""
        if not self.document_number:
            frappe.throw("Document number is required.", title="Missing Number")

    def before_submit(self):
        """On submit, mark as verified and update investor KYC."""
        self.verification_status = "Verified"
        self.verification_date = today()
        self.update_investor_kyc_status()

    def on_update(self):
        """Update investor KYC status when document verification changes."""
        if self.docstatus == 0:
            self.update_investor_kyc_status()

    def update_investor_kyc_status(self):
        """Propagate KYC status to linked investor profile."""
        if not self.investor:
            return

        # Get all KYC documents for this investor
        all_docs = frappe.get_all(
            "KYC Document",
            filters={"investor": self.investor},
            fields=["verification_status", "name"],
        )

        if not all_docs:
            return

        statuses = [d["verification_status"] for d in all_docs]

        # Determine overall KYC status
        if any(s == "Rejected" for s in statuses):
            new_status = "Rejected"
        elif all(s == "Verified" for s in statuses):
            new_status = "Verified"
        elif any(s == "In Progress" for s in statuses):
            new_status = "In Progress"
        elif any(s == "Pending" for s in statuses):
            new_status = "Pending"
        else:
            new_status = "Not Started"

        investor = frappe.get_doc("Investor Profile", self.investor)
        if investor.kyc_status != new_status:
            investor.kyc_status = new_status
            if new_status == "Verified":
                investor.kyc_completed_date = today()
            investor.save(ignore_permissions=True)


@frappe.whitelist()
def verify_document(document_name):
    """API: Mark a KYC document as verified."""
    doc = frappe.get_doc("KYC Document", document_name)
    doc.verification_status = "Verified"
    doc.verification_date = today()
    doc.verified_by = frappe.session.user
    doc.save()
    doc.submit()
    return doc


@frappe.whitelist()
def reject_document(document_name, reason):
    """API: Reject a KYC document with a reason."""
    doc = frappe.get_doc("KYC Document", document_name)
    doc.verification_status = "Rejected"
    doc.rejection_reason = reason
    doc.verified_by = frappe.session.user
    doc.save()
    return doc


@frappe.whitelist()
def get_investor_kyc_documents(investor):
    """API: Get all KYC documents for an investor."""
    return frappe.get_all(
        "KYC Document",
        filters={"investor": investor},
        fields=[
            "name",
            "document_type",
            "document_number",
            "verification_status",
            "verification_method",
            "verified_by",
            "verification_date",
            "date_of_expiry",
            "ckyc_number",
        ],
        order_by="modified desc",
    )
