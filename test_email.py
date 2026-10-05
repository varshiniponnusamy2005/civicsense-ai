import os
import smtplib
import ssl
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("MAIL_USERNAME")
password = os.getenv("MAIL_PASSWORD")

print("Email:", email)
print("Password loaded:", bool(password))

try:
    context = ssl.create_default_context()

    print("Connecting to Gmail...")

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=context,
        timeout=20
    ) as server:

        print("Connected to Gmail")
        print("Trying login...")

        server.login(email, password)

        print("Gmail login successful!")

except Exception as error:
    print("ERROR:", repr(error))