import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_disease_alert_email(
    disease: str,
    severity: str,
    spread_risk: str,
    message: str,
    latitude: float | None = None,
    longitude: float | None = None,
):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        raise ValueError("Email configuration is missing in .env")

    subject = f"[AloeGreen Alert] {disease} detected - Severity: {severity}"

    location_text = "Location not available"
    if latitude is not None and longitude is not None:
        location_text = (
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}\n"
            f"Google Maps: https://www.google.com/maps?q={latitude},{longitude}"
        )

    body = f"""
AloeGreen Community Disease Alert

Disease: {disease}
Severity: {severity}
Spread Risk: {spread_risk}

Custom Message:
{message}

Plant Site Location:
{location_text}
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())