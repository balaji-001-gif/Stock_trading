# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class IntegrationRequestLog(Document):
    """Audit trail for all external API connector calls."""
    pass
