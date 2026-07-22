# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff


class BoardPack(Document):
    """Board/trustee meeting pack with agenda, documents, and minutes."""

    def validate(self):
        if self.meeting_date and date_diff(self.meeting_date, today()) < 0:
            frappe.msgprint(
                "Warning: Meeting date is in the past.",
                alert=True,
                indicator="orange",
            )


@frappe.whitelist()
def get_board_meeting_schedule(fund_master):
    """API: Get board meeting schedule."""
    return frappe.get_all(
        "Board Pack",
        filters={"fund_master": fund_master},
        fields=["name", "meeting_title", "meeting_type", "meeting_date", "status", "next_meeting_date"],
        order_by="meeting_date desc",
    )
