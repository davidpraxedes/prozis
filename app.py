from flask import Flask, request, jsonify, send_from_directory, render_template_string, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Visitor, PageMetric, Order
from sqlalchemy import func
import requests
import os
import json
import sys
import datetime
import uuid

app = Flask(__name__, static_folder='.', template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_123") # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db').replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

# Credentials
CLIENT_ID = os.environ.get("WAYMB_CLIENT_ID", "modderstore_c18577a3")
CLIENT_SECRET = os.environ.get("WAYMB_CLIENT_SECRET", "850304b9-8f36-4b3d-880f-36ed75514cc7")
ACCOUNT_EMAIL = os.environ.get("WAYMB_ACCOUNT_EMAIL", "modderstore@gmail.com")
PUSHCUT_URL = "https://api.pushcut.io/XPTr5Kloj05Rr37Saz0D1/notifications/Aprovado%20delivery"

# Initialize DB
with app.app_context():
    db.create_all()
    
    # Check if 'flow' column exists in 'order' table (Migration helper)
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            # Check columns
            result = conn.execute(text("PRAGMA table_info('order')"))
            columns = [row[1] for row in result]
            if 'flow' not in columns:
                print("[MIGRATION] Adding 'flow' column to 'order' table")
                conn.execute(text("ALTER TABLE 'order' ADD COLUMN flow VARCHAR(20) DEFAULT 'promo'"))
                conn.commit()
            
            # Check traffic_source in order
            if 'traffic_source' not in columns:
                print("[MIGRATION] Adding 'traffic_source' column to 'order' table")
                conn.execute(text("ALTER TABLE 'order' ADD COLUMN traffic_source VARCHAR(100)"))
                conn.commit()

            # Check checkout_id in order
            if 'checkout_id' not in columns:
                print("[MIGRATION] Adding 'checkout_id' column to 'order' table")
                conn.execute(text("ALTER TABLE 'order' ADD COLUMN checkout_id VARCHAR(100)"))
                conn.commit()

            # Check traffic_source in visitor
            result = conn.execute(text("PRAGMA table_info('visitor')"))
            v_columns = [row[1] for row in result]
            if 'traffic_source' not in v_columns:
                print("[MIGRATION] Adding 'traffic_source' column to 'visitor' table")
                conn.execute(text("ALTER TABLE 'visitor' ADD COLUMN traffic_source VARCHAR(100)"))
                conn.commit()
    except Exception as e:
        print(f"[MIGRATION ERROR] {e}")

    # Create default admin if not exists
    if not User.query.filter_by(username='shelby').first():
        admin = User(username='shelby', password='admin') # Default user
        db.session.add(admin)
        db.session.commit()
        print("[INIT] User created: shelby / admin")

def log(msg):
    print(f"[BACKEND] {msg}")
    sys.stdout.flush()


def get_client_ip():
    """Get real client IP from headers (for Railway/proxy environments)"""
    # Try X-Forwarded-For first (most common)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # Try X-Real-IP
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # Fallback to remote_addr
    return request.remote_addr

def get_location_data(ip):
    try:
        # Skip private/local IPs
        if ip.startswith(('127.', '10.', '172.', '192.168.', '100.64.')) or ip in ['localhost', '::1']:
            return "Local", "Local"
        
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = r.json()
        if data.get('status') == 'success':
            return data.get('city', 'Unknown'), data.get('country', 'Unknown')
    except:
        pass
    return "Unknown", "Unknown"

# --- Tracking API ---

@app.route('/api/track/init', methods=['POST'])
def track_init():
    try:
        data = request.json
        sid = data.get('session_id')
        path = data.get('path')
        ip = get_client_ip()
        
        visitor = Visitor.query.filter_by(session_id=sid).first()
        if not visitor:
            city, country = get_location_data(ip)
            visitor = Visitor(
                session_id=sid,
                ip_address=ip,
                city=city,
                country=country,
                traffic_source=data.get('traffic_source'),
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(visitor)
        
        visitor.last_seen = datetime.datetime.utcnow()
        visitor.current_page = path
        db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/track/heartbeat', methods=['POST'])
def track_heartbeat(): # Supports Beacon (text/plain) or JSON
    try:
        if request.content_type == 'text/plain': # Beacon sometimes sends as text
            data = json.loads(request.data)
        else:
            data = request.json

        sid = data.get('session_id')
        path = data.get('path')
        duration = float(data.get('duration', 0))

        visitor = Visitor.query.filter_by(session_id=sid).first()
        if visitor:
            visitor.last_seen = datetime.datetime.utcnow()
            visitor.current_page = path
            
            # Update Page Metric
            metric = PageMetric.query.filter_by(visitor_id=visitor.id, page_path=path).first()
            if not metric:
                metric = PageMetric(visitor_id=visitor.id, page_path=path)
                db.session.add(metric)
            
            # Only update if duration increases (simple max-hold logic for session)
            if duration > metric.duration_seconds:
                metric.duration_seconds = duration
                
            db.session.commit()
    except Exception as e:
        log(f"Tracking Error: {e}")
    return jsonify({"status": "ok"})


# --- Admin Routes ---

def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect('/admin/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_index.html')

@app.route('/admin/login')
def admin_login_view():
    if session.get('logged_in'):
        return redirect('/admin')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/admin/login')

# --- API Endpoints (Admin Kit) ---

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    # Simple check against User table
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['logged_in'] = True
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    session.pop('logged_in', None)
    return jsonify({"success": True})

@app.route('/api/admin/live')
@login_required
def api_admin_live():
    # Active visitors in last 30 minutes
    limit_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    visitors = Visitor.query.filter(Visitor.last_seen >= limit_time).order_by(Visitor.last_seen.desc()).all()
    
    users = []
    for v in visitors:
        # Determine metrics or type
        v_type = "pageview"
        if "checkout" in (v.current_page or ""): v_type = "checkout"
        
        users.append({
            "session_id": v.session_id,
            "ip": v.ip_address,
            "user_agent": v.user_agent,
            "page": v.current_page,
            "timestamp": v.last_seen.timestamp(),
            "type": v_type,
            "meta": {
                "location": f"{v.city}, {v.country}",
                "searched_profile": "-" # Not captured yet
            }
        })

    return jsonify({
        "count": len(users),
        "users": users
    })

@app.route('/api/admin/orders')
@login_required
def api_admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).limit(100).all()
    out = []
    for o in orders:
        payer = {}
        try: payer = json.loads(o.customer_data) if o.customer_data else {}
        except: pass
        
        out.append({
            "id": o.id,
            "transaction_id": o.checkout_id or "N/A",
            "amount": o.amount,
            "method": o.method,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
            "payer": payer,
            "meta": {
                "bumps": [], # Not implemented
                "coupon": None
            }
        })
    return jsonify(out)

@app.route('/api/admin/stats')
@login_required
def api_admin_stats():
    today = datetime.datetime.utcnow().date()
    
    # Visits Today
    visits_today = Visitor.query.filter(Visitor.last_seen >= today).count()
    
    # Orders Today
    orders_today = Order.query.filter(func.date(Order.created_at) == today).count()
    orders_total = Order.query.count()
    
    # Revenue
    revenue_today = db.session.query(func.sum(Order.amount)).filter(func.date(Order.created_at) == today, Order.status == 'PAID').scalar() or 0.0
    revenue_total = db.session.query(func.sum(Order.amount)).filter(Order.status == 'PAID').scalar() or 0.0
    
    # Conversion
    conv_today = (orders_today / visits_today * 100) if visits_today > 0 else 0
    conv_total = 0 # Simple calc
    
    return jsonify({
        "visits_today": visits_today,
        "orders_today": orders_today,
        "orders_total": orders_total,
        "revenue_today": float(revenue_today),
        "revenue_total": float(revenue_total),
        "conversion_today": float(conv_today),
        "conversion_total": 0
    })

@app.route('/api/admin/orders/delete', methods=['POST'])
@login_required
def api_delete_order():
    data = request.json
    try:
        order = Order.query.get(data.get('id'))
        if order:
            db.session.delete(order)
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/ban-ip', methods=['POST'])
@login_required
def api_ban_ip():
    data = request.json or {}
    ip_to_ban = data.get('ip')
    
    if not ip_to_ban:
        return jsonify({"success": False, "error": "IP missing"}), 400
        
    try:
        # For this MVP, we might not have a dedicated Ban table, 
        # so we'll just delete the Visitor sessions from this IP to "kick" them 
        # or we could add a "banned" flag to Visitor. 
        # Let's delete them for now as per specific request "Purge/Ban behavior".
        
        # 1. Delete all current visitor sessions for this IP
        visitors = Visitor.query.filter_by(ip_address=ip_to_ban).all()
        count = len(visitors)
        for v in visitors:
            db.session.delete(v)
            
        db.session.commit()
        return jsonify({"success": True, "message": f"Banned/Kicked {count} sessions from {ip_to_ban}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/purge-live', methods=['POST'])
@login_required
def api_purge_live():
    try:
        # Delete all visitors
        db.session.query(Visitor).delete()
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/site-status')
def api_site_status():
    return jsonify({"status": "safe", "message": "Site Seguro"})

@app.route('/api/admin/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    if request.method == 'POST':
        return jsonify({"success": True})
    return jsonify({}) # Empty settings

# Webhook Alias
@app.route('/api/webhook/waymb', methods=['POST'])
def webhook_waymb_alias():
    # Reuse existing logic
    return mbway_webhook()

# --- Public Routes ---

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
        flow = data.get("flow", "promo") # Get flow source
        
        # Try to link session
        try:
             # Just a heuristic, we can pass session_id from frontend if needed, 
             # but IP matching is okay-ish for MVP or we add it to payload later.
             # For now let's hope frontend generates tracked session.
             # Actually, best practice is to pass header or payload.
             # Let's assume frontend sends nothing specialized yet, so we match by IP (latest active session on IP)
             ip = get_client_ip()
             visitor = Visitor.query.filter_by(ip_address=ip).order_by(Visitor.last_seen.desc()).first()
        except:
            visitor = None

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
            
        if "document" in payer:
            d = "".join(filter(str.isdigit, str(payer["document"])))
            if len(d) > 9: d = d[-9:]
            payer["document"] = d

        # Construct WayMB Body (without currency to match working test)
        waymb_body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "account_email": ACCOUNT_EMAIL,
            "amount": amount,
            "method": method,
            "payer": payer
        }
        
        log(f"Calling WayMB API...")

        try:
            r = requests.post("https://api.waymb.com/transactions/create", 
                             json=waymb_body, 
                             headers={'Content-Type': 'application/json'}, 
                             timeout=30)
            
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
                
                # SAVE ORDER TO DB
                new_order = Order(
                    amount=amount,
                    method=method,
                    status="CREATED",
                    flow=flow,
                    traffic_source=data.get('traffic_source') or (visitor.traffic_source if visitor else None),
                    customer_data=json.dumps(payer, indent=2),
                    visitor_id=visitor.id if visitor else None,
                    checkout_id=str(resp.get("id", "")) # Request ID from WayMB
                )
                db.session.add(new_order)
                db.session.commit()

                # Notify Pushcut
                try:                    
                    target_pushcut = PUSHCUT_URL
                    msg = f"Pedido gerado: {amount}€ ({method.upper()})"
                    
                    requests.post(target_pushcut, json={
                        "text": msg,
                        "title": "Sephora Promo"
                    }, timeout=3)
                except: pass
                
                return jsonify({"success": True, "data": resp})
            else:
                log(f"Payment Failed by Gateway: {resp}")
                
                 # SAVE FAILED ORDER ATTEMPT? (Optional, let's save for debug)
                status_code = "FAILED_GATEWAY"
                
                # Check for Invalid MBWay Number (Gateway returns 404 or 500 for invalid numbers)
                if method == 'mbway' and r.status_code in [404, 500]:
                    status_code = "MBWAY_INVALID"

                failed_order = Order(
                    amount=amount,
                    method=method,
                    status=status_code,
                    flow=flow,
                    traffic_source=data.get('traffic_source') or (visitor.traffic_source if visitor else None),
                    customer_data=json.dumps(payer, indent=2),
                    visitor_id=visitor.id if visitor else None
                )
                db.session.add(failed_order)
                db.session.commit()
                
                # If it's the specific MBWay error, return that key to frontend
                if status_code == "MBWAY_INVALID":
                    return jsonify({
                        "success": False,
                        "error": "MBWAY_INVALID", 
                        "details": resp,
                        "gateway_status": r.status_code
                    })

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
    text = data.get("text", "Novo pedido")
    title = data.get("title", "Sephora")
    
    # Single endpoint per flow
    url = PUSHCUT_URL
    
    try:
        requests.post(url, json={"text": text, "title": title}, timeout=5)
        return jsonify({"success": True})
    except:
        return jsonify({"success": False}), 500

@app.route('/api/webhook/mbway', methods=['POST'])
def mbway_webhook():
    try:
        data = request.json or {}
        log(f"WEBHOOK RECEIVED: {json.dumps(data)}")

        amount = 0.0
        if "amount" in data:
            try: amount = float(data["amount"])
            except: pass
        elif "valor" in data:
            try: amount = float(data["valor"])
            except: pass
            
        tx_id = data.get("id") or data.get("transaction_id")
        
        # === INSTASPT FILTER (12.90 EUR) ===
        if abs(amount - 12.90) < 0.01:
            log(f"InstaSpy payment detected: {amount}€")
            requests.post(
                PUSHCUT_URL,
                json={
                    "text": f"Valor: {amount}€\nID: {tx_id or 'N/A'}",
                    "title": "Assinatura InstaSpy aprovado"
                },
                timeout=4
            )
            return jsonify({"status": "received", "project": "InstaSpy"}), 200
        
        # === WORTEN LOGIC (continua igual) ===
        order = None
        if tx_id:
            order = Order.query.filter_by(checkout_id=str(tx_id)).first()
            
        if not order and amount > 0:
            order = Order.query.filter(
                Order.amount == amount, 
                Order.status != "PAID",
                Order.created_at >= datetime.utcnow() - timedelta(minutes=30)
            ).order_by(Order.created_at.desc()).first()

        if order:
            order.status = "PAID"
            db.session.commit()
            log(f"Order #{order.id} marked as PAID")
            flow = order.flow
        else:
            flow = "root" if abs(amount - 12.49) < 0.01 else "promo"
        
        target_pushcut = PUSHCUT_URL
        
        msg_text = f"Pagamento Confirmado: {amount}€" if amount > 0 else "Pagamento MBWAY Recebido!"
        
        requests.post(target_pushcut, json={
            "text": msg_text, 
            "title": "Sephora Sucesso"
        }, timeout=4)
        
        return jsonify({"status": "received", "project": "Sephora"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
