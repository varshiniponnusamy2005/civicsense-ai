from datetime import datetime
from bson import ObjectId

from database import notifications_collection


# ==========================================================
# CREATE NOTIFICATION
# ==========================================================

def create_notification(notification_data):
    """
    Create a new notification for a citizen.
    """

    notification = {
        "user_id": str(notification_data.get("user_id", "")),
        "complaint_id": str(
            notification_data.get("complaint_id", "")
        ),

        "type": notification_data.get(
            "type",
            "GENERAL"
        ),

        "title": notification_data.get(
            "title",
            "Notification"
        ),

        "message": notification_data.get(
            "message",
            ""
        ),

        "status": notification_data.get(
            "status",
            ""
        ),

        "read": False,

        "created_at": datetime.utcnow(),
    }

    result = notifications_collection.insert_one(
        notification
    )

    return str(result.inserted_id)


# ==========================================================
# GET USER NOTIFICATIONS
# ==========================================================

def get_notifications_by_user(user_id):
    """
    Get all notifications belonging to a user.
    Latest notification comes first.
    """

    notifications = notifications_collection.find(
        {
            "user_id": str(user_id)
        }
    ).sort(
        "created_at",
        -1
    )

    result = []

    for notification in notifications:

        notification["_id"] = str(
            notification["_id"]
        )

        if notification.get("created_at"):
            notification["created_at"] = (
                notification["created_at"].isoformat()
            )

        result.append(notification)

    return result


# ==========================================================
# MARK NOTIFICATION AS READ
# ==========================================================

def mark_notification_read(notification_id):
    """
    Mark one notification as read.
    """

    try:

        object_id = ObjectId(
            notification_id
        )

    except Exception:
        return False

    result = notifications_collection.update_one(
        {
            "_id": object_id
        },
        {
            "$set": {
                "read": True
            }
        }
    )

    return result.modified_count > 0


# ==========================================================
# MARK ALL USER NOTIFICATIONS AS READ
# ==========================================================

def mark_all_notifications_read(user_id):
    """
    Mark all notifications of a user as read.
    """

    result = notifications_collection.update_many(
        {
            "user_id": str(user_id)
        },
        {
            "$set": {
                "read": True
            }
        }
    )

    return result.modified_count