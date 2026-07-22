# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 10 API Endpoints — Family Office & Wealth Management."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# FAMILY OFFICE MASTER APIs
# =============================================================================

@frappe.whitelist()
def create_family_office(family_name, family_type, principal_name=None, **kwargs):
    """Create a new family office entity."""
    doc = frappe.get_doc({
        "doctype": "Family Office Master",
        "family_name": family_name,
        "family_code": kwargs.get("family_code"),
        "family_type": family_type,
        "office_type": kwargs.get("office_type", "Full Service"),
        "principal_name": principal_name,
        "status": "Active",
    })
    doc.insert()
    return doc


@frappe.whitelist()
def get_family_office_view(family_office_name):
    """Get complete family office overview with all linked data."""
    from bizaxl.bizaxl.doctype.family_office_master.family_office_master import (
        get_family_overview,
    )

    return get_family_overview(family_office_name)


@frappe.whitelist()
def list_family_offices():
    """List all family offices."""
    return frappe.get_all(
        "Family Office Master",
        fields=["name", "family_name", "family_code", "family_type", "status", "total_estimated_wealth"],
        order_by="family_name asc",
    )


@frappe.whitelist()
def add_family_member(family_office, member_name, entity_type="Individual", relationship="Other", **kwargs):
    """Add a member to a family office."""
    fo = frappe.get_doc("Family Office Master", family_office)
    fo.append("family_members", {
        "member_name": member_name,
        "entity_type": entity_type,
        "relationship": relationship,
        "generation": kwargs.get("generation"),
        "date_of_birth": kwargs.get("date_of_birth"),
        "percentage_ownership": flt(kwargs.get("percentage_ownership", 0)),
        "notes": kwargs.get("notes"),
    })
    fo.flags.ignore_permissions = True
    fo.save()
    return fo


# =============================================================================
# CONSOLIDATED PORTFOLIO APIs
# =============================================================================

@frappe.whitelist()
def get_wealth_summary(family_office_name):
    """Get wealth allocation summary by asset class."""
    from bizaxl.bizaxl.doctype.consolidated_portfolio.consolidated_portfolio import (
        get_wealth_allocation,
    )

    return get_wealth_allocation(family_office_name)


@frappe.whitelist()
def add_asset_to_portfolio(family_office, asset_class, security_name, estimated_value, **kwargs):
    """Add an asset to the consolidated portfolio."""
    from bizaxl.bizaxl.doctype.consolidated_portfolio.consolidated_portfolio import (
        add_portfolio_item,
    )

    return add_portfolio_item(family_office, asset_class, security_name, estimated_value, **kwargs)


@frappe.whitelist()
def get_portfolio_by_entity(family_office_name, holding_entity):
    """Get assets held by a specific entity within the family office."""
    return frappe.get_all(
        "Consolidated Portfolio",
        filters={"family_office": family_office_name, "holding_entity": holding_entity, "status": "Active"},
        fields=["asset_class", "security_name", "total_estimated_value", "cost_basis", "unrealized_gain_loss"],
        order_by="total_estimated_value desc",
    )


# =============================================================================
# TAX OPTIMIZATION APIs
# =============================================================================

@frappe.whitelist()
def get_tax_overview(family_office_name, fiscal_year=None):
    """Get tax optimization summary."""
    from bizaxl.bizaxl.doctype.tax_optimization_plan.tax_optimization_plan import (
        get_tax_summary,
    )

    return get_tax_summary(family_office_name, fiscal_year)


@frappe.whitelist()
def create_tax_plan(family_office, plan_name, fiscal_year, plan_type, **kwargs):
    """Create a new tax optimization plan."""
    doc = frappe.get_doc({
        "doctype": "Tax Optimization Plan",
        "family_office": family_office,
        "plan_name": plan_name,
        "fiscal_year": fiscal_year,
        "plan_type": plan_type,
        "stcg_realized": flt(kwargs.get("stcg_realized", 0)),
        "ltcg_realized": flt(kwargs.get("ltcg_realized", 0)),
        "estimated_savings": flt(kwargs.get("estimated_savings", 0)),
        "status": "Draft",
    })
    doc.insert()
    return doc


# =============================================================================
# SUCCESSION PLANNING APIs
# =============================================================================

@frappe.whitelist()
def get_succession_overview(family_office_name):
    """Get succession planning summary."""
    from bizaxl.bizaxl.doctype.succession_plan.succession_plan import (
        get_succession_summary,
    )

    return get_succession_summary(family_office_name)


@frappe.whitelist()
def create_succession_plan(family_office, plan_name, plan_type, **kwargs):
    """Create a new succession/estate plan."""
    doc = frappe.get_doc({
        "doctype": "Succession Plan",
        "family_office": family_office,
        "plan_name": plan_name,
        "plan_type": plan_type,
        "plan_status": "Draft",
        "effective_date": kwargs.get("effective_date"),
        "last_review_date": kwargs.get("last_review_date", today()),
        "next_review_date": kwargs.get("next_review_date"),
        "legal_advisor_name": kwargs.get("legal_advisor_name"),
    })
    doc.insert()
    return doc


# =============================================================================
# CONSOLIDATED FAMILY OFFICE DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_family_wealth_dashboard(family_office_name):
    """Get comprehensive family wealth dashboard."""
    fo = frappe.get_doc("Family Office Master", family_office_name)

    wealth = frappe.get_all(
        "Consolidated Portfolio",
        filters={"family_office": family_office_name, "status": "Active"},
        fields=["asset_class", "sum(total_estimated_value) as value"],
        group_by="asset_class",
    )

    tax = frappe.get_all(
        "Tax Optimization Plan",
        filters={"family_office": family_office_name},
        fields=["sum(estimated_savings) as total_savings"],
    )

    succession = frappe.get_all(
        "Succession Plan",
        filters={"family_office": family_office_name},
        fields=["count(*) as count"],
    )

    total_wealth = sum(flt(w["value"]) for w in wealth)

    return {
        "family_office": family_office_name,
        "family_name": fo.family_name,
        "total_members": fo.total_members,
        "generations_tracked": fo.generations_tracked,
        "total_wealth": total_wealth,
        "wealth_by_asset_class": wealth,
        "tax_savings": tax[0].total_savings if tax else 0,
        "succession_plans": succession[0].count if succession else 0,
        "portfolio_count": frappe.db.count(
            "Consolidated Portfolio",
            filters={"family_office": family_office_name, "status": "Active"},
        ),
    }


@frappe.whitelist()
def get_wealth_trend(family_office_name):
    """Get wealth trend data across all asset classes."""
    portfolios = frappe.get_all(
        "Consolidated Portfolio",
        filters={"family_office": family_office_name, "status": "Active"},
        fields=["asset_class", "total_estimated_value", "cost_basis", "unrealized_gain_loss", "valuation_date"],
    )

    total_value = sum(flt(p["total_estimated_value"]) for p in portfolios)
    total_cost = sum(flt(p["cost_basis"]) for p in portfolios)
    total_gain = sum(flt(p["unrealized_gain_loss"]) for p in portfolios)

    return {
        "total_value": total_value,
        "total_cost_basis": total_cost,
        "net_unrealized_gain": total_gain,
        "return_percentage": (total_gain / total_cost * 100) if total_cost else 0,
        "asset_breakdown": [
            {
                "asset_class": p["asset_class"],
                "value": p["total_estimated_value"],
                "cost": p["cost_basis"],
                "gain_loss": p["unrealized_gain_loss"],
            }
            for p in portfolios
        ],
    }
