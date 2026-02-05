
import os
import secrets
import json
import time
import uuid
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response

# ==========================================
# CONFIGURAÇÃO DE BANCO DE DADOS
# ==========================================
# Substitua pela URL do seu novo banco (ex: Neon Postgres)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:port/dbname')

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erro de Conexão DB: {e}")
        return None

# ==========================================
# AUTH & ADMIN DECORATORS
# ==========================================
def check_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROTAS DO ADMIN (FRONTEND)
# ==========================================

# Rota da Dashboard Principal
@app.route('/admin')
@check_auth
def admin_dashboard():
    return render_template('admin_index.html')

# Rota de Login
@app.route('/admin/login')
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

# ==========================================
# API ENDPOINTS (BACKEND LOGIC)
# ==========================================

# 1. Autenticação na API
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    if not conn: return jsonify({'error': 'DB Error'}), 500
    
    cur = conn.cursor()
    # Verifica tabela 'admins' (Simples)
    cur.execute("SELECT id FROM admins WHERE email = %s AND password = %s", (email, password))
    admin = cur.fetchone()
    cur.close()
    conn.close()

    if admin:
        session['logged_in'] = True
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Credenciais Inválidas'}), 401

# 2. Dados da Live View
@app.route('/api/admin/live')
@check_auth
def api_admin_live():
    # Retorna sessões ativas (últimos 30min)
    conn = get_db_connection()
    if not conn: return jsonify({'error': 'DB Error'}), 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Busca da tabela active_sessions
    cur.execute("""
        SELECT session_id, ip, user_agent, page, timestamp, meta_json as meta, type 
        FROM active_sessions 
        WHERE timestamp > EXTRACT(EPOCH FROM NOW()) - 1800 
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify({
        'count': len(rows),
        'users': rows
    })

# 3. Webhook de Pagamento (Gateway)
# ESSENCIAL: Recebe o aviso de pagamento e atualiza o pedido
@app.route('/api/webhook/waymb', methods=['POST'])
def webhook_waymb():
    try:
        data = request.json or {}
        tx_id = data.get('transactionID') or data.get('id')
        
        if not tx_id: return jsonify({'error': 'Missing ID'}), 400

        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # Atualiza status para PAID
            cur.execute("UPDATE orders SET status = 'PAID', updated_at = NOW() WHERE transaction_id = %s RETURNING id, amount, method", (tx_id,))
            row = cur.fetchone()
            conn.commit()
            
            if row:
                print(f"✅ Pedido {tx_id} PAGO (Webhook)")
                # AQUI: Se quiser mandar Pushcut ou Email, adicione aqui
                
            cur.close()
            conn.close()
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erro webhook: {e}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# DATABASE SETUP (INIT)
# ==========================================
# Rode isso uma vez para criar as tabelas no novo banco
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Tabela de Pedidos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            transaction_id VARCHAR(100) UNIQUE,
            amount NUMERIC(10,2),
            method VARCHAR(20),
            status VARCHAR(20) DEFAULT 'PENDING',
            payer_json JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    """)
    
    # Tabela de Sessões (Live View)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_sessions (
            session_id VARCHAR(100) PRIMARY KEY,
            ip VARCHAR(50),
            user_agent TEXT,
            page VARCHAR(100),
            type VARCHAR(20),
            timestamp DOUBLE PRECISION,
            meta_json JSONB
        );
    """)

    # Tabela de Admins
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100)
        );
    """)
    
    # Criar admin padrão se não existir
    try:
        cur.execute("INSERT INTO admins (email, password) VALUES ('admin@spy.com', 'admin123') ON CONFLICT DO NOTHING")
    except: pass

    conn.commit()
    cur.close()
    conn.close()
    print("DB Initialized")

if __name__ == '__main__':
    # init_db() # Descomente para criar as tabelas na 1ª vez
    app.run(port=5000)
