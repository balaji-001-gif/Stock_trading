# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
AML / Sanctions Screening Connector — Stub-to-Live Integration

Anti-Money Laundering checks across multiple global databases.

Supports:
1. PEP Screening — Politically Exposed Person check against global PEP lists
2. OFAC Sanctions — US OFAC SDN (Specially Designated Nationals) list check
3. UN / EU Sanctions — United Nations and European Union sanctions lists
4. PMLA Screening — Indian PMLA (Prevention of Money Laundering Act) compliance
5. Adverse Media — Negative news and media screening
6. Risk Scoring — Automated risk score computation based on check results

Stub mode: Simulates screening against realistic test scenarios
Live mode: Integrates with actual AML/sanctions screening APIs (World-Check, LexisNexis, etc.)
"""

import frappe
import json
import random
from datetime import datetime, timedelta, date
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated PEP database
STUB_PEP_RECORDS = [
    {"name": "Narendra Modi", "type": "Head of State", "country": "India", "position": "Prime Minister"},
    {"name": "Droupadi Murmu", "type": "Head of State", "country": "India", "position": "President"},
    {"name": "Nirmala Sitharaman", "type": "Minister", "country": "India", "position": "Finance Minister"},
    {"name": "Shaktikanta Das", "type": "Senior Official", "country": "India", "position": "RBI Governor"},
]

# Simulated sanctions database
STUB_SANCTIONS_RECORDS = [
    {"name": "Dawood Ibrahim", "list": "OFAC SDN", "country": "India", "category": "Organized Crime"},
    {"name": "Hafiz Saeed", "list": "UN 1267", "country": "Pakistan", "category": "Terrorism"},
    {"name": "Masood Azhar", "list": "UN 1267", "country": "India/Pakistan", "category": "Terrorism"},
]


class AMLScreeningConnector(BaseConnector):
    """AML / Sanctions Screening — PEP, OFAC, UN, PMLA, adverse media checks."""

    connector_name = "aml_screening"
    label = "AML / Sanctions Screening"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: PEP Screening
    # =========================================================================

    def screen_pep(self, full_name, country="India"):
        """Screen a name against global PEP databases."""
        try:
            if self.is_stub:
                result = self._stub_screen_pep(full_name, country)
            else:
                result = self._live_screen_pep(full_name, country)
            self.log_request("screen_pep", {"name": full_name, "country": country}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "check": "pep", "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Sanctions Screening
    # =========================================================================

    def screen_sanctions(self, full_name):
        """Screen against OFAC, UN, and EU sanctions lists."""
        try:
            if self.is_stub:
                result = self._stub_screen_sanctions(full_name)
            else:
                result = self._live_screen_sanctions(full_name)
            self.log_request("screen_sanctions", {"name": full_name}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "check": "sanctions", "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Full AML Screening
    # =========================================================================

    def full_screen(self, full_name, pan_number=None, country="India"):
        """Run complete AML screening — PEP + Sanctions + Adverse Media + Risk Score."""
        try:
            if self.is_stub:
                pep = self._stub_screen_pep(full_name, country)
                sanctions = self._stub_screen_sanctions(full_name)
                adverse = self._stub_adverse_media(full_name)
                risk = self._stub_risk_score(pep, sanctions, adverse)
                result = {
                    "status": "Success",
                    "mode": "stub",
                    "screening_ref": f"AML-{random_string(12).upper()}",
                    "pep": pep,
                    "sanctions": sanctions,
                    "adverse_media": adverse,
                    "risk_score": risk,
                    "overall_status": "Cleared" if risk.get("level") in ("Low", "Medium") else "Flagged",
                }
            else:
                result = self._live_full_screen(full_name, pan_number, country)
            self.log_request("full_screen", {"name": full_name, "pan": pan_number}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Adverse Media
    # =========================================================================

    def screen_adverse_media(self, full_name):
        """Screen for adverse media / negative news."""
        try:
            if self.is_stub:
                result = self._stub_adverse_media(full_name)
            else:
                result = self._live_adverse_media(full_name)
            self.log_request("screen_adverse_media", {"name": full_name}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "check": "adverse_media", "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_screen_pep(self, full_name, country):
        """Simulate PEP screening against global database."""
        matches = []
        for pep in STUB_PEP_RECORDS:
            if any(word.lower() in full_name.lower() for word in pep["name"].split()):
                matches.append({
                    "matched_name": pep["name"],
                    "match_score": random.randint(85, 100),
                    "pep_type": pep["type"],
                    "country": pep["country"],
                    "position": pep["position"],
                    "source": "World-Check / OpenSanctions",
                    "last_updated": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                })

        return {
            "status": "Success",
            "check": "PEP",
            "screened_name": full_name,
            "matches_found": len(matches),
            "matches": matches,
            "conclusion": "Match Found" if matches else "Clear",
        }

    def _stub_screen_sanctions(self, full_name):
        """Simulate sanctions screening."""
        matches = []
        for sanction in STUB_SANCTIONS_RECORDS:
            if any(word.lower() in full_name.lower() for word in sanction["name"].split()):
                matches.append({
                    "matched_name": sanction["name"],
                    "match_score": random.randint(90, 100),
                    "sanctions_list": sanction["list"],
                    "country": sanction["country"],
                    "category": sanction["category"],
                    "source": "OFAC SDN / UN 1267",
                    "last_updated": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
                })

        return {
            "status": "Success",
            "check": "Sanctions",
            "screened_name": full_name,
            "lists_checked": ["OFAC SDN", "UN 1267", "EU Consolidated", "UK Sanctions"],
            "matches_found": len(matches),
            "matches": matches,
            "conclusion": "Match Found" if matches else "Clear",
        }

    def _stub_adverse_media(self, full_name):
        """Simulate adverse media screening."""
        random_articles = []
        # Randomly generate 0-2 adverse media hits
        if random.random() < 0.15:
            random_articles.append({
                "title": "Regulatory investigation into company linked to " + full_name.split()[0],
                "source": "Financial Times",
                "date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "relevance": "Medium",
                "summary": "News article referencing similar name. Further investigation recommended.",
            })

        return {
            "status": "Success",
            "check": "Adverse Media",
            "screened_name": full_name,
            "sources_searched": ["News", "Blogs", "Legal Databases", "Regulatory Filings"],
            "matches_found": len(random_articles),
            "matches": random_articles,
            "conclusion": "Match Found" if random_articles else "Clear",
        }

    def _stub_risk_score(self, pep_result, sanctions_result, adverse_result):
        """Calculate risk score based on all check results."""
        score = random.randint(5, 30)  # Base score low for most individuals
        factors = []

        if pep_result.get("matches_found", 0) > 0:
            score += 30
            factors.append("PEP Match")

        if sanctions_result.get("matches_found", 0) > 0:
            score += 50
            factors.append("Sanctions Match")

        if adverse_result.get("matches_found", 0) > 0:
            score += 15
            factors.append("Adverse Media")

        score = min(score, 100)

        if score >= 75:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 25:
            level = "Medium"
        else:
            level = "Low"

        return {
            "score": score,
            "level": level,
            "factors": factors,
            "assessment": "Standard" if level in ("Low", "Medium") else "Enhanced Due Diligence Required",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_screen_pep(self, full_name, country):
        raise NotImplementedError("Live PEP screening requires World-Check / LexisNexis API credentials.")

    def _live_screen_sanctions(self, full_name):
        raise NotImplementedError("Live sanctions screening requires OFAC/UN API credentials.")

    def _live_full_screen(self, full_name, pan_number, country):
        raise NotImplementedError("Live full AML screening requires third-party API credentials.")

    def _live_adverse_media(self, full_name):
        raise NotImplementedError("Live adverse media screening requires news API credentials.")
