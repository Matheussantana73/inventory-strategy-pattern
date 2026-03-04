-- Script de inicialização do banco de dados
-- Este script é executado quando o container PostgreSQL é criado pela primeira vez

-- Criar tabelas base (serão criadas automaticamente pelos serviços, mas isso garante a estrutura)

-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao VARCHAR(500),
    preco NUMERIC(10, 2) NOT NULL,
    peso FLOAT DEFAULT 0,
    quantidade_estoque INTEGER DEFAULT 0,
    categoria VARCHAR(100),
    sku VARCHAR(50) UNIQUE,
    ativo INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Tabela de pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) UNIQUE NOT NULL,
    usuario_id INTEGER,
    status VARCHAR(30) DEFAULT 'pendente',
    tipo_desconto VARCHAR(30) DEFAULT 'sem_desconto',
    tipo_frete VARCHAR(30) DEFAULT 'fixo_50',
    valor_produtos NUMERIC(10, 2) DEFAULT 0,
    valor_desconto NUMERIC(10, 2) DEFAULT 0,
    valor_frete NUMERIC(10, 2) DEFAULT 0,
    valor_total NUMERIC(10, 2) DEFAULT 0,
    peso_total FLOAT DEFAULT 0,
    distancia_km FLOAT DEFAULT 0,
    endereco_entrega VARCHAR(500),
    observacoes VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Tabela de itens do pedido
CREATE TABLE IF NOT EXISTS itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL,
    nome_produto VARCHAR(200) NOT NULL,
    preco_unitario NUMERIC(10, 2) NOT NULL,
    quantidade INTEGER NOT NULL,
    peso_unitario FLOAT DEFAULT 0,
    subtotal NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Tabela de tokens revogados
CREATE TABLE IF NOT EXISTS tokens_revogados (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(36) UNIQUE NOT NULL,
    expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome);
CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);
CREATE INDEX IF NOT EXISTS idx_produtos_sku ON produtos(sku);
CREATE INDEX IF NOT EXISTS idx_pedidos_numero ON pedidos(numero);
CREATE INDEX IF NOT EXISTS idx_pedidos_usuario_id ON pedidos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos(status);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_id ON itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_itens_produto_id ON itens_pedido(produto_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_tokens_jti ON tokens_revogados(jti);

-- Inserir dados de exemplo
INSERT INTO produtos (nome, descricao, preco, peso, quantidade_estoque, categoria, sku) VALUES
    ('Notebook Dell Inspiron', 'Notebook 15.6" Intel Core i5, 8GB RAM, 256GB SSD', 3500.00, 2.5, 10, 'Eletrônicos', 'NOTE-DELL-001'),
    ('Mouse Logitech MX Master', 'Mouse sem fio ergonômico profissional', 450.00, 0.3, 25, 'Periféricos', 'MOUSE-LOG-001'),
    ('Teclado Mecânico Redragon', 'Teclado mecânico RGB switches brown', 280.00, 0.8, 15, 'Periféricos', 'TECL-RED-001'),
    ('Monitor LG 27"', 'Monitor IPS 27" Full HD 75Hz', 1200.00, 5.0, 8, 'Monitores', 'MON-LG-001'),
    ('Headset HyperX Cloud II', 'Headset gamer com som surround 7.1', 650.00, 0.4, 20, 'Áudio', 'HEAD-HYP-001'),
    ('SSD Kingston 500GB', 'SSD NVMe M.2 500GB leitura 3500MB/s', 320.00, 0.05, 30, 'Armazenamento', 'SSD-KIN-001'),
    ('Webcam Logitech C920', 'Webcam Full HD 1080p com microfone', 550.00, 0.2, 12, 'Periféricos', 'WEB-LOG-001'),
    ('Cadeira Gamer DT3', 'Cadeira ergonômica para gamers', 1800.00, 15.0, 5, 'Móveis', 'CAD-DT3-001')
ON CONFLICT (sku) DO NOTHING;

-- Inserir usuário admin padrão (senha: admin123)
-- Hash gerado com bcrypt
INSERT INTO usuarios (email, nome, senha_hash, is_admin) VALUES
    ('admin@estoque.com', 'Administrador', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S6/V6gBylNk1lK', true)
ON CONFLICT (email) DO NOTHING;

COMMIT;
