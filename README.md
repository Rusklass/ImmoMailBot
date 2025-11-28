# Immo Bot

An automated Telegram bot that monitors your email for new real estate listings (ImmoScout24) and automatically sends a contact request.

## Features
- Monitors email for new notifications via IMAP.
- Extracts links to new listings.
- Uses Selenium (undetected-chromedriver) to open the listing.
- Automatically fills and sends a contact form.
- Sends status updates to Telegram.

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**
    - Copy `.env.example` to `.env`.
    - Fill in your details in `.env`:
        - `EMAIL_USER`: Your email address.
        - `EMAIL_PASS`: Your email app password (not your regular password!).
        - `TG_BOT_TOKEN`: Your Telegram Bot Token.
        - `TG_CHAT_ID`: Your Telegram Chat ID.

3.  **Run**
    ```bash
    python main.py
    ```

## Running on macOS

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Rusklass/ImmoMailBot.git
    cd ImmoMailBot
    ```

2.  **Install Dependencies**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Run the Bot**
    ```bash
    python3 main.py
    ```

4.  **Create macOS App (Executable)**
    To create a standalone app that you can double-click:
    ```bash
    pyinstaller --onefile --name ImmoBot --windowed main.py
    ```
    - The app will be in the `dist` folder.
    - Note: You might need to allow the app in "System Settings > Privacy & Security" if it's blocked.

## Disclaimer
This bot is for educational purposes. Automated interaction with websites may violate their Terms of Service. Use at your own risk.
