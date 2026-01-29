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
        "phone": "912345678"
    }
}

def run_test(name, payload_override):
    print(f"\n--- TESTING: {name} ---")
    
    # Merge override into base
    payload = BASE_PAYLOAD.copy()
    payload["payer"] = payload["payer"].copy() # Deep copy payer
    
    for key, value in payload_override.items():
        payload["payer"][key] = value
        
    print(f"Payer Data: {payload['payer']}")
    
    try:
        r = requests.post("https://api.waymb.com/transactions/create", 
                         json=payload, 
                         headers={'Content-Type': 'application/json'}, 
                         timeout=30)
        
        print(f"Result: {r.status_code}")
        if r.status_code == 500:
            print(f"Error Body: {r.text}")
        else:
            print("SUCCESS")
            
    except Exception as e:
        print(f"Exception: {e}")
        
    time.sleep(1) # Be nice to the API

# 1. Baseline (Should Work)
run_test("BASELINE (Known Good)", {})

# 2. Target Phone (Raw)
run_test("Target Phone (912765874)", {"phone": "912765874"})

# 3. Target Phone (+351)
run_test("Target Phone (+351...)", {"phone": "+351912765874"})

# 4. Target Phone (00351)
run_test("Target Phone (00351...)", {"phone": "00351912765874"})

# 5. Target Name (Real User Name)
run_test("Target Name (alessando nogueira)", {"name": "alessando nogueira"})

# 6. Target Document (Real User NIF)
run_test("Target Document (789654232)", {"document": "789654232"})
