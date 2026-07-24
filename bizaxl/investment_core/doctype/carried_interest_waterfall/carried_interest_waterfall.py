# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CarriedInterestWaterfall(Document):
    """Waterfall distribution engine — return capital, preferred return, catch-up, LP/GP split."""

    def validate(self):
        self.calculate_waterfall()

    def before_submit(self):
        if self.status == "Draft":
            self.status = "Calculated"

    def calculate_waterfall(self):
        """Execute the 4-tier waterfall calculation."""
        distributable = flt(self.total_distributable)
        committed = flt(self.total_committed_capital)

        # Guard against negative or zero distributions
        if distributable <= 0:
            self.total_distributed = 0
            self.remaining_for_distribution = 0
            self.return_of_capital = 0
            self.preferred_return_amount = 0
            self.catch_up_amount = 0
            self.lp_carry_amount = 0
            self.gp_carry_amount = 0
            self.total_profits = 0
            self.waterfall_tiers = []
            return

        remaining = distributable

        # Clear existing tiers
        self.waterfall_tiers = []
        cumulative = 0
        tier_number = 0

        # Tier 1: Return of Capital to LPs
        tier1_amount = min(remaining, committed)
        if tier1_amount > 0:
            tier_number += 1
            cumulative += tier1_amount
            self.append("waterfall_tiers", {
                "tier_number": tier_number,
                "tier_name": "Return of Capital",
                "tier_type": "Return of Capital",
                "amount": tier1_amount,
                "cumulative_amount": cumulative,
                "recipient": "LP (Limited Partners)",
                "description": f"100% to LPs until they receive {committed}",
            })
            remaining -= tier1_amount
        self.return_of_capital = tier1_amount

        # Tier 2: Preferred Return to LPs
        pref_rate = flt(self.get_preferred_return_rate())
        pref_amount = min(remaining, flt(committed) * (pref_rate / 100)) if pref_rate > 0 else 0
        if pref_amount > 0 and remaining > 0:
            tier_number += 1
            cumulative += pref_amount
            self.append("waterfall_tiers", {
                "tier_number": tier_number,
                "tier_name": "Preferred Return",
                "tier_type": "Preferred Return",
                "amount": pref_amount,
                "cumulative_amount": cumulative,
                "recipient": "LP (Limited Partners)",
                "description": f"Preferred return of {pref_rate}% to LPs",
            })
            remaining -= pref_amount
        self.preferred_return_amount = pref_amount

        # Tier 3: GP Catch-up
        gp_catchup_pct = flt(self.gp_share_percentage or 20)
        catchup_amount = 0
        if remaining > 0 and pref_amount > 0:
            catchup_amount = min(remaining, flt(pref_amount) * (gp_catchup_pct / (100 - gp_catchup_pct)))
            if catchup_amount > 0:
                tier_number += 1
                cumulative += catchup_amount
                self.append("waterfall_tiers", {
                    "tier_number": tier_number,
                    "tier_name": "GP Catch-up",
                    "tier_type": "GP Catch-up",
                    "amount": catchup_amount,
                    "cumulative_amount": cumulative,
                    "recipient": "GP (General Partner)",
                    "description": f"{gp_catchup_pct}% catch-up to GP",
                })
                remaining -= catchup_amount
        self.catch_up_amount = catchup_amount

        # Tier 4: LP/GP Split
        if remaining > 0:
            tier_number += 1
            lp_split = flt(self.lp_share_percentage or 80)
            gp_split = flt(self.gp_share_percentage or 20)
            lp_amount = remaining * (lp_split / 100)
            gp_amount = remaining * (gp_split / 100)

            cumulative += remaining
            self.append("waterfall_tiers", {
                "tier_number": tier_number,
                "tier_name": "LP/GP Split",
                "tier_type": "LP/GP Split",
                "amount": remaining,
                "cumulative_amount": cumulative,
                "recipient": "Both",
                "description": f"{lp_split}% to LP / {gp_split}% to GP",
            })

            self.lp_carry_amount = lp_amount
            self.gp_carry_amount = gp_amount
        else:
            self.lp_carry_amount = 0
            self.gp_carry_amount = 0

        self.total_distributed = cumulative
        self.remaining_for_distribution = flt(distributable) - cumulative
        self.total_profits = flt(distributable) - flt(committed)

        # Net IRR approximation
        if self.gross_irr:
            total_fees = flt(self.gp_carry_amount) + flt(self.catch_up_amount)
            self.net_irr_to_lps = flt(self.gross_irr) - (total_fees / flt(distributable) * 100) if distributable else 0

    def get_preferred_return_rate(self):
        """Get preferred return rate from linked fund series or fee structure."""
        if self.fund_series:
            rate = frappe.get_value("Fund Series", self.fund_series, "hurdle_rate")
            if rate:
                return rate
        # Fallback to fee structure
        fee = frappe.get_all(
            "Fee Structure",
            filters={"fund_master": self.fund_master, "fee_type": "Carried Interest", "status": "Active"},
            fields=["preferred_return_rate"],
            limit=1,
        )
        return fee[0].preferred_return_rate if fee else 8  # Default 8%


@frappe.whitelist()
def calculate_waterfall(fund_master, total_distributable, waterfall_date=None):
    """API: Calculate waterfall distribution for a fund."""
    from frappe.utils import today

    wf = frappe.get_doc({
        "doctype": "Carried Interest Waterfall",
        "fund_master": fund_master,
        "waterfall_date": waterfall_date or today(),
        "waterfall_type": "European (Total Return)",
        "total_distributable": flt(total_distributable),
        "status": "Draft",
    })
    wf.insert()
    return wf


@frappe.whitelist()
def get_waterfall_history(fund_master):
    """API: Get waterfall history for a fund."""
    return frappe.get_all(
        "Carried Interest Waterfall",
        filters={"fund_master": fund_master},
        fields=[
            "name", "waterfall_date", "waterfall_type",
            "total_distributable", "return_of_capital",
            "preferred_return_amount", "catch_up_amount",
            "lp_carry_amount", "gp_carry_amount",
            "total_distributed", "status",
        ],
        order_by="waterfall_date desc",
    )
