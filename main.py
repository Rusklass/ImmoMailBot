import imaplib
import email
import re
import time
import os
import sys
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv, set_key

# --- CONSTANTS ---
ENV_FILE = ".env"
CHROME_PROFILE_PATH = os.path.join(os.getcwd(), "immo_profile")

MESSAGE_TEXT = """
Sehr geehrte Damen und Herren,

wir sind das Ehepaar Klassen und suchen in Bonn eine ruhige und gepflegte Wohnung, in die wir unsere langjährige Stabilität und Ordnung einbringen möchten.
Einige Fakten, die uns zu einem ausgezeichneten und unkomplizierten Mieter machen:
Langjährige Stabilität: Wir sind seit über 30 Jahren verheiratet und suchen ein Zuhause, in dem wir uns langfristig wohlfühlen können. Wir garantieren Ihnen ein verlässliches Mietverhältnis, das keinerlei Fluktuation unterliegt.
Finanzielle Planbarkeit: Die Mietzahlungen sind absolut gesichert, da sie direkt vom Jobcenter Bonn übernommen werden. Das Risiko eines Zahlungsausfalls entfällt für Sie vollständig. Alle Bescheide und Unterlagen hierzu liegen uns vor und können sofort eingereicht werden.
Erhalt Ihres Eigentums: Wir sind Nichtraucher und tierfrei. Wir legen größten Wert auf Ordnung und einen respektvollen Umgang mit der Wohnung, da wir selbst gerne in einer gepflegten Umgebung leben.
Über eine Einladung zur Besichtigung würden wir uns sehr freuen, um Ihnen persönlich zu zeigen, dass wir die richtigen Mieter für Ihr Objekt sind.


Mit freundlichen Grüßen,
Alexander Klassen
"""

# --- SETUP WIZARD ---
def setup_wizard():
    """Interactive setup for first-time run"""
    print("------------------------------------------------")
    print("🤖 Immo Bot Setup Wizard")
    print("------------------------------------------------")
    print("It seems like you haven't configured the bot yet.")
    print("Please enter your credentials below. They will be saved securely locally.\n")

    email_user = input("Enter your Email (Gmail): ").strip()
    email_pass = input("Enter your Email App Password: ").strip()
    tg_token = input("Enter your Telegram Bot Token: ").strip()
    tg_chat_id = input("Enter your Telegram Chat ID: ").strip()

    # Save to .env
    with open(ENV_FILE, "w") as f:
        f.write(f"EMAIL_USER={email_user}\n")
        f.write(f"EMAIL_PASS={email_pass}\n")
        f.write(f"IMAP_SERVER=imap.gmail.com\n")
        f.write(f"TG_BOT_TOKEN={tg_token}\n")
        f.write(f"TG_CHAT_ID={tg_chat_id}\n")
    
    print("\n✅ Configuration saved! Starting bot...\n")
    load_dotenv(override=True)

# --- FUNCTIONS ---

def get_env_variable(var_name):
    val = os.getenv(var_name)
    if not val:
        return None
    return val

def send_telegram(text):
    """Send notification to Telegram"""
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    
    if not token or not chat_id:
        print(f"⚠️ Telegram not configured. Skipping message: {text}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_links_from_email():
    """Check email for new ImmoScout/Immowelt links"""
    links = []
    
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")

    if not email_user or not email_pass:
        print("❌ Email credentials missing.")
        return links

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        # Search for unread emails
        status, messages = mail.search(None, '(UNSEEN)')
        
        if status != "OK":
            return links

        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            subject = getattr(msg.get("subject"), "decode", lambda: msg.get("subject"))() 
            
            print(f"Checking email: {subject}")
            
            # Parse email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            
            # Search for link
            found_urls = re.findall(r'https?://(?:push\.search\.is24\.de|go\.immobilienscout24\.de|www\.immobilienscout24\.de)[^\s"\'<>]+', body)
            
            for url in found_urls:
                url = url.split('"')[0].split('<')[0]
                links.append(url)

    except Exception as e:
        print(f"Email Error: {e}")
    
    if len(links) > 0:
        print(f"🔎 Found {len(links)} new offers!")
        send_telegram(f"🔎 Found {len(links)} new offers!")
        for url in links:
             send_telegram(f"👉 Link: {url}")

    return links

def process_link(driver, url):
    """Follow the link and send message"""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # 1. Check for Cookie banner
        try:
            cookie_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "gdpr-banner-accept"))
            )
            cookie_btn.click()
        except:
            pass 

        # 2. Look for "Kontakt" button
        contact_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-qa="sendButton"]')))
        contact_btn.click()
        
        # 3. Enter text
        time.sleep(2) 
        textarea = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
        
        textarea.clear()
        textarea.send_keys(MESSAGE_TEXT)
        
        # 4. Send
        submit_btn = driver.find_element(By.CSS_SELECTOR, '[data-qa="sendButtonBasic"]') 
        submit_btn.click()
        
        print(f"Message sent: {url}")
        send_telegram(f"✅ Application sent automatically!\n{url}")
        
    except Exception as e:
        error_msg = f"❌ Failed to send application: {e}"
        print(error_msg)
        send_telegram(error_msg + f"\nLink: {url}")

# --- MAIN LOOP ---

def main():
    # 1. Load config or run wizard
    load_dotenv()
    
    if not os.getenv("EMAIL_USER") or not os.getenv("TG_BOT_TOKEN"):
        setup_wizard()

    print("🤖 Bot started. Press Ctrl+C to exit.")
    send_telegram("🤖 Bot started and is monitoring email.")

    # Browser setup
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}") 
    
    driver = uc.Chrome(options=options)
    
    try:
        while True:
            links = get_links_from_email()
            
            for url in links:
                process_link(driver, url)
            
            time.sleep(30) 
            
    except KeyboardInterrupt:
        print("Stopping bot...")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()