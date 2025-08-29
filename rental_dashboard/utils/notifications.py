import smtplib
from email.mime.text import MIMEText

def send_email_node(state: dict) -> dict:
    """
    Sends an email using values directly from the given state dict.
    
    Expected keys in state:
      - email_id (recipient email)
      - subject
      - message
      - sender_email (optional, defaults to harshkumar15774@gmail.com)
      - app_password (optional, your Gmail app password)
    """

    recipient = state.get("email_id")
    subject = state.get("subject")
    body = state.get("message")

    sender_email = state.get("sender_email", "harshkumar15774@gmail.com")
    app_password = state.get("app_password", "siunhidntjzxbhvc")

    if not recipient:
        raise ValueError("Missing 'email_id' in state.")
    if not subject:
        raise ValueError("Missing 'subject' in state.")
    if not body:
        raise ValueError("Missing 'message' in state.")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

    print(f"✅ Email sent to {recipient} with subject '{subject}'")
    return state
