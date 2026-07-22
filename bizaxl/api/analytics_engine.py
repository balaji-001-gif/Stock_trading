# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 9 API Endpoints — MIS, Analytics & Mobile."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# MIS REPORT APIs
# =============================================================================

@frappe.whitelist()
def create_mis_report(report_name, report_category, fund_master=None, **kwargs):
    """Create a new MIS report configuration."""
    doc = frappe.get_doc({
        "doctype": "MIS Report",
        "report_name": report_name,
        "report_category": report_category,
        "fund_master": fund_master,
        "report_type": kwargs.get("report_type", "Summary"),
        "report_format": kwargs.get("report_format", "PDF"),
        "frequency": kwargs.get("frequency", "On-Demand"),
        "status": "Draft",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def run_report(report_name):
    """Execute an MIS report and generate output."""
    from bizaxl.bizaxl.doctype.mis_report.mis_report import generate_mis_report

    return generate_mis_report(report_name)


@frappe.whitelist()
def list_reports(fund_master=None, category=None, limit=50):
    """List MIS reports with optional filters."""
    filters = {}
    if fund_master:
        filters["fund_master"] = fund_master
    if category:
        filters["report_category"] = category

    return frappe.get_all(
        "MIS Report",
        filters=filters,
        fields=[
            "name", "report_name", "report_category", "report_type",
            "frequency", "status", "generated_on", "last_run_date",
        ],
        order_by="modified desc",
        limit_page_length=limit,
    )


@frappe.whitelist()
def schedule_report(report_name, schedule_frequency, next_run_date):
    """Schedule a report for automatic generation."""
    doc = frappe.get_doc("MIS Report", report_name)
    doc.schedule_enabled = 1
    doc.schedule_frequency = schedule_frequency
    doc.next_run_date = next_run_date
    doc.status = "Scheduled"
    doc.flags.ignore_permissions = True
    doc.save()
    return {"status": "scheduled", "report": report_name, "next_run": str(next_run_date)}


# =============================================================================
# PERFORMANCE ATTRIBUTION APIs
# =============================================================================

@frappe.whitelist()
def run_attribution(fund_master, attribution_date=None, period="Monthly"):
    """Run performance attribution analysis for a fund."""
    from bizaxl.bizaxl.doctype.performance_attribution.performance_attribution import (
        calculate_attribution,
    )

    return calculate_attribution(fund_master, attribution_date, period)


@frappe.whitelist()
def get_performance_trend(fund_master):
    """Get performance attribution trend data."""
    from bizaxl.bizaxl.doctype.performance_attribution.performance_attribution import (
        get_performance_summary,
    )

    return get_performance_summary(fund_master)


@frappe.whitelist()
def attribution_history(fund_master, limit=12):
    """Get performance attribution history."""
    from bizaxl.bizaxl.doctype.performance_attribution.performance_attribution import (
        get_attribution_history,
    )

    return get_attribution_history(fund_master, limit)


# =============================================================================
# RISK ANALYTICS APIs
# =============================================================================

@frappe.whitelist()
def compute_risk(fund_master, calculation_date=None):
    """Compute comprehensive risk metrics for a fund."""
    from bizaxl.bizaxl.doctype.risk_analytics.risk_analytics import compute_risk_metrics

    return compute_risk_metrics(fund_master, calculation_date)


@frappe.whitelist()
def get_risk_overview(fund_master):
    """Get latest risk metrics overview for dashboards."""
    from bizaxl.bizaxl.doctype.risk_analytics.risk_analytics import get_risk_summary

    return get_risk_summary(fund_master)


@frappe.whitelist()
def risk_metric_trend(fund_master, metric="sharpe_ratio", limit=12):
    """Get trend data for a specific risk metric."""
    from bizaxl.bizaxl.doctype.risk_analytics.risk_analytics import get_risk_trend

    return get_risk_trend(fund_master, metric, limit)


# =============================================================================
# AI INSIGHT APIs
# =============================================================================

@frappe.whitelist()
def generate_insights(fund_master):
    """Generate AI-powered portfolio insights."""
    from bizaxl.bizaxl.doctype.ai_insight.ai_insight import generate_portfolio_insights

    return generate_portfolio_insights(fund_master)


@frappe.whitelist()
def get_insight_feed(fund_master=None, priority=None, category=None):
    """Get active AI insights feed."""
    from bizaxl.bizaxl.doctype.ai_insight.ai_insight import get_active_insights

    return get_active_insights(fund_master, priority, category)


@frappe.whitelist()
def dismiss_insight(insight_name, action_notes=None):
    """Dismiss an AI insight."""
    from bizaxl.bizaxl.doctype.ai_insight.ai_insight import dismiss_insight as _dismiss

    return _dismiss(insight_name, action_notes)


@frappe.whitelist()
def get_insight_dashboard(fund_master):
    """Get AI insight dashboard analytics."""
    from bizaxl.bizaxl.doctype.ai_insight.ai_insight import get_insight_dashboard as _dashboard

    return _dashboard(fund_master)


# =============================================================================
# CONSOLIDATED ANALYTICS DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_analytics_dashboard(fund_master):
    """Get the full analytics dashboard — risk, performance, insights, and reports."""
    from bizaxl.bizaxl.doctype.risk_analytics.risk_analytics import get_risk_summary
    from bizaxl.bizaxl.doctype.performance_attribution.performance_attribution import (
        get_performance_summary,
    )
    from bizaxl.bizaxl.doctype.ai_insight.ai_insight import get_active_insights

    return {
        "fund_master": fund_master,
        "risk_metrics": get_risk_summary(fund_master),
        "performance": get_performance_summary(fund_master),
        "active_insights": get_active_insights(fund_master),
        "recent_reports": frappe.get_all(
            "MIS Report",
            filters={"fund_master": fund_master, "status": "Generated"},
            fields=["name", "report_name", "report_category", "generated_on"],
            order_by="generated_on desc",
            limit=10,
        ),
    }


@frappe.whitelist()
def get_advisory_dashboard(fund_master):
    """Get advisor-facing dashboard with actionable recommendations."""
    from bizaxl.bizaxl.doctype.risk_analytics.risk_analytics import get_risk_summary
    from bizaxl.bizaxl.doctype.performance_attribution.performance_attribution import (
        get_performance_summary,
    )
    from bizaxl.bizaxl.doctype.ai_insight.ai_insight import get_active_insights

    risk = get_risk_summary(fund_master)
    performance = get_performance_summary(fund_master)
    insights = get_active_insights(fund_master, priority="High")

    # Holdings with red flags
    over_allocated = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["security_name", "market_value", "unrealized_pnl"],
        order_by="market_value desc",
    )
    navs = frappe.get_all(
        "NAV History",
        filters={"fund_master": fund_master, "docstatus": 1},
        fields=["nav", "nav_date", "nav_change_percentage"],
        order_by="nav_date desc",
        limit=3,
    )

    return {
        "fund_master": fund_master,
        "latest_navs": navs,
        "risk_overview": risk,
        "performance_overview": performance.get("latest"),
        "recommendations": insights[:5] if insights else [],
        "holdings": over_allocated,
    }
