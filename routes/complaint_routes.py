from flask import Blueprint, request, jsonify
from bson import ObjectId
import os
import uuid

from models.complaint_model import create_complaint
from database import complaints_collection

from ai.duplicate_detection import check_duplicate
from ai.priority_prediction import predict_priority
from ai.complaint_classification import classify_complaint
from ai.image_classification import classify_image

from routing.routing_logic import route_complaint

from utils.notification_service import create_notification


complaint_bp = Blueprint(
    "complaint",
    __name__,
    url_prefix="/api/complaints"
)


# =========================================================
# IMAGE UPLOAD FOLDER
# =========================================================

UPLOAD_FOLDER = "uploads/complaints"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# COMPLAINT TITLE
# =========================================================

def get_complaint_title(
    classification,
    description
):

    text = description.lower()

    if classification == "Water Supply":
        return "Water Leakage Complaint"

    if classification == "Electricity":
        return "Streetlight Failure Complaint"

    if classification == "Public Works":

        if (
            "pothole" in text
            or "potholes" in text
        ):
            return "Pothole Complaint"

        return "Road Issue Complaint"

    return "Civic Complaint"


# =========================================================
# REGISTER COMPLAINT
# =========================================================

@complaint_bp.route(
    "/",
    methods=["POST"]
)
def register_complaint():

    # -----------------------------------------------------
    # GET FORM DATA
    # -----------------------------------------------------

    description = request.form.get(
        "description"
    )

    location = request.form.get(
        "location"
    )

    user_id = request.form.get(
        "user_id"
    )

    category = request.form.get(
        "category",
        "General"
    )

    image = request.files.get(
        "image"
    )


    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if not description or not description.strip():

        return jsonify({
            "message": (
                "Complaint description "
                "is required"
            )
        }), 400


    if not location or not location.strip():

        return jsonify({
            "message": (
                "Complaint location "
                "is required"
            )
        }), 400


    if not user_id:

        return jsonify({
            "message": (
                "User information "
                "is required"
            )
        }), 400


    description = description.strip()
    location = location.strip()


    # =====================================================
    # TEXT CLASSIFICATION
    # =====================================================

    text_classification = classify_complaint(
        description
    )


    print(
        "================================="
    )

    print(
        "Text Classification:",
        text_classification
    )


    # =====================================================
    # IMAGE PROCESSING
    # =====================================================

    image_path = None
    image_result = None


    if image:

        # -------------------------------------------------
        # CHECK FILE NAME
        # -------------------------------------------------

        original_name = image.filename

        if not original_name:

            return jsonify({
                "message": (
                    "Invalid image file."
                )
            }), 400


        # -------------------------------------------------
        # CHECK EXTENSION
        # -------------------------------------------------

        extension = os.path.splitext(
            original_name
        )[1].lower()


        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ]


        if extension not in allowed_extensions:

            return jsonify({
                "message": (
                    "Only JPG, JPEG, PNG "
                    "and WEBP images are allowed."
                )
            }), 400


        # -------------------------------------------------
        # CREATE UNIQUE FILE NAME
        # -------------------------------------------------

        unique_name = (
            str(uuid.uuid4())
            + extension
        )


        image_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )


        # -------------------------------------------------
        # SAVE IMAGE
        # -------------------------------------------------

        image.save(
            image_path
        )


        print(
            "Image saved:",
            image_path
        )


        # =================================================
        # AI IMAGE CLASSIFICATION
        # =================================================

        image_result = classify_image(
            image_path
        )


        print(
            "AI Image Classification:",
            image_result
        )


        image_classification = image_result.get(
            "classification",
            "Other"
        )


        image_confidence = image_result.get(
            "confidence",
            0
        )


        image_label = image_result.get(
            "label",
            "Unknown"
        )


        is_civic = image_result.get(
            "is_civic",
            False
        )


        print(
            "Image Classification:",
            image_classification
        )

        print(
            "Image Confidence:",
            image_confidence
        )

        print(
            "Image Label:",
            image_label
        )

        print(
            "Is Civic:",
            is_civic
        )


        # =================================================
        # REJECT NON-CIVIC IMAGE
        # =================================================

        if not is_civic:

            if (
                image_path
                and os.path.exists(image_path)
            ):

                os.remove(
                    image_path
                )


            return jsonify({

                "message": (
                    "This image does not appear "
                    "to show a valid civic problem. "
                    "Please upload an image of a "
                    "water, electricity, streetlight, "
                    "pothole, or road-related issue."
                ),

                "error_type": (
                    "NON_CIVIC_IMAGE"
                ),

                "image_classification": (
                    image_classification
                ),

                "image_confidence": (
                    image_confidence
                ),

                "image_label": (
                    image_label
                ),

                "is_civic": False

            }), 400


        # =================================================
        # IMAGE + DESCRIPTION MISMATCH
        # =================================================

        if (
            image_classification != "Other"
            and text_classification != "Other"
            and image_classification
            != text_classification
        ):

            print(
                "IMAGE / DESCRIPTION MISMATCH"
            )

            print(
                "Image:",
                image_classification
            )

            print(
                "Description:",
                text_classification
            )


            if (
                image_path
                and os.path.exists(image_path)
            ):

                os.remove(
                    image_path
                )


            return jsonify({

                "message": (
                    "Wrong image: image and "
                    "complaint description "
                    "do not match."
                ),

                "error_type": (
                    "IMAGE_DESCRIPTION_MISMATCH"
                ),

                "image_classification": (
                    image_classification
                ),

                "description_classification": (
                    text_classification
                ),

                "image_confidence": (
                    image_confidence
                ),

                "image_label": (
                    image_label
                ),

                "is_civic": True

            }), 400


    # =====================================================
    # DUPLICATE DETECTION
    # =====================================================

    duplicate_result = check_duplicate(
        description
    )


    print(
        "Duplicate Detection:",
        duplicate_result
    )


    # =====================================================
    # PRIORITY PREDICTION
    # =====================================================
    #
    # IMPORTANT:
    # Priority is now calculated using:
    #
    # 1. Complaint category
    # 2. Complaint description / severity
    # 3. Complaint location / area impact
    #
    # Location is passed to predict_priority().
    #

    priority = predict_priority(
        text_classification,
        description,
        location
    )


    print(
        "Priority:",
        priority
    )


    # =====================================================
    # DEPARTMENT ROUTING
    # =====================================================

    assigned_department = route_complaint(
        text_classification
    )


    print(
        "Assigned Department:",
        assigned_department
    )


    # =====================================================
    # COMPLAINT TITLE
    # =====================================================

    complaint_title = get_complaint_title(
        text_classification,
        description
    )


    # =====================================================
    # CHECK DUPLICATE
    # =====================================================

    is_duplicate = duplicate_result.get(
        "is_duplicate",
        False
    )


    # =====================================================
    # INITIAL STATUS
    # =====================================================

    if is_duplicate:

        status = "Rejected"

    else:

        status = "Pending"


    # =====================================================
    # CREATE COMPLAINT DATA
    # =====================================================

    complaint_data = {

        "user_id": str(user_id),

        "title": complaint_title,

        "description": description,

        "category": text_classification,

        "location": location,

        "image": image_path,

        "is_duplicate": is_duplicate,

        "duplicate_id": (
            duplicate_result.get(
                "duplicate_id"
            )
        ),

        "priority": priority,

        "department": text_classification,

        "assigned_department": (
            assigned_department
        ),

        "status": status
    }


    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    complaint_id = create_complaint(
        complaint_data
    )


    print(
        "Complaint Created:",
        complaint_id
    )


    # =====================================================
    # USER NOTIFICATION
    # =====================================================

    try:

        # -------------------------------------------------
        # DUPLICATE COMPLAINT
        # -------------------------------------------------

        if is_duplicate:

            notification_message = (

                f"{complaint_title} — "
                "Status: Rejected. "
                "Our system identified this "
                "complaint as a duplicate "
                "of an existing complaint."
            )


        # -------------------------------------------------
        # NORMAL COMPLAINT
        # -------------------------------------------------

        else:

            notification_message = (

                f"{complaint_title} — "
                "Status: Pending. "
                "Your complaint has been "
                "submitted successfully and "
                "is waiting for department action."
            )


        # -------------------------------------------------
        # CREATE IN-APP NOTIFICATION
        # -------------------------------------------------

        notification_id = create_notification(

            user_id=user_id,

            complaint_id=complaint_id,

            message=notification_message,

            complaint_title=complaint_title,

            status=status,

            category=text_classification
        )


        if notification_id:

            print(
                "Notification created:",
                notification_id
            )

        else:

            print(
                "Notification was not created."
            )


    except Exception as notification_error:

        # -------------------------------------------------
        # IMPORTANT
        # -------------------------------------------------
        # Notification failure should NOT make the
        # complaint submission fail.
        # -------------------------------------------------

        print(
            "Notification error:",
            notification_error
        )


    print(
        "================================="
    )


    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({

        "message": (
            "Complaint registered successfully"
        ),

        "complaint_id": complaint_id,

        "complaint_title": complaint_title,

        "description": description,

        "location": location,

        "category": text_classification,

        "classification": (
            text_classification
        ),

        "duplicate_detection": (
            duplicate_result
        ),

        "is_duplicate": is_duplicate,

        "duplicate_id": (
            duplicate_result.get(
                "duplicate_id"
            )
        ),

        "priority": priority,

        "department": (
            text_classification
        ),

        "assigned_department": (
            assigned_department
        ),

        "status": status,

        "image_uploaded": (
            True if image else False
        ),

        "image_classification": (
            image_result.get(
                "classification"
            )
            if image_result
            else None
        ),

        "image_confidence": (
            image_result.get(
                "confidence"
            )
            if image_result
            else None
        ),

        "image_label": (
            image_result.get(
                "label"
            )
            if image_result
            else None
        )

    }), 201


# =========================================================
# GET ALL COMPLAINTS
# =========================================================

@complaint_bp.route(
    "/",
    methods=["GET"]
)
def get_all_complaints():

    complaints = list(
        complaints_collection.find()
    )


    for complaint in complaints:

        complaint["_id"] = str(
            complaint["_id"]
        )


    return jsonify(
        complaints
    ), 200


# =========================================================
# GET SINGLE COMPLAINT
# =========================================================

@complaint_bp.route(
    "/<complaint_id>",
    methods=["GET"]
)
def get_complaint(
    complaint_id
):

    try:

        complaint = complaints_collection.find_one({

            "_id": ObjectId(
                complaint_id
            )

        })


        if not complaint:

            return jsonify({
                "message": (
                    "Complaint not found"
                )
            }), 404


        complaint["_id"] = str(
            complaint["_id"]
        )


        return jsonify(
            complaint
        ), 200


    except Exception:

        return jsonify({
            "message": (
                "Invalid complaint ID"
            )
        }), 400