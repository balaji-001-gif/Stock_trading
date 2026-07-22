# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime


class ESignRequest(Document):
    """Aadhaar e-Sign / DigiLocker document signing request."""

    def validate(self):
        self.set_defaults()
        self.validate_expiry()
        self.validate_verification()

    def set_defaults(self):
        """Set request_date if not provided."""
        if not self.request_date:
            self.request_date = today()

    def validate_expiry(self):
        """Warn if the signing request has expired."""
        if self.expiry_date and self.expiry_date < today():
            frappe.msgprint(
                f"Warning: This e-Sign request expired on {self.expiry_date}. "
                "Consider updating the expiry date if signing is still in progress.",
                alert=True,
            )

    def validate_verification(self):
        """Ensure verification fields are consistent."""
        if self.verified:
            if not self.verified_by:
                frappe.throw("Verified By is required when marking as verified.")
            if not self.verification_date:
                self.verification_date = today()

    def before_submit(self):
        """Before submit, mark as sent for signing."""
        if self.status == "Draft":
            self.status = "Sent for Signing"


@frappe.whitelist()
def verify_esign(esign_name):
    """API: Mark an e-Sign request as verified."""
    doc = frappe.get_doc("e-Sign Request", esign_name)
    if doc.status != "Signed":
        frappe.throw(f"Cannot verify e-Sign request in status: {doc.status}. Must be 'Signed'.")

    doc.verified = 1
    doc.verified_by = frappe.session.user
    doc.verification_date = today()
    doc.flags.ignore_permissions = True
    doc.save()

    return {"status": "success", "message": f"e-Sign request {esign_name} verified."}


@frappe.whitelist()
def complete_esign(esign_name, signed_document=None):
    """API: Mark an e-Sign request as completed/signed."""
    doc = frappe.get_doc("e-Sign Request", esign_name)
    if doc.status not in ("Sent for Signing",):
        frappe.throw(f"Cannot complete e-Sign request in status: {doc.status}")

    doc.status = "Signed"
    doc.signed_date = now_datetime()
    if signed_document:
        doc.signed_document = signed_document
    doc.flags.ignore_permissions = True
    doc.save()

    return {"status": "success", "message": f"e-Sign request {esign_name} completed."}


@frappe.whitelist()
def get_pending_esign_requests(investor=None):
    """API: Get all pending e-Sign requests, optionally filtered by investor."""
    filters = {"status": ["in", ("Draft", "Sent for Signing")]}
    if investor:
        filters["investor"] = investor

    return frappe.get_all(
        "e-Sign Request",
        filters=filters,
        fields=[
            "name", "investor", "document_type", "document_reference",
            "esign_method", "request_date", "expiry_date", "status",
        ],
        order_by="request_date asc",
    )
