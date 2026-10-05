from flask import Blueprint, jsonify, request

from models.notification_model import (
    get_notifications_by_user,
    mark_notification_read,
    mark_all_notifications_read,
)


# ==========================================================
# BLUEPRINT
# ==========================================================

notification_bp = Blueprint(
    "notification_bp",
    __name__,
    url_prefix="/api/notifications"
)


# ==========================================================
# GET USER NOTIFICATIONS
# ==========================================================

@notification_bp.route(
    "/user/<user_id>",
    methods=["GET"]
)
def get_user_notifications(user_id):

    try:

        notifications = get_notifications_by_user(
            user_id
        )

        return jsonify({
            "success": True,
            "notifications": notifications
        }), 200

    except Exception as e:

        print(
            "Notification fetch error:",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to fetch notifications."
        }), 500


# ==========================================================
# MARK ONE NOTIFICATION AS READ
# ==========================================================

@notification_bp.route(
    "/<notification_id>/read",
    methods=["PUT"]
)
def read_notification(notification_id):

    try:

        success = mark_notification_read(
            notification_id
        )

        if not success:

            return jsonify({
                "success": False,
                "message": "Notification not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Notification marked as read."
        }), 200

    except Exception as e:

        print(
            "Notification read error:",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to update notification."
        }), 500


# ==========================================================
# MARK ALL NOTIFICATIONS AS READ
# ==========================================================

@notification_bp.route(
    "/user/<user_id>/read-all",
    methods=["PUT"]
)
def read_all_notifications(user_id):

    try:

        updated_count = (
            mark_all_notifications_read(
                user_id
            )
        )

        return jsonify({
            "success": True,
            "message": "All notifications marked as read.",
            "updated_count": updated_count
        }), 200

    except Exception as e:

        print(
            "Read all notifications error:",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to update notifications."
        }), 500