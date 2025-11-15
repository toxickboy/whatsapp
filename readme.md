# WhatsApp Bulk Messaging Script

Simple Python script to send WhatsApp messages to multiple contacts using WhatsApp Business API.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Credentials

1. Go to https://developers.facebook.com/
2. Create/select your app
3. Add WhatsApp product
4. Copy your **Phone Number ID** and **Access Token**

### 3. Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id_here
```

### 4. Prepare Contacts

Create `contacts.csv`:
```csv
phone,name,company
919876543210,John Doe,ABC Corp
918765432109,Jane Smith,XYZ Ltd
```

**Note:** Phone format: country code + number (no + or spaces)

### 5. Run

```bash
python message_sender.py
```

## Configuration

Edit `.env` to customize:
- `DELAY_SECONDS` - Delay between messages (default: 2.0)
- `MESSAGE_TEMPLATE` - Your message with `{name}`, `{company}` placeholders
- `CONTACTS_FILE` - Path to your CSV file

## Logs

Script generates:
- `whatsapp_log_*.log` - Detailed logs
- `failed_messages_*.json` - Failed deliveries (if any)

## Important

⚠️ **This is a prototype script for testing only**
- Start with small batches (5-10 contacts)
- Keep delay at 2+ seconds to avoid rate limits
- Never commit `.env` file to version control