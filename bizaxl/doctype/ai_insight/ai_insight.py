# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class AIInsight(Document):
    """AI-powered portfolio insights, risk alerts, and recommendations."""

    def validate(self):
        self.set_defaults()
        self.validate_priority()

    def set_defaults(self):
        if not self.generated_date:
            self.generated_date = now_datetime()
        if not self.status:
            self.status = "New"

    def validate_priority(self):
        if self.urgency == "Today" and self.priority not in ("High", "Critical"):
            frappe.msgprint(
                "Consider setting priority to High or Critical for 'Today' urgency.",
                alert=True,
            )

    def before_submit(self):
        if self.status == "New":
            self.status = "Reviewed"


@frappe.whitelist()
def generate_portfolio_insights(fund_master):
    """API: Generate AI-powered insights for a fund based on current data."""
    insights = []

    # 1. Concentration risk insight
    _check_concentration_risk(fund_master, insights)

    # 2. Performance decline insight
    _check_performance_decline(fund_master, insights)

    # 3. Rebalancing opportunity insight
    _check_rebalancing_opportunity(fund_master, insights)

    # 4. Tax-loss harvesting insight
    _check_tax_harvesting(fund_master, insights)

    # 5. Fee analysis insight
    _check_fee_analysis(fund_master, insights)

    created = []
    for insight_data in insights:
        doc = frappe.get_doc({
            "doctype": "AI Insight",
            "fund_master": fund_master,
            "generated_date": now_datetime(),
            "status": "New",
            **insight_data,
        })
        doc.insert()
        created.append(doc.name)

    return {"fund_master": fund_master, "insights_created": len(created), "insights": created}


def _check_concentration_risk(fund_master, insights):
    """Check if any single holding exceeds 15% of portfolio."""
    total_value = 0
    holdings = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["security_name", "market_value"],
    )
    total_value = sum(flt(h["market_value"]) for h in holdings)
    if not total_value:
        return

    for h in holdings:
        pct = (flt(h["market_value"]) / total_value) * 100
        if pct > 15:
            insights.append({
                "insight_category": "Portfolio Health",
                "insight_type": "Pattern Detection",
                "title": "Concentration Risk Detected",
                "summary": f"{h['security_name']} represents {pct:.1f}% of the portfolio, exceeding the 15% threshold.",
                "priority": "High" if pct > 25 else "Medium",
                "urgency": "This Week" if pct > 25 else "This Month",
                "recommendation": f"Consider reducing {h['security_name']} position to mitigate concentration risk.",
                "recommended_action": "Reduce Exposure",
                "confidence_score": 85,
                "impact_score": min(pct, 100),
                "source": "AI Engine",
            })


def _check_performance_decline(fund_master, insights):
    """Check if recent NAV performance shows concerning decline."""
    navs = frappe.get_all(
        "NAV History",
        filters={"fund_master": fund_master, "docstatus": 1},
        fields=["nav_date", "nav_change_percentage"],
        order_by="nav_date desc",
        limit=10,
    )
    negative_streak = 0
    for n in navs:
        if flt(n.get("nav_change_percentage", 0)) < -2:
            negative_streak += 1
        else:
            break

    if negative_streak >= 3:
        insights.append({
            "insight_category": "Risk Alert",
            "insight_type": "Anomaly Detection",
            "title": "Sustained NAV Decline",
            "summary": f"NAV has declined more than 2% for {negative_streak} consecutive periods.",
            "priority": "High",
            "urgency": "Today",
            "recommendation": "Review portfolio holdings and market conditions. Consider hedging or reducing exposure to declining sectors.",
            "recommended_action": "Review Only",
            "confidence_score": 75,
            "impact_score": 70,
            "source": "AI Engine",
        })


def _check_rebalancing_opportunity(fund_master, insights):
    """Check if any asset class has drifted significantly from target."""
    holdings = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["asset_class", "market_value"],
    )
    total = sum(flt(h["market_value"]) for h in holdings)
    if not total:
        return

    allocation = {}
    for h in holdings:
        ac = h.get("asset_class") or "Unclassified"
        pct = (flt(h["market_value"]) / total) * 100
        allocation[ac] = allocation.get(ac, 0) + pct

    for ac, pct in allocation.items():
        # Simplified: flag if any asset class > 60% (indicating over-concentration)
        if pct > 60:
            insights.append({
                "insight_category": "Rebalancing",
                "insight_type": "Automated Analysis",
                "title": f"Rebalancing Opportunity: {ac}",
                "summary": f"{ac} allocation is at {pct:.1f}%, which may exceed target allocation.",
                "priority": "Medium",
                "urgency": "This Month",
                "recommendation": f"Consider rebalancing by reducing {ac} allocation and increasing other asset classes.",
                "recommended_action": "Rebalance Portfolio",
                "confidence_score": 80,
                "impact_score": 50,
                "source": "AI Engine",
            })


def _check_tax_harvesting(fund_master, insights):
    """Check for tax-loss harvesting opportunities."""
    losers = frappe.get_all(
        "Holdings Register",
        filters={"fund_master": fund_master, "status": "Active", "unrealized_pnl": ["<", 0]},
        fields=["security_name", "unrealized_pnl", "market_value"],
        order_by="unrealized_pnl asc",
        limit=5,
    )
    if losers:
        total_loss = sum(abs(flt(l["unrealized_pnl"])) for l in losers)
        if total_loss > 10000:
            names = ", ".join(l["security_name"] for l in losers[:3])
            insights.append({
                "insight_category": "Tax Optimization",
                "insight_type": "Automated Analysis",
                "title": "Tax-Loss Harvesting Opportunity",
                "summary": f"Identified {len(losers)} holdings with total unrealized loss of {total_loss:,.0f}. Top: {names}.",
                "priority": "Medium",
                "urgency": "This Month",
                "recommendation": "Consider harvesting losses to offset capital gains. Ensure wash-sale rules are considered.",
                "recommended_action": "Tax Harvest",
                "confidence_score": 70,
                "impact_score": 60,
                "source": "AI Engine",
            })


def _check_fee_analysis(fund_master, insights):
    """Check if fee accruals are within expected ranges."""
    fees = frappe.get_all(
        "Fee Accrual",
        filters={"fund_master": fund_master},
        fields=["fee_type", "sum(gross_fee_amount) as total"],
        group_by="fee_type",
    )
    aum = frappe.get_value("Fund Master", fund_master, "aum_current") or 0
    if fees and aum > 0:
        for f in fees:
            fee_pct = (flt(f["total"]) / aum) * 100
            if fee_pct > 2.5:
                insights.append({
                    "insight_category": "Performance Insight",
                    "insight_type": "Automated Analysis",
                    "title": f"Elevated {f['fee_type']} Detected",
                    "summary": f"{f['fee_type']} of {flt(f['total']):,.0f} represents {fee_pct:.2f}% of AUM.",
                    "priority": "Medium",
                    "urgency": "This Month",
                    "recommendation": f"Review {f['fee_type']} structure. Consider negotiating or optimizing fee arrangements.",
                    "recommended_action": "Review Only",
                    "confidence_score": 65,
                    "impact_score": 40,
                    "source": "AI Engine",
                })


@frappe.whitelist()
def get_active_insights(fund_master=None, priority=None, category=None):
    """API: Get active (non-dismissed) insights with optional filters."""
    filters = {"status": ["!=", "Dismissed"]}
    if fund_master:
        filters["fund_master"] = fund_master
    if priority:
        filters["priority"] = priority
    if category:
        filters["insight_category"] = category

    return frappe.get_all(
        "AI Insight",
        filters=filters,
        fields=[
            "name", "insight_category", "title", "summary",
            "priority", "urgency", "status", "generated_date",
            "confidence_score", "impact_score", "recommended_action",
        ],
        order_by="priority desc, generated_date desc",
    )


@frappe.whitelist()
def dismiss_insight(insight_name, action_notes=None):
    """API: Dismiss an AI insight with optional action notes."""
    doc = frappe.get_doc("AI Insight", insight_name)
    doc.status = "Dismissed"
    if action_notes:
        doc.action_taken = action_notes
        doc.action_date = now_datetime()
    doc.flags.ignore_permissions = True
    doc.save()
    return {"status": "dismissed", "insight": insight_name}


@frappe.whitelist()
def get_insight_dashboard(fund_master):
    """API: Get AI insight dashboard summary."""
    total = frappe.db.count("AI Insight", filters={"fund_master": fund_master})
    by_priority = frappe.get_all(
        "AI Insight",
        filters={"fund_master": fund_master},
        fields=["priority", "count(*) as count"],
        group_by="priority",
    )
    by_category = frappe.get_all(
        "AI Insight",
        filters={"fund_master": fund_master},
        fields=["insight_category", "count(*) as count"],
        group_by="insight_category",
    )
    active = frappe.db.count(
        "AI Insight",
        filters={"fund_master": fund_master, "status": ["!=", "Dismissed"]},
    )
    high_priority = frappe.db.count(
        "AI Insight",
        filters={"fund_master": fund_master, "status": ["!=", "Dismissed"], "priority": ["in", ("High", "Critical")]},
    )

    return {
        "total_insights": total,
        "active_insights": active,
        "high_priority_active": high_priority,
        "by_priority": by_priority,
        "by_category": by_category,
    }
