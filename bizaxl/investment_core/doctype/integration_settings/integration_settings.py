# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class IntegrationSettings(Document):
    """Manages API credentials and endpoints for external integrations.

    All integrations use stub-to-live mode:
    - When credentials are empty → stub mode (simulated responses)
    - When credentials are configured → live mode (real API calls)
    - No code changes required to switch modes
    """

    def validate(self):
        self.validate_connector_name()

    def validate_connector_name(self):
        """Ensure connector name follows convention."""
        if self.connector_name:
            self.connector_name = self.connector_name.lower().strip()

    def on_update(self):
        """Clear cached connector instances when settings change."""
        frappe.cache().delete_value(f"integration_settings:{self.connector_name}")

    def get_credentials(self):
        """Return dict of credentials for use by connectors."""
        return {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "endpoint_url": self.endpoint_url,
            "environment": self.environment,
        }

    @property
    def is_configured(self):
        """Check if this integration has live credentials configured.
        Requires both API key and secret to switch to live mode.
        """
        return bool(self.api_key and self.api_secret)
