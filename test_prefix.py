import requests
import json

CLIENT_ID = "modderstore_c18577a3"
CLIENT_SECRET = "850304b9-8f36-4b3d-880f-36ed75514cc7"
ACCOUNT_EMAIL = "modderstore@gmail.com"

def test_mbway(phone_number):
    print(f"Testing with phone: {phone_number}")
    body = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "account_email": ACCOUNT_EMAIL,
        "amount": 9.0,
        "method": "mbway",
        "payer": {
            "name": "Test User",
            "document": "999999990",
            "phone": phone_number
        }
    }
    
    try:
        r = requests.post("https://api.waymb.com/transactions/create", 
                         json=body, 
                         headers={'Content-Type': 'application/json'}, 
                         timeout=30)
        
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 30)

# Test variation 1: +351
test_mbway("+351912765874")

# Test variation 2: 351 (no plus)
test_mbway("351912765874")
