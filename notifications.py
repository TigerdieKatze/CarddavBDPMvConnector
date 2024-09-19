import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import CONFIG, logger

def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = CONFIG["SMTP_USERNAME"]
    msg['To'] = CONFIG["NOTIFICATION_EMAIL"]
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(CONFIG["SMTP_SERVER"], CONFIG["SMTP_PORT"]) as server:
            server.starttls()
            server.login(CONFIG["SMTP_USERNAME"], CONFIG["SMTP_PASSWORD"])
            server.send_message(msg)
        logger.info(f"Email sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")