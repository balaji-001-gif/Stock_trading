# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, now_datetime


class MISReport(Document):
    """MIS report configuration and generation engine."""

    def validate(self):
        self.validate_schedule()
        self.validate_parameters()

    def validate_schedule(self):
        if self.schedule_enabled and not self.schedule_frequency:
            frappe.throw("Schedule frequency is required when auto-schedule is enabled.")
        if self.schedule_enabled and not self.next_run_date:
            self.next_run_date = today()

    def validate_parameters(self):
        if self.parameters_json:
            try:
                json.loads(self.parameters_json)
            except json.JSONDecodeError:
                frappe.throw("Parameters must be valid JSON.")

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Scheduled"

    def generate_report(self):
        """Generate the MIS report by aggregating data from relevant modules."""
        try:
            data = self._collect_report_data()
            output = self._format_output(data)

            self.report_output = output
            self.generated_on = now_datetime()
            self.last_run_date = now_datetime()
            self.last_run_by = frappe.session.user
            self.status = "Generated"
            self.save()

            return {"status": "success", "report_name": self.name, "generated_on": str(self.generated_on)}
        except Exception as e:
            self.status = "Failed"
            self.error_log = str(e)
            self.save()
            frappe.throw(f"Report generation failed: {str(e)}")

    def _collect_report_data(self):
        """Collect data based on report category."""
        fund = self.fund_master
        category = self.report_category

        if category == "Fund Performance":
            return self._get_performance_data(fund)
        elif category == "Investor Reporting":
            return self._get_investor_data(fund)
        elif category == "Risk & Analytics":
            return self._get_risk_data(fund)
        elif category == "Fee & Income":
            return self._get_fee_data(fund)
        elif category == "Portfolio Holdings":
            return self._get_holdings_data(fund)
        elif category == "Regulatory Compliance":
            return self._get_compliance_data(fund)
        elif category == "Tax Reporting":
            return self._get_tax_data(fund)
        elif category == "Advisor Dashboard":
            return self._get_advisor_data(fund)
        else:
            return {"message": "Custom report — no automatic data collection."}

    def _get_performance_data(self, fund):
        nav = frappe.get_all(
            "NAV History",
            filters={"fund_master": fund, "docstatus": 1},
            fields=["nav_date", "nav", "nav_change_percentage", "total_aum"],
            order_by="nav_date desc",
            limit=30,
        )
        pnl = frappe.get_all(
            "PNL Attribution",
            filters={"fund_master": fund},
            fields=["pnl_type", "sum(gross_realized_pnl) as total"],
            group_by="pnl_type",
        )
        return {"nav_history": nav, "pnl_summary": pnl}

    def _get_investor_data(self, fund):
        investors = frappe.get_all(
            "Investor Profile",
            fields=["name", "first_name", "last_name", "investor_category", "kyc_status", "status"],
            order_by="creation desc",
        )
        return {"total_investors": len(investors), "investors": investors}

    def _get_risk_data(self, fund):
        risk = frappe.get_all(
            "Risk Analytics",
            filters={"fund_master": fund},
            fields=["*"],
            order_by="calculation_date desc",
            limit=1,
        )
        return {"latest_risk_metrics": risk[0] if risk else None}

    def _get_fee_data(self, fund):
        fees = frappe.get_all(
            "Fee Accrual",
            filters={"fund_master": fund},
            fields=["fee_type", "sum(gross_fee_amount) as total_gross", "sum(net_fee_amount) as total_net"],
            group_by="fee_type",
        )
        return {"fee_breakdown": fees}

    def _get_holdings_data(self, fund):
        holdings = frappe.get_all(
            "Holdings Register",
            filters={"fund_master": fund, "status": "Active"},
            fields=["security_name", "asset_class", "total_quantity", "market_value", "unrealized_pnl"],
            order_by="market_value desc",
        )
        total = sum(flt(h["market_value"]) for h in holdings)
        return {"holdings": holdings, "total_portfolio_value": total}

    def _get_compliance_data(self, fund):
        filings = frappe.get_all(
            "SEBI Report",
            filters={"fund_master": fund},
            fields=["report_type", "filing_status", "due_date", "filing_date"],
            order_by="due_date desc",
            limit=20,
        )
        return {"compliance_filings": filings}

    def _get_tax_data(self, fund):
        tds = frappe.get_all(
            "TDS Computation",
            filters={"fund_master": fund},
            fields=["transaction_type", "sum(total_tds) as total_tds", "sum(net_amount) as total_net"],
            group_by="transaction_type",
        )
        return {"tds_summary": tds}

    def _get_advisor_data(self, fund):
        performance = self._get_performance_data(fund)
        risk = self._get_risk_data(fund)
        return {"performance": performance, "risk": risk}

    def _format_output(self, data):
        import json
        return json.dumps(data, indent=2, default=str)


@frappe.whitelist()
def generate_mis_report(report_name):
    """API: Generate an MIS report."""
    doc = frappe.get_doc("MIS Report", report_name)
    return doc.generate_report()


@frappe.whitelist()
def get_scheduled_reports(fund_master=None):
    """API: Get all scheduled reports."""
    filters = {"status": "Scheduled", "schedule_enabled": 1}
    if fund_master:
        filters["fund_master"] = fund_master
    return frappe.get_all(
        "MIS Report",
        filters=filters,
        fields=["name", "report_name", "report_category", "schedule_frequency", "next_run_date", "last_run_date"],
        order_by="next_run_date asc",
    )


@frappe.whitelist()
def get_recent_reports(fund_master=None, limit=20):
    """API: Get recently generated reports."""
    filters = {"status": "Generated"}
    if fund_master:
        filters["fund_master"] = fund_master
    return frappe.get_all(
        "MIS Report",
        filters=filters,
        fields=["name", "report_name", "report_category", "generated_on", "last_run_by", "report_format"],
        order_by="generated_on desc",
        limit_page_length=limit,
    )
