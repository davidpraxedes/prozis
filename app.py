from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
import sys

app = Flask(__name__, static_folder='.')
CORS(app)

# Credentials
CLIENT_ID = os.environ.get("WAYMB_CLIENT_ID", "modderstore_c18577a3")
CLIENT_SECRET = os.environ.get("WAYMB_CLIENT_SECRET", "850304b9-8f36-4b3d-880f-36ed75514cc7")
ACCOUNT_EMAIL = os.environ.get("WAYMB_ACCOUNT_EMAIL", "modderstore@gmail.com")
PUSHCUT_URL = "https://api.pushcut.io/XPTr5Kloj05Rr37Saz0D1/notifications/Pendente%20delivery"

def log(msg):
    print(f"[BACKEND] {msg}")
    sys.stdout.flush()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/promo')
def promo_index():
    return send_from_directory('promo', 'index.html')


@app.route('/api/payment', methods=['POST'])
def create_payment():
    try:
        data = request.json
        log(f"New Payment Request: {json.dumps(data)}")
        
        payer = data.get("payer", {})
        method = data.get("method")
        amt_raw = data.get("amount", 9)

        # Force Amount as Float (matching successful test)
        try:
            amount = float(amt_raw)
        except:
            amount = 9.0

        # STRICT SANITIZATION
        if "phone" in payer:
            p = "".join(filter(str.isdigit, str(payer["phone"])))
            if p.startswith("351") and len(p) > 9: p = p[3:]
            if len(p) > 9: p = p[-9:]
            payer["phone"] = p
            log(f"Sanitized Phone: {p}")
            
        if "document" in payer:
            d = "".join(filter(str.isdigit, str(payer["document"])))
            if len(d) > 9: d = d[-9:]
            payer["document"] = d
            log(f"Sanitized NIF: {d}")

        # Construct WayMB Body (without currency to match working test)
        waymb_body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "account_email": ACCOUNT_EMAIL,
            "amount": amount,
            "method": method,
            "payer": payer
        }
        
        log(f"Calling WayMB API with: {json.dumps(waymb_body)}")

        try:
            r = requests.post("https://api.waymb.com/transactions/create", 
                             json=waymb_body, 
                             headers={'Content-Type': 'application/json'}, 
                             timeout=30)
            
            log(f"WayMB Status Code: {r.status_code}")
            log(f"WayMB Raw Response: {r.text}")

            try:
                resp = r.json()
            except:
                resp = {"raw_error": r.text}
            
            # success flags
            is_ok = False
            if r.status_code in [200, 201] and not resp.get("error"):
                is_ok = True

            if is_ok:
                log("Payment Created OK.")
                # Notify Pushcut
                # Logic: 9.00 -> Root (New URL) | 9.90 -> Promo (Old URL)
                try:
                    target_pushcut = PUSHCUT_URL # Default (Old/Promo)
                    if abs(amount - 9.00) < 0.01:
                        target_pushcut = "https://api.pushcut.io/BUhzeYVmAEGsoX2PSQwh1/notifications/venda%20aprovada%20"
                    
                    requests.post(target_pushcut, json={
                        "text": f"Pedido: {amount}€ ({method.upper()})",
                        "title": "Worten Promo"
                    }, timeout=3)
                except: pass
                return jsonify({"success": True, "data": resp})
            else:
                log(f"Payment Failed by Gateway: {resp}")
                # Return success: False BUT with details
                return jsonify({
                    "success": False, 
                    "error": resp.get("error", "Gateway Rejection"),
                    "details": resp,
                    "gateway_status": r.status_code
                })

        except Exception as e:
            log(f"Gateway Communication Error: {str(e)}")
            return jsonify({"success": False, "error": f"Erro de comunicação: {str(e)}"}), 502

    except Exception as e:
        log(f"Fatal Route Error: {str(e)}")
        return jsonify({"success": False, "error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/status', methods=['POST'])
def check_status():
    data = request.json
    tx_id = data.get("id")
    try:
        r = requests.post("https://api.waymb.com/transactions/info", json={"id": tx_id}, timeout=15)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notify', methods=['POST'])
def send_notification():
    data = request.json
    type = data.get("type", "Pendente delivery")
    text = data.get("text", "Novo pedido")
    title = data.get("title", "Worten")
    
    # Determine base URL based on amount/context if passed, otherwise default logic
    # Ideally should pass a flag, but for now let's stick to the requested change:
    # Root (9.00) -> New URL. Promo (9.90) -> Old URL.
    # The client calls this endpoint for 'Aprovado delivery'. 
    # We need to know which flow it is.
    # Let's check text content for price as a heuristic since client sends "9,90 €" or "9,00 €"
    
    base_url = "https://api.pushcut.io/XPTr5Kloj05Rr37Saz0D1/notifications" # Old/Promo
    if "9,00" in text or "9.00" in text:
        base_url = "https://api.pushcut.io/BUhzeYVmAEGsoX2PSQwh1/notifications" # New/Root
        
    # Handle "venda aprovada" mapping if needed
    safe_type = type.replace(' ', '%20')
    if base_url != "https://api.pushcut.io/XPTr5Kloj05Rr37Saz0D1/notifications":
       # For the new API, the user specified ".../notifications/venda%20aprovada%20"
       # If the type is 'Aprovado delivery', we might want to map it to 'venda aprovada'
       if type == "Aprovado delivery":
           safe_type = "venda%20aprovada%20"
    
    url = f"{base_url}/{safe_type}"
    try:
        requests.post(url, json={"text": text, "title": title}, timeout=5)
        return jsonify({"success": True})
    except:
        return jsonify({"success": False}), 500

@app.route('/api/webhook/mbway', methods=['POST'])
def mbway_webhook():
    try:
        # Log the incoming payload for debug
        data = request.json or {}
        log(f"WEBHOOK RECEIVED: {json.dumps(data)}")

        # Try to extract amount from payload (assuming structure based on common gateways)
        # If structure is unknown, we default to generic message
        amount = 0.0
        
        # Heuristic to find amount in common fields if not explicit
        if "amount" in data:
            try: amount = float(data["amount"])
            except: pass
        elif "valor" in data:
            try: amount = float(data["valor"])
            except: pass
            
        # Determine Pushcut URL
        target_pushcut = PUSHCUT_URL # Promo (9.90) default
        if abs(amount - 9.00) < 0.01:
            target_pushcut = "https://api.pushcut.io/BUhzeYVmAEGsoX2PSQwh1/notifications/venda%20aprovada%20"
        
        # Prepare Notification
        msg_text = f"Pagamento Confirmado: {amount}€" if amount > 0 else "Pagamento MBWAY Recebido!"
        
        # Send to Pushcut
        requests.post(target_pushcut, json={
            "text": msg_text, 
            "title": "Worten Sucesso"
        }, timeout=4)
        
        return jsonify({"status": "received"}), 200

    except Exception as e:
        log(f"Webhook Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
