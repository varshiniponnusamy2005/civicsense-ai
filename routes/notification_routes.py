from flask import Blueprint, request, jsonify

from utils.notification_service import (
    create_notification,
    get_user_notifications
)


notification_bp = Blueprint(
    "notification",
    __name__,
    url_prefix="/api/notifications"
)


# -------------------------------------------------
# Create Notification
# -------------------------------------------------
@notification_bp.route("/create", methods=["POST"])
def add_notification():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Notification data is required"
        }), 400

    user_id = data.get("user_id")
    complaint_id = data.get("complaint_id")
    message = data.get("message")

    complaint_title = data.get("complaint_title")
    status = data.get("status")
    category = data.get("category")

    if not user_id or not complaint_id or not message:
        return jsonify({
            "message": "user_id, complaint_id and message are required"
        }), 400

    notification_id = create_notification(
        user_id,
        complaint_id,
        message,
        complaint_title,
        status,
        category
    )

    return jsonify({
        "message": "Notification created successfully",
        "notification_id": notification_id
    }), 201


# -------------------------------------------------
# Get User Notifications
# -------------------------------------------------
@notification_bp.route("/<user_id>", methods=["GET"])
def get_notifications(user_id):

    notifications = get_user_notifications(user_id)

    return jsonify({
        "user_id": user_id,
        "notification_count": len(notifications),
        "notifications": notifications
    }), 200