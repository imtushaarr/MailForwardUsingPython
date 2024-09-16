import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# IMAP and SMTP server settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Email credentials
SENDER_EMAIL = "sender_mail@gmail.com"  # Replace with your email
SENDER_PASSWORD = "less_secure_password"  # Replace with your app-specific password
FORWARD_TO_EMAIL = "forward_mail@gmail.com"  # Replace with the email to forward to

def fetch_latest_email():
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(SENDER_EMAIL, SENDER_PASSWORD)
    mail.select("inbox")

    # Search for all emails in the inbox
    status, messages = mail.search(None, "ALL")

    if status != "OK":
        print("Failed to retrieve emails.")
        return None

    # Get the list of email IDs
    email_ids = messages[0].split()

    # Fetch the latest email
    latest_email_id = email_ids[-1]
    status, data = mail.fetch(latest_email_id, "(RFC822)")

    if status != "OK":
        print("Failed to fetch the email.")
        return None

    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)

    mail.logout()
    return msg

def forward_email(msg):
    # Create a new email message for forwarding
    forward_msg = MIMEMultipart()
    forward_msg["From"] = SENDER_EMAIL
    forward_msg["To"] = FORWARD_TO_EMAIL
    forward_msg["Subject"] = "Fwd: " + msg["Subject"]

    # If the message is multipart (e.g., with attachments), handle each part
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain":
                part_payload = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                forward_msg.attach(MIMEText(part_payload, "plain"))
            elif content_type == "text/html":
                part_payload = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                forward_msg.attach(MIMEText(part_payload, "html"))
            # Handle other content types if needed
    else:
        part_payload = msg.get_payload(decode=True).decode(msg.get_content_charset(), 'ignore')
        forward_msg.attach(MIMEText(part_payload, "plain"))

    # Send the email via SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, FORWARD_TO_EMAIL, forward_msg.as_string())

if __name__ == "__main__":
    latest_email = fetch_latest_email()

    if latest_email:
        forward_email(latest_email)
        print(f"Email forwarded to {FORWARD_TO_EMAIL}")
    else:
        print("No email to forward.")
