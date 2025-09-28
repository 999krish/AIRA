import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from pathlib import Path

USERS_FILE = Path("users.json")

# --- 1. LOCAL USER MANAGEMENT ---

def _load_user_data():
    """Loads user data from the local JSON file."""
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def _save_user_data(data):
    """Saves user data to the local JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def sign_up_user_local(email, password):
    """Signs up a new user and saves to the local file."""
    users = _load_user_data()
    if email in users:
        return None, "An account with this email already exists."
    
    # In a real app, hash the password! For this demo, we store it directly.
    users[email] = {"password": password}
    _save_user_data(users)
    return email, None # Return email as a user identifier

def login_user_local(email, password):
    """Logs in a user by checking credentials against the local file."""
    users = _load_user_data()
    if email not in users:
        return None, "No account found with this email."
    
    if users[email]["password"] == password:
        return email, None # Login successful
    else:
        return None, "Incorrect password."

# --- 2. EMAIL NOTIFICATION ---

def send_email_notification(recipient_email: str, subject: str, body: str):
    """
    Sends an email notification using an Outlook account via SMTP.
    Credentials must be stored in Streamlit's secrets.toml.
    """
    try:
        # Fetch credentials securely from secrets
        sender_email = st.secrets["email_credentials"]["sender_email"]
        sender_password = st.secrets["email_credentials"]["sender_password"]
        smtp_server = "smtp.office365.com"
        smtp_port = 587
    except KeyError:
        return False, "Email credentials are not configured in secrets.toml."

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        return True, "Email sent successfully!"
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False, f"Failed to send email: {e}"
