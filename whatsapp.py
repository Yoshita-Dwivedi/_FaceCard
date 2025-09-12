from twilio.rest import Client
import datetime
import os
from dotenv import load_dotenv

# Load variables from your .env file
load_dotenv()

def send_whatsapp_notification(student_name, student_whatsapp_number, subject):
    # Get your new keys securely from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    # --- Definitive Test for Twilio Keys ---
    print("--- Running Definitive Test for Twilio Keys ---")
    print(f"DEBUG: Loaded Account SID: {account_sid}")
    print(f"DEBUG: Auth Token Loaded?: {'Yes' if auth_token else 'NO, IT IS EMPTY'}")
    print("---------------------------------------------")

    # Check if keys were loaded successfully
    if not account_sid or not auth_token:
        print("ERROR: Twilio credentials were not loaded from the .env file.")
        return

    # Create a Twilio client
    client = Client(account_sid, auth_token)
    
    # Prepare the message
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    message_body = f"Hi {student_name}, your attendance for {subject} has been successfully marked at {current_time}. ✅"
    
    # Try to send the message
    try:
        message = client.messages.create(
                              body=message_body,
                              from_='whatsapp:+14155238886', # This is the Twilio Sandbox number
                              to=f'whatsapp:{student_whatsapp_number}'
                          )
        print(f"Message sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"Error sending Twilio message: {e}")