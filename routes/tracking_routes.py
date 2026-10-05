from flask import Blueprint, jsonify
from bson import ObjectId

from database import complaints_collection


tracking_bp = Blueprint(
    "tracking",
    __name__,
    url_prefix="/api/tracking"
)


@tracking_bp.route("/<complaint_id>", methods=["GET"])
def track_complaint(complaint_id):

    try:
        complaint = complaints_collection.find_one({
            "_id": ObjectId(complaint_id)
        })

        if not complaint:
            return jsonify({
                "message": "Complaint not found"
            }), 404

        return jsonify({
            "complaint_id": str(complaint["_id"]),
            "title": complaint.get("title", ""),
            "description": complaint.get("description", ""),
            "category": complaint.get("category", ""),
            "location": complaint.get("location", ""),
            "priority": complaint.get("priority", ""),
            "department": complaint.get("department", ""),
            "assigned_department": complaint.get(
                "assigned_department", ""
            ),
            "status": complaint.get(
                "status", "Pending"
            ),
            "remarks": complaint.get(
                "remarks", ""
            )
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Invalid complaint ID",
            "error": str(e)
        }), 400