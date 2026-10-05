import os
import smtplib
import ssl

from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

SENDER_EMAIL = os.getenv("MAIL_USERNAME")
SENDER_PASSWORD = os.getenv("MAIL_PASSWORD")
print("MAIL USER:", SENDER_EMAIL)
print("MAIL PASSWORD LOADED:", bool(SENDER_PASSWORD))

def send_otp_email(receiver_email, otp):

    if not SENDER_EMAIL:
        print("Email Error: MAIL_USERNAME is missing")
        return False

    if not SENDER_PASSWORD:
        print("Email Error: MAIL_PASSWORD is missing")
        return False

    try:
        message = EmailMessage()

        message["Subject"] = "CivicSense AI - Password Reset OTP"
        message["From"] = SENDER_EMAIL
        message["To"] = receiver_email

        message.set_content(
            f"""
Hello,

Your CivicSense AI password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset,
please ignore this email.

Regards,
CivicSense AI Team
"""
        )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT,
            context=context,
            timeout=20
        ) as server:

            server.login(
                SENDER_EMAIL,
                SENDER_PASSWORD
            )

            server.send_message(message)

        print("OTP email sent successfully to:", receiver_email)

        return True

    except Exception as error:

        print("Email sending error:", error)

        return False