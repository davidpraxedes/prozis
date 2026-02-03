import requests
import time

PUSHCUT_URL = "https://api.pushcut.io/ZJtFapxqtRs_gYalo0G8Z/notifications/MinhaNotifica%C3%A7%C3%A3o"

def trigger_batch_tests():
    # 5 MB WAY
    for i in range(5):
        send_notification("MBWAY", i+1)
        time.sleep(1) # Be nice to the API

    # 5 Multibanco
    for i in range(5):
        send_notification("Multibanco", i+1)
        time.sleep(1)

def send_notification(method, count):
    msg = f"PORTES PAGOS: 12,99 € ({method})"
    
    payload = {
        "text": msg,
        "title": "Prozis Envio",
        "input": "{\"flow\": \"root\"}" 
    }
    
    print(f"[{method} #{count}] Sending notification...")
    
    try:
        response = requests.post(PUSHCUT_URL, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            print(f"[{method} #{count}] Success!")
        else:
            print(f"[{method} #{count}] Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[{method} #{count}] Error: {e}")

if __name__ == "__main__":
    trigger_batch_tests()
