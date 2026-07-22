# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""Module 5 API Endpoints — Fee & Income Engine."""

import frappe
from frappe.utils import flt, today


# =============================================================================
# FEE ACCRUAL APIs
# =============================================================================

@frappe.whitelist()
def accrue_monthly_fee(fund_master, fee_type="Management Fee", year=None, month=None):
    """Accrue management/performance/carry fees for a fund for a given month."""
    from bizaxl.bizaxl.doctype.fee_accrual.fee_accrual import calculate_monthly_fee

    return calculate_monthly_fee(fund_master, fee_type, year, month)


@frappe.whitelist()
def get_fee_summary(fund_master, from_date=None, to_date=None):
    """Get fee accrual summary for a fund over a period."""
    from bizaxl.bizaxl.doctype.fee_accrual.fee_accrual import get_fee_accruals

    return get_fee_accruals(fund_master, from_date, to_date)


@frappe.whitelist()
def get_fee_dashboard(fund_master):
    """Get aggregated fee dashboard for a fund."""
    from bizaxl.bizaxl.doctype.fee_accrual.fee_accrual import get_fee_accruals

    accruals = get_fee_accruals(fund_master)

    total_gross = sum(flt(a.get("gross_fee_amount", 0)) for a in accruals)
    total_net = sum(flt(a.get("net_fee_amount", 0)) for a in accruals)
    total_waiver = sum(flt(a.get("waiver_amount", 0)) for a in accruals)

    fee_type_breakdown = frappe.get_all(
        "Fee Accrual",
        filters={"fund_master": fund_master},
        fields=[
            "fee_type", "sum(gross_fee_amount) as total_gross",
            "sum(net_fee_amount) as total_net",
        ],
        group_by="fee_type",
    )

    # Get active fee structures
    fee_structures = frappe.get_all(
        "Fee Structure",
        filters={"fund_master": fund_master, "status": "Active"},
        fields=["fee_name", "fee_type", "management_fee_rate", "performance_fee_rate"],
    )

    return {
        "fund_master": fund_master,
        "total_gross_fees": total_gross,
        "total_net_fees": total_net,
        "total_waivers": total_waiver,
        "fee_type_breakdown": fee_type_breakdown,
        "active_fee_structures": fee_structures,
        "accrual_count": len(accruals),
    }


# =============================================================================
# CARRIED INTEREST / WATERFALL APIs
# =============================================================================

@frappe.whitelist()
def run_waterfall(fund_master, total_distributable, waterfall_date=None):
    """Run a new waterfall distribution calculation for a fund."""
    from bizaxl.bizaxl.doctype.carried_interest_waterfall.carried_interest_waterfall import (
        calculate_waterfall,
    )

    return calculate_waterfall(fund_master, total_distributable, waterfall_date)


@frappe.whitelist()
def get_waterfall_summary(fund_master):
    """Get waterfall distribution history for a fund."""
    from bizaxl.bizaxl.doctype.carried_interest_waterfall.carried_interest_waterfall import (
        get_waterfall_history,
    )

    return get_waterfall_history(fund_master)


@frappe.whitelist()
def get_waterfall_detail(waterfall_name):
    """Get detailed waterfall breakdown with all tiers."""
    wf = frappe.get_doc("Carried Interest Waterfall", waterfall_name)
    return {
        "name": wf.name,
        "waterfall_date": wf.waterfall_date,
        "waterfall_type": wf.waterfall_type,
        "total_committed_capital": wf.total_committed_capital,
        "total_distributable": wf.total_distributable,
        "return_of_capital": wf.return_of_capital,
        "preferred_return_amount": wf.preferred_return_amount,
        "catch_up_amount": wf.catch_up_amount,
        "lp_carry_amount": wf.lp_carry_amount,
        "gp_carry_amount": wf.gp_carry_amount,
        "total_distributed": wf.total_distributed,
        "remaining_for_distribution": wf.remaining_for_distribution,
        "total_profits": wf.total_profits,
        "gross_irr": wf.gross_irr,
        "net_irr_to_lps": wf.net_irr_to_lps,
        "status": wf.status,
        "tiers": [
            {
                "tier_number": t.tier_number,
                "tier_name": t.tier_name,
                "tier_type": t.tier_type,
                "amount": t.amount,
                "cumulative_amount": t.cumulative_amount,
                "recipient": t.recipient,
                "description": t.description,
            }
            for t in wf.waterfall_tiers
        ],
    }


# =============================================================================
# TDS COMPUTATION APIs
# =============================================================================

@frappe.whitelist()
def compute_tds_deduction(gross_amount, tds_rate, surcharge_rate=0, cess_rate=4):
    """Compute TDS/withholding tax without creating a document."""
    from bizaxl.bizaxl.doctype.tds_computation.tds_computation import compute_tds

    return compute_tds(gross_amount, tds_rate, surcharge_rate, cess_rate)


@frappe.whitelist()
def get_tds_report(fund_master, fiscal_year=None):
    """Get TDS report for a fund, grouped by transaction type."""
    from bizaxl.bizaxl.doctype.tds_computation.tds_computation import get_tds_summary

    return get_tds_summary(fund_master, fiscal_year)


@frappe.whitelist()
def record_tds_deduction(fund_master, transaction_type, gross_amount, tds_rate, **kwargs):
    """Record a TDS deduction against a payment or distribution."""
    doc = frappe.get_doc({
        "doctype": "TDS Computation",
        "fund_master": fund_master,
        "transaction_type": transaction_type,
        "gross_amount": flt(gross_amount),
        "tds_rate": flt(tds_rate),
        "surcharge_rate": flt(kwargs.get("surcharge_rate", 0)),
        "cess_rate": flt(kwargs.get("cess_rate", 4)),
        "section_code": kwargs.get("section_code", "194K"),
        "tds_deposit_status": "Unpaid",
        "tds_filing_status": "Not Filed",
    })
    doc.insert()
    doc.submit()
    return doc


# =============================================================================
# PERFORMANCE FEE APIs
# =============================================================================

@frappe.whitelist()
def crystallize_performance(fund_master, share_class, crystallization_date=None):
    """Crystallize performance fee for a fund share class."""
    from bizaxl.bizaxl.doctype.performance_fee_engine.performance_fee_engine import (
        crystallize_performance_fee,
    )

    return crystallize_performance_fee(fund_master, share_class, crystallization_date)


@frappe.whitelist()
def get_performance_fee_summary(fund_master, share_class=None):
    """Get performance fee history for a fund."""
    from bizaxl.bizaxl.doctype.performance_fee_engine.performance_fee_engine import (
        get_performance_fee_history,
    )

    return get_performance_fee_history(fund_master, share_class)


# =============================================================================
# CONSOLIDATED FEE & INCOME DASHBOARD
# =============================================================================

@frappe.whitelist()
def get_income_dashboard(fund_master):
    """Get consolidated income dashboard — fees, waterfall, and TDS."""
    from bizaxl.bizaxl.doctype.fee_accrual.fee_accrual import get_fee_accruals
    from bizaxl.bizaxl.doctype.carried_interest_waterfall.carried_interest_waterfall import (
        get_waterfall_history,
    )
    from bizaxl.bizaxl.doctype.performance_fee_engine.performance_fee_engine import (
        get_performance_fee_history,
    )
    from bizaxl.bizaxl.doctype.tds_computation.tds_computation import get_tds_summary

    return {
        "fund_master": fund_master,
        "fee_accruals": get_fee_accruals(fund_master),
        "waterfall_history": get_waterfall_history(fund_master),
        "performance_fees": get_performance_fee_history(fund_master),
        "tds_summary": get_tds_summary(fund_master),
    }
