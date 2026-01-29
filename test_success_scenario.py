import requests
import json

CLIENT_ID = "modderstore_c18577a3"
CLIENT_SECRET = "850304b9-8f36-4b3d-880f-36ed75514cc7"
ACCOUNT_EMAIL = "modderstore@gmail.com"

def test_success_case():
    print("Testing with USER PROVIDED SUCCESS PAYLOAD (Phone: 912345678)...")
    
    # EXACT payload structure and values from the user's snippet
    body = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "account_email": ACCOUNT_EMAIL,
        "amount": 9.00,
        "method": "mbway",
        "payer": {
            "name": "Verification User",
            "document": "999999990",
            "phone": "912345678"  # Key difference: The test number
        }
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

test_success_case()
