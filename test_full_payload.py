import requests
import json

CLIENT_ID = "modderstore_c18577a3"
CLIENT_SECRET = "850304b9-8f36-4b3d-880f-36ed75514cc7"
ACCOUNT_EMAIL = "modderstore@gmail.com"

# Using dummy URLs for testing as requested structure
CALLBACK_URL = "https://raspa-production.up.railway.app/webhook/waymb" 
SUCCESS_URL = "https://raspa-production.up.railway.app/payment_success.html"
FAILED_URL = "https://raspa-production.up.railway.app/payment_failed.html"

def test_full_payload():
    print("Testing with FULL PAYLOAD structure...")
    
    body = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "account_email": ACCOUNT_EMAIL,
        "amount": 9.00,
        "method": "mbway",
        "payer": {
            "name": "Test User",
            "document": "999999990",
            "phone": "+351912765874"
        },
        "currency": "EUR",
        "callbackUrl": CALLBACK_URL,
        "success_url": SUCCESS_URL,
        "failed_url": FAILED_URL
    }
    
    print(f"Sending Payload:\n{json.dumps(body, indent=2)}")
    
    try:
        r = requests.post("https://api.waymb.com/transactions/create", 
                         json=body, 
                         headers={'Content-Type': 'application/json'}, 
                         timeout=30)
        
        print(f"\nStatus Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 30)

test_full_payload()
