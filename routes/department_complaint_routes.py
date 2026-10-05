from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from database import (
    complaints_collection,
    status_history_collection
)

from utils.notification_service import (
    create_notification
)


# =========================================================
# BLUEPRINT
# =========================================================

department_complaint_bp = Blueprint(
    "department_complaint",
    __name__,
    url_prefix="/api/department"
)


# =========================================================
# VALID STATUSES
# =========================================================

VALID_STATUSES = [
    "Pending",
    "In Progress",
    "Resolved",
    "Rejected"
]


# =========================================================
# GET DEPARTMENT COMPLAINTS
# =========================================================

@department_complaint_bp.route(
    "/<department_name>/complaints",
    methods=["GET"]
)
def get_department_complaints(
    department_name
):

    try:

        complaints = list(
            complaints_collection.find({
                "assigned_department":
                    department_name
            })
        )

        current_time = datetime.now(
            timezone.utc
        )

        visible_complaints = []

        for complaint in complaints:

            status = complaint.get(
                "status"
            )

            # -------------------------------------------------
            # Resolved complaints are visible for 24 hours only
            # -------------------------------------------------

            if status == "Resolved":

                resolved_at = complaint.get(
                    "resolved_at"
                )

                if not resolved_at:
                    continue

                if resolved_at.tzinfo is None:

                    resolved_at = (
                        resolved_at.replace(
                            tzinfo=timezone.utc
                        )
                    )

                hide_after = (
                    resolved_at +
                    timedelta(hours=24)
                )

                if current_time >= hide_after:

                    continue

            # -------------------------------------------------
            # Convert ObjectId
            # -------------------------------------------------

            complaint["_id"] = str(
                complaint["_id"]
            )

            visible_complaints.append(
                complaint
            )

        return jsonify({

            "department":
                department_name,

            "complaint_count":
                len(visible_complaints),

            "complaints":
                visible_complaints

        }), 200

    except Exception as e:

        print(
            "Get department complaints error:",
            e
        )

        return jsonify({
            "message":
                "Unable to fetch department complaints",

            "error":
                str(e)

        }), 500


# =========================================================
# UPDATE DEPARTMENT COMPLAINT STATUS
# =========================================================

@department_complaint_bp.route(
    "/<department_name>/complaints/<complaint_id>/status",
    methods=["PUT"]
)
def update_department_complaint_status(
    department_name,
    complaint_id
):

    # =====================================================
    # GET REQUEST DATA
    # =====================================================

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "message":
                "Status data is required"
        }), 400

    new_status = data.get(
        "status"
    )

    remarks = data.get(
        "remarks",
        ""
    )

    # =====================================================
    # VALIDATE STATUS
    # =====================================================

    if not new_status:

        return jsonify({
            "message":
                "Status is required"
        }), 400

    if new_status not in VALID_STATUSES:

        return jsonify({
            "message":
                "Invalid status",

            "valid_statuses":
                VALID_STATUSES

        }), 400

    # =====================================================
    # VALIDATE COMPLAINT ID
    # =====================================================

    try:

        complaint_object_id = ObjectId(
            complaint_id
        )

    except Exception:

        return jsonify({
            "message":
                "Invalid complaint ID"
        }), 400

    try:

        # =================================================
        # FIND COMPLAINT
        # =================================================

        complaint = complaints_collection.find_one({

            "_id":
                complaint_object_id,

            "assigned_department":
                department_name

        })

        if not complaint:

            return jsonify({
                "message":
                    "Complaint not found for this department"
            }), 404

        # =================================================
        # OLD STATUS
        # =================================================

        old_status = complaint.get(
            "status",
            "Pending"
        )

        # =================================================
        # PREPARE UPDATE
        # =================================================

        update_data = {

            "status":
                new_status,

            "remarks":
                remarks

        }

        # =================================================
        # RESOLVED TIMESTAMP
        # =================================================

        if new_status == "Resolved":

            update_data[
                "resolved_at"
            ] = datetime.now(
                timezone.utc
            )

        else:

            update_data[
                "resolved_at"
            ] = None

        # =================================================
        # UPDATE COMPLAINT
        # =================================================

        complaints_collection.update_one(

            {
                "_id":
                    complaint_object_id
            },

            {
                "$set":
                    update_data
            }
        )

        print(
            "========================================"
        )

        print(
            "Complaint Status Updated"
        )

        print(
            "Complaint ID:",
            complaint_id
        )

        print(
            "Old Status:",
            old_status
        )

        print(
            "New Status:",
            new_status
        )

        print(
            "========================================"
        )

        # =================================================
        # SAVE STATUS HISTORY
        # =================================================

        status_history_collection.insert_one({

            "complaint_id":
                complaint_id,

            "user_id":
                complaint.get(
                    "user_id"
                ),

            "status":
                new_status,

            "remarks":
                remarks,

            "updated_at":
                datetime.now(
                    timezone.utc
                )

        })

        # =================================================
        # USER INFORMATION
        # =================================================

        user_id = complaint.get(
            "user_id"
        )

        # =================================================
        # NOTIFICATION
        # =================================================

        notification_id = None

        if user_id:

            complaint_title = (
                complaint.get(
                    "title"
                )
                or "Civic Complaint"
            )

            category = (
                complaint.get(
                    "category"
                )
                or "General"
            )

            # ---------------------------------------------
            # STATUS MESSAGE
            # ---------------------------------------------

            if new_status == "Resolved":

                message = (
                    f"{complaint_title} - "
                    "Status: Resolved - "
                    "Your complaint has been "
                    "resolved successfully."
                )

            elif new_status == "In Progress":

                message = (
                    f"{complaint_title} - "
                    "Status: In Progress - "
                    "Your complaint is currently "
                    "being worked on by the "
                    "concerned department."
                )

            elif new_status == "Rejected":

                message = (
                    f"{complaint_title} - "
                    "Status: Rejected - "
                    "Your complaint has been "
                    "rejected."
                )

            else:

                message = (
                    f"{complaint_title} - "
                    "Status: Pending - "
                    "Your complaint is waiting "
                    "for department action."
                )

            # ---------------------------------------------
            # CREATE NOTIFICATION
            # ---------------------------------------------

            notification_id = create_notification(

                user_id=user_id,

                complaint_id=complaint_id,

                message=message,

                complaint_title=complaint_title,

                status=new_status,

                category=category

            )

            if notification_id:

                notification_message = (
                    "Notification created successfully"
                )

            else:

                notification_message = (
                    "Complaint updated, but "
                    "notification could not be created"
                )

        else:

            notification_message = (
                "Complaint updated, but "
                "user ID was not available"
            )

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "message":
                "Department complaint status "
                "updated successfully",

            "department":
                department_name,

            "complaint_id":
                complaint_id,

            "old_status":
                old_status,

            "status":
                new_status,

            "remarks":
                remarks,

            "notification":
                notification_message,

            "notification_id":
                notification_id

        }), 200

    except Exception as e:

        print(
            "========================================"
        )

        print(
            "Department status update error:",
            e
        )

        print(
            "========================================"
        )

        return jsonify({

            "message":
                "Unable to update complaint status",

            "error":
                str(e)

        }), 500