# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class AutoCorrespondence(Document):
    """Automated correspondence dispatch for investor communications."""

    def validate(self):
        self.set_defaults()
        self.validate_delivery()

    def set_defaults(self):
        """Set default sent_date if status is Sent."""
        if self.status == "Sent" and not self.sent_date:
            self.sent_date = now_datetime()

    def validate_delivery(self):
        """Validate channel and delivery status combinations."""
        if self.status == "Sent" and not self.channel:
            frappe.throw("Channel is required when status is Sent.")

        if self.status == "Sent" and not self.subject:
            frappe.throw("Subject is required when sending correspondence.")


@frappe.whitelist()
def dispatch_correspondence(correspondence_name):
    """API: Trigger dispatch of a pending correspondence."""
    doc = frappe.get_doc("Auto Correspondence", correspondence_name)
    if doc.status not in ("Draft", "Queued"):
        frappe.throw(f"Cannot dispatch correspondence in status: {doc.status}")

    try:
        # Simulate sending — replace with actual email/SMS/WhatsApp dispatch
        doc.status = "Sent"
        doc.sent_date = now_datetime()
        doc.delivery_status = "Delivered"
        doc.flags.ignore_permissions = True
        doc.save()

        frappe.msgprint(f"Correspondence {correspondence_name} dispatched successfully.")
        return {"status": "success", "message": f"Correspondence dispatched."}
    except Exception as e:
        # Commit failure state before frappe.throw() rolls back the transaction
        frappe.db.set_value("Auto Correspondence", correspondence_name, {
            "status": "Failed",
            "error_log": str(e),
        })
        frappe.db.commit()
        frappe.throw(f"Dispatch failed: {str(e)}")


@frappe.whitelist()
def get_investor_correspondence(investor, limit=20):
    """API: Get recent correspondence for an investor."""
    return frappe.get_all(
        "Auto Correspondence",
        filters={"investor": investor},
        fields=[
            "name", "correspondence_type", "trigger_event", "subject",
            "sent_date", "status", "channel", "delivery_status",
        ],
        order_by="sent_date desc",
        limit=limit,
    )


@frappe.whitelist()
def get_pending_correspondence():
    """API: Get all queued or pending correspondence awaiting dispatch."""
    return frappe.get_all(
        "Auto Correspondence",
        filters={"status": ["in", ("Draft", "Queued")]},
        fields=[
            "name", "investor", "correspondence_type", "subject",
            "channel", "creation",
        ],
        order_by="creation asc",
    )
