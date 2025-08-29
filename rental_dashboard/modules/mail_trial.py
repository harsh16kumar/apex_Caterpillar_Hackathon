import smtplib
from email.mime.text import MIMEText

def send_email_alert():
    recipient = "harshnpng@gmail.com"
    subject = "Vehicle under used"
    body = "Vehicle Underused"

    sender_email = "harshkumar15774@gmail.com"
    app_password = "siunhidntjzxbhvc"
    recipient_email = recipient


    if not sender_email or not app_password:
        raise ValueError("Email credentials not set in environment variables")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #     server.login(sender_email, sender_password)
    #     server.sendmail(sender_email, recipient, msg.as_string())

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

    print(f"Email sent to {recipient}")