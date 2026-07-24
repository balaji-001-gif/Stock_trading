# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
Video KYC Connector — Stub-to-Live Integration

In-app Video KYC for remote investor onboarding as per SEBI/CDSL guidelines.

Supports:
1. Agent Queue — Assign and manage KYC agents for video verification
2. Session Recording — Start/stop video KYC sessions with recording
3. Frame Capture — Capture live frames for liveness detection and verification
4. Document Verification — Cross-verify identity documents during video call
5. OCR & Liveness — Automated document OCR and liveness detection (stub)

Stub mode: Simulates complete video KYC flow with test recordings
Live mode: Integrates with video KYC platforms (SignDesk, Jocata, etc.)
"""

import frappe
import json
import random
from datetime import datetime, timedelta
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


# Simulated KYC agent pool
STUB_KYC_AGENTS = [
    {"agent_id": "AG001", "name": "Rahul Verma", "status": "Available", "languages": ["Hindi", "English"], "sessions_today": 3},
    {"agent_id": "AG002", "name": "Priya Singh", "status": "Available", "languages": ["English", "Tamil", "Telugu"], "sessions_today": 5},
    {"agent_id": "AG003", "name": "Amit Kumar", "status": "In Call", "languages": ["Hindi", "English", "Punjabi"], "sessions_today": 7},
    {"agent_id": "AG004", "name": "Sneha Reddy", "status": "Break", "languages": ["Telugu", "English", "Kannada"], "sessions_today": 2},
    {"agent_id": "AG005", "name": "Vikram Joshi", "status": "Available", "languages": ["Hindi", "English", "Marathi", "Gujarati"], "sessions_today": 1},
]


class VideoKYCConnector(BaseConnector):
    """Video KYC integration — agent queue, session recording, frame capture."""

    connector_name = "video_kyc"
    label = "Video KYC"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Agent Management
    # =========================================================================

    def get_agent_queue(self, status=None):
        """Get available KYC agents and their queue status."""
        try:
            if self.is_stub:
                result = self._stub_agent_queue(status)
            else:
                result = self._live_agent_queue(status)
            self.log_request("get_agent_queue", {"status": status}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def assign_agent(self, investor_name, preferred_language="English"):
        """Assign a KYC agent to an investor for video verification."""
        try:
            if self.is_stub:
                result = self._stub_assign_agent(investor_name, preferred_language)
            else:
                result = self._live_assign_agent(investor_name, preferred_language)
            self.log_request("assign_agent", {"investor": investor_name, "language": preferred_language}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Session Management
    # =========================================================================

    def start_session(self, investor_name, pan_number, investor_type="Individual"):
        """Start a video KYC session for an investor."""
        try:
            if self.is_stub:
                result = self._stub_start_session(investor_name, pan_number, investor_type)
            else:
                result = self._live_start_session(investor_name, pan_number, investor_type)
            self.log_request("start_session", {"investor": investor_name, "pan": pan_number}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def complete_session(self, session_id, agent_notes=None):
        """Complete a video KYC session with agent notes and verification result."""
        try:
            if self.is_stub:
                result = self._stub_complete_session(session_id, agent_notes)
            else:
                result = self._live_complete_session(session_id, agent_notes)
            self.log_request("complete_session", {"session_id": session_id}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def get_session_status(self, session_id):
        """Get current status of a video KYC session."""
        try:
            if self.is_stub:
                result = self._stub_session_status(session_id)
            else:
                result = self._live_session_status(session_id)
            self.log_request("get_session_status", {"session_id": session_id}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Frame Capture & Liveness
    # =========================================================================

    def capture_frame(self, session_id):
        """Capture a live frame during video KYC session."""
        try:
            if self.is_stub:
                result = self._stub_capture_frame(session_id)
            else:
                result = self._live_capture_frame(session_id)
            self.log_request("capture_frame", {"session_id": session_id}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def check_liveness(self, frame_data):
        """Check liveness using frame analysis."""
        try:
            if self.is_stub:
                result = self._stub_liveness_check(frame_data)
            else:
                result = self._live_liveness_check(frame_data)
            self.log_request("check_liveness", {"frame_length": len(str(frame_data))}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def verify_document(self, document_image, document_type="PAN"):
        """OCR and verify identity document during video KYC."""
        try:
            if self.is_stub:
                result = self._stub_verify_document(document_image, document_type)
            else:
                result = self._live_verify_document(document_image, document_type)
            self.log_request("verify_document", {"document_type": document_type}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_agent_queue(self, status=None):
        """Simulate agent queue from KYC provider."""
        agents = STUB_KYC_AGENTS
        if status:
            agents = [a for a in agents if a["status"].lower() == status.lower()]
        return {
            "status": "Success",
            "mode": "stub",
            "total_agents": len(agents),
            "available_agents": len([a for a in agents if a["status"] == "Available"]),
            "agents": agents,
        }

    def _stub_assign_agent(self, investor_name, preferred_language):
        """Simulate assigning an available agent."""
        available = [a for a in STUB_KYC_AGENTS
                     if a["status"] == "Available" and preferred_language in a["languages"]]
        if not available:
            available = [a for a in STUB_KYC_AGENTS if a["status"] == "Available"]
        if not available:
            return {"status": "Error", "error": "No agents available. Please try later.", "mode": "stub"}

        agent = random.choice(available)
        return {
            "status": "Success",
            "mode": "stub",
            "agent_assigned": agent["name"],
            "agent_id": agent["agent_id"],
            "languages": agent["languages"],
            "sessions_completed_today": agent["sessions_today"],
            "estimated_wait_seconds": random.randint(5, 60),
            "meeting_url": f"https://video.bizaxl.com/kyc/room/{random_string(8).lower()}",
            "assigned_at": now_datetime().isoformat(),
        }

    def _stub_start_session(self, investor_name, pan_number, investor_type):
        """Simulate starting a video KYC session."""
        session_id = f"VKYC-{random_string(12).upper()}"
        return {
            "status": "Success",
            "mode": "stub",
            "session_id": session_id,
            "investor_name": investor_name,
            "pan_number": pan_number,
            "investor_type": investor_type,
            "session_started_at": now_datetime().isoformat(),
            "recording_url": f"https://storage.bizaxl.com/recordings/{session_id}.mp4",
            "estimated_duration_seconds": random.randint(120, 300),
            "meeting_status": "Active",
        }

    def _stub_complete_session(self, session_id, agent_notes):
        """Simulate completing a video KYC session."""
        verified = random.random() < 0.85  # 85% verification success rate
        return {
            "status": "Success",
            "mode": "stub",
            "session_id": session_id,
            "verification_status": "Verified" if verified else "Failed",
            "verification_result": {
                "face_match": round(random.uniform(0.78, 0.99), 2),
                "document_match": round(random.uniform(0.82, 1.0), 2),
                "liveness_score": round(random.uniform(0.85, 0.99), 2),
                "overall_score": round(random.uniform(0.80, 0.99), 2) if verified else round(random.uniform(0.35, 0.60), 2),
            },
            "agent_notes": agent_notes or "Investor identity verified successfully.",
            "session_ended_at": (get_datetime() + timedelta(seconds=random.randint(120, 300))).isoformat(),
            "recording_duration_seconds": random.randint(120, 300),
        }

    def _stub_session_status(self, session_id):
        """Simulate checking session status."""
        statuses = ["Initiated", "Active", "Active", "Active", "Completed", "Completed"]
        recording_url = f"https://storage.bizaxl.com/recordings/{session_id}.mp4"
        return {
            "status": "Success",
            "mode": "stub",
            "session_id": session_id,
            "session_status": random.choice(statuses),
            "elapsed_seconds": random.randint(30, 250),
            "recording_url": recording_url,
            "has_recording": True,
            "last_frame_captured_at": (get_datetime() - timedelta(seconds=random.randint(5, 60))).isoformat(),
        }

    def _stub_capture_frame(self, session_id):
        """Simulate capturing a live video frame."""
        return {
            "status": "Success",
            "mode": "stub",
            "session_id": session_id,
            "frame_id": f"FRM-{random_string(10).upper()}",
            "captured_at": now_datetime().isoformat(),
            "frame_quality": random.choice(["High", "Medium"]),
            "face_detected": True,
            "face_confidence": round(random.uniform(0.85, 0.99), 2),
            "blur_score": round(random.uniform(0.02, 0.15), 3),
            "frame_url": f"https://storage.bizaxl.com/frames/{session_id}/{random_string(8)}.jpg",
        }

    def _stub_liveness_check(self, frame_data):
        """Simulate liveness detection."""
        return {
            "status": "Success",
            "mode": "stub",
            "liveness_decision": "Live",
            "liveness_score": round(random.uniform(0.88, 0.99), 2),
            "spoof_probability": round(random.uniform(0.001, 0.12), 3),
            "depth_analysis": "Passed",
            "blink_detected": True,
            "movement_detected": True,
        }

    def _stub_verify_document(self, document_image, document_type):
        """Simulate document OCR and verification."""
        docs = {
            "PAN": {"number": "ABCDE1234F", "name": "Aarav Sharma", "dob": "15/08/1990"},
            "AADHAAR": {"number": "XXXX-XXXX-1234", "name": "Aarav Sharma", "dob": "15/08/1990"},
            "VOTER_ID": {"number": f"INX{random_string(7).upper()}", "name": "Aarav Sharma"},
            "DRIVING_LICENSE": {"number": f"DL-{random_string(10).upper()}", "name": "Aarav Sharma", "dob": "15/08/1990"},
        }
        doc_data = docs.get(document_type, {"number": f"DOC-{random_string(8).upper()}", "name": "Verified Investor"})
        return {
            "status": "Success",
            "mode": "stub",
            "document_type": document_type,
            "extracted_data": doc_data,
            "ocr_confidence": round(random.uniform(0.85, 0.99), 2),
            "document_validated": True,
            "expiry_check": "Valid" if document_type != "DRIVING_LICENSE" else "Not Expired",
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_agent_queue(self, status):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_assign_agent(self, investor_name, preferred_language):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_start_session(self, investor_name, pan_number, investor_type):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_complete_session(self, session_id, agent_notes):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_session_status(self, session_id):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_capture_frame(self, session_id):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_liveness_check(self, frame_data):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")

    def _live_verify_document(self, document_image, document_type):
        raise NotImplementedError("Live Video KYC requires SignDesk/Jocata API credentials.")
