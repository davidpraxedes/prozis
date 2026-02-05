
# 📦 Kit de Exportação do Front Admin (SpyInsta Dashboard)

Este kit contém **exatamente** o Painel Admin que você solicitou ("Dashboard com Live View, Matrix, Ícones e tudo mais") pronto para ser conectado em qualquer projeto Python/Flask.

## 📂 Estrutura das Pastas

- `templates/`
  - `admin_index.html`: O Dashboard principal (com o visual Matrix, tabela, live view).
  - `admin_login.html`: A tela de login (estilo hacker).
- `styles/`
  - `admin.css`: O arquivo de estilos que faz tudo ficar bonito e dark.
- `schema.sql`: O código SQL para criar as tabelas no banco de dados (Neon, Postgres, etc).
- `backend_logic.py`: O código Python (Flask) necessário para fazer o painel funcionar.

---

## 🚀 Como Integrar no Novo Projeto (Roleta/Engenharia)

Entregue esta pasta para a IA ou Desenvolvedor e diga:

> "Aqui estão os arquivos do Front. Eu quero que você use este `admin_index.html` como dashboard principal. Ele precisa de 3 rotas no backend para funcionar:"

### 1. Rotas Necessárias (Backend)

O `admin_index.html` faz chamadas para estas rotas. Elas estão prontas no arquivo `backend_logic.py`:

1.  **GET `/api/admin/live`**:
    *   Retorna JSON com a lista de usuários online.
    *   Formato esperado: `{ count: 10, users: [ ... ] }`
2.  **POST `/api/admin/login`**:
    *   Verifica email/senha e retorna `{ success: true }`.
3.  **POST `/api/webhook/waymb`** (Gateway):
    *   Recebe o aviso de pagamento e atualiza o pedido para "PAID".

### 2. Banco de Dados

Rode o script `schema.sql` no banco de dados do novo projeto para criar as tabelas:
*   `orders`: Para guardar as vendas/pedidos.
*   `active_sessions`: Para o Live View (espião).

### 3. Integração com a Roleta

Como você vai usar uma "Engenharia de Roleta", o fluxo será:

1.  O cliente joga na Roleta.
2.  Quando ele gera um pagamento, o seu backend deve salvar na tabela `orders`.
3.  O Gateway chama o Webhook (`/api/webhook/waymb`) e o sistema atualiza para `PAID`.
4.  O Admin Dashboard lê dessa tabela `orders` e mostra tudo na tela.

---

✅ **Pronto!** Com esses arquivos, o visual e a lógica do painel serão idênticos ao original.
