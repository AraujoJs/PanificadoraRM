# PanificadoraRM

Sistema de gerenciamento de vendas para padaria. Desenvolvido com Flask (Python), SQLAlchemy e SQLite.

## Funcionalidades

- Autenticação com JWT (login/logout)
- Cadastro de usuários (admin e user)
- Catálogo de produtos com controle de estoque
- **Carrinho de compras** — adicione vários itens e finalize a venda de uma vez
- Histórico de vendas
- Relatórios: faturamento total, por método de pagamento e produtos mais vendidos

## Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd PanificadoraRM

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
copy .env.example .env
# Edite o .env e defina uma SECRET_KEY forte

# 5. Inicialize o banco de dados
python init_db.py

# 6. Inicie o servidor
python run.py
```

Acesse: http://127.0.0.1:5000

## Credenciais padrão (após init_db.py)

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Admin  | joao@panificadora.com | admin1234 |
| User   | maria@panificadora.com | maria1234 |
| User   | carlos@panificadora.com | carlos1234 |

> ⚠️ Troque as senhas antes de usar em produção!

## Estrutura do Projeto

```
PanificadoraRM/
├── run.py              # Ponto de entrada
├── init_db.py          # Seed do banco de dados
├── requirements.txt
├── .env                # Variáveis de ambiente (não commitar!)
├── .env.example        # Modelo de variáveis
├── utils/auth.py       # Decorator token_required (JWT)
└── app/
    ├── auth/           # Login, logout, registro
    ├── products/       # CRUD de produtos
    ├── sales/          # Vendas e itens de venda
    ├── home/           # Interface web (Jinja2)
    └── static/         # CSS (main.css)
```

## API (endpoints principais)

| Método | URL | Descrição |
|--------|-----|-----------|
| POST | /auth/entrar | Login → retorna JWT |
| POST | /auth/registrar | Cadastrar usuário |
| GET  | /api/v1/produtos/ | Listar produtos |
| POST | /api/v1/produtos/ | Criar produto (admin) |
| PUT  | /api/v1/produtos/<id> | Editar produto (admin) |
| DELETE | /api/v1/produtos/<id> | Remover produto (admin) |
| GET  | /api/v1/vendas/ | Listar vendas |
| POST | /api/v1/vendas/ | Criar venda (com múltiplos itens) |

### Exemplo: Criar venda

```json
POST /api/v1/vendas/
Authorization: Bearer <token>

{
  "payment_method": "Pix",
  "items": [
    { "product_id": "uuid-do-produto", "quantity": 3 },
    { "product_id": "uuid-do-produto", "quantity": 1 }
  ]
}
```

## Produção

Para produção, configure o `.env` com PostgreSQL:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/panificadora_db
SECRET_KEY=<chave-longa-e-aleatória>
```

Gere uma chave segura:
```python
import secrets; print(secrets.token_hex(32))
```