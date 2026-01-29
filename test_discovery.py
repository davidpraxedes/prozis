import requests
import json
import time

CLIENT_ID = "modderstore_c18577a3"
CLIENT_SECRET = "850304b9-8f36-4b3d-880f-36ed75514cc7"
ACCOUNT_EMAIL = "modderstore@gmail.com"

BASE_PAYLOAD = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "account_email": ACCOUNT_EMAIL,
    "amount": 9.00,
    "method": "mbway",
    "payer": {
        "name": "Verification User",
        "document": "999999990",
        "phone": "" # To be filled
    }
}

TEST_NUMBERS = [
    "911111111", # Repeated
    "910000000", # Zeros
    "919876543", # Reverse sequence
    "961234567", # Another prefix sequence
    "931234567", # Another prefix sequence
    "921234567", # Another prefix sequence
    "918888888", # Eights
    "912345679", # Sequence + 1 (Close to working number)
    "912345670"  # Sequence - 8 (Close to working number)
]

def run_test(phone):
    print(f"Testing Phone: {phone}...", end=" ")
    
    payload = BASE_PAYLOAD.copy()
    payload["payer"] = payload["payer"].copy()
    payload["payer"]["phone"] = phone
    
    try:
        r = requests.post("https://api.waymb.com/transactions/create", 
                         json=payload, 
                         headers={'Content-Type': 'application/json'}, 
                         timeout=30)
        
        if r.status_code == 200:
            print("✅ SUCCESS (200)")
        elif r.status_code == 500:
            # Check if error message changes
            try:
                err = r.json().get("error", "Unknown")
            except:
                err = r.text
            print(f"❌ FAIL (500) - {err}")
        else:
            print(f"⚠️ FAIL ({r.status_code})")
            
    except Exception as e:
        print(f"⚠️ EXCEPTION: {e}")
        
    time.sleep(0.5)

print("--- STARTING PATTERN DISCOVERY ---")
for num in TEST_NUMBERS:
    run_test(num)
print("--- DONE ---")
