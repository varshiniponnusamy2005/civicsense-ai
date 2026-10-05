import re
import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify

from models.user_model import (
    create_user,
    get_user_by_email,
    get_user_by_mobile,
    get_user_by_identifier,
    verify_password,
    update_password
)

from utils.email_service import send_otp_email


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# ==================================================
# DEPARTMENT USERS
# ==================================================

DEPARTMENT_MEMBERS = {

    "varshiniknpm@gmail.com": {
        "name": "Public Works Officer",
        "department": "Public Works",
        "role": "department"
    },

    "santhipriyadarshini2@gmail.com": {
        "name": "Water Supply Officer",
        "department": "Water Supply",
        "role": "department"
    },

    "dhivyadarshinipalanivel@gmail.com": {
        "name": "Electricity Officer",
        "department": "Electricity",
        "role": "department"
    }
}


# ==================================================
# DEVELOPMENT DEPARTMENT PASSWORD
# ==================================================

DEPARTMENT_PASSWORD = "CivicSense@123"


# ==================================================
# OTP STORAGE
# ==================================================

password_reset_otps = {}


# ==================================================
# VALIDATION HELPERS
# ==================================================

def is_valid_email(email):

    if not email:
        return False

    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    return re.match(
        pattern,
        email
    ) is not None


def is_valid_mobile(mobile):

    if not mobile:
        return False

    pattern = r"^[6-9]\d{9}$"

    return re.match(
        pattern,
        mobile
    ) is not None


# ==================================================
# REGISTER
# ==================================================

@auth_bp.route(
    "/register",
    methods=["POST"]
)
def register():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        name = str(
            data.get("name", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip().lower()

        mobile = str(
            data.get("mobile", "")
        ).strip()

        password = str(
            data.get("password", "")
        )

        # ------------------------------------------
        # NAME
        # ------------------------------------------

        if not name:

            return jsonify({
                "message":
                    "Full name is required."
            }), 400

        # ------------------------------------------
        # EMAIL / MOBILE
        # ------------------------------------------

        if not email and not mobile:

            return jsonify({
                "message":
                    "Please provide either email or mobile number."
            }), 400

        # ------------------------------------------
        # EMAIL VALIDATION
        # ------------------------------------------

        if email and not is_valid_email(email):

            return jsonify({
                "message":
                    "Please enter a valid email address."
            }), 400

        # ------------------------------------------
        # MOBILE VALIDATION
        # ------------------------------------------

        if mobile and not is_valid_mobile(
            mobile
        ):

            return jsonify({
                "message":
                    "Please enter a valid 10-digit mobile number."
            }), 400

        # ------------------------------------------
        # PASSWORD
        # ------------------------------------------

        if not password:

            return jsonify({
                "message":
                    "Password is required."
            }), 400

        if len(password) < 8:

            return jsonify({
                "message":
                    "Password must contain at least 8 characters."
            }), 400

        # ------------------------------------------
        # DUPLICATE EMAIL
        # ------------------------------------------

        if email:

            existing_email_user = (
                get_user_by_email(email)
            )

            if existing_email_user:

                return jsonify({
                    "message":
                        "An account with this email already exists."
                }), 409

        # ------------------------------------------
        # DUPLICATE MOBILE
        # ------------------------------------------

        if mobile:

            existing_mobile_user = (
                get_user_by_mobile(mobile)
            )

            if existing_mobile_user:

                return jsonify({
                    "message":
                        "An account with this mobile number already exists."
                }), 409

        # ------------------------------------------
        # CREATE USER
        # ------------------------------------------

        user_data = {
            "name": name,
            "email": email if email else None,
            "mobile": mobile if mobile else None,
            "role": "user",
            "password": password
        }

        user_id = create_user(
            user_data
        )

        # ------------------------------------------
        # SUCCESS
        # ------------------------------------------

        return jsonify({

            "message":
                "Account created successfully.",

            "user_id":
                user_id

        }), 201

    except Exception as error:

        print(
            "Registration error:",
            error
        )

        return jsonify({
            "message":
                "Unable to create account."
        }), 500


# ==================================================
# LOGIN
# ==================================================

@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        identifier = str(
            data.get("identifier", "")
        ).strip()

        password = str(
            data.get("password", "")
        )

        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not identifier:

            return jsonify({
                "message":
                    "Email, mobile number or name is required."
            }), 400

        if not password:

            return jsonify({
                "message":
                    "Password is required."
            }), 400

        # ------------------------------------------
        # NORMALIZE
        # ------------------------------------------

        normalized_identifier = (
            identifier.lower()
            if "@" in identifier
            else identifier
        )

        # ==================================================
        # DEPARTMENT LOGIN
        # ==================================================

        department_member = (
            DEPARTMENT_MEMBERS.get(
                normalized_identifier
            )
        )

        if department_member:

            if password != DEPARTMENT_PASSWORD:

                return jsonify({
                    "message":
                        "Invalid department login credentials."
                }), 401

            return jsonify({

                "message":
                    "Login successful.",

                "user": {

                    "_id":
                        "department-" +
                        normalized_identifier,

                    "name":
                        department_member["name"],

                    "email":
                        normalized_identifier,

                    "mobile":
                        None,

                    "department":
                        department_member["department"],

                    "department_name":
                        department_member["department"],

                    "assigned_department":
                        department_member["department"],

                    "role":
                        "department"
                }

            }), 200

        # ==================================================
        # CITIZEN LOGIN
        # ==================================================

        user = get_user_by_identifier(
            identifier
        )

        if not user:

            return jsonify({
                "message":
                    "Invalid email/mobile/name or password."
            }), 401

        # ------------------------------------------
        # PASSWORD
        # ------------------------------------------

        password_valid = verify_password(
            password,
            user.get("password")
        )

        if not password_valid:

            return jsonify({
                "message":
                    "Invalid email/mobile/name or password."
            }), 401

        # ------------------------------------------
        # SUCCESS
        # ------------------------------------------

        return jsonify({

            "message":
                "Login successful.",

            "user": {

                "_id":
                    str(
                        user.get("_id")
                    ),

                "name":
                    user.get("name"),

                "email":
                    user.get("email"),

                "mobile":
                    user.get("mobile"),

                "role":
                    user.get(
                        "role",
                        "user"
                    ),

                "department":
                    user.get(
                        "department"
                    ),

                "department_name":
                    user.get(
                        "department_name"
                    ),

                "assigned_department":
                    user.get(
                        "assigned_department"
                    )
            }

        }), 200

    except Exception as error:

        print(
            "Login error:",
            error
        )

        return jsonify({
            "message":
                "Unable to login."
        }), 500


# ==================================================
# FORGOT PASSWORD - SEND OTP
# ==================================================

@auth_bp.route(
    "/forgot-password",
    methods=["POST"]
)
def forgot_password():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        identifier = str(
            data.get("identifier", "")
        ).strip()

        if not identifier:

            return jsonify({
                "message":
                    "Please enter your registered email or mobile number."
            }), 400

        # ------------------------------------------
        # FIND USER
        # ------------------------------------------

        user = get_user_by_identifier(
            identifier
        )

        if not user:

            return jsonify({
                "message":
                    "No account found with the given email or mobile number."
            }), 404

        # ------------------------------------------
        # GET REGISTERED EMAIL
        # ------------------------------------------

        registered_email = (
            user.get("email")
        )

        if not registered_email:

            return jsonify({
                "message":
                    "This account does not have a registered email address."
            }), 400

        registered_email = (
            registered_email
            .strip()
            .lower()
        )

        # ------------------------------------------
        # GENERATE 6 DIGIT OTP
        # ------------------------------------------

        otp = str(
            secrets.randbelow(900000) + 100000
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=5)
        )

        # ------------------------------------------
        # STORE OTP
        # ------------------------------------------

        password_reset_otps[
            registered_email
        ] = {

            "otp": otp,

            "expires_at":
                expires_at,

            "verified": False
        }

        # ------------------------------------------
        # SEND EMAIL
        # ------------------------------------------

        email_sent = send_otp_email(
            registered_email,
            otp
        )

        if not email_sent:

            password_reset_otps.pop(
                registered_email,
                None
            )

            return jsonify({
                "message":
                    "Unable to send OTP email. Please check email configuration."
            }), 500

        print(
            "Password reset OTP generated for:",
            registered_email
        )

        return jsonify({

            "message":
                "OTP has been sent to your registered email address.",

            "email":
                registered_email

        }), 200

    except Exception as error:

        print(
            "Forgot password error:",
            error
        )

        return jsonify({

            "message":
                "Unable to process password reset request."

        }), 500


# ==================================================
# VERIFY OTP
# ==================================================

@auth_bp.route(
    "/verify-reset-otp",
    methods=["POST"]
)
def verify_reset_otp():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        email = str(
            data.get("email", "")
        ).strip().lower()

        otp = str(
            data.get("otp", "")
        ).strip()

        if not email or not otp:

            return jsonify({
                "message":
                    "Email and OTP are required."
            }), 400

        reset_data = password_reset_otps.get(
            email
        )

        if not reset_data:

            return jsonify({
                "message":
                    "OTP not found or expired. Please request a new OTP."
            }), 400

        # ------------------------------------------
        # CHECK EXPIRY
        # ------------------------------------------

        current_time = datetime.now(
            timezone.utc
        )

        if current_time > reset_data["expires_at"]:

            password_reset_otps.pop(
                email,
                None
            )

            return jsonify({
                "message":
                    "OTP has expired. Please request a new OTP."
            }), 400

        # ------------------------------------------
        # CHECK OTP
        # ------------------------------------------

        if otp != reset_data["otp"]:

            return jsonify({
                "message":
                    "Invalid OTP."
            }), 400

        # ------------------------------------------
        # OTP VERIFIED
        # ------------------------------------------

        reset_data["verified"] = True

        return jsonify({

            "message":
                "OTP verified successfully."

        }), 200

    except Exception as error:

        print(
            "OTP verification error:",
            error
        )

        return jsonify({

            "message":
                "Unable to verify OTP."

        }), 500


# ==================================================
# RESET PASSWORD
# ==================================================

@auth_bp.route(
    "/reset-password",
    methods=["POST"]
)
def reset_password():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        email = str(
            data.get("email", "")
        ).strip().lower()

        new_password = str(
            data.get("new_password", "")
        )

        confirm_password = str(
            data.get("confirm_password", "")
        )

        if not email:

            return jsonify({
                "message":
                    "Email is required."
            }), 400

        if not new_password:

            return jsonify({
                "message":
                    "New password is required."
            }), 400

        if len(new_password) < 8:

            return jsonify({
                "message":
                    "Password must contain at least 8 characters."
            }), 400

        if new_password != confirm_password:

            return jsonify({
                "message":
                    "Passwords do not match."
            }), 400

        # ------------------------------------------
        # CHECK OTP VERIFICATION
        # ------------------------------------------

        reset_data = password_reset_otps.get(
            email
        )

        if not reset_data:

            return jsonify({
                "message":
                    "Password reset session expired. Please request a new OTP."
            }), 400

        if not reset_data.get(
            "verified",
            False
        ):

            return jsonify({
                "message":
                    "Please verify the OTP first."
            }), 400

        # ------------------------------------------
        # CHECK USER
        # ------------------------------------------

        user = get_user_by_email(
            email
        )

        if not user:

            return jsonify({
                "message":
                    "User account not found."
            }), 404

        # ------------------------------------------
        # UPDATE PASSWORD
        # ------------------------------------------

        password_updated = update_password(
            email,
            new_password
        )

        if not password_updated:

            return jsonify({
                "message":
                    "Unable to update password."
            }), 500

        # ------------------------------------------
        # REMOVE OTP
        # ------------------------------------------

        password_reset_otps.pop(
            email,
            None
        )

        return jsonify({

            "message":
                "Password reset successfully. Please login with your new password."

        }), 200

    except Exception as error:

        print(
            "Reset password error:",
            error
        )

        return jsonify({

            "message":
                "Unable to reset password."

        }), 500