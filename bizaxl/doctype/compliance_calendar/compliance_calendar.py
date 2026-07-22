# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class ComplianceCalendar(Document):
    """Compliance deadline calendar with overdue detection."""

    def validate(self):
        if self.due_date and self.due_date < today() and self.status == "Open":
            self.status = "Overdue"
