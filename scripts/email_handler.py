import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
import smtplib
import time
import pandas as pd
import time
from datetime import datetime, timedelta
import smtplib


# ---------- CONFIGURATION ----------
IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
EMAIL = 'leakhaa.warehouse.bot123@gmail.com'
PASSWORD = 'owpc kbzs lskr cfte'  # Gmail app password
WAREHOUSE_TEAM_EMAIL = 'leakhaganesh@gmail.com'  # Replace with your target email address

# ---------- READ UNREAD EMAILS AND RETURN LIST ----------
def get_unread_emails(from_filter=None):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    result, data = mail.search(None, 'UNSEEN')
    mail_ids = data[0].split()

    email_data = []

    for mail_id in mail_ids:
        result, message_data = mail.fetch(mail_id, '(RFC822)')
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg['subject']
        sender_email = msg['From']

        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # Log for debug
        print(f"Subject: {subject}")
        print("Body Preview:", body[:100].encode('ascii', errors='replace').decode('ascii'))

        # Send confirmation
        confirmation = f"Mail with subject '{subject}' has been read successfully."
        send_email(WAREHOUSE_TEAM_EMAIL, "Mail Read Confirmation", confirmation)

        # Append to list
        email_data.append((subject.strip(), body.strip(), sender_email.strip()))

    return email_data


def wait_for_excel_from_sap(subject_keyword="SAP Reply", timeout=180, check_interval=15):
    print("Waiting for SAP Excel mail...")

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")

            status, data = mail.search(None, f'(UNSEEN SUBJECT "{subject_keyword}")')

            for num in data[0].split():
                typ, msg_data = mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                for part in msg.walk():
                    if part.get_content_type() == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        attachment = part.get_payload(decode=True)
                        df = pd.read_excel(io.BytesIO(attachment))
                        print("Excel received from SAP.")
                        return df

            time.sleep(check_interval)
        except Exception as e:
            print("Error while checking mail:", e)

    print("No reply received from SAP in given time.")
    return None

def wait_for_trigger_confirmation_from_sap(keyword: str, timeout_minutes: int = 10):
    """
    Waits for an email from SAP confirming action (Triggered/Not Triggered).
    Returns either 'triggered', 'not_triggered', or None if timeout.
    """
 

    deadline = datetime.now() + timedelta(minutes=timeout_minutes)

    while datetime.now() < deadline:
        emails = get_unread_emails(from_filter="warehouse.sap.123@gmail.com")
        for subject, body,sender in emails:
            if keyword.lower() in body.lower():
                if "triggered" in body.lower():
                    return "triggered"
                elif "not triggered" in body.lower():
                    return "not_triggered"
        time.sleep(30)
    return None

# ---------- SEND EMAIL ----------
def send_email(to, subject, body, html_format=False):
    msg = MIMEMultipart()  # ✅ Correctly create a multipart email
    msg['From'] = EMAIL
    msg['To'] = to
    msg['Subject'] = subject

    if html_format:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    # ✅ Send the email using SMTP
    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
