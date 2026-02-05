
-- 1. Tabela de Pedidos (Compras)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE,
    amount NUMERIC(10,2),
    method VARCHAR(20), -- 'MBWAY' ou 'MULTIBANCO'
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'PAID', 'FAILED'
    payer_json JSONB, -- Dados do cliente (Nome, Email, Tel)
    reference_data_json JSONB, -- Dados do gateway (Entidade, Ref)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 2. Tabela de Sessões (Live View)
-- Usada para mostrar quem está online no painel
CREATE TABLE IF NOT EXISTS active_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    ip VARCHAR(50),
    user_agent TEXT,
    page VARCHAR(100), -- Página atual
    type VARCHAR(20), -- 'pageview', 'checkout'
    timestamp DOUBLE PRECISION, -- Epoch time da última ação
    meta_json JSONB, -- Localização, Perfil Pesquisado, etc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela de Admins
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100) -- Pode ser hash ou texto simples (cuidado)
);

-- Inserir Admin Padrão
INSERT INTO admins (email, password) VALUES ('admin@instaspy.com', 'admin123') ON CONFLICT DO NOTHING;
