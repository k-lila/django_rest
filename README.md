# django_rest — Bookstore API

API REST de gerenciamento de livraria construída com Django REST Framework.

**Stack:** Python 3.12 · Django 5 · Django REST Framework 3.15 · PostgreSQL · Token Authentication · Docker

---

## Arquitetura

```
Cliente (curl / front-end)
        │
        ▼
   Django :8000         ← único ponto de entrada
   ├── /api-token-auth/     → autenticação (obtém token)
   ├── /bookstore/v1/category/  → CategoryViewSet  (público)
   ├── /bookstore/v1/product/   → ProductViewSet   (público)
   ├── /bookstore/v1/order/     → OrderViewSet     (requer token)
   └── /admin/              → Django Admin
              │
              └── PostgreSQL   (persistência)
```

---

## Pré-requisitos

| Ferramenta              | Versão mínima | Necessário para              |
| ----------------------- | ------------- | ---------------------------- |
| Docker + Docker Compose | 24+           | Execução via container       |
| Python                  | 3.10          | Execução manual              |
| Poetry                  | 1.8+          | Gerenciamento de dependências|

---

## Execução com Docker (recomendado)

```bash
# Subir Django + PostgreSQL
docker-compose up --build

# Rodar em background
docker-compose up -d

# Aplicar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Acompanhar logs
docker-compose logs -f web

# Derrubar (incluindo volumes)
docker-compose down -v
```

---

## Execução manual (sem Docker)

### 1. Dependências

```bash
poetry install
```

### 2. Banco de dados

Por padrão, sem variáveis de ambiente configuradas, o projeto usa **SQLite** (`db.sqlite3`). Para usar PostgreSQL, configure as variáveis descritas abaixo.

```bash
poetry run python manage.py migrate
```

### 3. Servidor

```bash
poetry run python manage.py runserver
```

### Variáveis de ambiente

| Variável       | Padrão (dev)                           | Descrição                       |
| -------------- | -------------------------------------- | --------------------------------|
| `DEBUG`        | `0`                                    | Ativa modo debug (`1` = ligado) |
| `SECRET_KEY`   | `foo`                                  | Chave secreta Django            |
| `SQL_ENGINE`   | `django.db.backends.sqlite3`           | Backend do banco de dados       |
| `SQL_DATABASE` | `db.sqlite3`                           | Nome do banco                   |
| `SQL_USER`     | `user`                                 | Usuário do banco                |
| `SQL_PASSWORD` | `password`                             | Senha do banco                  |
| `SQL_HOST`     | `localhost`                            | Host do banco                   |
| `SQL_PORT`     | `5432`                                 | Porta do banco                  |

No Docker, essas variáveis já estão configuradas via `env.dev`.

---

## Endpoints da API

### Autenticação

```
POST /api-token-auth/    → retorna token dado username e password
```

### Produtos e Categorias — públicos

```
GET    /bookstore/v1/category/        listar categorias (5 por página)
POST   /bookstore/v1/category/        criar categoria
GET    /bookstore/v1/category/{id}/   detalhe
PUT    /bookstore/v1/category/{id}/   atualizar
DELETE /bookstore/v1/category/{id}/   deletar

GET    /bookstore/v1/product/         listar produtos
POST   /bookstore/v1/product/         criar produto
GET    /bookstore/v1/product/{id}/    detalhe
PUT    /bookstore/v1/product/{id}/    atualizar
DELETE /bookstore/v1/product/{id}/    deletar
```

### Pedidos — requer token

```
GET    /bookstore/v1/order/           listar pedidos
POST   /bookstore/v1/order/           criar pedido
GET    /bookstore/v1/order/{id}/      detalhe
PUT    /bookstore/v1/order/{id}/      atualizar
DELETE /bookstore/v1/order/{id}/      deletar
```

Todos os endpoints estão disponíveis também em `/bookstore/v2/`.

### Exemplo de uso

```bash
# 1. Obter token
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=admin&password=admin"

# 2. Criar pedido
curl -X POST http://localhost:8000/bookstore/v1/order/ \
  -H "Authorization: Token <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{"products_id": [1, 2], "user": 1}'
```

---

## URLs de acesso

| Serviço      | URL                              |
| ------------ | -------------------------------- |
| API          | http://localhost:8000            |
| Django Admin | http://localhost:8000/admin/     |
| Debug Toolbar| http://localhost:8000/__debug__/ |

---

## Testes

```bash
# Rodar todos os testes
poetry run pytest

# Com output detalhado
poetry run pytest -v

# Testar um módulo específico
poetry run pytest tests/viewsets/test_order_viewset.py
```

Os testes usam **factory-boy** para geração de dados e cobrem modelos, serializers e viewsets.
