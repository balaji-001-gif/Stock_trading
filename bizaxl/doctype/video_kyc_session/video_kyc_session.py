# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class VideoKYCSession(Document):
    """Tracks video KYC sessions for remote investor onboarding."""
    pass


@frappe.whitelist()
def start_video_kyc(investor, pan_number, preferred_language="English", investor_type="Individual"):
    """API: Start a video KYC session for an investor."""
    from bizaxl.bizaxl.integrations.video_kyc import VideoKYCConnector

    investor_doc = frappe.get_doc("Investor Profile", investor)
    full_name = f"{investor_doc.first_name} {investor_doc.last_name or ''}".strip()

    connector = VideoKYCConnector()

    # Assign agent
    agent_result = connector.assign_agent(full_name, preferred_language)
    if agent_result.get("status") != "Success":
        return agent_result

    # Start session
    session_result = connector.start_session(full_name, pan_number, investor_type)
    if session_result.get("status") != "Success":
        return session_result

    # Create Video KYC Session record
    doc = frappe.get_doc({
        "doctype": "Video KYC Session",
        "investor": investor,
        "session_id": session_result.get("session_id"),
        "agent_name": agent_result.get("agent_assigned"),
        "agent_id": agent_result.get("agent_id"),
        "status": "Initiated",
        "pan_number": pan_number,
        "investor_type": investor_type,
        "preferred_language": preferred_language,
        "session_started_at": now_datetime(),
        "recording_url": session_result.get("recording_url"),
        "connector_mode": connector.mode,
    })
    doc.insert()

    return {
        "name": doc.name,
        "session_id": doc.session_id,
        "agent_name": doc.agent_name,
        "meeting_url": agent_result.get("meeting_url"),
        "status": doc.status,
        "connector_mode": doc.connector_mode,
    }


@frappe.whitelist()
def complete_video_kyc(vkyc_session, agent_notes=None):
    """API: Complete a video KYC session."""
    from bizaxl.bizaxl.integrations.video_kyc import VideoKYCConnector

    doc = frappe.get_doc("Video KYC Session", vkyc_session)
    connector = VideoKYCConnector()

    result = connector.complete_session(doc.session_id, agent_notes)
    if result.get("status") != "Success":
        return result

    verification = result.get("verification_result", {})
    doc.db_set("status", "Completed")
    doc.db_set("verification_result", result.get("verification_status"))
    doc.db_set("session_ended_at", now_datetime())
    doc.db_set("liveness_score", verification.get("liveness_score", 0) * 100)
    doc.db_set("face_match_score", verification.get("face_match", 0) * 100)
    doc.db_set("document_match_score", verification.get("document_match", 0) * 100)
    doc.db_set("agent_notes", agent_notes)
    doc.db_set("recording_duration", result.get("recording_duration_seconds", 0))

    # Update investor profile KYC status
    if result.get("verification_status") == "Verified":
        frappe.db.set_value("Investor Profile", doc.investor, "kyc_status", "Verified")
        frappe.db.set_value("Investor Profile", doc.investor, "kyc_date", today())

    return {
        "name": doc.name,
        "verification_status": result.get("verification_status"),
        "overall_score": verification.get("overall_score", 0),
        "session_duration": result.get("recording_duration_seconds"),
    }


@frappe.whitelist()
def get_agent_queue(status=None):
    """API: Get available KYC agents."""
    from bizaxl.bizaxl.integrations.video_kyc import VideoKYCConnector
    connector = VideoKYCConnector()
    return connector.get_agent_queue(status)


@frappe.whitelist()
def list_vkyc_sessions(investor=None, status=None):
    """API: List video KYC sessions."""
    filters = {}
    if investor:
        filters["investor"] = investor
    if status:
        filters["status"] = status

    return frappe.get_all(
        "Video KYC Session",
        filters=filters,
        fields=["name", "investor", "session_id", "agent_name", "status",
                "verification_result", "session_started_at", "session_ended_at",
                "liveness_score", "connector_mode"],
        order_by="session_started_at desc",
        limit_page_length=50,
    )
