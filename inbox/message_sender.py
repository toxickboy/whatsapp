import requests
import json
import csv
import time
import logging
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f'whatsapp_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class WhatsAppBulkSender:
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.success_count = 0
        self.failed_count = 0
        self.failed_messages = []

    def send_message(self, recipient_phone: str, message: str, use_template: bool = False) -> bool:
        """Send a WhatsApp message (text or template)"""

        if use_template:
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "template",
                "template": {
                    "name": "hello_world",
                    "language": {"code": "en_US"}
                }
            }
        else:
            payload = { 
                        "messaging_product": "whatsapp",
                        "to": recipient_phone,
                        "type": "text",
                        "text": {"body": message}

            }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            try:
                resp_json = response.json()
            except Exception:
                resp_json = {"raw": response.text}

            if response.status_code == 200:
                logging.info(f"[SUCCESS] Sent to {recipient_phone} | Response: {resp_json}")
                self.success_count += 1
                return True
            else:
                error_msg = resp_json.get("error", {}).get("message", "Unknown error")
                logging.error(f"[FAILED] {recipient_phone} | {error_msg} | Full: {resp_json}")
                self.failed_count += 1
                self.failed_messages.append({"phone": recipient_phone, "error": error_msg})
                return False

        except Exception as e:
            logging.error(f"[EXCEPTION] {recipient_phone} | {str(e)}")
            self.failed_count += 1
            self.failed_messages.append({"phone": recipient_phone, "error": str(e)})
            return False

    def personalize_message(self, template: str, data: Dict) -> str:
        try:
            return template.format(**data)
        except KeyError as e:
            logging.warning(f"Missing placeholder {e} in template")
            return template

    def load_contacts_from_csv(self, csv_file: str) -> List[Dict]:
        contacts = []
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    contacts.append(row)
            logging.info(f"Loaded {len(contacts)} contacts from {csv_file}")
            return contacts
        except Exception as e:
            logging.error(f"Error loading CSV: {str(e)}")
            return []

    def send_bulk_messages(self, contacts: List[Dict], message_template: str,
                           delay_seconds: float = 0.0, use_template: bool = False):
        total = len(contacts)
        logging.info(f"Starting bulk send to {total} contacts...")

        for idx, contact in enumerate(contacts, 1):
            phone = contact.get("phone", "").strip()
            if not phone:
                logging.warning(f"Skipping contact {idx}: No phone number")
                continue

            phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            message = self.personalize_message(message_template, contact)

            logging.info(f"[{idx}/{total}] Sending to {phone}...")
            self.send_message(phone, message, use_template=use_template)

            if idx < total:
                time.sleep(delay_seconds)

        self.print_summary()

    def print_summary(self):
        logging.info("\n" + "="*50)
        logging.info("SENDING SUMMARY")
        logging.info("="*50)
        logging.info(f"Total Successful: {self.success_count}")
        logging.info(f"Total Failed: {self.failed_count}")

        if self.failed_messages:
            failed_file = f"failed_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(failed_file, "w") as f:
                json.dump(self.failed_messages, f, indent=2)
            logging.info(f"Failed messages saved to: {failed_file}")


def main():
    ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
    PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    CONTACTS_FILE = os.getenv("CONTACTS_FILE", "contacts.csv")
    MESSAGE_TEMPLATE = os.getenv("MESSAGE_TEMPLATE", "Hello {name}, this is a test message.")
    DELAY_SECONDS = float(os.getenv("DELAY_SECONDS", "0"))
    USE_TEMPLATE = os.getenv("USE_TEMPLATE", "false").lower() == "true"

    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("[ERROR] Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID in .env")
        return

    if not os.path.exists(CONTACTS_FILE):
        print(f"[ERROR] Contacts file '{CONTACTS_FILE}' not found")
        return

    sender = WhatsAppBulkSender(ACCESS_TOKEN, PHONE_NUMBER_ID)
    contacts = sender.load_contacts_from_csv(CONTACTS_FILE)

    if not contacts:
        print("[ERROR] No contacts found")
        return

    print(f"\n[READY] Will send to {len(contacts)} contacts")
    print(f"[DELAY] {DELAY_SECONDS} seconds between messages")
    print(f"[MODE] {'TEMPLATE (hello_world)' if USE_TEMPLATE else 'TEXT'}")
    confirm = input("\nProceed? (yes/no): ")

    if confirm.lower() != "yes":
        print("[CANCELLED] Sending cancelled")
        return

    sender.send_bulk_messages(contacts, MESSAGE_TEMPLATE, DELAY_SECONDS, use_template=USE_TEMPLATE)


if __name__ == "__main__":
    main()