# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class AIAnalyticsResult(Document):
    """Tracks AI/ML analytics run results — risk, tax harvesting, rebalancing, attribution."""
    pass


@frappe.whitelist()
def run_risk_analysis(fund_master=None, investor=None, lookback_months=12, risk_free_rate=6.5):
    """API: Run comprehensive risk metrics analysis."""
    from bizaxl.bizaxl.integrations.ai_ml_analytics import MLAnalyticsConnector

    connector = MLAnalyticsConnector()
    result = connector.calculate_risk_metrics(None, None, risk_free_rate, lookback_months)

    if result.get("status") != "Success":
        return result

    metrics = result.get("metrics", {})
    doc = frappe.get_doc({
        "doctype": "AI Analytics Result",
        "fund_master": fund_master,
        "investor": investor,
        "analysis_type": "Risk Metrics",
        "analysis_date": today(),
        "status": "Completed",
        "model_version": result.get("model_version"),
        "connector_mode": result.get("mode"),
        "result_summary": f"Sharpe: {metrics.get('sharpe_ratio')}, Alpha: {metrics.get('alpha')}%, Beta: {metrics.get('beta')}, VaR(95%): {metrics.get('var_95')}%",
        "result_detail": frappe.as_json(metrics),
        "risk_metrics_summary": frappe.as_json({
            "sharpe_ratio": metrics.get("sharpe_ratio"),
            "sortino_ratio": metrics.get("sortino_ratio"),
            "alpha": metrics.get("alpha"),
            "beta": metrics.get("beta"),
            "var_95": metrics.get("var_95"),
            "var_99": metrics.get("var_99"),
            "max_drawdown": metrics.get("max_drawdown"),
            "tracking_error": metrics.get("tracking_error"),
            "information_ratio": metrics.get("information_ratio"),
        }),
    })
    doc.insert()

    # Also store as AI Insight
    frappe.get_doc({
        "doctype": "AI Insight",
        "fund_master": fund_master,
        "investor": investor,
        "insight_category": "Risk Alert",
        "insight_type": "Automated Analysis",
        "generated_date": now_datetime(),
        "status": "New",
        "priority": "Medium",
        "source": "AI Engine",
        "title": f"Risk Metrics Analysis — Sharpe: {metrics.get('sharpe_ratio')}, VaR: {metrics.get('var_95')}%",
        "summary": doc.result_summary,
        "confidence_score": 85,
        "impact_score": 70,
    }).insert()

    return {
        "name": doc.name,
        "metrics": metrics,
    }


@frappe.whitelist()
def run_tax_harvest_analysis(investor, portfolio_value=None, tax_slab="30%"):
    """API: Find tax-loss harvesting opportunities."""
    from bizaxl.bizaxl.integrations.ai_ml_analytics import MLAnalyticsConnector

    # Fetch holdings
    holdings = frappe.get_all("Holdings Register",
        filters={"investor": investor} if investor else {},
        fields=["name", "security_name", "quantity", "cost_basis", "market_value"],
        limit_page_length=100,
    )

    connector = MLAnalyticsConnector()
    result = connector.find_tax_harvest_opportunities(holdings, portfolio_value, tax_slab)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "AI Analytics Result",
        "investor": investor,
        "analysis_type": "Tax Harvesting",
        "analysis_date": today(),
        "status": "Completed",
        "connector_mode": result.get("mode"),
        "result_summary": f"Found {result.get('opportunities_found')} opportunities, estimated tax savings: ₹{result.get('estimated_tax_savings', 0):,.0f}",
        "result_detail": frappe.as_json(result),
        "recommendations": frappe.as_json(result.get("recommendations", [])),
    })
    doc.insert()

    # Create AI Insight
    if result.get("opportunities_found", 0) > 0:
        frappe.get_doc({
            "doctype": "AI Insight",
            "investor": investor,
            "insight_category": "Tax Optimization",
            "insight_type": "Automated Analysis",
            "generated_date": now_datetime(),
            "status": "New",
            "priority": "High",
            "source": "AI Engine",
            "title": f"Tax-Loss Harvesting: {result.get('opportunities_found')} opportunities identified",
            "summary": f"Total harvestable loss: ₹{result.get('total_harvestable_loss', 0):,.0f}, Tax savings: ₹{result.get('estimated_tax_savings', 0):,.0f}",
            "confidence_score": 90,
            "impact_score": 80,
        }).insert()

    return {
        "name": doc.name,
        "opportunities_found": result.get("opportunities_found"),
        "estimated_tax_savings": result.get("estimated_tax_savings"),
        "opportunities": result.get("opportunities"),
    }


@frappe.whitelist()
def run_rebalancing_analysis(fund_master=None, investor=None, drift_threshold=5.0):
    """API: Run rebalancing analysis."""
    from bizaxl.bizaxl.integrations.ai_ml_analytics import MLAnalyticsConnector

    connector = MLAnalyticsConnector()
    result = connector.recommend_rebalance(None, None, drift_threshold)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "AI Analytics Result",
        "fund_master": fund_master,
        "investor": investor,
        "analysis_type": "Rebalancing",
        "analysis_date": today(),
        "status": "Completed",
        "connector_mode": result.get("mode"),
        "result_summary": f"Rebalancing {'required' if result.get('rebalance_required') else 'not required'}. Actions: {result.get('actions_required')}. Max drift: {result.get('max_drift')}%",
        "result_detail": frappe.as_json(result),
        "recommendations": frappe.as_json(result.get("rebalance_actions", [])),
    })
    doc.insert()

    if result.get("rebalance_required"):
        frappe.get_doc({
            "doctype": "AI Insight",
            "fund_master": fund_master,
            "investor": investor,
            "insight_category": "Rebalancing",
            "insight_type": "Automated Analysis",
            "generated_date": now_datetime(),
            "status": "New",
            "priority": "Medium",
            "source": "AI Engine",
            "title": f"Portfolio Rebalancing: {result.get('actions_required')} actions required",
            "summary": doc.result_summary,
            "confidence_score": 85,
            "impact_score": 65,
        }).insert()

    return {
        "name": doc.name,
        "rebalance_required": result.get("rebalance_required"),
        "actions": result.get("rebalance_actions"),
    }


@frappe.whitelist()
def run_performance_attribution(fund_master, sectors=None):
    """API: Run performance attribution analysis."""
    from bizaxl.bizaxl.integrations.ai_ml_analytics import MLAnalyticsConnector

    connector = MLAnalyticsConnector()
    result = connector.calculate_performance_attribution(None, None, sectors)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "AI Analytics Result",
        "fund_master": fund_master,
        "analysis_type": "Performance Attribution",
        "analysis_date": today(),
        "status": "Completed",
        "connector_mode": result.get("mode"),
        "result_summary": f"Total Return: {result.get('total_return')}%, Benchmark: {result.get('benchmark_return')}%, Excess: {result.get('excess_return')}%",
        "result_detail": frappe.as_json(result),
    })
    doc.insert()

    return {
        "name": doc.name,
        "total_return": result.get("total_return"),
        "excess_return": result.get("excess_return"),
        "allocation_effect": result.get("allocation_effect"),
        "selection_effect": result.get("selection_effect"),
    }


@frappe.whitelist()
def run_market_regime_analysis():
    """API: Detect current market regime."""
    from bizaxl.bizaxl.integrations.ai_ml_analytics import MLAnalyticsConnector

    connector = MLAnalyticsConnector()
    result = connector.detect_market_regime(None)

    if result.get("status") != "Success":
        return result

    doc = frappe.get_doc({
        "doctype": "AI Analytics Result",
        "analysis_type": "Market Regime",
        "analysis_date": today(),
        "status": "Completed",
        "connector_mode": result.get("mode"),
        "result_summary": f"Regime: {result.get('detected_regime')} (Confidence: {result.get('regime_confidence')}%)",
        "result_detail": frappe.as_json(result),
    })
    doc.insert()

    return {
        "name": doc.name,
        "regime": result.get("detected_regime"),
        "confidence": result.get("regime_confidence"),
        "indicators": result.get("indicators"),
    }


@frappe.whitelist()
def list_ai_analyses(analysis_type=None):
    """API: List AI analytics results."""
    filters = {}
    if analysis_type:
        filters["analysis_type"] = analysis_type

    return frappe.get_all(
        "AI Analytics Result",
        filters=filters,
        fields=["name", "analysis_type", "analysis_date", "status",
                "result_summary", "fund_master", "investor", "connector_mode"],
        order_by="analysis_date desc",
        limit_page_length=50,
    )
