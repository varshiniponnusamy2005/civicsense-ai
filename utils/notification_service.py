from database import db
from datetime import datetime, timezone


# =========================================================
# NOTIFICATIONS COLLECTION
# =========================================================

notifications_collection = db["notifications"]


# =========================================================
# CREATE NOTIFICATION
# =========================================================

def create_notification(
    user_id,
    complaint_id,
    message,
    complaint_title=None,
    status=None,
    category=None
):
    """
    Create an in-app notification for a citizen.

    Notification is stored in MongoDB and later
    displayed by the frontend NotificationPanel.
    """

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if not user_id:

        print(
            "Notification Error: user_id is missing"
        )

        return None


    if not complaint_id:

        print(
            "Notification Error: complaint_id is missing"
        )

        return None


    if not message:

        print(
            "Notification Error: message is missing"
        )

        return None


    # -----------------------------------------------------
    # CREATE NOTIFICATION DOCUMENT
    # -----------------------------------------------------

    notification = {

        "user_id": str(
            user_id
        ),

        "complaint_id": str(
            complaint_id
        ),

        "message": str(
            message
        ),

        "complaint_title": (
            complaint_title
            if complaint_title
            else "Civic Complaint"
        ),

        "status": (
            status
            if status
            else "Updated"
        ),

        "category": (
            category
            if category
            else "General"
        ),

        "created_at": datetime.now(
            timezone.utc
        ),

        "is_read": False
    }


    # -----------------------------------------------------
    # SAVE TO MONGODB
    # -----------------------------------------------------

    try:

        result = notifications_collection.insert_one(
            notification
        )


        notification_id = str(
            result.inserted_id
        )


        print(
            "========================================"
        )

        print(
            "Notification Created Successfully"
        )

        print(
            "Notification ID:",
            notification_id
        )

        print(
            "User ID:",
            user_id
        )

        print(
            "Complaint ID:",
            complaint_id
        )

        print(
            "Status:",
            status
        )

        print(
            "Category:",
            category
        )

        print(
            "Message:",
            message
        )

        print(
            "========================================"
        )


        return notification_id


    except Exception as e:

        print(
            "Notification creation error:",
            e
        )

        return None


# =========================================================
# GET USER NOTIFICATIONS
# =========================================================

def get_user_notifications(
    user_id
):
    """
    Get notifications belonging to a particular citizen.

    Resolved notifications are automatically hidden
    after 24 hours.
    """

    # -----------------------------------------------------
    # VALIDATE USER ID
    # -----------------------------------------------------

    if not user_id:

        return []


    current_time = datetime.now(
        timezone.utc
    )


    # -----------------------------------------------------
    # FETCH NOTIFICATIONS
    # -----------------------------------------------------

    try:

        notifications = list(

            notifications_collection.find({

                "user_id": str(
                    user_id
                )

            }).sort(

                "created_at",
                -1

            )

        )


    except Exception as e:

        print(
            "Notification fetch error:",
            e
        )

        return []


    # -----------------------------------------------------
    # FILTER NOTIFICATIONS
    # -----------------------------------------------------

    filtered_notifications = []


    for notification in notifications:

        # =================================================
        # RESOLVED NOTIFICATION
        # =================================================

        if notification.get(
            "status"
        ) == "Resolved":

            created_at = notification.get(
                "created_at"
            )


            if created_at:

                # MongoDB datetime can sometimes be naive
                if created_at.tzinfo is None:

                    created_at = created_at.replace(
                        tzinfo=timezone.utc
                    )


                age = (
                    current_time -
                    created_at
                )


                # Hide resolved notification
                # after 24 hours

                if (
                    age.total_seconds()
                    >= 24 * 60 * 60
                ):

                    continue


        # =================================================
        # CONVERT OBJECT ID TO STRING
        # =================================================

        notification["_id"] = str(
            notification["_id"]
        )


        # =================================================
        # CONVERT DATETIME TO ISO STRING
        # =================================================

        created_at = notification.get(
            "created_at"
        )


        if created_at:

            if created_at.tzinfo is None:

                created_at = created_at.replace(
                    tzinfo=timezone.utc
                )


            notification["created_at"] = (
                created_at.isoformat()
            )


        # =================================================
        # DEFAULT COMPLAINT TITLE
        # =================================================

        if not notification.get(
            "complaint_title"
        ):

            notification[
                "complaint_title"
            ] = "Civic Complaint"


        # =================================================
        # DEFAULT STATUS
        # =================================================

        if not notification.get(
            "status"
        ):

            notification[
                "status"
            ] = "Updated"


        # =================================================
        # DEFAULT CATEGORY
        # =================================================

        if not notification.get(
            "category"
        ):

            notification[
                "category"
            ] = "General"


        # =================================================
        # DEFAULT READ STATUS
        # =================================================

        if "is_read" not in notification:

            notification[
                "is_read"
            ] = False


        # =================================================
        # ADD TO RESULT
        # =================================================

        filtered_notifications.append(
            notification
        )


    return filtered_notifications