# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class NotificationLog(Document):
    """Tracks all sent notifications across SMS, WhatsApp, Email channels."""
    pass


@frappe.whitelist()
def send_notification(channel, recipient, template_key, **kwargs):
    """API: Send a templated notification via any channel."""
    from bizaxl.bizaxl.integrations.notification_service import NotificationConnector

    connector = NotificationConnector()

    # Build template variables from kwargs
    template_vars = {k: v for k, v in kwargs.items() if k not in ("reference_doctype", "reference_name")}

    if channel == "email":
        result = connector.send_email(
            recipient,
            connector._render_template(template_key, "email_subject", template_vars),
            connector._render_template(template_key, "email_body", template_vars),
        )
    elif channel == "sms":
        msg = connector._render_template(template_key, "sms", template_vars)
        result = connector.send_sms(recipient, msg)
    elif channel == "whatsapp":
        result = connector.send_whatsapp(recipient, template_key=template_key, template_vars=template_vars)
    else:
        return {"status": "Failed", "error": f"Unsupported channel: {channel}"}

    # Log to Notification Log
    if result.get("status") == "Success":
        try:
            log = frappe.get_doc({
                "doctype": "Notification Log",
                "channel": channel.title(),
                "recipient": recipient,
                "subject": result.get("subject") or kwargs.get("subject", ""),
                "template_key": template_key,
                "message_id": result.get("message_id"),
                "delivery_status": result.get("delivery_status", "Sent"),
                "sent_at": now_datetime(),
                "reference_doctype": kwargs.get("reference_doctype"),
                "reference_name": kwargs.get("reference_name"),
                "connector_mode": result.get("mode", "stub"),
            })
            log.insert(ignore_permissions=True)
        except Exception:
            pass

    return result


@frappe.whitelist()
def send_bulk_notification(channel, recipients, template_key, template_vars, **kwargs):
    """API: Send bulk notification to multiple recipients."""
    results = []
    for recipient in recipients:
        result = send_notification(channel, recipient.strip(), template_key, **template_vars, **kwargs)
        results.append({"recipient": recipient, "status": result.get("status"), "message_id": result.get("message_id")})
    return {"results": results, "total": len(results), "successful": sum(1 for r in results if r["status"] == "Success")}


@frappe.whitelist()
def get_notification_logs(reference_doctype=None, reference_name=None, channel=None):
    """API: Get notification logs with filters."""
    filters = {}
    if reference_doctype:
        filters["reference_doctype"] = reference_doctype
    if reference_name:
        filters["reference_name"] = reference_name
    if channel:
        filters["channel"] = channel.title()

    return frappe.get_all(
        "Notification Log",
        filters=filters,
        fields=["name", "channel", "recipient", "subject", "template_key",
                "message_id", "delivery_status", "sent_at", "connector_mode"],
        order_by="sent_at desc",
        limit_page_length=50,
    )
