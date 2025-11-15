import os
from dotenv import load_dotenv

print("=== Debugging .env file ===\n")

# Check if .env exists
if os.path.exists('.env'):
    print("✓ .env file found")
    print(f"File size: {os.path.getsize('.env')} bytes\n")
else:
    print("✗ .env file NOT found!")
    exit()

# Show raw content (be careful - this shows your tokens!)
print("--- Raw .env Content ---")
with open('.env', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        # Hide sensitive data
        if 'TOKEN' in line or 'PASSWORD' in line:
            print(f"Line {i}: {line.split('=')[0]}=***HIDDEN***")
        else:
            print(f"Line {i}: {repr(line)}")

print("\n--- Loading with python-dotenv ---")
result = load_dotenv()
print(f"Load result: {result}")

print("\n--- Environment Variables ---")
print(f"WHATSAPP_ACCESS_TOKEN: {'SET' if os.getenv('WHATSAPP_ACCESS_TOKEN') else 'NOT SET'}")
print(f"WHATSAPP_PHONE_NUMBER_ID: {os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'NOT SET')}")
print(f"CONTACTS_FILE: {os.getenv('CONTACTS_FILE', 'NOT SET')}")
print(f"DELAY_SECONDS: {os.getenv('DELAY_SECONDS', 'NOT SET')}")
print(f"MESSAGE_TEMPLATE: {'SET' if os.getenv('MESSAGE_TEMPLATE') else 'NOT SET'}")