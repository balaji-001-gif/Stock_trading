# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
SMS / WhatsApp / Email Notification Connector — Stub-to-Live Integration

Multi-channel notification service for drawdown notices, redemption confirmations,
NAV alerts, dividend notices, OTP delivery, and automated correspondence.

Supports:
1. SMS — Transactional SMS via API gateway (OTP, alerts, confirmations)
2. WhatsApp — Templated WhatsApp messages via business API
3. Email — HTML-formatted email with attachments via SMTP/API
4. Notification Templates — Pre-defined templates for each use case
5. Delivery Status — Track delivery, read receipts, and failures

Stub mode: Logs notifications to Notification Log, simulates delivery
Live mode: Sends through configured SMS/WhatsApp/Email gateway APIs
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime
from frappe import _


# Template definitions for key notification types
NOTIFICATION_TEMPLATES = {
    "otp": {
        "sms": "Your OTP for {purpose} is {otp}. Valid for 10 minutes. - BIZAXL",
        "email_subject": "OTP for {purpose} - BIZAXL",
        "email_body": """
            <h3>OTP Verification</h3>
            <p>Your OTP for <strong>{purpose}</strong> is:</p>
            <h2 style="letter-spacing: 4px; background: #f4f4f4; padding: 12px; text-align: center;">{otp}</h2>
            <p>This OTP is valid for <strong>10 minutes</strong>.</p>
            <p>If you did not request this, please ignore this message.</p>
            <hr><p style="color: #888; font-size: 12px;">BIZAXL Investment Platform</p>
        """,
    },
    "drawdown_notice": {
        "sms": "Drawdown Notice: {fund_name} is calling Rs.{amount} per unit. Due: {due_date}. - BIZAXL",
        "email_subject": "Capital Call / Drawdown Notice - {fund_name}",
        "email_body": """
            <h3>Capital Call Notice</h3>
            <p>Dear Investor,</p>
            <p>This is a drawdown notice for <strong>{fund_name}</strong>.</p>
            <table style="border:1px solid #ddd;padding:8px;">
            <tr><td>Amount Called:</td><td><strong>Rs.{amount}</strong></td></tr>
            <tr><td>Due Date:</td><td><strong>{due_date}</strong></td></tr>
            <tr><td>Bank Details:</td><td>{bank_details}</td></tr>
            </table>
            <p>Please transfer the amount by the due date.</p>
            <hr><p style="color: #888; font-size: 12px;">BIZAXL Investment Platform</p>
        """,
    },
    "redemption_confirmation": {
        "sms": "Redemption Rs.{amount} processed for {fund_name}. Ref: {ref_no}. Will credit in T+{settlement_days}. - BIZAXL",
        "email_subject": "Redemption Confirmation - {fund_name}",
        "email_body": """
            <h3>Redemption Confirmation</h3>
            <p>Your redemption request has been processed.</p>
            <table style="border:1px solid #ddd;padding:8px;">
            <tr><td>Fund:</td><td>{fund_name}</td></tr>
            <tr><td>Amount:</td><td><strong>Rs.{amount}</strong></td></tr>
            <tr><td>Redemption Price:</td><td>Rs.{nav}</td></tr>
            <tr><td>Settlement:</td><td>T+{settlement_days} ({expected_date})</td></tr>
            </table>
            <hr><p style="color: #888; font-size: 12px;">BIZAXL Investment Platform</p>
        """,
    },
    "nav_alert": {
        "sms": "NAV Alert: {scheme_name} NAV is Rs.{nav} as of {date}. Change: {change_pct}%. - BIZAXL",
        "email_subject": "Daily NAV Alert - {scheme_name}",
        "email_body": """
            <h3>NAV Update</h3>
            <table style="border:1px solid #ddd;padding:8px;">
            <tr><td>Scheme:</td><td>{scheme_name}</td></tr>
            <tr><td>NAV:</td><td><strong>Rs.{nav}</strong></td></tr>
            <tr><td>Date:</td><td>{date}</td></tr>
            <tr><td>Change:</td><td>{change_pct}%</td></tr>
            </table>
            <hr><p style="color: #888; font-size: 12px;">BIZAXL Investment Platform</p>
        """,
    },
    "dividend_notice": {
        "sms": "Dividend Declared: {scheme_name} - Rs.{dividend_per_unit} per unit. Record Date: {record_date}. - BIZAXL",
        "email_subject": "Dividend Declaration - {scheme_name}",
        "email_body": """
            <h3>Dividend Declaration</h3>
            <table style="border:1px solid #ddd;padding:8px;">
            <tr><td>Scheme:</td><td>{scheme_name}</td></tr>
            <tr><td>Dividend:</td><td><strong>Rs.{dividend_per_unit} per unit</strong></td></tr>
            <tr><td>Record Date:</td><td>{record_date}</td></tr>
            <tr><td>Payment Date:</td><td>{payment_date}</td></tr>
            </table>
            <hr><p style="color: #888; font-size: 12px;">BIZAXL Investment Platform</p>
        """,
    },
    "statement_available": {
        "email_subject": "Your Account Statement is Ready - BIZAXL",
        "email_body": """
            <h3>Account Statement Available</h3>
            <p>Your account statement for the period <strong>{period}</strong> is now available.</p>
            <p><a href="{download_link}" style="background:#2563eb;color:white;padding:10px 20px;
            text-decoration:none;border-radius:5px;">Download Statement</a></p>
            <hr><p style="color: #888; font-size: 12px;">BIZAXL Investment Platform</p>
        """,
    },
}


class NotificationConnector(BaseConnector):
    """Multi-channel notification service — SMS, WhatsApp, Email."""

    connector_name = "notification_service"
    label = "SMS / WhatsApp / Email"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        """Live mode requires at least one channel gateway configured."""
        return bool(self._get_api_key())

    # =========================================================================
    # PUBLIC API: Send SMS
    # =========================================================================

    def send_sms(self, mobile_number, message, template_key=None, template_vars=None):
        """Send SMS notification."""
        request = {"to": mobile_number[:8] + "XXXX", "msg_len": len(message)}

        try:
            if template_key and template_vars:
                message = self._render_template(template_key, "sms", template_vars)

            if self.is_stub:
                result = self._stub_send_sms(mobile_number, message)
            else:
                result = self._live_send_sms(mobile_number, message)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "channel": "sms", "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Send WhatsApp
    # =========================================================================

    def send_whatsapp(self, mobile_number, message=None, template_key=None, template_vars=None, media_url=None):
        """Send WhatsApp message (text or template)."""
        request = {"to": mobile_number[:8] + "XXXX", "template": bool(template_key)}

        try:
            if template_key and template_vars:
                message = self._render_template(template_key, "sms", template_vars)

            if self.is_stub:
                result = self._stub_send_whatsapp(mobile_number, message or "Template message")
            else:
                result = self._live_send_whatsapp(mobile_number, message or "Template message", media_url)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "channel": "whatsapp", "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Send Email
    # =========================================================================

    def send_email(self, to_email, subject, html_body, attachments=None, cc=None):
        """Send HTML email notification."""
        request = {"to": to_email, "subject": subject[:50], "has_attachments": bool(attachments)}

        try:
            if self.is_stub:
                result = self._stub_send_email(to_email, subject, html_body, attachments)
            else:
                result = self._live_send_email(to_email, subject, html_body, attachments, cc)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "channel": "email", "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Template-based send
    # =========================================================================

    def send_notification(self, channel, template_key, recipient, template_vars, attachments=None):
        """Send a templated notification via the specified channel."""
        if channel == "sms":
            msg = self._render_template(template_key, "sms", template_vars)
            return self.send_sms(recipient, msg)
        elif channel == "whatsapp":
            return self.send_whatsapp(recipient, template_key=template_key, template_vars=template_vars)
        elif channel == "email":
            subject = self._render_template(template_key, "email_subject", template_vars)
            body = self._render_template(template_key, "email_body", template_vars)
            return self.send_email(recipient, subject, body, attachments)
        return {"status": "Failed", "error": f"Unknown channel: {channel}", "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Delivery Status
    # =========================================================================

    def get_delivery_status(self, notification_ref):
        """Check delivery status of a sent notification."""
        try:
            if self.is_stub:
                result = self._stub_delivery_status(notification_ref)
            else:
                result = self._live_delivery_status(notification_ref)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_send_sms(self, mobile, message):
        """Simulate SMS sending via API gateway."""
        return {
            "status": "Success",
            "mode": "stub",
            "channel": "sms",
            "to": mobile[:8] + "XXXX",
            "message_id": f"SMS{random_string(16).upper()}",
            "delivery_status": "Delivered",
            "carrier": random.choice(["Airtel", "Jio", "Vi", "BSNL"]),
            "sent_at": now_datetime().isoformat(),
            "credits_used": 1,
        }

    def _stub_send_whatsapp(self, mobile, message):
        """Simulate WhatsApp message."""
        return {
            "status": "Success",
            "mode": "stub",
            "channel": "whatsapp",
            "to": mobile[:8] + "XXXX",
            "message_id": f"WA{random_string(16).upper()}",
            "delivery_status": "Sent",
            "read_receipt": random.choice([True, False]),
            "sent_at": now_datetime().isoformat(),
        }

    def _stub_send_email(self, to, subject, html, attachments):
        """Simulate email sending."""
        return {
            "status": "Success",
            "mode": "stub",
            "channel": "email",
            "to": to,
            "subject": subject,
            "message_id": f"EM{random_string(16).upper()}",
            "delivery_status": "Delivered",
            "has_attachments": bool(attachments),
            "sent_at": now_datetime().isoformat(),
        }

    def _stub_delivery_status(self, notification_ref):
        """Simulate delivery status check."""
        return {
            "status": "Success",
            "mode": "stub",
            "notification_ref": notification_ref,
            "delivery_status": "Delivered",
            "delivered_at": (get_datetime() - timedelta(minutes=2)).isoformat(),
            "read": random.choice([True, False]),
        }

    # =========================================================================
    # Template Engine
    # =========================================================================

    def _render_template(self, template_key, field, variables):
        """Render a notification template with variables."""
        template_group = NOTIFICATION_TEMPLATES.get(template_key, {})
        template = template_group.get(field, "")
        if not template and field == "sms":
            template = template_group.get("sms", "")
        try:
            return template.format(**variables)
        except KeyError as e:
            return template  # Return unformatted if variables missing

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_send_sms(self, mobile, message):
        raise NotImplementedError("Live SMS requires SMS gateway API credentials.")

    def _live_send_whatsapp(self, mobile, message, media_url):
        raise NotImplementedError("Live WhatsApp requires WhatsApp Business API credentials.")

    def _live_send_email(self, to, subject, html, attachments, cc):
        raise NotImplementedError("Live email requires SMTP / email API credentials.")

    def _live_delivery_status(self, notification_ref):
        raise NotImplementedError("Live delivery status requires gateway API access.")
