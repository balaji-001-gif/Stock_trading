# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, flt, validate_email_address
import re


class InvestorProfile(Document):
    """Master record for an investor across all investment verticals."""

    def validate(self):
        self.validate_pan()
        self.validate_aadhaar()
        self.validate_email()
        self.validate_mobile()
        self.validate_ifsc()
        self.validate_nominee()

    def before_submit(self):
        if self.kyc_status == "Not Started":
            self.kyc_status = "Pending"
        self.status = "Active"
        self.onboarding_date = self.onboarding_date or today()

    def validate_pan(self):
        """Validate PAN number format (AAAAA9999A)."""
        if self.pan_number:
            pan = self.pan_number.upper().strip()
            if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan):
                frappe.throw(
                    "Invalid PAN number format. Expected format: AAAAA9999A",
                    title="Invalid PAN",
                )
            self.pan_number = pan

    def validate_aadhaar(self):
        """Validate Aadhaar number (12 digits)."""
        if self.aadhaar_number:
            aadhaar = re.sub(r"\s+", "", self.aadhaar_number)
            if not re.match(r"^\d{12}$", aadhaar):
                frappe.throw(
                    "Invalid Aadhaar number. Must be 12 digits.",
                    title="Invalid Aadhaar",
                )
            self.aadhaar_number = aadhaar

    def validate_email(self):
        """Validate email address format."""
        if self.email and not validate_email_address(self.email):
            frappe.throw(
                f"Invalid email address: {self.email}",
                title="Invalid Email",
            )

    def validate_mobile(self):
        """Validate Indian mobile number (10 digits)."""
        if self.mobile_number:
            mobile = re.sub(r"\s+", "", self.mobile_number)
            mobile = re.sub(r"^(\+91|91)", "", mobile)
            if not re.match(r"^[6-9]\d{9}$", mobile):
                frappe.throw(
                    "Invalid Indian mobile number. Must be 10 digits starting with 6-9.",
                    title="Invalid Mobile",
                )

    def validate_ifsc(self):
        """Validate IFSC code format."""
        if self.ifsc_code:
            ifsc = self.ifsc_code.upper().strip()
            if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc):
                frappe.throw(
                    "Invalid IFSC code format. Expected: AAAA0XXXXXX",
                    title="Invalid IFSC",
                )
            self.ifsc_code = ifsc

    def validate_nominee(self):
        """Validate nominee percentage."""
        if self.nominee_percentage and self.nominee_percentage > 100:
            frappe.throw(
                "Nominee allocation cannot exceed 100%.",
                title="Invalid Nominee",
            )

    def update_kyc_status(self, new_status):
        """Update KYC status with audit trail."""
        old_status = self.kyc_status
        self.kyc_status = new_status
        if new_status == "Verified":
            self.kyc_completed_date = today()
        self.save()

        frappe.db.set_value(
            "Investor Profile",
            self.name,
            {"kyc_status": new_status, "kyc_completed_date": self.kyc_completed_date},
        )

        # Add audit comment
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Investor Profile",
            "reference_name": self.name,
            "comment_email": frappe.session.user,
            "content": f"KYC status changed from {old_status} to {new_status}",
        }).insert()

    def get_fatca_summary(self):
        """Get FATCA declaration summary."""
        return {
            "tax_residency": self.tax_residency_country_1,
            "tin": self.tin_number_1,
            "second_residency": self.tax_residency_country_2 or None,
            "fatca_status": self.fatca_status,
            "us_person": self.us_person,
            "declaration_date": self.fatca_declaration_date,
        }

    def get_portfolio_summary(self):
        """Get summary of investor's holdings across all funds."""
        subscriptions = frappe.get_all(
            "Subscription Request",
            filters={
                "investor": self.name,
                "docstatus": 1,
                "status": ["in", ["Allotted", "Active", "Partially Redeemed"]],
            },
            fields=["fund_master", "share_class", "allotted_units", "total_investment"],
        )
        return {
            "total_funds": len(set(s["fund_master"] for s in subscriptions)),
            "total_investment": sum(s["total_investment"] for s in subscriptions),
            "subscriptions": subscriptions,
        }


@frappe.whitelist()
def create_investor(**kwargs):
    """API: Create a new investor profile with basic validation."""
    required = ["first_name", "pan_number", "email", "mobile_number"]
    for field in required:
        if not kwargs.get(field):
            frappe.throw(f"{field.replace('_', ' ').title()} is required.")

    doc = frappe.get_doc({
        "doctype": "Investor Profile",
        "first_name": kwargs.get("first_name"),
        "last_name": kwargs.get("last_name"),
        "pan_number": kwargs.get("pan_number"),
        "email": kwargs.get("email"),
        "mobile_number": kwargs.get("mobile_number"),
        "investor_category": kwargs.get("investor_category", "Retail Individual"),
        "investor_type": kwargs.get("investor_type", "Individual"),
        "kyc_status": "Not Started",
        "status": "Active",
    })

    for key, value in kwargs.items():
        if hasattr(doc, key) and not doc.get(key):
            try:
                doc.set(key, value)
            except Exception:
                pass

    doc.insert()
    return doc


@frappe.whitelist()
def search_investor(search_term):
    """API: Search investors by PAN, name, email, or mobile."""
    conditions = [
        {"pan_number": ["like", f"%{search_term}%"]},
        {"first_name": ["like", f"%{search_term}%"]},
        {"last_name": ["like", f"%{search_term}%"]},
        {"email": ["like", f"%{search_term}%"]},
        {"mobile_number": ["like", f"%{search_term}%"]},
    ]

    results = []
    for condition in conditions:
        results.extend(
            frappe.get_all(
                "Investor Profile",
                filters=condition,
                fields=[
                    "name",
                    "first_name",
                    "last_name",
                    "pan_number",
                    "email",
                    "mobile_number",
                    "investor_category",
                    "kyc_status",
                    "status",
                ],
                limit_page_length=20,
            )
        )

    # Deduplicate
    seen = set()
    unique = []
    for r in results:
        if r["name"] not in seen:
            seen.add(r["name"])
            unique.append(r)
    return unique


@frappe.whitelist()
def get_kyc_statistics():
    """API: Get KYC statistics for dashboard."""
    stats = frappe.db.get_all(
        "Investor Profile",
        fields=["kyc_status", "count(*) as count"],
        group_by="kyc_status",
    )
    total = frappe.db.count("Investor Profile")
    return {
        "total_investors": total,
        "kyc_breakdown": stats,
        "verification_rate": (
            round(
                (sum(s["count"] for s in stats if s["kyc_status"] == "Verified") / total) * 100,
                1,
            )
            if total
            else 0
        ),
    }
