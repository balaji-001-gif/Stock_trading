# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class FundConfiguration(Document):
    """Central configuration linking Fund Master with all sub-entities."""

    def validate(self):
        self.validate_dates()
        self.validate_fund_references()
        self.set_configuration_name()

    def before_save(self):
        self.refresh_child_tables()

    def validate_dates(self):
        if self.effective_from and self.effective_to:
            if self.effective_from >= self.effective_to:
                frappe.throw(
                    "Effective To must be after Effective From.",
                    title="Invalid Date Range",
                )

    def validate_fund_references(self):
        if not self.fund_master:
            frappe.throw("Fund Master is required.", title="Missing Reference")

    def set_configuration_name(self):
        if not self.configuration_name:
            fund = frappe.get_value(
                "Fund Master", self.fund_master, "fund_name"
            )
            self.configuration_name = f"Configuration - {fund or self.fund_master}"

    def refresh_child_tables(self):
        """Refresh child tables with latest data from linked DocTypes."""
        if not self.fund_master:
            return

        # Refresh share classes
        if self.share_classes_enabled:
            self.share_classes_table = []
            share_classes = frappe.get_all(
                "Share Class",
                filters={"fund_master": self.fund_master, "status": "Active"},
                fields=["name", "class_type", "nav", "expense_ratio", "status"],
            )
            for sc in share_classes:
                self.append(
                    "share_classes_table",
                    {
                        "share_class": sc.name,
                        "class_type": sc.class_type,
                        "nav": sc.nav,
                        "expense_ratio": sc.expense_ratio,
                        "status": sc.status,
                    },
                )

        # Refresh series
        if self.series_enabled:
            self.active_series_table = []
            series = frappe.get_all(
                "Fund Series",
                filters={"fund_master": self.fund_master},
                fields=["name", "series_name", "series_type", "series_corpus_committed", "status"],
            )
            for s in series:
                self.append(
                    "active_series_table",
                    {
                        "fund_series": s.name,
                        "series_name": s.series_name,
                        "series_type": s.series_type,
                        "committed_corpus": s.series_corpus_committed,
                        "status": s.status,
                    },
                )

        # Refresh fee structures
        if self.fee_enabled:
            self.active_fee_structures = []
            fees = frappe.get_all(
                "Fee Structure",
                filters={
                    "fund_master": self.fund_master,
                    "status": "Active",
                    "effective_from": ["<=", today()],
                },
                fields=["name", "fee_type", "management_fee_rate", "management_fee_frequency", "status"],
            )
            for f in fees:
                self.append(
                    "active_fee_structures",
                    {
                        "fee_structure": f.name,
                        "fee_type": f.fee_type,
                        "fee_rate": f.management_fee_rate,
                        "fee_frequency": f.management_fee_frequency,
                        "status": f.status,
                    },
                )

    def get_configuration_summary(self):
        """Get a complete summary of this configuration."""
        return {
            "fund": self.fund_master,
            "regulatory": self.regulatory_category,
            "currencies": {
                "base": self.base_currency,
                "reporting": self.reporting_currency,
            },
            "managers": {
                "fund_manager": self.fund_manager,
                "portfolio_manager": self.portfolio_manager,
                "compliance_officer": self.compliance_officer,
            },
            "share_classes": [s.share_class for s in self.share_classes_table],
            "series": [s.fund_series for s in self.active_series_table],
            "fees": [f.fee_structure for f in self.active_fee_structures],
            "operations": {
                "nav_frequency": self.nav_frequency,
                "cutoff_equity": self.cut_off_time_equity,
                "cutoff_debt": self.cut_off_time_debt,
                "settlement_equity": self.settlement_cycle_equity,
                "settlement_debt": self.settlement_cycle_debt,
            },
        }


@frappe.whitelist()
def get_fund_configuration(fund_master):
    """API: Get the active configuration for a fund."""
    config = frappe.get_all(
        "Fund Configuration",
        filters={
            "fund_master": fund_master,
            "status": "Active",
        },
        fields=["name", "configuration_name", "effective_from", "version"],
        order_by="effective_from desc",
        limit=1,
    )
    if config:
        return frappe.get_doc("Fund Configuration", config[0].name)
    return None
