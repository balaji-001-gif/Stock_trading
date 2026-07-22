# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
Base Connector — Stub-to-Live Integration Framework

All 20 external API integrations inherit from this base class.
- Stub mode: Simulates API responses using realistic test data
- Live mode: Makes real API calls when credentials are configured
- Auto-detection: Mode switches automatically based on credential availability
- No code changes: Integration logic is identical in both modes
"""

import frappe
import json
from frappe.utils import now_datetime, today, flt
from frappe import _


class BaseConnector:
    """
    Abstract base class for all BIZAXL external API connectors.

    Subclasses must define:
        - connector_name (str): Unique identifier, e.g., 'uidai_ekyc'
        - label (str): Human-readable name, e.g., 'UIDAI Aadhaar eKYC'
        - settings_doctype (str): Frappe DocType holding API credentials

    Subclasses should override:
        - stub_*(...): Implement simulated API responses
        - live_*(...): Implement real API calls
    """

    connector_name = ""
    label = ""
    settings_doctype = "Integration Settings"

    def __init__(self):
        self.settings = self._load_settings()
        self._mode = None  # Lazily evaluated

    # -------------------------------------------------------------------------
    # Mode detection
    # -------------------------------------------------------------------------

    @property
    def mode(self):
        """'live' if credentials are configured, otherwise 'stub'."""
        if self._mode is None:
            self._mode = self._detect_mode()
        return self._mode

    def _detect_mode(self):
        """Check if required credentials exist for live mode."""
        if not self.settings:
            return "stub"
        return "live" if self._has_credentials() else "stub"

    def _has_credentials(self):
        """
        Override in subclass to check for live API credentials.
        Must return True/False.
        """
        return False

    def _load_settings(self):
        """Load integration settings from Frappe."""
        try:
            if frappe.db.exists(self.settings_doctype, self.connector_name):
                return frappe.get_doc(self.settings_doctype, self.connector_name)
        except Exception:
            pass
        return None

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------

    def log_request(self, method, request_data, response_data, status="Success", error=None):
        """Log API request/response for audit trail."""
        try:
            log = frappe.get_doc({
                "doctype": "Integration Request Log",
                "integration": self.label,
                "method": method,
                "mode": self.mode,
                "request_data": json.dumps(request_data, default=str, indent=2)[:3000],
                "response_data": json.dumps(response_data, default=str, indent=2)[:3000],
                "status": status,
                "error": str(error)[:500] if error else None,
                "timestamp": now_datetime(),
            })
            log.insert(ignore_permissions=True)
        except Exception:
            pass  # Don't break the main flow for logging failures

    # -------------------------------------------------------------------------
    # Convenience helpers
    # -------------------------------------------------------------------------

    def _get_api_key(self):
        """Get API key from settings."""
        return self.settings.get("api_key") if self.settings else None

    def _get_api_secret(self):
        """Get API secret from settings."""
        return self.settings.get("api_secret") if self.settings else None

    def _get_endpoint(self):
        """Get configured endpoint URL or default."""
        return self.settings.get("endpoint_url") if self.settings else None

    @property
    def is_stub(self):
        """Check if running in stub mode."""
        return self.mode == "stub"

    @property
    def is_live(self):
        """Check if running in live mode."""
        return self.mode == "live"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.label} [{self.mode.upper()}]>"
