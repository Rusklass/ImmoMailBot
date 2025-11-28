import imaplib
import time
import os
from email.mime.text import MIMEText
from email.utils import formatdate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")

def simulate_incoming_email():
    print("🚀 Simulating incoming ImmoScout email...")

    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Error: Credentials missing in .env")
        return

    # Create a fake email
    subject = "Neue Angebote: 3 Zimmer in Bonn"
    # A sample body with a link that matches the regex in main.py
    # Regex: https?://(?:push\.search\.is24\.de|go\.immobilienscout24\.de)[^\s"\'<>]+
    body = """
    Hallo,
    
    hier sind neue Angebote für Sie:
    
    Expose ansehen:
    https://www.immobilienscout24.de/expose/123456789
    
    Viel Erfolg!
    """
    
    msg = MIMEText(body)
    msg["From"] = "myscout@immobilienscout24.de"
    msg["To"] = EMAIL_USER
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        # Append to Inbox
        # Note: Some providers might put this in Sent, but usually APPEND works for Inbox too if allowed.
        # If it fails, we might need to use SMTP to send to self, but APPEND is "simulation" without network sending.
        result = mail.append("INBOX", None, None, msg.as_bytes())
        
        if result[0] == 'OK':
            print("✅ Test email successfully added to INBOX!")
            print("👉 Now run 'python main.py' to see if the bot picks it up.")
        else:
            print(f"❌ Failed to append email: {result}")
            
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simulate_incoming_email()
