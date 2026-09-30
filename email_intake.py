"""
Communication / Intake Agent - checks an inbox for new emails with
document attachments (PDF/image) and automatically runs each one
through the existing document pipeline (run_pipeline.py).

Uses IMAP with a Gmail App Password - simpler to set up than the full
Gmail API OAuth flow, and functionally does the same job for this
project: reading an inbox and pulling attachments.

Setup (one-time):
1. On your Gmail account, turn on 2-Step Verification (Google Account
   -> Security -> 2-Step Verification).
2. Go to https://myaccount.google.com/apppasswords, create an app
   password (name it e.g. "autoops"), and copy the 16-character code.
3. Add to .env:
       EMAIL_ADDRESS=youraddress@gmail.com
       EMAIL_APP_PASSWORD=<the 16-character app password, no spaces>

Usage:
    python email_intake.py
    (checks once and exits - run it again anytime, or see the note
    at the bottom about running it on a loop)
"""
import os
import imaplib
import email
from datetime import datetime
from dotenv import load_dotenv

from run_pipeline import run as run_document_pipeline

load_dotenv()

IMAP_SERVER = "imap.gmail.com"
INCOMING_DIR = "sample_docs/incoming"
ALLOWED_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png")


def check_inbox():
    email_address = os.environ["EMAIL_ADDRESS"]
    app_password = os.environ["EMAIL_APP_PASSWORD"]

    os.makedirs(INCOMING_DIR, exist_ok=True)

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(email_address, app_password)
    mail.select("inbox")

    # UNSEEN = only new/unread emails - fetching marks them read,
    # so each email is only processed once across runs.
    status, message_ids = mail.search(None, "UNSEEN")
    ids = message_ids[0].split()

    if not ids:
        print("No new emails.")
        mail.logout()
        return

    print(f"Found {len(ids)} new email(s).")

    for msg_id in ids:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        sender = msg.get("From")
        subject = msg.get("Subject")
        print(f"\nProcessing email from {sender} - subject: {subject}")

        found_attachment = False
        for part in msg.walk():
            filename = part.get_filename()
            if not filename or not filename.lower().endswith(ALLOWED_EXTENSIONS):
                continue

            found_attachment = True
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(INCOMING_DIR, safe_filename)

            with open(filepath, "wb") as f:
                f.write(part.get_payload(decode=True))

            print(f"  Saved attachment: {filepath}")
            print(f"  Running document pipeline...")
            try:
                run_document_pipeline(filepath)
            except Exception as e:
                print(f"  ERROR processing {filepath}: {e}")

        if not found_attachment:
            print("  No document attachments found in this email - skipped.")

    mail.logout()


if __name__ == "__main__":
    check_inbox()

# Note: this checks the inbox ONCE per run. For a live "always watching"
# demo, you'd wrap check_inbox() in a loop with a delay, e.g.:
#
#   import time
#   while True:
#       check_inbox()
#       time.sleep(60)  # check every 60 seconds
#
# Keep it as single-run for now while testing - a loop is easy to add
# once you're confident this works correctly.