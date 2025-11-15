import csv
import os

print("=== Debugging Contacts.csv ===\n")

# Check if file exists
if os.path.exists('contacts.csv'):
    print("✓ contacts.csv found")
    print(f"File size: {os.path.getsize('contacts.csv')} bytes\n")
else:
    print("✗ contacts.csv NOT found!")
    exit()

# Read raw content
print("--- Raw File Content ---")
with open('contacts.csv', 'r', encoding='utf-8') as f:
    content = f.read()
    print(repr(content))  # Shows hidden characters
    print()

# Try reading with CSV reader
print("--- CSV Reader Output ---")
try:
    with open('contacts.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        print(f"Headers: {reader.fieldnames}")
        
        contacts = []
        for idx, row in enumerate(reader, 1):
            print(f"Row {idx}: {row}")
            contacts.append(row)
        
        print(f"\nTotal rows read: {len(contacts)}")
        
        # Check for issues
        if len(contacts) == 0:
            print("\n⚠️ No data rows found!")
            print("Possible issues:")
            print("- Empty lines after header")
            print("- Wrong encoding")
            print("- File not saved properly")
            
except Exception as e:
    print(f"✗ Error reading CSV: {e}")

print("\n--- Checking phone numbers ---")
with open('contacts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        phone = row.get('phone', '')
        print(f"Phone: '{phone}' | Length: {len(phone)} | Has spaces: {' ' in phone}")