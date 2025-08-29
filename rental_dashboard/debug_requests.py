from database.db import get_all_rental_requests
from modules.mail_trial import send_email_alert

if __name__ == "__main__":
    send_email_alert()
