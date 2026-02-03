import requests
import json

PUSHCUT_URL = "https://api.pushcut.io/ZJtFapxqtRs_gYalo0G8Z/notifications/MinhaNotifica%C3%A7%C3%A3o"

def trigger_test_notification():
    amount = 9.00
    method = "MBWAY"
    msg = f"Pedido gerado: {amount}€ ({method.upper()})"
    
    payload = {
        "text": msg,
        "title": "Worten Promo"
    }
    
    print(f"Sending notification to {PUSHCUT_URL}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(PUSHCUT_URL, json=payload, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("Notification sent successfully!")
        else:
            print("Failed to send notification.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_test_notification()
