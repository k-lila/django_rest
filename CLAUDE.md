# CLAUDE.md — django_rest (Bookstore API)

API REST para livraria desenvolvida como projeto de portfólio com Django 5 + Django REST Framework. Deploy no Render.com.

## Visão Geral

- **URL de produção**: `https://ebac-bookstore-api.onrender.com`
- **Domínio**: gerenciamento de produtos, categorias e pedidos de livros
- **Autenticação**: pública para produtos/categorias; token obrigatório para pedidos

---

## Setup Local com Docker

**Pré-requisitos**: Docker e Docker Compose instalados.

```bash
# Subir todos os serviços (Django + PostgreSQL)
docker-compose up --build

# Rodar em background
docker-compose up -d

# Aplicar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Parar os serviços
docker-compose down
```

O serviço Django fica em `http://localhost:8000`.

**Ambiente de desenvolvimento sem Docker** (requer PostgreSQL local ou SQLite):

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

---

## Estrutura do Projeto

```
django_rest/
├── django_rest/              # Configuração principal
│   ├── settings.py           # Settings (env vars para DB, SECRET_KEY, DEBUG)
│   ├── urls.py               # Roteamento raiz com versionamento v1/v2
│   ├── wsgi.py
│   └── asgi.py
├── product/                  # App: catálogo de produtos
│   ├── models/               # Category, Product
│   ├── serializers/          # CategorySerializer, ProductSerializer
│   ├── viewsets/             # CategoryViewSet, ProductViewSet
│   ├── factories.py          # CategoryFactory, ProductFactory (para testes)
│   └── urls.py
├── order/                    # App: pedidos
│   ├── models/               # Order
│   ├── serializers/          # OrderSerializer (calcula total dinamicamente)
│   ├── viewsets/             # OrderViewSet (requer autenticação)
│   ├── factories.py          # UserFactory, OrderFactory (para testes)
│   └── urls.py
├── tests/
│   ├── models/               # test_category, test_product, test_order
│   ├── serializers/          # test_*_serializer
│   └── viewsets/             # test_*_viewset
├── .github/workflows/
│   ├── build.yml             # CI: roda testes em todo push
│   └── workflow-pr.yml       # CI: testes + wemake style check em PRs
├── dockerfile
├── docker-compose.yml
├── env.dev                   # Variáveis de ambiente para desenvolvimento local
├── pyproject.toml            # Dependências via Poetry
└── pytest.ini
```

---

## Arquitetura

### Modelos

| Modelo | App | Campos principais |
|--------|-----|-------------------|
| `Category` | product | title, slug (unique), description, active |
| `Product` | product | title, description, price (int), active, category (M2M) |
| `Order` | order | product (M2M → Product), user (FK → User, CASCADE) |

### Padrão de serializers

Todos os serializers usam campos separados para leitura e escrita em relacionamentos M2M:
- Campo de leitura: serializer aninhado (ex: `product`, `category`)
- Campo de escrita: `PrimaryKeyRelatedField` (ex: `products_id`, `categories_id`)

`OrderSerializer` calcula `total` dinamicamente somando `price` de todos os produtos associados.

### Viewsets

| ViewSet | App | Auth | Permissão |
|---------|-----|------|-----------|
| `CategoryViewSet` | product | — | Pública |
| `ProductViewSet` | product | — | Pública |
| `OrderViewSet` | order | TokenAuthentication | IsAuthenticated |

Todos são `ModelViewSet` com queryset ordenado por `id`.

### Autenticação Global (settings.py)

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
}
```

---

## Endpoints da API

### Autenticação

```
POST /api-token-auth/          → retorna token dado username+password
```

### Produtos e Categorias (públicos)

```
GET    /bookstore/v1/category/         → listar categorias (paginado, 5/página)
POST   /bookstore/v1/category/         → criar categoria
GET    /bookstore/v1/category/{id}/    → detalhe
PUT    /bookstore/v1/category/{id}/    → atualizar
DELETE /bookstore/v1/category/{id}/    → deletar

GET    /bookstore/v1/product/          → listar produtos
POST   /bookstore/v1/product/          → criar produto
GET    /bookstore/v1/product/{id}/     → detalhe
PUT    /bookstore/v1/product/{id}/     → atualizar
DELETE /bookstore/v1/product/{id}/     → deletar
```

### Pedidos (requer token)

```
GET    /bookstore/v1/order/            → listar pedidos (Authorization: Token <token>)
POST   /bookstore/v1/order/            → criar pedido
GET    /bookstore/v1/order/{id}/       → detalhe
PUT    /bookstore/v1/order/{id}/       → atualizar
DELETE /bookstore/v1/order/{id}/       → deletar
```

Todos os endpoints acima existem também em `/bookstore/v2/` (atualmente mapeados para as mesmas views).

### Exemplo de uso

```bash
# Obter token
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=admin&password=admin"

# Criar pedido
curl -X POST http://localhost:8000/bookstore/v1/order/ \
  -H "Authorization: Token <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{"products_id": [1, 2]}'
```

---

## Testes

O projeto usa **pytest** com **factory-boy** para dados de teste.

```bash
# Rodar todos os testes
poetry run pytest

# Com output verbose
poetry run pytest -v

# Testar um módulo específico
poetry run pytest tests/viewsets/test_order_viewset.py

# Também disponível (usado no CI)
poetry run python manage.py test
```

**Estrutura de testes**: cada app tem testes de modelos, serializers e viewsets. Os viewsets de `order` usam `APIClient` com header de token (`HTTP_AUTHORIZATION: Token <key>`).

**Factories disponíveis**:
- `product.factories`: `CategoryFactory`, `ProductFactory`
- `order.factories`: `UserFactory`, `OrderFactory`

---

## Variáveis de Ambiente

Configuradas via `env.dev` (desenvolvimento) e variáveis de ambiente no Render (produção).

| Variável | Padrão (dev) | Descrição |
|----------|-------------|-----------|
| `DEBUG` | `1` | Habilita modo debug (usar `0` em produção) |
| `SECRET_KEY` | `foo` | Chave secreta Django (substituir em produção) |
| `SQL_ENGINE` | `django.db.backends.postgresql` | Backend de banco |
| `SQL_DATABASE` | `bookstore_db` | Nome do banco |
| `SQL_USER` | `postgre` | Usuário do banco |
| `SQL_PASSWORD` | `postgre` | Senha do banco |
| `SQL_HOST` | `db` | Host do banco (nome do serviço Docker) |
| `SQL_PORT` | `5432` | Porta do banco |

Fallback sem variáveis: SQLite (`db.sqlite3` na raiz do projeto).

---

## CI/CD

### GitHub Actions

| Workflow | Trigger | O que faz |
|----------|---------|-----------|
| `build.yml` | push em qualquer branch | Instala deps + roda `manage.py test` |
| `workflow-pr.yml` | pull_request | Instala deps + testa + Wemake style check (continua em erro) |

---

## Comandos Úteis

```bash
# Gerenciamento de dependências
poetry add <pacote>
poetry install

# Django management
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py shell_plus        # django-extensions
poetry run python manage.py createsuperuser

# Docker
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose logs -f web
docker-compose down -v   # remove volumes também
```

---

## Bugs Conhecidos

Bugs identificados na análise do projeto — corrigir antes de evoluir funcionalidades.

### Críticos

**1. `get_total` quebra com `price=None`**
- Arquivo: `order/serializers/order_serializer.py`
- `Product.price` é `null=True`, mas `get_total` faz `sum([p.price for p in ...])` sem tratar `None`.
- Fix: `sum([p.price or 0 for p in instance.product.all()])`

**2. `OrderSerializer` não retorna `id` do pedido**
- Arquivo: `order/serializers/order_serializer.py`
- `fields = ["product", "total", "user", "products_id"]` — falta `"id"`.
- Sem o ID, o cliente não consegue referenciar o pedido criado.

**3. Credencial do banco do Render exposta no código**
- Arquivo: `django_rest/settings.py` linha 72 (comentário)
- Connection string com usuário/senha real está versionada no git.
- Ação imediata: rotacionar a senha no painel do Render e remover o comentário.

### Importantes

**4. `settings.py` define `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` duas vezes**
- Linhas 7–11: definições iniciais hardcoded — **nunca usadas**, sobrescritas pelas linhas 120–124.
- Causa confusão e pode induzir a erro de leitura. Remover as primeiras três definições.

**5. Bug na `ProductFactory` — atributo `category` duplicado**
- Arquivo: `product/factories.py`
- `category = factory.LazyAttribute(CategoryFactory)` é sobrescrito pelo `@factory.post_generation def category` na linha seguinte. O `LazyAttribute` nunca executa.
- Remover a linha 20 (`category = factory.LazyAttribute(...)`).

**6. `Category.__unicode__` é Python 2**
- Arquivo: `product/models/category.py`
- Em Python 3, o método é `__str__`. O atual nunca é chamado; `str(category)` retorna `<Category object (1)>`.
- Renomear para `__str__`.

### Menores

**7. Modelos `Product` e `Order` sem `__str__`**
- Django admin e shell ficam ilegíveis sem representação textual dos objetos.

**8. Admin com modelos importados mas não registrados**
- `product/admin.py` e `order/admin.py` importam os modelos mas não chamam `admin.site.register()`.
- O admin Django não exibe nenhum modelo do projeto.

---

## Melhorias Prioritárias

Lista ordenada por impacto para guiar as próximas sessões de trabalho.

### Prioridade 1 — Segurança e corretude
- [ ] Rotacionar senha do banco no Render e remover credencial do `settings.py`
- [ ] Corrigir `get_total` para tratar `price=None`
- [ ] Adicionar `"id"` aos `fields` do `OrderSerializer`
- [ ] Remover definições duplicadas de `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` do `settings.py`

### Prioridade 2 — Qualidade do código
- [ ] Corrigir `Category.__unicode__` → `__str__`
- [ ] Adicionar `__str__` em `Product` e `Order`
- [ ] Corrigir bug do `LazyAttribute` na `ProductFactory`
- [ ] Registrar modelos no admin (`admin.site.register`)
- [ ] Configurar `whitenoise` + `STATIC_ROOT` para produção

### Prioridade 3 — Infraestrutura e CI
- [ ] Refatorar `dockerfile`: remover `poetry init`, unificar os dois `poetry install`
- [ ] Atualizar GitHub Actions de `@v2` para `@v4`
- [ ] Unificar framework de testes: migrar viewset tests de `APITestCase` para pytest puro; atualizar CI para rodar `pytest` em vez de `manage.py test`

### Prioridade 4 — Evolução da API
- [ ] Diferenciar v1 e v2 (hoje são aliases)
- [ ] Adicionar filtro/busca nos viewsets (`filter_backends`)
- [ ] Usar `request.user` no `OrderViewSet.create` em vez de aceitar `user` no body
- [ ] Adicionar documentação automática (ex: `drf-spectacular`)

---

## Observações de Design

| Item | Situação |
|------|----------|
| `price` como `PositiveIntegerField` | Pode representar centavos; `total` retorna inteiro |
| v1 e v2 mapeiam as mesmas views | Nenhum viewset usa o parâmetro `version` capturado pela regex |
| `ALLOWED_HOSTS` hardcoded | Inclui `ebac-bookstore-api.onrender.com` e `localhost`; mover para env var |
| `Order.total` calculado dinamicamente | Mudança de preço afeta pedidos antigos — sem snapshot |
| Category/Product endpoints públicos | Qualquer pessoa pode criar e deletar dados sem autenticação |
