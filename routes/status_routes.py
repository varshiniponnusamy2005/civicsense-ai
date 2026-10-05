from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

from database import complaints_collection, status_history_collection
from utils.notification_service import create_notification


status_bp = Blueprint(
    "status",
    __name__,
    url_prefix="/api/status"
)


VALID_STATUSES = [
    "Pending",
    "In Progress",
    "Resolved",
    "Rejected"
]


@status_bp.route(
    "/update",
    methods=["PUT"]
)
def update_status():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": (
                "Status update data is required"
            )
        }), 400


    complaint_id = data.get(
        "complaint_id"
    )

    new_status = data.get(
        "status"
    )

    remarks = data.get(
        "remarks",
        ""
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not complaint_id or not new_status:

        return jsonify({
            "message": (
                "Complaint ID and status "
                "are required"
            )
        }), 400


    if new_status not in VALID_STATUSES:

        return jsonify({
            "message": (
                "Invalid status"
            )
        }), 400


    try:

        object_id = ObjectId(
            complaint_id
        )


        # =================================================
        # FIND COMPLAINT
        # =================================================

        complaint = complaints_collection.find_one({
            "_id": object_id
        })


        if not complaint:

            return jsonify({
                "message": (
                    "Complaint not found"
                )
            }), 404


        old_status = complaint.get(
            "status",
            "Pending"
        )


        # =================================================
        # CHECK SAME STATUS
        # =================================================

        if old_status == new_status:

            return jsonify({
                "message": (
                    "Complaint already has "
                    "this status"
                ),

                "complaint_id": (
                    complaint_id
                ),

                "status": (
                    old_status
                ),

                "remarks": (
                    complaint.get(
                        "remarks",
                        ""
                    )
                )
            }), 200


        # =================================================
        # UPDATE COMPLAINT
        # =================================================

        updated_at = datetime.utcnow()


        complaints_collection.update_one(
            {
                "_id": object_id
            },
            {
                "$set": {
                    "status": new_status,
                    "remarks": remarks,
                    "updated_at": updated_at
                }
            }
        )


        # =================================================
        # SAVE STATUS HISTORY
        # =================================================

        status_history_collection.insert_one({

            "complaint_id": complaint_id,

            "user_id": complaint.get(
                "user_id"
            ),

            "old_status": old_status,

            "status": new_status,

            "remarks": remarks,

            "created_at": updated_at
        })


        # =================================================
        # CREATE CITIZEN NOTIFICATION
        # =================================================

        user_id = complaint.get(
            "user_id"
        )


        if user_id:

            complaint_title = complaint.get(
                "title",
                "Civic Complaint"
            )

            category = complaint.get(
                "category",
                "General"
            )


            if new_status == "Resolved":

                message = (
                    f"{complaint_title} — "
                    "Status: Resolved — "
                    "Your complaint has been "
                    "resolved successfully."
                )


            elif new_status == "In Progress":

                message = (
                    f"{complaint_title} — "
                    "Status: In Progress — "
                    "Your complaint is currently "
                    "being worked on."
                )


            elif new_status == "Rejected":

                message = (
                    f"{complaint_title} — "
                    "Status: Rejected — "
                    "Your complaint has been "
                    "rejected."
                )


            else:

                message = (
                    f"{complaint_title} — "
                    "Status: Pending — "
                    "Your complaint is waiting "
                    "for department action."
                )


            create_notification(
                user_id=user_id,
                complaint_id=complaint_id,
                message=message,
                complaint_title=complaint_title,
                status=new_status,
                category=category
            )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "message": (
                "Complaint status updated "
                "successfully"
            ),

            "complaint_id": (
                complaint_id
            ),

            "old_status": (
                old_status
            ),

            "status": (
                new_status
            ),

            "remarks": (
                remarks
            ),

            "updated_at": (
                updated_at.isoformat()
            )

        }), 200


    except Exception as error:

        print(
            "Status update error:",
            error
        )


        return jsonify({
            "message": (
                "Unable to update "
                "complaint status"
            )
        }), 500